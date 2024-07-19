"""
这个模块包含与大语言模型交互的各种实现
"""

import basic
from logs import get_logger

default_register = basic.default_context

chain_logger = get_logger("chain")


def register(cls):
    """
    用于将大语言模型注册到全局上下文
    """
    bean_name = cls.__name__
    try:
        chain_logger.debug(f"Registering chain: {bean_name}")
        default_register.validate_name(bean_name)
        ctx = {'logger': get_logger(f'chain-{bean_name}')}
        default_register.register(cls, ctx)
        chain_logger.info(f"Registered chain: {bean_name}")
    except ValueError as e:
        chain_logger.error(f"Failed to register chain: {bean_name}", e)
        raise e
    return cls
