import logging
from logging.handlers import RotatingFileHandler
import sys

class Logger:
              
    def rotating_file_logger(name, path, log_count=2, max_size_mb=5, level="debug"):
        log_levels = {"debug":logging.DEBUG,"info":logging.INFO,
                      "warning":logging.WARNING,"error":logging.ERROR,
                      "critical":logging.CRITICAL}
        formatter = logging.Formatter(fmt="%(asctime)s %(levelname)-8s %(message)s",
                                      datefmt="%Y-%m-%d %H:%M:%S")
        handler = RotatingFileHandler(path, mode="a", maxBytes=max_size_mb*1024*1024, backupCount=log_count, encoding=None, delay=0)
        handler.setFormatter(formatter)
        screen_handler = logging.StreamHandler(stream=sys.stdout)
        screen_handler.setFormatter(formatter)
        logger = logging.getLogger(name)
        logger.setLevel(log_levels[level])
        logger.addHandler(handler)
        logger.addHandler(screen_handler)
        return logger

    def screen_logger(name, level="debug"):
        log_levels = {"debug":logging.DEBUG,"info":logging.INFO,
                      "warning":logging.WARNING,"error":logging.ERROR,
                      "critical":logging.CRITICAL}
        formatter = logging.Formatter(fmt="%(asctime)s %(levelname)-8s %(message)s",
                                      datefmt="%Y-%m-%d %H:%M:%S")
        screen_handler = logging.StreamHandler(stream=sys.stdout)
        screen_handler.setFormatter(formatter)
        logger = logging.getLogger(name)
        logger.setLevel(log_levels[level])
        logger.addHandler(screen_handler)
        return logger
