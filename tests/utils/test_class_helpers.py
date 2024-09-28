from unittest import TestCase

from dddesign.utils.class_helpers import get_origin_class_of_method


class A:
    def method(self):
        pass


class B(A):
    def another_method(self):
        pass


class C(B):
    def method(self):
        pass


class D(C):
    pass


class TestGetOriginClassOfMethod(TestCase):
    def test_method_in_class(self):
        # Act & Assert
        self.assertEqual(get_origin_class_of_method(A, 'method'), A)
        self.assertEqual(get_origin_class_of_method(B, 'another_method'), B)
        self.assertEqual(get_origin_class_of_method(C, 'method'), C)
        self.assertEqual(get_origin_class_of_method(D, 'method'), C)

    def test_inherited_method(self):
        # Act & Assert
        self.assertEqual(get_origin_class_of_method(B, 'method'), A)
        self.assertEqual(get_origin_class_of_method(D, 'method'), C)
        self.assertEqual(get_origin_class_of_method(D, 'another_method'), B)

    def test_method_not_in_class(self):
        # Act & Assert
        self.assertIsNone(get_origin_class_of_method(A, 'nonexistent_method'))
        self.assertIsNone(get_origin_class_of_method(B, 'nonexistent_method'))
        self.assertIsNone(get_origin_class_of_method(C, 'nonexistent_method'))
        self.assertIsNone(get_origin_class_of_method(D, 'nonexistent_method'))
