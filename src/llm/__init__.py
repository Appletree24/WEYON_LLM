"""
这个模块包含与大语言模型交互的各种实现
"""

from basic import Register


class LlmRegister(Register):
    """
    大语言模型注册表
    """

    def __init__(self):
        super().__init__()


default_llm_context = LlmRegister()


def llm(cls):
    """
    装饰器，用于将大语言模型注册到全局变量中
    """
    bean_name = cls.__name__
    try:
        instance = cls()
        default_llm_context.register(instance, bean_name)
    except Exception as e:
        raise e

    return cls
