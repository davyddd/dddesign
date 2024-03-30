from unittest import TestCase

from pydantic import ValidationError

from dddesign.structure.applications.application_factory import ApplicationDependencyMapper
from dddesign.structure.domains.constants import BaseEnum
from dddesign.structure.infrastructure.adapters.external import ExternalAdapter
from dddesign.utils.type_helpers import is_subclass_smart


class FirstTestEnum(str, BaseEnum):
    VALUE1 = 'value1'
    VALUE2 = 'value2'


class SecondTestEnum(str, BaseEnum):
    VALUE1 = 'value1'
    VALUE2 = 'value2'


class TestApplicationDependencyMapper(TestCase):
    def test_correct_state(self):
        # Act
        instance = ApplicationDependencyMapper(
            application_attribute_name='external_adapter',
            request_attribute_value_map={FirstTestEnum.VALUE1: ExternalAdapter, FirstTestEnum.VALUE2: ExternalAdapter},
        )

        # Assert
        assert is_subclass_smart(instance.enum_class, FirstTestEnum)
        self.assertEqual(instance.get_request_attribute_name(), 'first_test_enum')
        with self.assertRaises(TypeError):
            instance.application_attribute_name = 'new value'

    def test_incorrect_request_attribute_value(self):
        # Act & Assert
        with self.assertRaises(ValidationError):
            ApplicationDependencyMapper(
                application_attribute_name='external_adapter',
                request_attribute_value_map={'incorrect_request_attribute_value': ExternalAdapter},
            )

    def test_another_types_request_attribute_values(self):
        # Act & Assert
        with self.assertRaises(ValidationError):
            ApplicationDependencyMapper(
                application_attribute_name='external_adapter',
                request_attribute_value_map={FirstTestEnum.VALUE1: ExternalAdapter, SecondTestEnum.VALUE1: ExternalAdapter},
            )

    def test_not_enough_request_attribute_values(self):
        # Act & Assert
        with self.assertRaises(ValidationError):
            ApplicationDependencyMapper(
                application_attribute_name='external_adapter',
                request_attribute_value_map={FirstTestEnum.VALUE1: ExternalAdapter},
            )
