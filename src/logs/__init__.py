import logging
from enum import Enum

from .log_config import __console_handle, __file_handle


class LogLevel(Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


__all_logs = {}


def get_logger(name: str = ''
               , level: LogLevel = LogLevel.INFO
               , output_file=None):
    if name in __all_logs:
        return __all_logs[name]
    logger = logging.getLogger(name)
    logger.setLevel(level.value)
    if not logger.hasHandlers():
        __console_handle(logger)
    if output_file:
        __file_handle(logger, output_file)
    __all_logs[name] = logger
    return logger
