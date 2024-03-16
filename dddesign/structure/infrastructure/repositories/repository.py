from pydantic import BaseModel


class Repository(BaseModel):
    class Config:
        allow_mutation = False
        arbitrary_types_allowed = True
