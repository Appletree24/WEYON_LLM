"""
这个模块包含嵌入模块的的各种实现

嵌入模块指的是将自然语言转换为向量的模块
"""

import basic
from logs import get_logger

default_register = basic.default_context

embed_logger = get_logger("embed")


def register(cls):
    """
    用于将嵌入模型注册到全局上下文
    """
    bean_name = cls.__name__
    try:
        embed_logger.debug(f"Registering Embedding: {bean_name}")
        default_register.validate_name(bean_name)
        ctx = {'logger': get_logger(f'embed-{bean_name}')}
        default_register.register(cls, ctx)
        embed_logger.info(f"Registered Embedding: {bean_name}")
    except ValueError as e:
        embed_logger.error(f"Failed to register Embedding: {bean_name}", e)
        raise e
    return cls
