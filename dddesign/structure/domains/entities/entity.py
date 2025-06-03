from typing import Optional, Set

from pydantic import BaseModel, ConfigDict


class Entity(BaseModel):
    model_config = ConfigDict(validate_assignment=True, arbitrary_types_allowed=True)

    def update(self, data: BaseModel, exclude_fields: Optional[Set[str]] = None):
        for field_name, value in data.model_dump(exclude_unset=True, exclude=exclude_fields).items():
            if field_name in self.model_fields and getattr(self, field_name) != value:
                setattr(self, field_name, value)


__all__ = ('Entity',)
