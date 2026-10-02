from typing import Annotated, Any

from pydantic import AfterValidator, field_validator


def validate_assignment(component_class: Any):
    # Arrange
    def title_some_field(value: str) -> str:
        return value.title()

    class ExampleApp(component_class):
        some_field: Annotated[str, AfterValidator(title_some_field)]

        @field_validator('some_field')
        @classmethod
        def strip_some_field(cls, value: str):
            return value.strip()

    # Act
    instance = ExampleApp(some_field=' value ')

    # Assert
    if instance.some_field != 'Value':
        raise AssertionError('The value was not validated')

    # Act
    instance.some_field = ' new value '

    # Assert
    if instance.some_field != 'New Value':
        raise AssertionError('The value was not validated')
