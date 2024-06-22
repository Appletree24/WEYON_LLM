from typing import Dict, Generic, TypeVar

T = TypeVar("T")


class Register(Dict[str, T], Generic[T]):

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

    def register(self, name: str, value: T):
        self.validate_name(name)
        self[name] = value

    def get_bean(self, name: str):
        return self.get(name, None)
