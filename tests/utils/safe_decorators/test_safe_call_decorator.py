from typing import Any
from unittest import TestCase
from unittest.mock import patch

from dddesign.utils.safe_decorators import safe_call


# Define some test functions to use with the decorator
@safe_call
def func_success(a: Any, b: Any):  # noqa: ARG001
    return a + b


@safe_call
def func_raises_exception(a: Any, b: Any):  # noqa: ARG001
    raise ValueError('Test exception')


@safe_call(default_result='default')
def func_with_default(a: Any, b: Any):  # noqa: ARG001
    raise ValueError('Test exception')


@safe_call(capture_exception=False)
def func_no_capture_exception(a: Any, b: Any):  # noqa: ARG001
    raise ValueError('Test exception')


@safe_call(exceptions=(ValueError,))
def func_specific_exception_handling(a: Any, b: Any):  # noqa: ARG001
    raise ValueError('Test exception')


@safe_call(exceptions=(ValueError,))
def func_specific_exception_not_handling(a: Any, b: Any):  # noqa: ARG001
    raise TypeError('Test exception')


class TestSafeCallDecorator(TestCase):
    def test_successful_call(self):
        # Act & Assert
        self.assertEqual(func_success(2, 3), 5)

    @patch('dddesign.utils.safe_decorators.logger')
    def test_exception_handling_with_capture(self, mock_logger):
        # Act & Assert
        self.assertIsNone(func_raises_exception(2, 3))
        mock_logger.exception.assert_called_once()

    @patch('dddesign.utils.safe_decorators.logger')
    def test_exception_handling_with_default_result(self, mock_logger):
        # Act & Assert
        self.assertEqual(func_with_default(2, 3), 'default')
        mock_logger.exception.assert_called_once()

    @patch('dddesign.utils.safe_decorators.logger')
    def test_no_capture_exception(self, mock_logger):
        # Act & Assert
        self.assertIsNone(func_no_capture_exception(2, 3))
        mock_logger.exception.assert_not_called()

    @patch('dddesign.utils.safe_decorators.logger')
    def test_specific_exception_handling(self, mock_logger):
        # Act & Assert
        self.assertIsNone(func_specific_exception_handling(2, 3))
        mock_logger.exception.assert_called_once()

    @patch('dddesign.utils.safe_decorators.logger')
    def test_specific_exception_not_handling(self, mock_logger):
        # Act & Assert
        with self.assertRaises(TypeError):
            func_specific_exception_not_handling(2, 3)
        mock_logger.exception.assert_not_called()
