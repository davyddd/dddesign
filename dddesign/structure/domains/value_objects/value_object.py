from pydantic import BaseModel


class ValueObject(BaseModel):
    class Config:
        allow_mutation = False
        arbitrary_types_allowed = True
