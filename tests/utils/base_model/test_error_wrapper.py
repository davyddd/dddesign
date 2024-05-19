from collections import defaultdict
from typing import Generator, List
from unittest import TestCase

from pydantic import BaseModel, ValidationError, validator
from pydantic.typing import AnyCallable

from dddesign.structure.domains.constants import BaseEnum
from dddesign.structure.domains.errors import BaseError, CollectionError
from dddesign.structure.domains.types import BaseType
from dddesign.utils.base_model import create_pydantic_error_instance, wrap_error
from dddesign.utils.base_model.error_wrapper import CONTEXT_MESSAGES_PARAM


class ErrorTextEnum(str, BaseEnum):
    INVALID_VALUE = 'Invalid value'
    MUST_BE_NON_NEGATIVE = 'Must be non-negative'
    LIST_MUST_HAVE_AT_MOST_2_ELEMENTS = 'List must have at most 2 elements'
    AN_ELEMENT_OF_LIST_MUST_BE_STR = 'An element of list must be str'


class ListMaxTwoStrElements(list, BaseType):
    @classmethod
    def __get_validators__(cls) -> Generator[AnyCallable, None, None]:
        yield cls.validate

    @classmethod
    def validate(cls, value: List) -> 'ListMaxTwoStrElements':
        errors = []
        if len(value) > 2:  # noqa: PLR2004
            errors.append(ErrorTextEnum.LIST_MUST_HAVE_AT_MOST_2_ELEMENTS)
        for obj in value:
            if not isinstance(obj, str):
                errors.append(ErrorTextEnum.AN_ELEMENT_OF_LIST_MUST_BE_STR)

        if errors:
            # If the `CONTEXT_MESSAGES_PARAM` is retrieved in the context,
            # then the `msg_template` will be ignored in the `wrap_error` function.
            raise create_pydantic_error_instance(
                base_error=ValueError,
                code='value_error',
                msg_template='Invalid value',
                context={CONTEXT_MESSAGES_PARAM: errors},
            )

        return cls(value)


class SomeModel(BaseModel):
    two_symbols_field: str
    positive_int_field: int
    list_max_two_elements_field: ListMaxTwoStrElements

    @validator('two_symbols_field')
    def validate_two_symbols_field(cls, value):
        if len(value) != 2:  # noqa: PLR2004
            raise ValueError(ErrorTextEnum.INVALID_VALUE)
        return value

    @validator('positive_int_field')
    def validate_positive_int_field(cls, value):
        if value < 0:
            raise ValueError(ErrorTextEnum.MUST_BE_NON_NEGATIVE)
        return value


class TestWrapErrorFunction(TestCase):
    def test_correct_error(self):
        # Arrange
        collection_error = None

        # Act
        try:
            SomeModel(two_symbols_field='abc', positive_int_field=-1, list_max_two_elements_field=['one', 2, 'three'])
        except ValidationError as e:
            collection_error = wrap_error(e)

        if collection_error is None:
            raise AssertionError('The `ValidationError` exception was not raised')

        # Assert
        self.assertIsInstance(collection_error, CollectionError)
        self.assertEqual(len(collection_error.errors), 4)
        self.assertTrue(all(isinstance(err, BaseError) for err in collection_error.errors))

        grouped_errors_by_field_name = defaultdict(list)
        for base_error in collection_error.errors:
            grouped_errors_by_field_name[base_error.field_name].append(base_error.message)

        self.assertIn('two_symbols_field', grouped_errors_by_field_name)
        self.assertIn('positive_int_field', grouped_errors_by_field_name)
        self.assertIn('list_max_two_elements_field', grouped_errors_by_field_name)
        self.assertNotIn(None, grouped_errors_by_field_name)

        self.assertIn(ErrorTextEnum.INVALID_VALUE, grouped_errors_by_field_name['two_symbols_field'])
        self.assertIn(ErrorTextEnum.MUST_BE_NON_NEGATIVE, grouped_errors_by_field_name['positive_int_field'])
        self.assertIn(
            ErrorTextEnum.LIST_MUST_HAVE_AT_MOST_2_ELEMENTS, grouped_errors_by_field_name['list_max_two_elements_field']
        )
        self.assertIn(ErrorTextEnum.AN_ELEMENT_OF_LIST_MUST_BE_STR, grouped_errors_by_field_name['list_max_two_elements_field'])

    def test_invalid_error(self):
        with self.assertRaises(TypeError):
            wrap_error(ValueError('This is not a ValidationError'))
