from unittest import TestCase

from dddesign.utils.convertors import convert_camel_case_to_snake_case


class TestSnakeCaseConvertor(TestCase):
    def test_converting_camel_case_to_snake_case(self):
        # Act & Assert
        self.assertEqual(convert_camel_case_to_snake_case('test'), 'test')
        self.assertEqual(convert_camel_case_to_snake_case('Test'), 'test')
        self.assertEqual(convert_camel_case_to_snake_case('TestTest'), 'test_test')
        self.assertEqual(convert_camel_case_to_snake_case('testTest'), 'test_test')
        self.assertEqual(convert_camel_case_to_snake_case('Testtest'), 'testtest')
