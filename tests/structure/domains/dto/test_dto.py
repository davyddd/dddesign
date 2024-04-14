from unittest import TestCase

from dddesign.structure.domains.dto import DataTransferObject
from tests.structure.validators import validate_arbitrary_types_allowed, validate_immutable


class TestDataTransferObject(TestCase):
    def test_immutable(self):
        validate_immutable(DataTransferObject)

    def test_arbitrary_types_allowed(self):
        validate_arbitrary_types_allowed(DataTransferObject)
