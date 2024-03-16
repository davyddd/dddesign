from pydantic import BaseModel


class Application(BaseModel):
    class Config:
        allow_mutation = False
        arbitrary_types_allowed = True
