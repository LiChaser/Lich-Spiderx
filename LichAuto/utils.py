import logging
import queue
import logging.handlers

# 创建一个全局的日志队列，供Web端消费
log_queue = queue.Queue()

class QueueHandler(logging.Handler):
    """
    自定义日志处理器，将日志放入队列
    """
    def emit(self, record):
        try:
            msg = self.format(record)
            log_queue.put(msg)
            # 保持队列不过大，只保留最近1000条
            if log_queue.qsize() > 1000:
                try:
                    log_queue.get_nowait()
                except queue.Empty:
                    pass
        except Exception:
            self.handleError(record)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('LichAuto')

# 添加队列处理器
queue_handler = QueueHandler()
queue_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(queue_handler)

# 全局初始化 OCR 引擎，避免每次调用重复加载模型导致卡顿
ocr_engine = None
def init_ocr():
    global ocr_engine
    if ocr_engine is None:
        try:
            import ddddocr
            ocr_engine = ddddocr.DdddOcr(show_ad=False)
            logger.info("OCR 引擎初始化完成")
        except Exception as e:
            logger.error(f"OCR 引擎初始化失败: {e}")

def get_ocr_result(image_bytes):
    """
    使用 ddddocr 识别验证码
    """
    global ocr_engine
    if not ocr_engine:
        init_ocr()
        
    if not ocr_engine:
        return ""
        
    try:
        res = ocr_engine.classification(image_bytes)
        logger.info(f"验证码识别结果: {res}")
        return res
    except Exception as e:
        logger.error(f"验证码识别失败: {e}")
        return ""

def load_file(filepath):
    """
    读取文件内容为列表
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logger.warning(f"文件未找到: {filepath}")
        return []
