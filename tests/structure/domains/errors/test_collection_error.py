from unittest import TestCase

from dddesign.structure.domains.errors.base_error import BaseError
from dddesign.structure.domains.errors.collection_error import CollectionError


class TestCollectionError(TestCase):
    def test_correct_state_without_errors(self):
        # Act
        error = CollectionError()

        # Assert
        self.assertEqual(error.errors, [])
        self.assertFalse(bool(error.errors))

    def test_correct_state_with_errors(self):
        # Act
        error = CollectionError()
        error.add(BaseError(message='Test message 1'))
        error.add(BaseError(message='Test message 2'))

        # Assert
        self.assertTrue(bool(error))
        self.assertEqual(len(tuple(_err for _err in error)), 2)

    def test_add_non_base_error(self):
        # Act
        error = CollectionError()

        # Assert
        with self.assertRaises(TypeError):
            error.add(ValueError('Test message'))
