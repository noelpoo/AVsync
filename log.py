import os
from logging import getLogger, INFO, DEBUG, Formatter, StreamHandler, FileHandler

logger = getLogger(name='default')

handler = StreamHandler()
debuggable = os.getenv('DEBUG', None) is not None
display_log_level = DEBUG if debuggable else INFO
handler.setLevel(display_log_level)
default_fmt = Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(default_fmt)
logger.addHandler(handler)
logger.setLevel(display_log_level)

default_log_level = INFO


def set_log_file(file_name):
    fh = FileHandler(file_name)
    fh.setLevel(display_log_level)
    file_log_formatter = Formatter('%(asctime)s [%(levelname)s] %(name)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    fh.setFormatter(file_log_formatter)
    logger.addHandler(fh)


def set_logger_name(name):
    logger.name = name


def set_default_log_lv(lv):
    global default_log_level
    default_log_level = lv


def set_formater(fmt):
    handler.setFormatter(fmt)


def log(msg):
    exc_info = 1 if isinstance(msg, Exception) else 0
    logger.log(default_log_level, msg, exc_info=exc_info)


def debug(msg):
    exc_info = 1 if isinstance(msg, Exception) else 0
    logger.debug(msg, exc_info=exc_info)


def info(msg):
    exc_info = 1 if isinstance(msg, Exception) else 0
    logger.info(msg, exc_info=exc_info)


def warn(msg):
    exc_info = 1 if isinstance(msg, Exception) else 0
    logger.warning(msg, exc_info=exc_info)


def error(msg):
    exc_info = 1 if isinstance(msg, Exception) else 0
    logger.error(msg, exc_info=exc_info)
