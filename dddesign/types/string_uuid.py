from typing import Any, Callable, Generator
from uuid import UUID

from dddesign.structure.domains.types import BaseType


class StringUUID(str, BaseType):
    """
    A UUID that is serialized as a string.

    The field will be validated as a UUID and then serialized (and stored internally) as a string.
    This is safe to use in cases where json.dumps() is utilized for serialization.
    You will not get punished by `TypeError: Object of type UUID is not JSON serializable` for this anymore.

    Example:
    ```python
        from pydantic import BaseModel

        class MyModel(BaseModel):
            id: StringUUID

        my_model = MyModel(id='123e4567-e89b-12d3-a456-426655440000')

        json.dumps(my_model.dict())  # it's working

        # You can compare it with a string or a UUID
        my_model.id == '123e4567-e89b-12d3-a456-426655440000'
        my_model.id == UUID('123e4567-e89b-12d3-a456-426655440000')
    ```
    """

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, UUID):
            other = type(self)(other)
        return super().__eq__(other)

    def __hash__(self) -> int:
        return hash(str(self))

    @classmethod
    def __get_validators__(cls) -> Generator[Callable[[Any], 'StringUUID'], None, None]:
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> 'StringUUID':
        value = UUID(str(value))
        return cls(value)
