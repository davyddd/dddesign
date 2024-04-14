from unittest import TestCase

from dddesign.structure.domains.value_objects import ValueObject
from tests.structure.validators import validate_arbitrary_types_allowed, validate_immutable


class TestValueObject(TestCase):
    def test_immutable(self):
        validate_immutable(ValueObject)

    def test_arbitrary_types_allowed(self):
        validate_arbitrary_types_allowed(ValueObject)
