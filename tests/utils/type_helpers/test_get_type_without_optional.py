from typing import List, Optional, Union
from unittest import TestCase

from dddesign.utils.type_helpers import get_type_without_optional


class TestGetTypeWithoutOptional(TestCase):
    def test_optional_type(self):
        # Act & Assert
        self.assertEqual(get_type_without_optional(Optional[int]), int)
        self.assertEqual(get_type_without_optional(Optional[str]), str)
        self.assertEqual(get_type_without_optional(Optional[List[int]]), List[int])

    def test_non_optional_type(self):
        # Act & Assert
        self.assertEqual(get_type_without_optional(int), int)
        self.assertEqual(get_type_without_optional(str), str)
        self.assertEqual(get_type_without_optional(List[int]), List[int])

    def test_union_with_none(self):
        # Act & Assert
        self.assertEqual(get_type_without_optional(Union[int, None]), int)
        self.assertEqual(get_type_without_optional(Union[str, None]), str)
        self.assertEqual(get_type_without_optional(Union[List[int], None]), List[int])

    def test_union_without_none(self):
        # Act & Assert
        self.assertEqual(get_type_without_optional(Union[int, str]), Union[int, str])
        self.assertEqual(get_type_without_optional(Union[List[int], dict]), Union[List[int], dict])

    def test_invalid_type(self):
        # Act & Assert
        self.assertEqual(get_type_without_optional(None), None)
        self.assertEqual(get_type_without_optional(123), 123)
