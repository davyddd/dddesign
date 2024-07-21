from typing import Any


def method(self):  # noqa: ARG001
    pass


def validate_arbitrary_types_allowed(component_class: Any, method_name: str = 'handle'):
    # Arrange
    class Custom:
        ...

    # Act & Assert
    try:
        ExampleApp = type(  # noqa: N806
            'ExampleApp',
            (component_class,),
            {'some_field': (str, ...), '__annotations__': {'some_field': str}, method_name: method},
        )

        ExampleApp(some_field='test')
    except RuntimeError as error:
        raise AssertionError('arbitrary types are not allowed') from error
