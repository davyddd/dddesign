from pydantic import BaseModel, ConfigDict

from dddesign.structure.domains.dto.dto import DataTransferObject


class Entity(BaseModel):
    model_config = ConfigDict(validate_assignment=True, arbitrary_types_allowed=True)

    def update(self, data: DataTransferObject):
        for field_name, value in data.dict(exclude_unset=True).items():
            if field_name in self.model_fields:
                setattr(self, field_name, value)
