from unittest import TestCase

from pydantic import ValidationError

from dddesign.structure.applications.application_factory import ApplicationDependencyMapper
from dddesign.structure.domains.constants import BaseEnum
from dddesign.structure.infrastructure.adapters.external import ExternalAdapter
from dddesign.utils.type_helpers import is_subclass_smart


class FirstTestEnum(str, BaseEnum):
    FIRST_VALUE1 = 'first_fvalue1'
    FIRST_VALUE2 = 'first_value2'


class SecondTestEnum(str, BaseEnum):
    SECOND_VALUE1 = 'second_value1'
    SECOND_VALUE2 = 'second_value2'


class Test1ExternalAdapter(ExternalAdapter):
    pass


class Test2ExternalAdapter(ExternalAdapter):
    pass


class TestApplicationDependencyMapper(TestCase):
    def test_correct_state(self):
        # Act
        instance = ApplicationDependencyMapper(
            application_attribute_name='external_adapter',
            request_attribute_value_map={
                FirstTestEnum.FIRST_VALUE1: Test1ExternalAdapter(),
                FirstTestEnum.FIRST_VALUE2: Test2ExternalAdapter(),
            },
        )

        # Assert
        assert is_subclass_smart(instance.enum_class, FirstTestEnum)
        self.assertEqual(instance.get_request_attribute_name(), 'first_test_enum')
        with self.assertRaises(TypeError):
            instance.application_attribute_name = 'new value'

    def test_incorrect_type_dependency_value(self):
        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            ApplicationDependencyMapper(
                application_attribute_name='external_adapter_class',
                request_attribute_value_map={
                    FirstTestEnum.FIRST_VALUE1: 'incorrect_type_dependency_value',
                    FirstTestEnum.FIRST_VALUE2: Test1ExternalAdapter(),
                },
            )
        self.assertEqual(context.exception.errors()[0]['type'], 'value_error.incorrect_type_dependency_value')

    def test_not_unique_dependency_values(self):
        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            ApplicationDependencyMapper(
                application_attribute_name='external_adapter_class',
                request_attribute_value_map={
                    FirstTestEnum.FIRST_VALUE1: Test1ExternalAdapter,
                    FirstTestEnum.FIRST_VALUE2: Test1ExternalAdapter,
                },
            )

        self.assertEqual(context.exception.errors()[0]['type'], 'value_error.not_unique_dependency_values')

    def test_incorrect_request_attribute_value(self):
        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            ApplicationDependencyMapper(
                application_attribute_name='external_adapter_class',
                request_attribute_value_map={'incorrect_request_attribute_value': ExternalAdapter},
            )
        self.assertEqual(context.exception.errors()[0]['type'], 'value_error.incorrect_request_attribute_value')

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
        self.assertEqual(context.exception.errors()[0]['type'], 'value_error.another_types_request_attribute_values')

    def test_not_enough_request_attribute_values(self):
        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            ApplicationDependencyMapper(
                application_attribute_name='external_adapter_class',
                request_attribute_value_map={FirstTestEnum.FIRST_VALUE1: ExternalAdapter},
            )
        self.assertEqual(context.exception.errors()[0]['type'], 'value_error.not_enough_request_attribute_values')
