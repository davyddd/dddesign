from pydantic import BaseModel, ConfigDict


class InternalAdapter(BaseModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)


__all__ = ('InternalAdapter',)
