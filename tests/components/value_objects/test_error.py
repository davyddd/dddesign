from unittest import TestCase

from dddesign.components.domains.value_objects import Error
from dddesign.structure.domains.errors import BaseError


class TestError(TestCase):
    def test_matching_with_base_error(self):
        # Act & Assert
        self.assertDictEqual(Error.__annotations__, BaseError.__annotations__)
