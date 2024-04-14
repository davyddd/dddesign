from unittest import TestCase

from dddesign.structure.infrastructure.repositories import Repository
from tests.structure.validators import validate_arbitrary_types_allowed, validate_immutable


class TestRepository(TestCase):
    def test_immutable(self):
        validate_immutable(Repository)

    def test_arbitrary_types_allowed(self):
        validate_arbitrary_types_allowed(Repository)
