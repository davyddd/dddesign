from typing import Any


def validate_immutable(component_class: Any):
    # Arrange
    class ExampleApp(component_class):
        some_field: str

    # Act
    instance = ExampleApp(some_field='value')

    # Assert
    try:
        instance.some_field = 'new value'
        raise AssertionError('TypeError was expected but not raised')
    except TypeError:
        pass
    except Exception as error:  # noqa: BLE001
        raise AssertionError(f'An unexpected exception {type(error)} was raised') from error
