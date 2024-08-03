from pydantic import BaseModel


class ValueObject(BaseModel):
    class Config:
        frozen = True
        arbitrary_types_allowed = True
