from enum import Enum
from typing import Any


class BaseEnum(Enum):
    def __str__(self):
        return str(self.value)

    @classmethod
    def has_value(cls, value: Any) -> bool:
        return value in cls._value2member_map_
