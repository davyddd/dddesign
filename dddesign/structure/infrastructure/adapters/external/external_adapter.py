from pydantic import BaseModel


class ExternalAdapter(BaseModel):
    class Config:
        allow_mutation = False
        arbitrary_types_allowed = True
