import classifier
import cracker_simple
import cracker_complex
from utils import logger
import sys

def main():
    try:
        logger.info("=== LichAuto 自动化渗透工具启动 ===")
        
        # 1. 资产分类
        logger.info("\n>>> 阶段 1: 资产分类与识别")
        classifier.classify_targets()
        
        # 2. 简单爆破
        logger.info("\n>>> 阶段 2: 简单模式爆破 (Requests)")
        cracker_simple.run_simple_crack()
        
        # 3. 复杂爆破
        logger.info("\n>>> 阶段 3: 复杂模式爆破 (Playwright)")
        try:
            cracker_complex.run_complex_crack()
        except KeyboardInterrupt:
            # 这里的 KeyboardInterrupt 通常会被 cracker_complex 内部捕获
            # 但如果在此处被捕获，我们也需要优雅退出
            logger.warning("\n用户在主流程中终止了程序。")
        except Exception as e:
            logger.error(f"复杂模式运行时发生错误 (可能未安装浏览器): {e}")
            logger.info("提示: 请先运行 `playwright install` 安装浏览器驱动")
        
        logger.info("\n=== 所有任务执行完毕 ===")

    except KeyboardInterrupt:
        logger.warning("\n!!! 程序被用户强制中断 (Ctrl+C) !!!")
        sys.exit(0)

if __name__ == '__main__':
    main()
