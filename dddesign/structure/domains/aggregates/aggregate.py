from pydantic import BaseModel


class Aggregate(BaseModel):
    class Config:
        arbitrary_types_allowed = True
