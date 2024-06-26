from unittest import TestCase

from dddesign.structure.applications import Application
from tests.structure.validators import validate_arbitrary_types_allowed, validate_immutable


class TestApplication(TestCase):
    def test_immutable(self):
        validate_immutable(Application)

    def test_arbitrary_types_allowed(self):
        validate_arbitrary_types_allowed(Application)
