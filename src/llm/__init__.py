"""
这个模块包含与大语言模型交互的各种实现
"""

import inspect

from langchain_core.language_models.chat_models import BaseChatModel

from basic import Register
from logs import get_logger


class LlmRegister(Register[BaseChatModel]):
    """
    大语言模型注册表
    """

    def __init__(self):
        super().__init__()


default_register = LlmRegister()

llm_logger = get_logger("llm")


def register(cls):
    """
    装饰器，用于将大语言模型注册到全局变量中
    """
    bean_name = cls.__name__
    try:
        sig = inspect.signature(cls)
        llm_logger.debug(f"Registering LLM: {bean_name}")
        default_register.validate_name(bean_name)
        context = {'logger': get_logger(f'llm-{bean_name}')}
        instance = cls(**context)
        default_register.register(bean_name, instance)
        llm_logger.info(f"Registered LLM: {bean_name}")
    except ValueError as e:
        llm_logger.error(f"Failed to register LLM: {bean_name}", e)
        raise e
    return cls
