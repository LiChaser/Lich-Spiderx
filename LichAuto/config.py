import os

# 获取当前文件所在目录的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 目标 URL 列表文件
URL_LIST_FILE = os.path.join(BASE_DIR, 'listdir', 'url.txt')

# 分类结果文件
SIMPLE_LIST_FILE = os.path.join(BASE_DIR, 'listdir', 'simple_list.txt')
COMPLEX_LIST_FILE = os.path.join(BASE_DIR, 'listdir', 'complex_list.txt')
UNKNOWN_LIST_FILE = os.path.join(BASE_DIR, 'listdir', 'unknown_list.txt')

# 字典配置
USERNAME_FILE = os.path.join(BASE_DIR, 'listdir', 'usernames.txt')
PASSWORD_FILE = os.path.join(BASE_DIR, 'listdir', 'passwords.txt')

# 默认字典 (如果没有文件则使用这些)
DEFAULT_USERNAMES = ['admin', 'root', 'user', 'test']
DEFAULT_PASSWORDS = ['123456', 'password', 'admin123', '12345678']

# 加密/复杂页面判定关键词
ENCRYPTION_KEYWORDS = [
    'encrypt', 'rsa', 'aes', 'md5', 'crypto', 
    'security.js', 'jsencrypt', 'login.js'
]

# 请求配置
TIMEOUT = 10
THREADS = 3 # 降低默认线程数，防止卡死


# Playwright 配置
HEADLESS = True  # 是否无头模式 (False 为显示浏览器，方便调试)

# 爆破策略
STOP_ON_SUCCESS = True # 默认开启：发现首个成功密码后，跳过当前用户的后续密码尝试

# 错误关键词 (用于判断登录失败)
ERROR_KEYWORDS = ['error', 'fail', 'incorrect', 'invalid', '重试', '错误', '失败', '账号', '密码', '密码错误', '登录失败']

# 成功关键词 (用于判断登录成功 - 强特征)
SUCCESS_KEYWORDS = ['success', 'welcome', 'admin', 'dashboard', '成功', '欢迎', '退出', 'logout']