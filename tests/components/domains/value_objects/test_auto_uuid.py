from unittest import TestCase
from uuid import UUID, uuid4

from parameterized import parameterized
from pydantic import BaseModel as BaseModelV2, Field as FieldV2, ValidationError as ValidationErrorV2
from pydantic.v1 import BaseModel as BaseModelV1, Field as FieldV1, ValidationError as ValidationErrorV1

from dddesign.components.domains.value_objects import AutoUUID


class CustomerId(AutoUUID):
    pass


class CustomerV1(BaseModelV1):
    customer_id: CustomerId = FieldV1(default_factory=CustomerId)
    name: str


class CustomerV2(BaseModelV2):
    customer_id: CustomerId = FieldV2(default_factory=CustomerId)
    name: str


class TestAutoUUID(TestCase):
    @parameterized.expand((AutoUUID, CustomerId))
    def test_auto_generation_no_args(self, klass):
        # Act
        uuid1 = klass()
        uuid2 = klass()

        # Assert
        self.assertIsInstance(uuid1, klass)
        self.assertIsInstance(uuid1, AutoUUID)
        self.assertIsInstance(uuid1, UUID)
        self.assertNotEqual(uuid1, uuid2)

    def test_from_hex_string_with_hyphens(self):
        # Arrange
        hex_string = '12345678-1234-5678-1234-567812345678'

        # Act
        result = AutoUUID(hex_string)

        # Assert
        self.assertEqual(str(result), hex_string)

    def test_from_hex_string_no_hyphens(self):
        # Arrange
        hex_string = '12345678123456781234567812345678'

        # Act
        result = AutoUUID(hex_string)

        # Assert
        self.assertEqual(result.hex, hex_string)

    def test_from_int(self):
        # Arrange
        int_value = 123456789012345678901234567890123456

        # Act
        result = AutoUUID(int=int_value)

        # Assert
        self.assertEqual(result.int, int_value)

    def test_from_uuid_instance(self):
        # Arrange
        original_uuid = uuid4()

        # Act
        result = AutoUUID(original_uuid)

        # Assert
        self.assertEqual(result.hex, original_uuid.hex)

    def test_from_bytes(self):
        # Arrange
        bytes_value = uuid4().bytes

        # Act
        result = AutoUUID(bytes=bytes_value)

        # Assert
        self.assertEqual(result.bytes, bytes_value)

    @parameterized.expand((CustomerV1, CustomerV2))
    def test_pydantic_validation_auto_generation(self, pydantic_class):
        # Act
        customer = pydantic_class(name='John Doe')

        # Assert
        self.assertIsInstance(customer.customer_id, CustomerId)
        self.assertIsInstance(customer.customer_id, UUID)

    @parameterized.expand((CustomerV1, CustomerV2))
    def test_pydantic_validation_from_hex_string_with_hyphens(self, pydantic_class):
        # Arrange
        hex_string = '12345678-1234-5678-1234-567812345678'

        # Act
        customer = pydantic_class(customer_id=hex_string, name='Test User')

        # Assert
        self.assertEqual(str(customer.customer_id), hex_string)
        self.assertIsInstance(customer.customer_id, UUID)

    @parameterized.expand((CustomerV1, CustomerV2))
    def test_pydantic_validation_from_uuid(self, pydantic_class):
        # Arrange
        original_uuid = uuid4()

        # Act
        customer = pydantic_class(customer_id=original_uuid, name='Test User')

        # Assert
        self.assertEqual(customer.customer_id.hex, original_uuid.hex)
        self.assertIsInstance(customer.customer_id, UUID)

    @parameterized.expand(((CustomerV1, ValidationErrorV1), (CustomerV2, ValidationErrorV2)))
    def test_pydantic_validation_invalid_hex_string(self, pydantic_class, validation_error):
        # Act & Assert
        with self.assertRaises(validation_error):
            pydantic_class(customer_id='invalid-uuid', name='Test User')

    @parameterized.expand(((CustomerV1, 'dict'), (CustomerV2, 'model_dump')))
    def test_pydantic_serialization(self, pydantic_class, model_dump_name):
        # Arrange
        hex_string = '12345678-1234-5678-1234-567812345678'
        customer = pydantic_class(customer_id=hex_string, name='Test User')

        # Act
        serialized = getattr(customer, model_dump_name)()

        # Assert
        self.assertEqual(str(serialized['customer_id']), hex_string)
