from pydantic import BaseModel


class InternalAdapter(BaseModel):
    class Config:
        allow_mutation = False
        arbitrary_types_allowed = True
