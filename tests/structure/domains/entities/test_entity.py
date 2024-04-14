from unittest import TestCase

from dddesign.structure.domains.entities import Entity
from tests.structure.validators import validate_arbitrary_types_allowed, validate_assignment


class TestEntity(TestCase):
    def test_arbitrary_types_allowed(self):
        validate_arbitrary_types_allowed(Entity)

    def test_assignment(self):
        validate_assignment(Entity)
