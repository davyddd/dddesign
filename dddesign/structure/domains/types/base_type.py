from abc import ABCMeta, abstractmethod
from typing import Generator

from pydantic.typing import AnyCallable


class BaseType(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def __get_validators__(cls) -> Generator[AnyCallable, None, None]:
        ...
