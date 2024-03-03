from typing import List

from dddesign.structure.domains.errors.base_error import BaseError


class CollectionError(Exception):
    errors: List[BaseError]

    def __init__(self):
        self.errors = []
        self._index = 0

    def __bool__(self) -> bool:
        return bool(self.errors)

    def __iter__(self):
        return self

    def __next__(self) -> BaseError:
        if self._index >= len(self.errors):
            self._index = 0
            raise StopIteration

        result = self.errors[self._index]
        self._index += 1
        return result

    def add(self, error: BaseError):
        if not isinstance(error, BaseError):
            raise TypeError('`error` must be an instance of `BaseError`')

        self.errors.append(error)
