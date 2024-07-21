from typing import Any


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
    except TypeError:
        pass
    except Exception as error:  # noqa: BLE001
        raise AssertionError(f'An unexpected exception {type(error)} was raised') from error
