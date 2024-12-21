from pydantic import BaseModel, ConfigDict


class Application(BaseModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)


__all__ = ('Application',)
