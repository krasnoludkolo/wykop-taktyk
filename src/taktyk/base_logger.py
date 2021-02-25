import logging
from logging import FileHandler
from logging.handlers import TimedRotatingFileHandler

logger = logging.getLogger('wykop_taktyk')
logger.setLevel(logging.DEBUG)


def add_console_logger(level):
    ch = logging.StreamHandler()
    ch.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def add_file_logger(filename, level):
    ch = TimedRotatingFileHandler(filename, when='d', interval=1, backupCount=5)
    ch.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def add_error_file_logger(filename):
    ch = FileHandler(filename)
    ch.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
