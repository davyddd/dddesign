from unittest import TestCase

from dddesign.utils.function_exceptions_extractor import extract_function_exceptions


class CustomError(Exception):
    def __init__(self, message, code):
        super().__init__(message)
        self.message = message
        self.code = code


class TestExtractFunctionExceptions(TestCase):
    def test_func_without_exceptions(self):
        # Arrange
        def func_without_exceptions():
            pass

        # Act
        exceptions = list(extract_function_exceptions(func_without_exceptions))

        # Assert
        self.assertEqual(exceptions, [])

    def test_func_with_one_exception(self):
        # Arrange
        def func_with_one_exception():
            raise ValueError('Invalid value')

        # Act
        exceptions = list(extract_function_exceptions(func_with_one_exception))

        # Assert
        self.assertEqual(len(exceptions), 1)
        self.assertEqual(exceptions[0].exception_class, ValueError)
        self.assertEqual(exceptions[0].args, ('Invalid value',))
        self.assertEqual(exceptions[0].kwargs, {})

    def test_func_with_two_exceptions(self):
        # Arrange
        def func_with_two_exceptions(attribute: bool):
            if attribute:
                raise KeyError('Missing key')
            raise IndexError('Index out of range')

        # Act
        exceptions = list(extract_function_exceptions(func_with_two_exceptions))
        key_error_exception = next(exception for exception in exceptions if exception.exception_class is KeyError)
        index_error_exception = next(exception for exception in exceptions if exception.exception_class is IndexError)

        # Assert
        self.assertEqual(len(exceptions), 2)
        self.assertIs(index_error_exception.exception_class, IndexError)
        self.assertEqual(index_error_exception.args, ('Index out of range',))
        self.assertEqual(index_error_exception.kwargs, {})
        self.assertIsInstance(index_error_exception.get_exception_instance(), IndexError)
        self.assertEqual(key_error_exception.exception_class, KeyError)
        self.assertEqual(key_error_exception.args, ('Missing key',))
        self.assertEqual(key_error_exception.kwargs, {})
        self.assertIsInstance(key_error_exception.get_exception_instance(), KeyError)

    def test_func_with_custom_exception(self):
        # Arrange
        def func_with_custom_exception():
            raise CustomError('An error occurred', 404)

        # Act
        exceptions = list(extract_function_exceptions(func_with_custom_exception))

        # Assert
        self.assertEqual(len(exceptions), 1)
        self.assertEqual(exceptions[0].exception_class, CustomError)
        self.assertEqual(exceptions[0].args, ('An error occurred', 404))
        self.assertEqual(exceptions[0].kwargs, {})

    def test_func_with_invalid_exception(self):
        # Arrange
        def func_with_invalid_exception():
            raise 'This is not an exception'  # noqa: B016

        # Act
        exceptions = list(extract_function_exceptions(func_with_invalid_exception))

        # Assert
        self.assertEqual(len(exceptions), 0)
