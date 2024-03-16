from pydantic import BaseModel


class Aggregate(BaseModel):
    class Config:
        validate_assignment = True
        arbitrary_types_allowed = True
