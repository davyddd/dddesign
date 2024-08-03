from pydantic import BaseModel


class ExternalAdapter(BaseModel):
    class Config:
        frozen = True
        arbitrary_types_allowed = True
