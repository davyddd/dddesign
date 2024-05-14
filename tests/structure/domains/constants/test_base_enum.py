from unittest import TestCase

from dddesign.structure.domains.constants import BaseEnum


class IntEnum(int, BaseEnum):
    FIRST = 1
    SECOND = 2


class StrEnum(str, BaseEnum):
    FIRST = '1'
    SECOND = '2'


class TestBaseEnum(TestCase):
    def test_has_value_int(self):
        # Act & Assert
        self.assertTrue(IntEnum.has_value(1))
        self.assertTrue(IntEnum.has_value(2))
        self.assertFalse(IntEnum.has_value(3))
        self.assertFalse(IntEnum.has_value('4'))

    def test_has_value_str(self):
        # Act & Assert
        self.assertTrue(StrEnum.has_value('1'))
        self.assertTrue(StrEnum.has_value('2'))
        self.assertFalse(StrEnum.has_value('3'))
        self.assertFalse(StrEnum.has_value(4))
