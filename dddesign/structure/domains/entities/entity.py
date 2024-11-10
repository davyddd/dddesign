from typing import Optional, Set

from pydantic import BaseModel, ConfigDict

from dddesign.structure.domains.dto.dto import DataTransferObject


class Entity(BaseModel):
    model_config = ConfigDict(validate_assignment=True, arbitrary_types_allowed=True)

    def update(self, data: DataTransferObject, exclude_fields: Optional[Set[str]] = None):
        for field_name, value in data.model_dump(exclude_unset=True, exclude=exclude_fields).items():
            if field_name in self.model_fields:
                setattr(self, field_name, value)
