from abc import ABCMeta, abstractmethod

from pydantic import BaseModel


class Service(BaseModel, metaclass=ABCMeta):
    class Config:
        arbitrary_types_allowed = True

    @abstractmethod
    def handle(self):
        ...
