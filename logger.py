import logging
import logging.handlers
import os

def setup_logger(display_name: str, log_level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(display_name)
    logger.setLevel(log_level)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s", 
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{display_name}.log")
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger