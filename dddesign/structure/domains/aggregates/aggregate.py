from pydantic import BaseModel, ConfigDict


class Aggregate(BaseModel):
    model_config = ConfigDict(validate_assignment=True, arbitrary_types_allowed=True)


__all__ = ('Aggregate',)
