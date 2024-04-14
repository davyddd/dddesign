from unittest import TestCase

from dddesign.structure.infrastructure.adapters.external import ExternalAdapter
from tests.structure.validators import validate_arbitrary_types_allowed, validate_immutable


class TestExternalAdapter(TestCase):
    def test_immutable(self):
        validate_immutable(ExternalAdapter)

    def test_arbitrary_types_allowed(self):
        validate_arbitrary_types_allowed(ExternalAdapter)
