from typing import Callable, Union
from unittest import TestCase

from dddesign.utils.type_helpers import get_new_function

GLOBAL_PARAMETER: int = 42


def original_function(x: Union[int, float]) -> Union[int, float]:
    return x + 1


def original_function_retrieved_global_parameter() -> int:
    return GLOBAL_PARAMETER


def create_original_closure_function() -> Callable[[Union[int, float]], Union[int, float]]:
    y = 10

    def original_closure_function(x: Union[int, float]) -> Union[int, float]:
        return x + y

    return original_closure_function


class TestGetNewFunction(TestCase):
    def test_new_function_with_same_name(self):
        # Act
        new_func = get_new_function(original_function)

        # Assert
        self.assertEqual(new_func(1), original_function(1))
        self.assertEqual(new_func.__name__, original_function.__name__)

    def test_new_function_with_new_name(self):
        # Arrange
        new_func_name = 'new_func'

        # Act
        new_func = get_new_function(original_function, new_name=new_func_name)

        # Assert
        self.assertEqual(new_func(1), original_function(1))
        self.assertEqual(new_func.__name__, new_func_name)
        self.assertNotEqual(new_func.__name__, original_function.__name__)

    def test_new_function_preserves_globals(self):
        # Act
        new_func = get_new_function(original_function_retrieved_global_parameter)

        # Assert
        self.assertEqual(new_func(), original_function_retrieved_global_parameter())

    def test_new_function_preserves_closure(self):
        # Arrange
        original_closure_function = create_original_closure_function()

        # Act
        new_func = get_new_function(original_closure_function)

        # Assert
        self.assertEqual(new_func(5), 15)
        self.assertEqual(new_func.__name__, original_closure_function.__name__)
