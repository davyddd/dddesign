from pydantic import BaseModel, ConfigDict


class DataTransferObject(BaseModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)


__all__ = ('DataTransferObject',)
