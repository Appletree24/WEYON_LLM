from typing import Dict, Generic, TypeVar
import inspect

T = TypeVar("T")


def get_dir(file_path):
    from os import path
    file_path = path.abspath(file_path)
    return path.dirname(file_path)


class Context(Dict[str, T]):
    def fork(self):
        """
        复制一份
        :return:
        """
        return Context(self)


class ConfigurationContext(Context[T]):
    def __init__(self, file_name):
        super().__init__()
        config = self.parse(file_name)
        self.update(config)

    def parse(self, file_name: str):
        import yaml
        with open(file_name, 'r') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        if config.get('profiles', None):
            if config['profiles'].get('includes', None):
                from os import path
                base_path = get_dir(file_name)
                profiles = config['profiles']['includes']
                for profile in profiles:
                    abs_path = path.join(base_path, profile)
                    config.update(self.parse(abs_path))
        return config


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
            raise ValueError(f"{name} has registered")

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


config = ConfigurationContext(get_dir(__file__) + '/../../resources/application.yaml')

default_context = Register(config)
