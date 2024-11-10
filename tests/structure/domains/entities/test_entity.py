from typing import Optional
from unittest import TestCase
from uuid import uuid4

from parameterized import parameterized
from pydantic import Field

from dddesign.structure.domains.dto import DataTransferObject
from dddesign.structure.domains.entities import Entity
from tests.structure.validators import validate_arbitrary_types_allowed, validate_assignment

DEFAULT_VALUE = str(uuid4())


class SomeDTO(DataTransferObject):
    some_field: Optional[str] = None


class SomeEntity(Entity):
    some_field: str = Field(default=DEFAULT_VALUE)


class TestEntity(TestCase):
    def test_arbitrary_types_allowed(self):
        validate_arbitrary_types_allowed(Entity)

    def test_assignment(self):
        validate_assignment(Entity)

    @parameterized.expand(
        (
            ({}, DEFAULT_VALUE, None),
            ({'some_field': 'random'}, 'random', None),
            ({'some_field': 'random'}, DEFAULT_VALUE, {'some_field'}),
        )
    )
    def test_update_method(self, dto_initials, excepted_value, exclude_fields):
        # Arrange
        entity = SomeEntity()
        data = SomeDTO(**dto_initials)

        # Act
        entity.update(data=data, exclude_fields=exclude_fields)

        # Assert
        self.assertEqual(entity.some_field, excepted_value)
