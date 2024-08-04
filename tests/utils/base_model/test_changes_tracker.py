from typing import Dict, List
from unittest import TestCase

from parameterized import parameterized
from pydantic import BaseModel

from dddesign.utils.base_model import TrackChangesMixin


class NestedModel(BaseModel):
    str_field: str


class SomeModel(TrackChangesMixin, BaseModel):
    str_field: str
    int_field: int
    float_field: float
    dict_field: Dict[str, str]
    list_field: List[int]
    nested_model_field: NestedModel


class TestTrackChangesMixin(TestCase):
    def setUp(self):
        self.initial_state = {
            'str_field': 'initial',
            'int_field': 1,
            'float_field': 1.0,
            'dict_field': {'key': 'value'},
            'list_field': [1, 2, 3],
            'nested_model_field': {'str_field': 'initial'},
        }
        self.some_model_instance = SomeModel(**self.initial_state)

    def test_without_changes(self):
        # Act & Assert
        self.assertEqual(self.some_model_instance.initial_state, self.initial_state)
        self.assertFalse(self.some_model_instance.has_changed)
        self.assertEqual(self.some_model_instance.changed_fields, ())
        self.assertEqual(self.some_model_instance.changed_data, {})
        self.assertEqual(self.some_model_instance.diffs, {})

    def test_change_str_field(self):
        # Act
        self.some_model_instance.str_field = 'changed'

        # Assert
        self.assertEqual(self.some_model_instance.initial_state, self.initial_state)
        self.assertTrue(self.some_model_instance.has_changed)
        self.assertEqual(self.some_model_instance.changed_fields, ('str_field',))
        self.assertEqual(self.some_model_instance.changed_data, {'str_field': self.some_model_instance.str_field})
        self.assertEqual(
            self.some_model_instance.diffs, {'str_field': (self.initial_state['str_field'], self.some_model_instance.str_field)}
        )

    def test_change_int_field(self):
        # Act
        self.some_model_instance.int_field = 2

        # Assert
        self.assertEqual(self.some_model_instance.initial_state, self.initial_state)
        self.assertTrue(self.some_model_instance.has_changed)
        self.assertEqual(self.some_model_instance.changed_fields, ('int_field',))
        self.assertEqual(self.some_model_instance.changed_data, {'int_field': self.some_model_instance.int_field})
        self.assertEqual(
            self.some_model_instance.diffs, {'int_field': (self.initial_state['int_field'], self.some_model_instance.int_field)}
        )

    @parameterized.expand((('key', 'new_value'), ('new_key', 'value')))
    def test_change_dict_field(self, key, value):
        # Act
        self.some_model_instance.dict_field[key] = value

        # Assert
        self.assertEqual(self.some_model_instance.initial_state, self.initial_state)
        self.assertTrue(self.some_model_instance.has_changed)
        self.assertEqual(self.some_model_instance.changed_fields, ('dict_field',))
        self.assertEqual(self.some_model_instance.changed_data, {'dict_field': self.some_model_instance.dict_field})
        self.assertEqual(
            self.some_model_instance.diffs,
            {'dict_field': (self.initial_state['dict_field'], self.some_model_instance.dict_field)},
        )

    def test_change_list_field(self):
        # Act
        self.some_model_instance.list_field.append(4)

        # Assert
        self.assertEqual(self.some_model_instance.initial_state, self.initial_state)
        self.assertTrue(self.some_model_instance.has_changed)
        self.assertEqual(self.some_model_instance.changed_fields, ('list_field',))
        self.assertEqual(self.some_model_instance.changed_data, {'list_field': self.some_model_instance.list_field})
        self.assertEqual(
            self.some_model_instance.diffs,
            {'list_field': (self.initial_state['list_field'], self.some_model_instance.list_field)},
        )

    def test_change_nested_model(self):
        # Act
        self.some_model_instance.nested_model_field.str_field = 'changed'

        # Assert
        self.assertEqual(self.some_model_instance.initial_state, self.initial_state)
        self.assertTrue(self.some_model_instance.has_changed)
        self.assertEqual(self.some_model_instance.changed_fields, ('nested_model_field',))
        self.assertEqual(
            self.some_model_instance.changed_data, {'nested_model_field': self.some_model_instance.nested_model_field}
        )
        self.assertEqual(
            self.some_model_instance.diffs,
            {
                'nested_model_field': (
                    self.initial_state['nested_model_field'],
                    self.some_model_instance.nested_model_field.model_dump(),
                )
            },
        )

    def test_multiple_changes(self):
        # Act
        self.some_model_instance.str_field = 'changed'
        self.some_model_instance.int_field = 2

        # Assert
        self.assertEqual(self.some_model_instance.initial_state, self.initial_state)
        self.assertTrue(self.some_model_instance.has_changed)
        self.assertEqual(set(self.some_model_instance.changed_fields), {'str_field', 'int_field'})
        self.assertEqual(
            self.some_model_instance.changed_data,
            {'str_field': self.some_model_instance.str_field, 'int_field': self.some_model_instance.int_field},
        )
        self.assertEqual(
            self.some_model_instance.diffs,
            {
                'str_field': (self.initial_state['str_field'], self.some_model_instance.str_field),
                'int_field': (self.initial_state['int_field'], self.some_model_instance.int_field),
            },
        )

    def test_reset_initial_state(self):
        # Act
        self.some_model_instance.str_field = 'changed'
        self.some_model_instance.int_field = 2
        self.some_model_instance.update_initial_state()

        # Assert
        self.assertEqual(self.some_model_instance.initial_state, self.some_model_instance.model_dump())
        self.assertFalse(self.some_model_instance.has_changed)
        self.assertEqual(self.some_model_instance.changed_fields, ())
        self.assertEqual(self.some_model_instance.changed_data, {})
        self.assertEqual(self.some_model_instance.diffs, {})

    def test_partial_update_initial_state(self):
        # Arrange
        initial_state = self.initial_state.copy()

        # Act
        self.some_model_instance.str_field = 'changed'
        self.some_model_instance.int_field = 2

        initial_state['str_field'] = self.some_model_instance.str_field
        self.some_model_instance.update_initial_state(fields=('str_field',))

        # Assert
        self.assertEqual(self.some_model_instance.initial_state, initial_state)
        self.assertTrue(self.some_model_instance.has_changed)
        self.assertEqual(self.some_model_instance.changed_fields, ('int_field',))
        self.assertEqual(self.some_model_instance.changed_data, {'int_field': self.some_model_instance.int_field})
        self.assertEqual(
            self.some_model_instance.diffs, {'int_field': (self.initial_state['int_field'], self.some_model_instance.int_field)}
        )
