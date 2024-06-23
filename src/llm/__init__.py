"""
这个模块包含与大语言模型交互的各种实现
"""

from langchain_core.language_models.chat_models import BaseChatModel

import basic
from logs import get_logger


default_register = basic.default_context

llm_logger = get_logger("llm")


def register(cls):
    """
    装饰器，用于将大语言模型注册到全局变量中
    """
    bean_name = cls.__name__
    try:
        llm_logger.debug(f"Registering LLM: {bean_name}")
        default_register.validate_name(bean_name)
        ctx = {'logger': get_logger(f'llm-{bean_name}')}
        default_register.register(cls, ctx)
        llm_logger.info(f"Registered LLM: {bean_name}")
    except ValueError as e:
        llm_logger.error(f"Failed to register LLM: {bean_name}", e)
        raise e
    return cls
