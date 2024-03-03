from pydantic import BaseModel


class Application(BaseModel):
    class Config:
        arbitrary_types_allowed = True
