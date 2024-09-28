from typing import Optional, Union
from unittest import TestCase

from parameterized import parameterized

from dddesign.utils.annotation_helpers import get_annotation_without_optional
from tests.utils.annotation_helpers.constants import COMMON_PYTHON_TYPES, GENERIC_DICT_ANNOTATIONS, GENERIC_LIST_ANNOTATIONS


class TestGetAnnotationWithoutOptional(TestCase):
    @parameterized.expand((int | None, Optional[int], Union[int, None]))
    def test_optional_int_annotation(self, annotation):
        # Act & Assert
        self.assertEqual(get_annotation_without_optional(annotation), int)

    @parameterized.expand(
        tuple(zip(tuple(Union[annotation, None] for annotation in GENERIC_LIST_ANNOTATIONS), GENERIC_LIST_ANNOTATIONS))
    )
    def test_optional_generic_list_annotation(self, annotation, expected_annotation):
        # Act & Assert
        self.assertEqual(get_annotation_without_optional(annotation), expected_annotation)

    @parameterized.expand(
        tuple(zip(tuple(Union[annotation, None] for annotation in GENERIC_DICT_ANNOTATIONS), GENERIC_DICT_ANNOTATIONS))
    )
    def test_optional_generic_dict_annotation(self, annotation, expected_annotation):
        # Act & Assert
        self.assertEqual(get_annotation_without_optional(annotation), expected_annotation)

    @parameterized.expand((*COMMON_PYTHON_TYPES, *GENERIC_LIST_ANNOTATIONS, *GENERIC_DICT_ANNOTATIONS))
    def test_non_optional_annotation(self, annotation):
        # Act & Assert
        self.assertEqual(get_annotation_without_optional(annotation), annotation)

    def test_union_without_none(self):
        # Act & Assert
        with self.assertRaises(TypeError):
            get_annotation_without_optional(Union[int, str])
