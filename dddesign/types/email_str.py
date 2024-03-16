from typing import Any

from pydantic.networks import EmailStr as PydanticEmailStr

from dddesign.structure.domains.types.base_type import BaseType


class EmailStr(PydanticEmailStr, BaseType):
    @classmethod
    def validate(cls, value: Any) -> 'EmailStr':
        if isinstance(value, str):
            value = value.lower().strip()
        return cls(super().validate(value))
