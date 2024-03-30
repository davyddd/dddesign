from unittest import TestCase

from dddesign.structure.applications import Application


class TestApplication(TestCase):
    def test_immutable(self):
        # Arrange
        class ExampleApp(Application):
            some_field: str

        # Act
        instance = ExampleApp(some_field='value')

        # Assert
        with self.assertRaises(TypeError):
            instance.some_field = 'new value'

    def test_arbitrary_types_allowed(self):
        # Arrange
        class Custom:
            ...

        # Act & Assert
        try:
            class ExampleApp(Application):
                some_field: Custom
        except RuntimeError:
            self.fail('RuntimeError raised')
