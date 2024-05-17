from typing import Dict, List
from unittest import TestCase

from dddesign.utils.type_helpers import is_subclass_smart


class TestIsSubclassSmart(TestCase):
    def test_direct_subclass(self):
        # Act & Assert
        self.assertTrue(is_subclass_smart(bool, int))
        self.assertTrue(is_subclass_smart(int, object))
        self.assertTrue(is_subclass_smart(str, object))

    def test_not_subclass(self):
        # Act & Assert
        self.assertFalse(is_subclass_smart(str, list))
        self.assertFalse(is_subclass_smart(int, str))
        self.assertFalse(is_subclass_smart(float, int))

    def test_generic_subclass(self):
        # Act & Assert
        self.assertTrue(is_subclass_smart(Dict[int, int], dict))
        self.assertTrue(is_subclass_smart(List[int], list))
        self.assertFalse(is_subclass_smart(List[int], int))
        self.assertFalse(is_subclass_smart(List[int], dict))

    def test_invalid_class_type(self):
        # Act & Assert
        self.assertFalse(is_subclass_smart(123, object))
        self.assertFalse(is_subclass_smart('string', object))
        self.assertFalse(is_subclass_smart(None, object))

    def test_multiple_base_types(self):
        # Act & Assert
        self.assertTrue(is_subclass_smart(bool, int, object))
        self.assertTrue(is_subclass_smart(int, float, object))
        self.assertFalse(is_subclass_smart(str, list, dict))
