"""
这个模块包含与向量数据库交互的各种实现
"""

import basic
from logs import get_logger

default_register = basic.default_context

vector_logger = get_logger("vector store")


def register(cls):
    """
    用于将大语言模型注册到全局上下文
    """
    bean_name = cls.__name__
    try:
        vector_logger.debug(f"Registering Vector Store: {bean_name}")
        default_register.validate_name(bean_name)
        ctx = {'logger': get_logger(f'vs-{bean_name}')}
        default_register.register(cls, ctx)
        vector_logger.info(f"Registered Vector Store: {bean_name}")
    except ValueError as e:
        vector_logger.error(f"Failed to register Vector Store: {bean_name}", e)
        raise e
    return cls
