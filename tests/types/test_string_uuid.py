import uuid
from unittest import TestCase

from pydantic import BaseModel

from dddesign.types import StringUUID


class DataObject(BaseModel):
    data_id: StringUUID


class TestStringUUID(TestCase):
    def test_validate_uuid(self):
        # Arrange
        some_uuid = uuid.uuid4()

        # Act
        data = DataObject(data_id=some_uuid)

        # Assert
        self.assertIsInstance(data.data_id, str)
        self.assertIsInstance(hash(data.data_id), int)
        self.assertEqual(data.data_id, some_uuid)  # check equality with UUID type

    def test_validate_string_uuid(self):
        # Arrange
        some_uuid_str = str(uuid.uuid4())

        # Act
        data = DataObject(data_id=some_uuid_str)

        # Assert
        self.assertIsInstance(data.data_id, str)
        self.assertIsInstance(hash(data.data_id), int)
        self.assertEqual(data.data_id, some_uuid_str)  # check equality with str type

    def test_invalid_uuid(self):
        # Act & Assert
        with self.assertRaises(ValueError):
            DataObject(data_id='invalid uuid')
