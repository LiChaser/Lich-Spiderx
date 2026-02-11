from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
import threading
import queue
import time
import os
import datetime

# 导入功能模块
import config
import utils
import classifier
import cracker_simple
import cracker_complex

app = Flask(__name__)

# 任务管理
class TaskManager:
    def __init__(self):
        self.current_thread = None
        self.is_running = False

    def run_task(self, target_func, task_name):
        if self.is_running:
            return False, "当前已有任务在运行中，请等待完成或停止任务"
        
        # 重置所有模块的停止标志
        self._set_stop_flag(False)

        self.is_running = True
        self.current_thread = threading.Thread(target=self._wrapper, args=(target_func, task_name))
        self.current_thread.daemon = True
        self.current_thread.start()
        return True, f"任务 [{task_name}] 已启动"

    def _wrapper(self, func, name):
        utils.logger.info(f"=== 任务开始: {name} ===")
        try:
            func()
            utils.logger.info(f"=== 任务完成: {name} ===")
        except Exception as e:
            utils.logger.error(f"任务执行出错: {e}")
        finally:
            self.is_running = False

    def stop_task(self):
        if not self.is_running:
            return False, "没有正在运行的任务"
        
        # 发送停止信号给所有模块
        self._set_stop_flag(True)
        utils.logger.warning("正在发送停止信号...")
        return True, "停止信号已发送，正在等待线程结束"

    def _set_stop_flag(self, value):
        """
        统一设置所有功能模块的停止标志
        """
        # 设置 classifier.py 的停止标志
        if hasattr(classifier, 'STOP_FLAG'):
            classifier.STOP_FLAG = value
            
        # 设置 cracker_simple.py 的停止标志
        if hasattr(cracker_simple, 'STOP_FLAG'):
            cracker_simple.STOP_FLAG = value
            
        # 设置 cracker_complex.py 的停止标志
        if hasattr(cracker_complex, 'STOP_FLAG'):
            cracker_complex.STOP_FLAG = value

task_manager = TaskManager()

# --- 路由定义 ---

@app.route('/')
def dashboard():
    # 获取 listdir 下所有的 txt 文件供用户选择
    url_files = []
    listdir_path = os.path.join(config.BASE_DIR, 'listdir')
    if os.path.exists(listdir_path):
        url_files = [f for f in os.listdir(listdir_path) if f.endswith('.txt')]
    
    return render_template('dashboard.html', active_page='dashboard', url_files=url_files)

@app.route('/assets')
def assets_page():
    return render_template('assets.html', active_page='assets',
                           simple_list=utils.load_file(config.SIMPLE_LIST_FILE),
                           complex_list=utils.load_file(config.COMPLEX_LIST_FILE),
                           unknown_list=utils.load_file(config.UNKNOWN_LIST_FILE))

@app.route('/config', methods=['GET', 'POST'])
def config_page():
    if request.method == 'POST':
        action = request.form.get('action')
        filename = request.form.get('filename')
        
        if action == 'delete':
            # 删除自定义文件 (仅限 listdir 目录下的文件)
            if filename and filename.endswith('.txt') and '/' not in filename and '\\' not in filename:
                try:
                    os.remove(os.path.join('listdir', filename))
                    utils.logger.info(f"文件 {filename} 已删除")
                except Exception as e:
                    utils.logger.error(f"删除失败: {e}")
            return redirect(url_for('config_page'))
            
        elif action == 'create':
             new_filename = request.form.get('new_filename')
             if new_filename and new_filename.endswith('.txt') and '/' not in new_filename:
                 try:
                     with open(os.path.join('listdir', new_filename), 'w', encoding='utf-8') as f:
                         f.write('')
                     utils.logger.info(f"文件 {new_filename} 已创建")
                 except Exception as e:
                     utils.logger.error(f"创建失败: {e}")
             return redirect(url_for('config_page'))

        else: # 保存内容
            content = request.form.get('content')
            
            # 安全检查：只允许修改 listdir 目录下的 txt 文件
            # 这里简单做个映射，或者允许 listdir 下的所有 txt
            target_path = os.path.join('listdir', filename)
            
            if os.path.exists(target_path) and target_path.startswith('listdir'):
                with open(target_path, 'w', encoding='utf-8') as f:
                    f.write(content.replace('\r\n', '\n')) # 统一换行符
                utils.logger.info(f"配置文件 {filename} 已更新")
            
            return redirect(url_for('config_page'))

    # 获取 listdir 下所有 txt 文件
    files = {}
    if os.path.exists('listdir'):
        for f in os.listdir('listdir'):
            if f.endswith('.txt'):
                with open(os.path.join('listdir', f), 'r', encoding='utf-8') as file:
                    files[f] = file.read()

    return render_template('config.html', active_page='config', files=files)

@app.route('/results')
def results_page():
    # 解析 results.txt
    results = []
    result_file = "results.txt"
    if os.path.exists(result_file):
        with open(result_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 2:
                    results.append({
                        "url": parts[0].strip(),
                        "cred": parts[1].strip(),
                        "time": datetime.datetime.now().strftime("%Y-%m-%d") # 模拟时间，因为txt里没存
                    })
    return render_template('results.html', active_page='results', results=results)

# --- API 接口 ---

@app.route('/api/delete_result', methods=['POST'])
def delete_result():
    try:
        action = request.form.get('action')
        result_file = "results.txt"
        
        if not os.path.exists(result_file):
             return jsonify({"status": "error", "message": "结果文件不存在"})

        if action == 'clear_all':
             with open(result_file, 'w', encoding='utf-8') as f:
                 f.write('')
             return jsonify({"status": "success", "message": "已清空所有结果"})
        
        index = int(request.form.get('index'))
        
        lines = []
        with open(result_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        if 0 <= index < len(lines):
            del lines[index]
            with open(result_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            return jsonify({"status": "success", "message": "删除成功"})
        else:
            return jsonify({"status": "error", "message": "索引超出范围"})
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/download/<filename>')
def download_file(filename):
    # 安全检查：仅允许下载 listdir 下的文件
    if '/' in filename or '\\' in filename:
        return "非法路径", 400
    
    path = os.path.join(config.BASE_DIR, 'listdir', filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    else:
        return "文件不存在", 404

@app.route('/api/start_task/<action>', methods=['POST'])
def start_task(action):
    # 获取并更新全局配置
    stop_on_success = request.form.get('stop_on_success')
    show_browser = request.form.get('show_browser')
    
    if stop_on_success is not None:
        config.STOP_ON_SUCCESS = (stop_on_success == 'true')
        utils.logger.info(f"配置更新: 发现首个密码后停止 = {config.STOP_ON_SUCCESS}")

    if show_browser is not None:
        # 如果 show_browser 为 true，则 HEADLESS 为 False
        config.HEADLESS = (show_browser != 'true')
        utils.logger.info(f"配置更新: Headless模式 = {config.HEADLESS} (显示浏览器={show_browser})")

    # 更新错误关键词
    error_keywords_str = request.form.get('error_keywords')
    if error_keywords_str:
        # 支持中英文逗号
        keywords = [k.strip() for k in error_keywords_str.replace('，', ',').split(',') if k.strip()]
        if keywords:
            config.ERROR_KEYWORDS = keywords
            utils.logger.info(f"配置更新: 错误关键词 = {config.ERROR_KEYWORDS}")

    # 更新成功关键词
    success_keywords_str = request.form.get('success_keywords')
    if success_keywords_str:
        keywords = [k.strip() for k in success_keywords_str.replace('，', ',').split(',') if k.strip()]
        if keywords:
            config.SUCCESS_KEYWORDS = keywords
            utils.logger.info(f"配置更新: 成功关键词 = {config.SUCCESS_KEYWORDS}")

    # 处理自定义 URL 列表
    custom_url_list = request.form.get('custom_url_list')
    if custom_url_list and custom_url_list != 'default':
        target_path = os.path.join(config.BASE_DIR, 'listdir', custom_url_list)
        if os.path.exists(target_path):
             # 临时覆盖全局配置中的路径，注意这对所有任务生效
             # 更优雅的做法是传参给 run_task，但为了最小改动，这里修改 config
             if action == 'simple_crack':
                 config.SIMPLE_LIST_FILE = target_path
                 utils.logger.info(f"配置更新: 简单爆破将使用自定义列表 -> {target_path}")
             elif action == 'complex_crack':
                 config.COMPLEX_LIST_FILE = target_path
                 utils.logger.info(f"配置更新: 复杂爆破将使用自定义列表 -> {target_path}")
             elif action == 'classify':
                 config.URL_LIST_FILE = target_path
                 utils.logger.info(f"配置更新: 分类任务将使用自定义列表 -> {target_path}")
        else:
            utils.logger.warning(f"自定义列表文件不存在: {target_path}，将使用默认逻辑")

    if action == 'classify':
        success, msg = task_manager.run_task(classifier.classify_targets, "资产分类")
    elif action == 'simple_crack':
        success, msg = task_manager.run_task(cracker_simple.run_simple_crack, "简单爆破")
    elif action == 'complex_crack':
        success, msg = task_manager.run_task(cracker_complex.run_complex_crack, "复杂爆破")
    else:
        return jsonify({"status": "error", "message": "未知指令"}), 400
    
    return jsonify({"status": "success" if success else "error", "message": msg})

@app.route('/api/stop_task', methods=['POST'])
def stop_task():
    success, msg = task_manager.stop_task()
    return jsonify({"status": "success" if success else "error", "message": msg})

@app.route('/api/logs')
def get_logs():
    logs = []
    # 从队列中取出所有现有日志
    while not utils.log_queue.empty():
        try:
            logs.append(utils.log_queue.get_nowait())
        except queue.Empty:
            break
    return jsonify({"logs": logs})

@app.route('/api/stats')
def get_stats():
    # 统计各个文件的行数
    def count_lines(filepath):
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return sum(1 for line in f if line.strip())
        return 0

    stats = {
        "total": count_lines(config.URL_LIST_FILE),
        "simple": count_lines(config.SIMPLE_LIST_FILE),
        "complex": count_lines(config.COMPLEX_LIST_FILE),
        "success": count_lines("results.txt")
    }
    return jsonify(stats)

@app.route('/api/task_status')
def task_status():
    return jsonify({"running": task_manager.is_running})

if __name__ == '__main__':
    utils.logger.info("Web 服务器启动: http://127.0.0.1:5000")
    # debug=True 在 Windows 多线程下可能有问题，建议设为 False
    app.run(host='0.0.0.0', port=5000, debug=False)
