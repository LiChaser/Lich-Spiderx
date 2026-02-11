import requests
from bs4 import BeautifulSoup
import config
from utils import logger
import urllib3

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 全局停止标志
STOP_FLAG = False

def classify_targets():
    """
    读取 URL 列表，识别登录页，并分类为简单/复杂/未知目标
    """
    global STOP_FLAG
    logger.info("开始进行目标分类...")
    
    urls = []
    try:
        with open(config.URL_LIST_FILE, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logger.error(f"URL 列表文件未找到: {config.URL_LIST_FILE}")
        return

    simple_list = []
    complex_list = []
    unknown_list = [] # 存储无法访问或未识别出登录框的目标

import concurrent.futures

# ... (Previous imports)

def process_url(url, simple_list, complex_list, unknown_list):
    """
    处理单个 URL 的分类逻辑
    """
    global STOP_FLAG
    if STOP_FLAG: return

    if not url.startswith('http'):
        url = 'http://' + url
        
    try:
        logger.info(f"正在分析: {url}")
        resp = requests.get(url, timeout=config.TIMEOUT, verify=False)
        
        # 使用 BeautifulSoup 解析，更准确
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 查找密码框 (input type="password")
        password_input = soup.find('input', {'type': 'password'})
        
        if not password_input:
            logger.info(f"归入未知: {url} (未发现密码输入框)")
            unknown_list.append(f"{url} | 未发现密码框")
            return

        html_content = resp.text.lower()
        is_complex = False

        # 检查加密关键词
        for keyword in config.ENCRYPTION_KEYWORDS:
            if keyword in html_content:
                is_complex = True
                logger.info(f"发现加密特征 [{keyword}]: {url}")
                break
        
        if is_complex:
            complex_list.append(url)
        else:
            simple_list.append(url)

    except Exception as e:
        logger.error(f"无法访问 {url}: {e}")
        unknown_list.append(f"{url} | 访问失败: {str(e)}")

def classify_targets():
    """
    读取 URL 列表，识别登录页，并分类为简单/复杂/未知目标
    """
    global STOP_FLAG
    logger.info("开始进行目标分类...")
    
    urls = []
    try:
        with open(config.URL_LIST_FILE, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logger.error(f"URL 列表文件未找到: {config.URL_LIST_FILE}")
        return

    # 使用线程安全的数据结构或在主线程汇总并不方便，这里简单使用列表
    # 由于 append 操作在 CPython 中是原子性的(GIL)，对于简单列表追加通常是安全的
    # 但为了严谨，可以使用 Manager 或者在结束时汇总。鉴于这是简单脚本，直接用列表。
    simple_list = []
    complex_list = []
    unknown_list = [] 

    # 使用线程池并发处理
    with concurrent.futures.ThreadPoolExecutor(max_workers=config.THREADS) as executor:
        futures = [executor.submit(process_url, url, simple_list, complex_list, unknown_list) for url in urls]
        # 等待所有任务完成
        concurrent.futures.wait(futures)

    # 保存结果
    with open(config.SIMPLE_LIST_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(simple_list))
    
    with open(config.COMPLEX_LIST_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(complex_list))
        
    with open(config.UNKNOWN_LIST_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(unknown_list))

    logger.info(f"分类完成! 简单目标: {len(simple_list)}, 复杂目标: {len(complex_list)}, 未知/失败: {len(unknown_list)}")

if __name__ == '__main__':
    classify_targets()
