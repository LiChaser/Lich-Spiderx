# LichAuto1
模拟爬虫爆破登录AI手搓版备份...
README都不用自己写，比我想破脑袋的好

# LichAuto - 自动化爆破工具

LichAuto 是一个基于 Python Flask 和 Playwright 的自动化爆破工具，旨在帮助安全研究人员和渗透测试人员对 Web 应用程序的登录页面进行自动化测试。它支持对简单登录表单进行字典爆破，也能处理包含验证码、JS 加密等复杂登录流程的页面。

## 主要功能

*   **资产分类 (Classifier)**：
    *   根据 URL 特征（如是否包含加密关键词、是否存在密码输入框）将目标 URL 智能分类为“简单爆破”、“复杂爆破”或“未知”。
    *   帮助用户快速识别不同类型的登录页面，以便选择合适的爆破策略。

*   **简单爆破 (Simple Cracker)**：
    *   针对不含验证码或复杂加密的登录页面，通过 HTTP 请求进行高效字典爆破。
    *   支持自定义错误关键词和成功关键词，以精确判断登录结果。

*   **复杂爆破 (Complex Cracker)**：
    *   利用 Playwright 自动化浏览器，模拟用户行为，处理包含验证码（支持 OCR 识别）、JS 加密、动态表单等复杂登录流程的爆破任务。
    *   支持无头模式（Headless）和可视化模式（Show Browser），方便调试和观察。

*   **直观的 Web 界面 (Dashboard)**：
    *   提供用户友好的 Web 界面，用于管理目标 URL 列表、配置爆破参数、查看实时日志和爆破结果。
    *   所有操作均可通过浏览器完成，无需命令行交互。

*   **自定义 URL 列表管理**：
    *   用户可以在 Web 界面上传、创建、编辑和删除自定义 URL 列表文件。
    *   灵活管理爆破目标，支持针对不同场景的测试。

*   **结果管理**：
    *   清晰展示爆破成功的凭据（URL、用户名、密码）。
    *   支持清空历史爆破结果。

## 技术栈

*   **后端框架**：Python 3.x, Flask
*   **前端技术**：HTML, CSS, JavaScript
*   **浏览器自动化**：Playwright (Python)
*   **OCR 识别**：用于验证码识别 (通过 `utils.py` 中的 `get_ocr_result` 函数调用)
*   **HTTP 请求**：`requests` 库
*   **HTML 解析**：`BeautifulSoup`

## 安装

1.  **克隆仓库**：
    ```bash
    git clone https://github.com/your-username/LichAuto.git
    cd LichAuto/LichAuto
    ```
    *(请将 `https://github.com/your-username/LichAuto.git` 替换为实际的仓库地址)*

2.  **安装 Python 依赖**：
    ```bash
    pip install -r requirements.txt
    ```
    *(如果 `requirements.txt` 不存在，请手动安装以下依赖：`Flask`, `requests`, `beautifulsoup4`, `playwright`, `urllib3`, `Pillow`, `pytesseract` 等)*

3.  **安装 Playwright 浏览器驱动**：
    ```bash
    playwright install
    ```
    这将安装 Chromium, Firefox 和 WebKit 浏览器驱动。

## 使用方法

1.  **启动 Flask 应用**：
    在项目根目录（`LichAuto/LichAuto`）下运行：
    ```bash
    python app.py
    ```
    应用启动后，你将在控制台看到类似 `Web 服务器启动: http://127.0.0.1:5000` 的提示。

2.  **访问 Web 界面**：
    在浏览器中打开 `http://127.0.0.1:5000`。

3.  **配置与操作**：
    *   **Dashboard (仪表盘)**：查看任务状态、实时日志和统计信息。
    *   **Assets (资产)**：管理目标 URL 列表（`url.txt`, `simple_list.txt`, `complex_list.txt`, `unknown_list.txt`）。
    *   **Config (配置)**：管理字典文件（`usernames.txt`, `passwords.txt`）和自定义 URL 列表。你可以在这里创建、编辑和删除 `.txt` 文件。
    *   **Results (结果)**：查看爆破成功的凭据。

4.  **启动任务**：
    在 Dashboard 页面，你可以选择并启动“资产分类”、“简单爆破”或“复杂爆破”任务。在启动任务前，请确保已配置好目标 URL 列表和字典文件。

## 配置说明

所有核心配置项都集中在 `config.py` 文件中。大部分配置项也可以通过 Web 界面进行动态修改。

*   `BASE_DIR`：项目根目录。
*   `URL_LIST_FILE`：原始目标 URL 列表文件路径。
*   `SIMPLE_LIST_FILE`, `COMPLEX_LIST_FILE`, `UNKNOWN_LIST_FILE`：分类后的 URL 列表文件路径。
*   `USERNAME_FILE`, `PASSWORD_FILE`：字典文件路径。
*   `DEFAULT_USERNAMES`, `DEFAULT_PASSWORDS`：如果字典文件为空，则使用这些默认值。
*   `ENCRYPTION_KEYWORDS`：用于判断页面是否包含加密特征的关键词。
*   `TIMEOUT`：HTTP 请求超时时间。
*   `THREADS`：复杂爆破任务的并发线程数。
*   `HEADLESS`：Playwright 是否以无头模式运行 (True 为无头，False 为显示浏览器)。
*   `STOP_ON_SUCCESS`：是否在发现首个成功凭据后停止当前用户的爆破。
*   `ERROR_KEYWORDS`：用于判断登录失败的关键词列表。
*   `SUCCESS_KEYWORDS`：用于判断登录成功的关键词列表（强特征）。

## 贡献

欢迎提交 Pull Request 或报告 Bug。

## 许可证

[待定，请根据实际情况添加许可证信息，例如 MIT, Apache 2.0 等]
