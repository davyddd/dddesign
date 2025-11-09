from unittest import TestCase

from parameterized import parameterized

from dddesign.structure.domains.constants import ChoiceEnum


class PriorityEnum(int, ChoiceEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class StatusEnum(str, ChoiceEnum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    PENDING_APPROVAL = 'pending_approval'


class TestChoiceEnum(TestCase):
    @parameterized.expand(
        ((PriorityEnum, 'LOW', 'Low'), (StatusEnum, 'ACTIVE', 'Active'), (StatusEnum, 'PENDING_APPROVAL', 'Pending Approval'))
    )
    def test_get_title(self, enum, attribute, check_title):
        # Act
        title = getattr(enum, attribute).get_title()

        # Assert
        self.assertEqual(title, check_title)

    @parameterized.expand(('PriorityEnum', 'StatusEnum'))
    def test_get_choices(self, enum):
        # Act
        enum_class = globals()[enum]
        choices = enum_class.get_choices()

        # Assert
        self.assertIsInstance(choices, tuple)
        self.assertEqual(len(choices), 3)
