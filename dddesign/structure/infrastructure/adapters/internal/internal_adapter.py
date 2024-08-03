from pydantic import BaseModel


class InternalAdapter(BaseModel):
    class Config:
        frozen = True
        arbitrary_types_allowed = True
