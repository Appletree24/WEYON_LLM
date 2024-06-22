from typing import Dict, Generic, TypeVar
import inspect

T = TypeVar("T")


class Context(Dict[str, T]):
    def fork(self):
        """
        复制一份
        :return:
        """
        return Context(self)


def _create_bean(cls, ctx: Dict):
    """
    创建bean
    :param cls: 类或者方法
    :param ctx: 上下文，会自动填充参数
    :return: 创建的实例
    """
    sig = inspect.signature(cls)
    context = {}
    for parameter in sig.parameters:
        if parameter.startswith('**'):
            return cls(**ctx)
        else:
            context[parameter] = ctx.get(parameter, None)

    return cls(**context)


class Register(Context[T]):

    def validate_name(self, name: str):
        """
        校验名称是否合法
        :param name:
        :return:
        :raise ValueError: 名字不合法
        """
        if not isinstance(name, str):
            raise ValueError(f"{name} is not a string")
        if not name:
            raise ValueError(f"{name} is empty")
        if name in self:
            raise ValueError(f"{name} not registered")

    def register(self, cls, contexts: Dict = None):
        name = cls.__name__
        self.validate_name(name)
        if contexts is not None:
            ctx = self.fork()
            ctx.update(contexts)
        else:
            ctx = self
        instance = _create_bean(cls, ctx)
        self.validate_name(name)
        self[name] = instance

    def get_bean(self, name: str):
        return self.get(name, None)
