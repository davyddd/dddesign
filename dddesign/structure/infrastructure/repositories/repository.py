import inspect
from typing import Optional, Set

from pydantic import BaseModel, ConfigDict

BASE_ALLOWED_METHODS = {
    'get',  # Returns one entity by PK
    'get_by_filters',  # Returns one entity matching filters
    'get_list',  # Returns a list of entities
    'get_map',  # Returns a mapping of entities (e.g. {pk: entity})
    'create',  # Creates one entity, accepts entity
    'update',  # Updates one entity, accepts entity
    'delete',  # Deletes one entity by PK
    'bulk_create',  # Creates multiple entities, accepts a collection of entities
    'bulk_update',  # Updates multiple entities, accepts a collection of entities
    'bulk_delete',  # Deletes multiple entities, accepts a collection of PKs
    'update_by_filters',  # Updates entities matching filters
    'delete_by_filters',  # Deletes entities matching filters
}


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
