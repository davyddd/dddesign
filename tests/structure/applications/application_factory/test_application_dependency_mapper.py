from unittest import TestCase

from pydantic import ValidationError

from dddesign.structure.applications.application_factory import ApplicationDependencyMapper
from dddesign.structure.domains.constants import BaseEnum
from dddesign.structure.infrastructure.adapters.external import ExternalAdapter
from dddesign.utils.annotation_helpers import is_subclass


class FirstTestEnum(str, BaseEnum):
    FIRST_VALUE1 = 'first_fvalue1'
    FIRST_VALUE2 = 'first_value2'


class SecondTestEnum(str, BaseEnum):
    SECOND_VALUE1 = 'second_value1'
    SECOND_VALUE2 = 'second_value2'


class Example1ExternalAdapter(ExternalAdapter):
    pass


class Example2ExternalAdapter(ExternalAdapter):
    pass


class TestApplicationDependencyMapper(TestCase):
    def test_correct_state(self):
        # Act
        instance = ApplicationDependencyMapper(
            application_attribute_name='external_adapter',
            request_attribute_value_map={
                FirstTestEnum.FIRST_VALUE1: Example1ExternalAdapter(),
                FirstTestEnum.FIRST_VALUE2: Example2ExternalAdapter(),
            },
        )

        # Assert
        assert is_subclass(instance.enum_class, FirstTestEnum)
        self.assertEqual(instance.get_request_attribute_name(), 'first_test_enum')

        with self.assertRaises(ValidationError) as context:
            instance.application_attribute_name = 'new value'
        error = context.exception.errors()[0]
        self.assertEqual(error['type'], 'frozen_instance')
        self.assertEqual(error['loc'][0], 'application_attribute_name')

    def test_incorrect_type_dependency_value(self):
        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            ApplicationDependencyMapper(
                application_attribute_name='external_adapter_class',
                request_attribute_value_map={
                    FirstTestEnum.FIRST_VALUE1: 'incorrect_type_dependency_value',
                    FirstTestEnum.FIRST_VALUE2: Example1ExternalAdapter(),
                },
            )
        error = context.exception.errors()[0]['ctx']['error']
        self.assertEqual(error.code, 'incorrect_type_dependency_value')

    def test_not_unique_dependency_values(self):
        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            ApplicationDependencyMapper(
                application_attribute_name='external_adapter_class',
                request_attribute_value_map={
                    FirstTestEnum.FIRST_VALUE1: Example1ExternalAdapter,
                    FirstTestEnum.FIRST_VALUE2: Example1ExternalAdapter,
                },
            )
        error = context.exception.errors()[0]['ctx']['error']
        self.assertEqual(error.code, 'not_unique_dependency_values')

    def test_incorrect_request_attribute_value(self):
        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            ApplicationDependencyMapper(
                application_attribute_name='external_adapter_class',
                request_attribute_value_map={'incorrect_request_attribute_value': ExternalAdapter},
            )
        error = context.exception.errors()[0]['ctx']['error']
        self.assertEqual(error.code, 'incorrect_request_attribute_value')

    def test_another_types_request_attribute_values(self):
        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            ApplicationDependencyMapper(
                application_attribute_name='external_adapter_class',
                request_attribute_value_map={
                    FirstTestEnum.FIRST_VALUE1: ExternalAdapter,
                    SecondTestEnum.SECOND_VALUE1: ExternalAdapter,
                },
            )
        error = context.exception.errors()[0]['ctx']['error']
        self.assertEqual(error.code, 'another_types_request_attribute_values')

    def test_not_enough_request_attribute_values(self):
        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            ApplicationDependencyMapper(
                application_attribute_name='external_adapter_class',
                request_attribute_value_map={FirstTestEnum.FIRST_VALUE1: ExternalAdapter},
            )
        error = context.exception.errors()[0]['ctx']['error']
        self.assertEqual(error.code, 'not_enough_request_attribute_values')
