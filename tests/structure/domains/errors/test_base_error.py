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

    def test_message_with_brace_literals_and_no_kwargs(self):
        # Act
        error = BaseError(message="String should match pattern '^[a-zA-Z0-9_]{1,32}$'")

        # Assert
        self.assertEqual(error.message, "String should match pattern '^[a-zA-Z0-9_]{1,32}$'")

    def test_message_mixes_brace_literal_with_named_placeholder(self):
        # Act
        error = BaseError(message='pattern {1,32} and {some_arg}', some_arg='x')

        # Assert
        self.assertEqual(error.message, 'pattern {1,32} and x')

    def test_missing_placeholder_argument_raises(self):
        # Act & Assert
        with self.assertRaises(ValueError) as ctx:
            BaseError(message='Error message: {error_message} and {some_arg}', error_message='x')
        self.assertIn('some_arg', str(ctx.exception))
