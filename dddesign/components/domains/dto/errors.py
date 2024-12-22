from typing import Annotated, List

from pydantic import Field

from dddesign.components.domains.value_objects import Error
from dddesign.structure.domains.dto import DataTransferObject
from dddesign.structure.domains.errors import CollectionError


class Errors(DataTransferObject):
    errors: Annotated[List[Error], Field(min_length=1)]

    @property
    def status_code(self) -> int:
        if len(self.errors) == 1:
            return self.errors[0].status_code
        else:
            return 400

    @classmethod
    def factory(cls, errors: CollectionError) -> 'Errors':
        return cls(errors=[Error(**error.__dict__) for error in errors])


__all__ = ('Errors',)
