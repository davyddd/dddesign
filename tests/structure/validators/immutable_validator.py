from typing import Any

from pydantic import ValidationError


def method(self):  # noqa: ARG001
    pass


def validate_immutable(component_class: Any, method_name: str = 'handle'):
    # Arrange
    ExampleApp = type(  # noqa: N806
        'ExampleApp',
        (component_class,),
        {'some_field': (str, ...), '__annotations__': {'some_field': str}, method_name: method},
    )

    # Act
    instance = ExampleApp(some_field='value')

    # Assert
    try:
        instance.some_field = 'new value'
        raise AssertionError('TypeError was expected but not raised')
    except ValidationError as error:
        _error = error.errors()[0]
        if _error['type'] != 'frozen_instance':
            raise AssertionError(f'An unexpected error type {_error["type"]} was raised') from error
        if _error['loc'][0] != 'some_field':
            raise AssertionError(f'An unexpected location {_error["loc"][0]} was raised') from error
    except Exception as error:  # noqa: BLE001
        raise AssertionError(f'An unexpected exception {type(error)} was raised') from error
