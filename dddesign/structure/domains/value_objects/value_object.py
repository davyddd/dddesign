from pydantic import BaseModel


class ValueObject(BaseModel):
    class Config:
        arbitrary_types_allowed = True
