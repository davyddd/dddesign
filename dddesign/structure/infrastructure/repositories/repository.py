import inspect
from typing import Optional, Set

from pydantic import BaseModel, ConfigDict

BASE_ALLOWED_METHODS = {'get', 'get_list', 'create', 'update', 'delete'}


class Repository(BaseModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    EXTERNAL_ALLOWED_METHODS: Optional[Set[str]] = None

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs):
        super().__pydantic_init_subclass__(**kwargs)

        allowed_methods = BASE_ALLOWED_METHODS
        external_allowed_methods = cls.model_fields['EXTERNAL_ALLOWED_METHODS'].get_default()
        if external_allowed_methods:
            allowed_methods = {*allowed_methods, *external_allowed_methods}

        methods = (name for name, member in cls.__dict__.items() if inspect.isfunction(member))

        for method in methods:
            if method.startswith('__') and method.endswith('__'):
                continue

            if method not in allowed_methods:
                raise TypeError(f'Method name `{method}` does not allowed')


__all__ = ('Repository', 'BASE_ALLOWED_METHODS')
