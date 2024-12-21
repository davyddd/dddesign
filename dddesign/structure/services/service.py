from abc import ABCMeta, abstractmethod

from pydantic import BaseModel, ConfigDict


class Service(BaseModel, metaclass=ABCMeta):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    @abstractmethod
    def handle(self):
        ...


__all__ = ('Service',)
