from pydantic import BaseModel


class Repository(BaseModel):
    class Config:
        arbitrary_types_allowed = True
