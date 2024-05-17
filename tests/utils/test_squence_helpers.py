from unittest import TestCase

from dddesign.utils.sequence_helpers import get_safe_element


class TestGetSafeElement(TestCase):
    def test_valid_index(self):
        self.assertEqual(get_safe_element(('a', 'b', 'c'), 0), 'a')
        self.assertEqual(get_safe_element(['a', 'b', 'c'], 1), 'b')
        self.assertEqual(get_safe_element('abc', 2), 'c')

    def test_index_out_of_range(self):
        self.assertIsNone(get_safe_element(('a', 'b', 'c'), -4))
        self.assertIsNone(get_safe_element(['a', 'b', 'c'], 5))
        self.assertIsNone(get_safe_element('abc', 10))

    def test_empty_sequence(self):
        self.assertIsNone(get_safe_element([], 0))
        self.assertIsNone(get_safe_element((), 0))
        self.assertIsNone(get_safe_element('', 0))

    def test_negative_index(self):
        self.assertEqual(get_safe_element(('a', 'b', 'c'), -1), 'c')
        self.assertEqual(get_safe_element(['a', 'b', 'c'], -2), 'b')
        self.assertEqual(get_safe_element('abc', -3), 'a')

    def test_non_sequence(self):
        with self.assertRaises(TypeError):
            get_safe_element(123, 1)
        with self.assertRaises(TypeError):
            get_safe_element(None, 0)
