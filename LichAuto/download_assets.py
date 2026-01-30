import requests
import os

# 目标文件及其下载地址
assets = {
    "static/vendor/css/bootstrap.min.css": "https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/5.1.3/css/bootstrap.min.css",
    "static/vendor/css/all.min.css": "https://cdn.bootcdn.net/ajax/libs/font-awesome/6.0.0/css/all.min.css",
    "static/vendor/js/jquery.min.js": "https://cdn.bootcdn.net/ajax/libs/jquery/3.6.0/jquery.min.js",
    "static/vendor/js/bootstrap.bundle.min.js": "https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/5.1.3/js/bootstrap.bundle.min.js",
    "static/vendor/js/chart.min.js": "https://cdn.bootcdn.net/ajax/libs/Chart.js/3.7.0/chart.min.js",
    # 补全缺失的字体文件
    "static/vendor/webfonts/fa-solid-900.woff2": "https://cdn.bootcdn.net/ajax/libs/font-awesome/6.0.0/webfonts/fa-solid-900.woff2",
    "static/vendor/webfonts/fa-solid-900.ttf": "https://cdn.bootcdn.net/ajax/libs/font-awesome/6.0.0/webfonts/fa-solid-900.ttf",
    "static/vendor/webfonts/fa-regular-400.woff2": "https://cdn.bootcdn.net/ajax/libs/font-awesome/6.0.0/webfonts/fa-regular-400.woff2",
    "static/vendor/webfonts/fa-regular-400.ttf": "https://cdn.bootcdn.net/ajax/libs/font-awesome/6.0.0/webfonts/fa-regular-400.ttf"
}

print("开始下载静态资源...")
# 确保目录存在
os.makedirs("static/vendor/webfonts", exist_ok=True)

for path, url in assets.items():
    try:
        print(f"正在下载: {url} -> {path}")
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            with open(path, "wb") as f:
                f.write(resp.content)
            print("下载成功!")
        else:
            print(f"下载失败: 状态码 {resp.status_code}")
    except Exception as e:
        print(f"下载出错: {e}")

print("资源下载完成。")
