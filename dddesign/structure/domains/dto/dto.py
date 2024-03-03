from pydantic import BaseModel


class DataTransferObject(BaseModel):
    class Config:
        arbitrary_types_allowed = True
        allow_mutation = False
