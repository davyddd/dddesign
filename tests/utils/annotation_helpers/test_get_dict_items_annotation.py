from unittest import TestCase

from parameterized import parameterized

from dddesign.utils.annotation_helpers import get_dict_items_annotation
from tests.utils.annotation_helpers.constants import GENERIC_DICT_ANNOTATIONS


class TestGetDictItemsAnnotation(TestCase):
    @parameterized.expand(GENERIC_DICT_ANNOTATIONS)
    def test_generic_dict_annotation(self, annotation):
        # Act
        key_annotation, value_annotation = get_dict_items_annotation(annotation)

        # Assert
        self.assertEqual(key_annotation, str)
        self.assertEqual(value_annotation, int)
