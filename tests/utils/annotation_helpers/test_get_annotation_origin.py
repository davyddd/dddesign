from unittest import TestCase

from parameterized import parameterized

from dddesign.utils.annotation_helpers import get_annotation_origin
from tests.utils.annotation_helpers.constants import (
    COMMON_PYTHON_TYPES,
    GENERIC_DICT_ANNOTATIONS,
    GENERIC_LIST_ANNOTATIONS,
    OPTIONAL_INT_ANNOTATIONS,
)


class TestGetAnnotationOrigin(TestCase):
    @parameterized.expand(COMMON_PYTHON_TYPES)
    def test_python_type(self, python_type):
        # Act & Assert
        self.assertEqual(get_annotation_origin(python_type), python_type)

    @parameterized.expand(GENERIC_LIST_ANNOTATIONS)
    def test_generic_list_annotation(self, annotation):
        # Act & Assert
        self.assertEqual(get_annotation_origin(annotation), list)

    @parameterized.expand(GENERIC_DICT_ANNOTATIONS)
    def test_generic_dict_annotation(self, annotation):
        # Act & Assert
        self.assertEqual(get_annotation_origin(annotation), dict)

    @parameterized.expand(OPTIONAL_INT_ANNOTATIONS)
    def test_optional_annotation(self, annotation):
        # Act & Assert
        with self.assertRaises(TypeError):
            get_annotation_origin(annotation)
