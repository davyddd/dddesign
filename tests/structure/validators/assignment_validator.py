from typing import Any

from pydantic import validator, root_validator


def validate_assignment(component_class: Any):
    # Arrange
    class ExampleApp(component_class):
        some_field: str

        @validator('some_field')
        def strip_some_field(cls, value):
            return value.strip()

        @root_validator
        def title_some_field(cls, values):
            values['some_field'] = values['some_field'].title()
            return values

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
