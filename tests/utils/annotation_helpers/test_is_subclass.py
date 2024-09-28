from unittest import TestCase

from parameterized import parameterized

from dddesign.utils.annotation_helpers import is_subclass
from tests.utils.annotation_helpers.constants import COMMON_PYTHON_TYPES, GENERIC_DICT_ANNOTATIONS, GENERIC_LIST_ANNOTATIONS


class TestIsSubclass(TestCase):
    @parameterized.expand(COMMON_PYTHON_TYPES)
    def test_python_type_is_subclass_of_itself(self, python_type):
        # Act & Assert
        self.assertTrue(is_subclass(python_type, python_type))

    @parameterized.expand(GENERIC_LIST_ANNOTATIONS)
    def test_generic_list_annotation_is_subclass_of_list(self, annotation):
        # Act & Assert
        self.assertTrue(is_subclass(annotation, list))

    @parameterized.expand(GENERIC_DICT_ANNOTATIONS)
    def test_generic_dict_annotation_is_subclass_of_list(self, annotation):
        # Act & Assert
        self.assertTrue(is_subclass(annotation, dict))

    @parameterized.expand((*COMMON_PYTHON_TYPES, *GENERIC_LIST_ANNOTATIONS, *GENERIC_DICT_ANNOTATIONS))
    def test_annotation_is_subclass_of_object(self, annotation):
        # Act & Assert
        self.assertTrue(is_subclass(annotation, object))

    @parameterized.expand((*COMMON_PYTHON_TYPES, *GENERIC_LIST_ANNOTATIONS, *GENERIC_DICT_ANNOTATIONS))
    def test_annotation_is_not_subclass_of_bytes(self, annotation):
        # Act & Assert
        self.assertFalse(is_subclass(annotation, bytes))
