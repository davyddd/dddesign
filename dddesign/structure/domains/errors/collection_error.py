from collections.abc import Iterator

from ddutils.convertors import convert_to_repr

from dddesign.structure.domains.errors.base_error import BaseError


class CollectionError(Exception):
    errors: list[BaseError]

    def __init__(self):
        self.errors = []

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return convert_to_repr(self)

    def __bool__(self) -> bool:
        return bool(self.errors)

    def __iter__(self) -> Iterator[BaseError]:
        return iter(self.errors)

    def add(self, error: BaseError):
        if not isinstance(error, BaseError):
            raise TypeError('`error` must be an instance of `BaseError`')

        self.errors.append(error)


__all__ = ('CollectionError',)
