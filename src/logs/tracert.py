"""
用于跟踪函数执行的函数装饰器
"""

import functools

from logs import get_logger

logger = get_logger(__name__)


def input(func):
    """
    Decorator to log function inputs.
    :param func:
    :return:
    """

    @functools.wraps(func)
    def function_input(*args, **kwargs):
        logger.info(f"Function {func.__name__} called with args: {args} and kwargs: {kwargs}")
        result = func(*args, **kwargs)
        return result

    return function_input


def output(func):
    """
    Decorator to log function outputs.
    :param func:
    :return:
    """

    @functools.wraps(func)
    def function_output(*args, **kwargs):
        result = func(*args, **kwargs)
        logger.info(f"Function {func.__name__} returned: {result}")
        return result

    return function_output


def time(func):
    """
    Decorator to log function execution time.
    :param func:
    :return:
    """

    @functools.wraps(func)
    def function_time(*args, **kwargs):
        import datetime as dt
        start_time = dt.datetime.now()
        result = func(*args, **kwargs)
        end_time = dt.datetime.now()
        execution_time = end_time - start_time
        logger.info(f"Function {func.__name__} executed in {execution_time.microseconds} ms")
        return result

    return function_time
