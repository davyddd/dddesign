from unittest import TestCase

from pydantic.errors import PydanticErrorMixin

from dddesign.utils.base_model import create_pydantic_error_instance


class TestCreatePydanticErrorInstance(TestCase):
    def test_create_pydantic_error_instance_without_context(self):
        # Arrange
        base_error = ValueError
        code = 'test_error_code'
        message = 'This is a test error message.'

        # Act
        pydantic_error = create_pydantic_error_instance(base_error=base_error, code=code, message=message)

        # Assert
        self.assertIsInstance(pydantic_error, base_error)
        self.assertIsInstance(pydantic_error, PydanticErrorMixin)
        self.assertEqual(getattr(pydantic_error, 'code', None), code)
        self.assertEqual(getattr(pydantic_error, 'message', None), message)

    def test_create_pydantic_error_instance_with_context(self):
        # Arrange
        base_error = TypeError
        code = 'test_error_code'
        message = 'This is a test error message with context: {context}.'
        context = {'context': 'some context'}

        # Act
        pydantic_error = create_pydantic_error_instance(base_error=base_error, code=code, message=message, context=context)

        # Assert
        self.assertIsInstance(pydantic_error, base_error)
        self.assertIsInstance(pydantic_error, PydanticErrorMixin)
        self.assertEqual(getattr(pydantic_error, 'code', None), code)
        self.assertEqual(getattr(pydantic_error, 'message', None), message.format(**context))
