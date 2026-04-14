# python-ai-service/src/core/logging.py
import sys
from loguru import logger


def setup_logger():
    """配置日志"""
    logger.remove()

    # 控制台输出
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )

    # 文件输出
    logger.add(
        "logs/ehs-{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="7 days",
        level="DEBUG"
    )

    return logger


log = setup_logger()
