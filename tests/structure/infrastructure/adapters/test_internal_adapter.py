from unittest import TestCase

from dddesign.structure.infrastructure.adapters.internal import InternalAdapter
from tests.structure.validators import validate_arbitrary_types_allowed, validate_immutable


class TestInternalAdapter(TestCase):
    def test_immutable(self):
        validate_immutable(InternalAdapter)

    def test_arbitrary_types_allowed(self):
        validate_arbitrary_types_allowed(InternalAdapter)
