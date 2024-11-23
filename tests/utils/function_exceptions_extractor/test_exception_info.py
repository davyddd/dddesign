import ast
from unittest import TestCase

from dddesign.utils.function_exceptions_extractor import ExceptionInfo


class CustomError(Exception):
    def __init__(self, message: str, code: int):
        self.message = message
        self.code = code


class TestExceptionInfo(TestCase):
    def test_exception_info_with_standard_exception(self):
        # Arrange
        args = (ast.Constant(value='error message'),)
        kwargs = {'code': ast.Constant(value=1)}

        # Act
        exception_info = ExceptionInfo(exception_class=ValueError, args=args, kwargs=kwargs)
        exception_instance = exception_info.get_exception_instance()

        # Assert
        self.assertIs(exception_info.exception_class, ValueError)
        self.assertEqual(exception_info.args, ('error message',))
        self.assertEqual(exception_info.kwargs, {'code': 1})
        self.assertIsInstance(exception_instance, ValueError)

    def test_exception_info_with_custom_exception(self):
        # Arrange
        args = (ast.Constant(value='error message'),)
        kwargs = {'code': ast.Constant(value=1)}

        # Act
        exception_info = ExceptionInfo(exception_class=CustomError, args=args, kwargs=kwargs)
        exception_instance = exception_info.get_exception_instance()

        # Assert
        self.assertIs(exception_info.exception_class, CustomError)
        self.assertEqual(exception_info.args, ('error message',))
        self.assertEqual(exception_info.kwargs, {'code': 1})
        self.assertIsInstance(exception_instance, CustomError)
        self.assertEqual(exception_instance.message, 'error message')
        self.assertEqual(exception_instance.code, 1)

    def test_exception_info_with_custom_exception_without_enough_arguments(self):
        # Arrange
        args = (ast.Constant(value='error message'),)
        kwargs = {}

        # Act
        exception_info = ExceptionInfo(exception_class=CustomError, args=args, kwargs=kwargs)
        exception_instance = exception_info.get_exception_instance()

        # Assert
        self.assertIs(exception_info.exception_class, CustomError)
        self.assertEqual(exception_info.args, ('error message',))
        self.assertEqual(exception_info.kwargs, {})
        self.assertIsInstance(exception_instance, CustomError)
        self.assertEqual(exception_instance.message, 'error message')
        self.assertEqual(exception_instance.code, '<code>')
