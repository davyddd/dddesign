from typing import Any


def validate_arbitrary_types_allowed(component_class: Any):
    # Arrange
    class Custom:
        ...

    # Act & Assert
    try:

        class ExampleApp(component_class):
            some_field: Custom
    except RuntimeError as error:
        raise AssertionError('arbitrary types are not allowed') from error
