from unittest import TestCase

from dddesign.components.domains.dto import Errors
from dddesign.structure.domains.errors import BaseError, CollectionError


class CustomError(BaseError):
    message = 'Custom error message'
    error_code = 'custom_error'
    status_code = 401


class TestErrors(TestCase):
    def test_smoke(self):
        # Arrange
        collection_error = CollectionError()
        collection_error.add(CustomError())

        # Act
        errors = Errors.factory(collection_error)

        # Assert
        self.assertEqual(len(errors.errors), 1)
        self.assertEqual(errors.status_code, CustomError.status_code)
        self.assertEqual(errors.errors[0].message, CustomError.message)
        self.assertEqual(errors.errors[0].error_code, CustomError.error_code)
        self.assertIsNone(errors.errors[0].field_name)
