from unittest import TestCase

from dddesign.structure.domains.errors.base_error import BaseError


class TestBaseError(TestCase):
    def test_correct_state(self):
        # Act
        error = BaseError(
            message='Error message: {error_message}',
            error_code='some_error',
            status_code=400,
            field_name='some_field',
            error_message='invalid value',
        )

        # Assert
        self.assertEqual(error.message, 'Error message: invalid value')
        self.assertEqual(error.error_code, 'some_error')
        self.assertEqual(error.status_code, 400)
        self.assertEqual(error.field_name, 'some_field')

    def test_correct_state_with_default_values(self):
        # Act
        error = BaseError(message='Error message: {error_message}', error_message='invalid value')

        # Assert
        self.assertEqual(error.message, 'Error message: invalid value')
        self.assertEqual(error.error_code, 'base_error')
        self.assertEqual(error.status_code, 400)
        self.assertEqual(error.field_name, None)

    def test_base_error_without_message(self):
        # Act & Assert
        with self.assertRaises(ValueError):
            BaseError()
