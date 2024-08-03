from pydantic import BaseModel


class Application(BaseModel):
    class Config:
        frozen = True
        arbitrary_types_allowed = True
