from typing import Dict


class Register(Dict):
    def register(self, name: str, value):
        if (name is not None
                and len(name) > 0
                and name in self):
            raise ValueError(f"{name} already registered")
        self[name] = value
