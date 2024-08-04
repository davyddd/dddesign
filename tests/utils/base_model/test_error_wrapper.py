from typing import Any, Dict, List
from unittest import TestCase

from pydantic import AfterValidator, BaseModel, ValidationError, field_validator, model_validator
from typing_extensions import Annotated

from dddesign.structure.domains.constants import BaseEnum
from dddesign.structure.domains.errors import BaseError, CollectionError
from dddesign.utils.base_model import create_pydantic_error_instance, wrap_error
from dddesign.utils.base_model.error_wrapper import CONTEXT_MESSAGES_PARAM


class ErrorTextEnum(str, BaseEnum):
    CONSISTENCY_ERROR = 'The `two_symbols_field` must be `ab` and the `positive_int_field` must be 1'
    MUST_BE_NON_NEGATIVE = 'Must be non-negative'
    MUST_HAVE_2_CHARACTERS = 'Must have 2 characters'
    LIST_MUST_HAVE_AT_MOST_2_ELEMENTS = 'List must have at most 2 elements'
    LIST_MUST_HAVE_FIRST_ELEMENT_AS_ONE = 'List must have first element as `one`'


def validate_list(value: List[str]) -> List[str]:
    errors = []
    if len(value) > 2:  # noqa: PLR2004
        errors.append(ErrorTextEnum.LIST_MUST_HAVE_AT_MOST_2_ELEMENTS.value)
    if len(value) == 0 or value[0] != 'one':
        errors.append(ErrorTextEnum.LIST_MUST_HAVE_FIRST_ELEMENT_AS_ONE.value)

    if errors:
        raise create_pydantic_error_instance(
            base_error=ValueError, message='Invalid value', context={CONTEXT_MESSAGES_PARAM: errors}
        )

    return value


class SomeModel(BaseModel):
    two_symbols_field: str
    positive_int_field: int
    dict_key_str_field: Dict[str, Any]
    list_max_two_elements_field: Annotated[List[str], AfterValidator(validate_list)]

    @field_validator('two_symbols_field')
    @classmethod
    def validate_two_symbols_field(cls, value):
        if len(value) != 2:  # noqa: PLR2004
            raise ValueError(ErrorTextEnum.MUST_HAVE_2_CHARACTERS.value)
        return value

    @field_validator('positive_int_field')
    @classmethod
    def validate_positive_int_field(cls, value):
        if value < 0:
            raise create_pydantic_error_instance(
                base_error=ValueError,
                code=ErrorTextEnum.MUST_BE_NON_NEGATIVE.name.lower(),
                message=ErrorTextEnum.MUST_BE_NON_NEGATIVE.value,
            )
        return value

    @model_validator(mode='after')
    def validate_consistency(self):
        if self.two_symbols_field != 'ab' or self.positive_int_field != 1:
            raise ValueError(ErrorTextEnum.CONSISTENCY_ERROR.value)
        return self


class TestWrapErrorFunction(TestCase):
    def test_field_validator_with_python_error(self):
        # Arrange
        collection_error = None

        # Act
        try:
            SomeModel(
                two_symbols_field='abc', positive_int_field=1, dict_key_str_field={}, list_max_two_elements_field=['one', 'two']
            )
        except ValidationError as e:
            collection_error = wrap_error(e)

        if collection_error is None:
            raise AssertionError('The `ValidationError` exception was not raised')

        # Assert
        self.assertIsInstance(collection_error, CollectionError)
        self.assertEqual(len(collection_error.errors), 1)
        self.assertTrue(all(isinstance(err, BaseError) for err in collection_error.errors))
        self.assertEqual('two_symbols_field', collection_error.errors[0].field_name)
        self.assertEqual(ErrorTextEnum.MUST_HAVE_2_CHARACTERS, collection_error.errors[0].message)

    def test_field_validator_with_pydantic_error(self):
        # Arrange
        collection_error = None

        # Act
        try:
            SomeModel(
                two_symbols_field='ab', positive_int_field=-1, dict_key_str_field={}, list_max_two_elements_field=['one', 'two']
            )
        except ValidationError as e:
            collection_error = wrap_error(e)

        if collection_error is None:
            raise AssertionError('The `ValidationError` exception was not raised')

        # Assert
        self.assertIsInstance(collection_error, CollectionError)
        self.assertEqual(len(collection_error.errors), 1)
        self.assertTrue(all(isinstance(err, BaseError) for err in collection_error.errors))
        self.assertEqual('positive_int_field', collection_error.errors[0].field_name)
        self.assertEqual(ErrorTextEnum.MUST_BE_NON_NEGATIVE, collection_error.errors[0].message)

    def test_model_validator(self):
        # Arrange
        collection_error = None

        # Act
        try:
            SomeModel(
                two_symbols_field='ab', positive_int_field=2, dict_key_str_field={}, list_max_two_elements_field=['one', 'two']
            )
        except ValidationError as e:
            collection_error = wrap_error(e)

        if collection_error is None:
            raise AssertionError('The `ValidationError` exception was not raised')

        # Assert
        self.assertIsInstance(collection_error, CollectionError)
        self.assertEqual(len(collection_error.errors), 1)
        self.assertTrue(all(isinstance(err, BaseError) for err in collection_error.errors))
        self.assertEqual(None, collection_error.errors[0].field_name)
        self.assertEqual(ErrorTextEnum.CONSISTENCY_ERROR, collection_error.errors[0].message)

    def test_dict_annotation_error(self):
        # Arrange
        collection_error = None

        # Act
        try:
            SomeModel(
                two_symbols_field='ab',
                positive_int_field=1,
                dict_key_str_field={1: 1},
                list_max_two_elements_field=['one', 'two'],
            )
        except ValidationError as e:
            collection_error = wrap_error(e)

        if collection_error is None:
            raise AssertionError('The `ValidationError` exception was not raised')

        # Assert
        self.assertIsInstance(collection_error, CollectionError)
        self.assertEqual(len(collection_error.errors), 1)
        self.assertTrue(all(isinstance(err, BaseError) for err in collection_error.errors))
        self.assertEqual('dict_key_str_field.1.[key]', collection_error.errors[0].field_name)
        self.assertEqual('Input should be a valid string', collection_error.errors[0].message)

    def test_list_annotation_error(self):
        # Arrange
        collection_error = None

        # Act
        try:
            SomeModel(
                two_symbols_field='ab', positive_int_field=1, dict_key_str_field={}, list_max_two_elements_field=['one', 2]
            )
        except ValidationError as e:
            collection_error = wrap_error(e)

        if collection_error is None:
            raise AssertionError('The `ValidationError` exception was not raised')

        # Assert
        self.assertIsInstance(collection_error, CollectionError)
        self.assertEqual(len(collection_error.errors), 1)
        self.assertTrue(all(isinstance(err, BaseError) for err in collection_error.errors))
        self.assertEqual('list_max_two_elements_field.1', collection_error.errors[0].field_name)
        self.assertEqual('Input should be a valid string', collection_error.errors[0].message)

    def test_context_messages_param(self):
        # Arrange
        collection_error = None

        # Act
        try:
            SomeModel(
                two_symbols_field='ab',
                positive_int_field=1,
                dict_key_str_field={},
                list_max_two_elements_field=['onee', 'two', 'three'],
            )
        except ValidationError as e:
            collection_error = wrap_error(e)

        if collection_error is None:
            raise AssertionError('The `ValidationError` exception was not raised')

        # Assert
        self.assertIsInstance(collection_error, CollectionError)
        self.assertEqual(len(collection_error.errors), 2)
        self.assertTrue(all(isinstance(err, BaseError) for err in collection_error.errors))
        self.assertEqual('list_max_two_elements_field', collection_error.errors[0].field_name)
        self.assertEqual(ErrorTextEnum.LIST_MUST_HAVE_AT_MOST_2_ELEMENTS, collection_error.errors[0].message)
        self.assertEqual('list_max_two_elements_field', collection_error.errors[1].field_name)
        self.assertEqual(ErrorTextEnum.LIST_MUST_HAVE_FIRST_ELEMENT_AS_ONE, collection_error.errors[1].message)

    def test_invalid_error(self):
        with self.assertRaises(TypeError):
            wrap_error(ValueError('This is not a ValidationError'))
