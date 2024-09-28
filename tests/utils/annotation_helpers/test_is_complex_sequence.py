from unittest import TestCase

from parameterized import parameterized

from dddesign.utils.annotation_helpers import NON_COMPLEX_SEQUENCE_TYPES, is_complex_sequence
from tests.utils.annotation_helpers.constants import GENERIC_DICT_ANNOTATIONS, GENERIC_LIST_ANNOTATIONS


class TestIsComplexSequence(TestCase):
    @parameterized.expand(GENERIC_LIST_ANNOTATIONS)
    def test_generic_list_annotation(self, annotation):
        # Act & Assert
        self.assertTrue(is_complex_sequence(annotation))

    @parameterized.expand(GENERIC_DICT_ANNOTATIONS)
    def test_generic_dict_annotation(self, annotation):
        # Act & Assert
        self.assertFalse(is_complex_sequence(annotation))

    @parameterized.expand(NON_COMPLEX_SEQUENCE_TYPES)
    def test_non_complex_sequence(self, annotation):
        # Act & Assert
        self.assertFalse(is_complex_sequence(annotation))
