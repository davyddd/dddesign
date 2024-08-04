import inspect
from typing import Generator, Set

from pydantic import BaseModel, ConfigDict


class Repository(BaseModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    ALLOWED_METHODS: Set[str] = {'get', 'get_list', 'create', 'update', 'delete'}

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs):
        super().__pydantic_init_subclass__(**kwargs)

        allowed_methods = cls.model_fields['ALLOWED_METHODS'].get_default()
        methods: Generator[str, ..., ...] = (name for name, member in cls.__dict__.items() if inspect.isfunction(member))

        for method in methods:
            if method.startswith('__') and method.endswith('__'):
                continue

            if method not in allowed_methods:
                raise TypeError(f'Method name `{method}` does not allowed')
