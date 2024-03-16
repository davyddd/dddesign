from pydantic import BaseModel


class DataTransferObject(BaseModel):
    class Config:
        allow_mutation = False
        arbitrary_types_allowed = True
