from pydantic import BaseModel


class ExternalAdapter(BaseModel):
    class Config:
        arbitrary_types_allowed = True
