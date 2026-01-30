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

    for url in urls:
        if STOP_FLAG:
            logger.warning("任务已停止")
            return

        if not url.startswith('http'):
            url = 'http://' + url
            
        try:
            logger.info(f"正在分析: {url}")
            resp = requests.get(url, timeout=config.TIMEOUT, verify=False)
            
            # 基础判断：必须包含密码输入框
            if 'type="password"' not in resp.text and "type='password'" not in resp.text:
                logger.info(f"归入未知: {url} (未发现密码输入框)")
                unknown_list.append(f"{url} | 未发现密码框")
                continue

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
