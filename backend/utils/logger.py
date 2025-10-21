import logging
import os
from datetime import datetime


def setup_logger():
    """Logger kurulumu"""

    # Logs dizini oluştur
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Logger formatı
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # File handler
    log_file = os.path.join(log_dir, f"friendzone_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(log_format))

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(logging.Formatter(log_format))

    # Root logger'ı yapılandır
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# Global logger instance
logger = setup_logger()