import inspect
from typing import Generator, Set

from pydantic import BaseModel


class Repository(BaseModel):
    ALLOWED_METHODS: Set[str] = {'get', 'get_list', 'create', 'update', 'delete'}

    class Config:
        allow_mutation = False
        arbitrary_types_allowed = True

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        allowed_methods = cls.__fields__['ALLOWED_METHODS'].get_default()
        methods: Generator[str, ..., ...] = (name for name, member in cls.__dict__.items() if inspect.isfunction(member))

        for method in methods:
            if method not in allowed_methods:
                raise TypeError(f'Method name `{method}` does not allowed')
