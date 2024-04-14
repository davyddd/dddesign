from unittest import TestCase

from dddesign.structure.services import Service
from tests.structure.validators import validate_arbitrary_types_allowed, validate_immutable


class TestService(TestCase):
    def test_immutable(self):
        validate_immutable(Service)

    def test_arbitrary_types_allowed(self):
        validate_arbitrary_types_allowed(Service)
