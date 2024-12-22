from typing import List

from ddutils.convertors import convert_to_repr

from dddesign.structure.domains.errors.base_error import BaseError


class CollectionError(Exception):
    errors: List[BaseError]

    def __init__(self):
        self.errors = []
        self.__index = 0

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return convert_to_repr(self)

    def __bool__(self) -> bool:
        return bool(self.errors)

    def __iter__(self):
        return self

    def __next__(self) -> BaseError:
        if self.__index >= len(self.errors):
            self._index = 0
            raise StopIteration

        result = self.errors[self.__index]
        self.__index += 1
        return result

    def add(self, error: BaseError):
        if not isinstance(error, BaseError):
            raise TypeError('`error` must be an instance of `BaseError`')

        self.errors.append(error)


__all__ = ('CollectionError',)
