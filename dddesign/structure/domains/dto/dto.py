from pydantic import BaseModel


class DataTransferObject(BaseModel):
    class Config:
        frozen = True
        arbitrary_types_allowed = True
