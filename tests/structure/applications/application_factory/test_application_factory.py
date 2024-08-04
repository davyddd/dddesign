from unittest import TestCase

from pydantic import ValidationError

from dddesign.structure.applications import Application, ApplicationDependencyMapper, ApplicationFactory
from dddesign.structure.applications.application_factory import RequestAttributeNotProvideError, RequestAttributeValueError
from dddesign.structure.domains.constants import BaseEnum
from dddesign.structure.infrastructure.adapters.external import ExternalAdapter


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


class ExampleWithoutDefaultStateApp(Application):
    external_adapter: ExternalAdapter


class ExampleWitDefaultStateApp(Application):
    external_adapter: ExternalAdapter = Example1ExternalAdapter()


class TestApplicationFactory(TestCase):
    def test_correct_state_fill_dependency_mapper(self):
        # Act
        application_factory = ApplicationFactory(
            application_class=ExampleWithoutDefaultStateApp,
            dependency_mappers=(
                ApplicationDependencyMapper(
                    application_attribute_name='external_adapter',
                    request_attribute_value_map={
                        FirstTestEnum.FIRST_VALUE1: Example1ExternalAdapter(),
                        FirstTestEnum.FIRST_VALUE2: Example2ExternalAdapter(),
                    },
                ),
            ),
        )

        # Assert
        instance1 = application_factory.get(**{'first_test_enum': FirstTestEnum.FIRST_VALUE1})
        self.assertIsInstance(instance1, ExampleWithoutDefaultStateApp)
        self.assertIsInstance(instance1.external_adapter, Example1ExternalAdapter)
        assert instance1 is application_factory.get(**{'first_test_enum': FirstTestEnum.FIRST_VALUE1})

        instance2 = application_factory.get(**{'first_test_enum': FirstTestEnum.FIRST_VALUE2})
        self.assertIsInstance(instance2, ExampleWithoutDefaultStateApp)
        self.assertIsInstance(instance2.external_adapter, Example2ExternalAdapter)
        assert instance2 is application_factory.get(**{'first_test_enum': FirstTestEnum.FIRST_VALUE2})

        with self.assertRaises(RequestAttributeNotProvideError):
            application_factory.get()

        with self.assertRaises(RequestAttributeValueError):
            application_factory.get(**{'first_test_enum': 'unknown_value'})

    def test_correct_state_empty_dependency_mapper(self):
        # Act
        application_factory = ApplicationFactory(application_class=ExampleWitDefaultStateApp)

        # Assert
        instance = application_factory.get()
        self.assertIsInstance(instance, ExampleWitDefaultStateApp)
        self.assertIsInstance(instance.external_adapter, Example1ExternalAdapter)
        assert instance is application_factory.get()

    def test_correct_state_empty_dependency_mapper_with_disabled_reuse_implementations(self):
        # Act
        application_factory = ApplicationFactory(application_class=ExampleWitDefaultStateApp, reuse_implementations=False)

        # Assert
        instance = application_factory.get()
        self.assertIsInstance(instance, ExampleWitDefaultStateApp)
        self.assertIsInstance(instance.external_adapter, Example1ExternalAdapter)
        assert instance is not application_factory.get()

    def test_correct_state_empty_dependency_mapper_with_called_unknown_attributes(self):
        # Act
        application_factory = ApplicationFactory(application_class=ExampleWitDefaultStateApp)

        # Assert
        instance = application_factory.get(**{'unknown_attribute': 'test'})
        self.assertIsInstance(instance, ExampleWitDefaultStateApp)
        self.assertIsInstance(instance.external_adapter, Example1ExternalAdapter)
        assert instance is application_factory.get()

    def test_not_enough_dependency_mapper(self):
        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            ApplicationFactory(application_class=ExampleWithoutDefaultStateApp)
        error = context.exception.errors()[0]['ctx']['error']
        self.assertEqual(error.code, 'not_enough_dependency_mappers')

    def test_not_enough_dependency_mapper_with_incorrect_application_attribute_name(self):
        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            ApplicationFactory(
                application_class=ExampleWithoutDefaultStateApp,
                dependency_mappers=(
                    ApplicationDependencyMapper(
                        application_attribute_name='incorrect_external_adapter',
                        request_attribute_value_map={
                            FirstTestEnum.FIRST_VALUE1: Example1ExternalAdapter(),
                            FirstTestEnum.FIRST_VALUE2: Example2ExternalAdapter(),
                        },
                    ),
                ),
            )
        error = context.exception.errors()[0]['ctx']['error']
        self.assertEqual(error.code, 'not_enough_dependency_mappers')

    def test_not_unique_enum_classes_in_dependency_mappers(self):
        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            ApplicationFactory(
                application_class=ExampleWithoutDefaultStateApp,
                dependency_mappers=(
                    ApplicationDependencyMapper(
                        application_attribute_name='example_external_adapter',
                        request_attribute_value_map={
                            FirstTestEnum.FIRST_VALUE1: Example1ExternalAdapter(),
                            FirstTestEnum.FIRST_VALUE2: Example2ExternalAdapter(),
                        },
                    ),
                    ApplicationDependencyMapper(
                        application_attribute_name='external_adapter',
                        request_attribute_value_map={
                            FirstTestEnum.FIRST_VALUE1: Example1ExternalAdapter(),
                            FirstTestEnum.FIRST_VALUE2: Example2ExternalAdapter(),
                        },
                    ),
                ),
            )
        error = context.exception.errors()[0]['ctx']['error']
        self.assertEqual(error.code, 'not_unique_enum_classes_in_dependency_mappers')

    def test_not_unique_application_attribute_name_in_dependency_mappers(self):
        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            ApplicationFactory(
                application_class=ExampleWithoutDefaultStateApp,
                dependency_mappers=(
                    ApplicationDependencyMapper(
                        application_attribute_name='external_adapter',
                        request_attribute_value_map={
                            FirstTestEnum.FIRST_VALUE1: Example1ExternalAdapter(),
                            FirstTestEnum.FIRST_VALUE2: Example2ExternalAdapter(),
                        },
                    ),
                    ApplicationDependencyMapper(
                        application_attribute_name='external_adapter',
                        request_attribute_value_map={
                            SecondTestEnum.SECOND_VALUE1: Example1ExternalAdapter(),
                            SecondTestEnum.SECOND_VALUE2: Example2ExternalAdapter(),
                        },
                    ),
                ),
            )
        error = context.exception.errors()[0]['ctx']['error']
        self.assertEqual(error.code, 'not_unique_application_attribute_name_in_dependency_mappers')

    def test_not_unique_request_attribute_name_in_dependency_mappers(self):
        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            ApplicationFactory(
                application_class=ExampleWithoutDefaultStateApp,
                dependency_mappers=(
                    ApplicationDependencyMapper(
                        request_attribute_name='external_adapter_enum',
                        application_attribute_name='first_external_adapter',
                        request_attribute_value_map={
                            FirstTestEnum.FIRST_VALUE1: Example1ExternalAdapter(),
                            FirstTestEnum.FIRST_VALUE2: Example2ExternalAdapter(),
                        },
                    ),
                    ApplicationDependencyMapper(
                        request_attribute_name='external_adapter_enum',
                        application_attribute_name='external_adapter',
                        request_attribute_value_map={
                            SecondTestEnum.SECOND_VALUE1: Example1ExternalAdapter(),
                            SecondTestEnum.SECOND_VALUE2: Example2ExternalAdapter(),
                        },
                    ),
                ),
            )
        error = context.exception.errors()[0]['ctx']['error']
        self.assertEqual(error.code, 'not_unique_request_attribute_name_in_dependency_mappers')
