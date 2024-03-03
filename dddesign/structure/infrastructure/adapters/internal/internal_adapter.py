from pydantic import BaseModel


class InternalAdapter(BaseModel):
    class Config:
        arbitrary_types_allowed = True
