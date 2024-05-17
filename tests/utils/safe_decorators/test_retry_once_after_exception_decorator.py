from typing import Any
from unittest import TestCase
from unittest.mock import patch

from dddesign.utils.safe_decorators import retry_once_after_exception


# Define some test functions to use with the decorator
@retry_once_after_exception
def func_success(a: Any, b: Any):  # noqa: ARG001
    return a + b


@retry_once_after_exception
def func_raises_once_then_succeeds(a: Any, b: Any, state: dict):  # noqa: ARG001
    if not state.get('retried', False):
        state['retried'] = True
        raise ValueError('Test exception')
    return a + b


@retry_once_after_exception
def func_raises_always(a: Any, b: Any):  # noqa: ARG001
    raise ValueError('Test exception')


@retry_once_after_exception(capture_exception=False)
def func_no_capture_exception(a: Any, b: Any):  # noqa: ARG001
    raise ValueError('Test exception')


@retry_once_after_exception(exceptions=(ValueError,))
def func_specific_exception_handling(a: Any, b: Any):  # noqa: ARG001
    raise ValueError('Test exception')


@retry_once_after_exception(exceptions=(ValueError,))
def func_specific_exception_not_handling(a: Any, b: Any):  # noqa: ARG001
    raise TypeError('Test exception')


class TestRetryOnceAfterExceptionDecorator(TestCase):
    def test_successful_call(self):
        self.assertEqual(func_success(2, 3), 5)

    @patch('dddesign.utils.safe_decorators.logger')
    def test_retry_once_after_exception(self, mock_logger):
        # Arrange
        state = {}

        # Act & Assert
        self.assertEqual(func_raises_once_then_succeeds(2, 3, state), 5)
        mock_logger.exception.assert_called_once()

    @patch('dddesign.utils.safe_decorators.logger')
    def test_always_raises_exception(self, mock_logger):
        # Act & Assert
        with self.assertRaises(ValueError):
            func_raises_always(2, 3)
        mock_logger.exception.assert_called_once()

    @patch('dddesign.utils.safe_decorators.logger')
    def test_no_capture_exception(self, mock_logger):
        # Act & Assert
        with self.assertRaises(ValueError):
            func_no_capture_exception(2, 3)
        mock_logger.exception.assert_not_called()

    @patch('dddesign.utils.safe_decorators.logger')
    def test_specific_exception_handling(self, mock_logger):
        # Act & Assert
        with self.assertRaises(ValueError):
            func_specific_exception_handling(2, 3)
        mock_logger.exception.assert_called_once()

    @patch('dddesign.utils.safe_decorators.logger')
    def test_specific_exception_not_handling(self, mock_logger):
        # Act & Assert
        with self.assertRaises(TypeError):
            func_specific_exception_not_handling(2, 3)
        mock_logger.exception.assert_not_called()
