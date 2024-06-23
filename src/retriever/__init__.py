"""
这个模块包含与Retriever的各种实现
"""

import basic
from logs import get_logger

default_register = basic.default_context

ret_logger = get_logger("ret")


def register(cls):
    """
    用于将Retriever注册到全局上下文
    """
    bean_name = cls.__name__
    try:
        ret_logger.debug(f"Registering Retriever: {bean_name}")
        default_register.validate_name(bean_name)
        ctx = {'logger': get_logger(f'ret-{bean_name}')}
        default_register.register(cls, ctx)
        ret_logger.info(f"Registered Retriever: {bean_name}")
    except ValueError as e:
        ret_logger.error(f"Failed to register Retriever: {bean_name}", e)
        raise e
    return cls
