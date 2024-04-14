from unittest import TestCase

from dddesign.structure.domains.aggregates import Aggregate
from tests.structure.validators import validate_arbitrary_types_allowed, validate_assignment


class TestAggregate(TestCase):
    def test_arbitrary_types_allowed(self):
        validate_arbitrary_types_allowed(Aggregate)

    def test_assignment(self):
        validate_assignment(Aggregate)
