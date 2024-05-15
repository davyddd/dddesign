from unittest import TestCase

from pydantic import BaseModel, ValidationError

from dddesign.types import EmailStr


class DataObject(BaseModel):
    email: EmailStr


class TestEmailStr(TestCase):
    def test_email_with_whitespaces(self):
        # Act
        data = DataObject(email=' test@test.com ')

        # Assert
        self.assertEqual(data.email, 'test@test.com')

    def test_insensitivity_email(self):
        # Act
        data = DataObject(email='TeSt@Test.cOm')

        # Assert
        self.assertEqual(data.email, 'test@test.com')

    def test_invalid_email(self):
        # Act & Assert
        with self.assertRaises(ValidationError):
            DataObject(email='test@test.test')

    def test_invalid_email_as_str(self):
        # Act & Assert
        with self.assertRaises(ValidationError):
            DataObject(email='invalid email')

    def test_invalid_email_as_int(self):
        # Act & Assert
        with self.assertRaises(ValidationError):
            DataObject(email=12345)
