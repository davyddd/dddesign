from typing import Any, Dict, List, Optional
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


class SomeEnum(str, BaseEnum):
    ONE = 'one'
    TWO = 'two'


class NestedModel(BaseModel):
    int_field: int


class SomeModel(BaseModel):
    two_symbols_field: str
    positive_int_field: int
    dict_key_str_field: Dict[str, Any]
    list_max_two_elements_field: Annotated[List[str], AfterValidator(validate_list)]
    enum_field: Optional[SomeEnum] = None
    nested_model_field: Optional[NestedModel] = None

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
    def setUp(self):
        self.correct_required_fields_data = {
            'two_symbols_field': 'ab',
            'positive_int_field': 1,
            'dict_key_str_field': {},
            'list_max_two_elements_field': ['one', 'two'],
        }

    def test_field_validator_with_python_error(self):
        # Arrange
        collection_error = None

        # Act
        try:
            SomeModel(**{**self.correct_required_fields_data, 'two_symbols_field': 'abc'})
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
            SomeModel(**{**self.correct_required_fields_data, 'positive_int_field': -1})
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
            SomeModel(**{**self.correct_required_fields_data, 'positive_int_field': 2})
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
            SomeModel(**{**self.correct_required_fields_data, 'dict_key_str_field': {1: 1}})
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
            SomeModel(**{**self.correct_required_fields_data, 'list_max_two_elements_field': ['one', 2]})
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
                **{**self.correct_required_fields_data, 'list_max_two_elements_field': ['incorrect_value', 'two', 'three']}
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
        # Act & Assert
        with self.assertRaises(TypeError):
            wrap_error(ValueError('This is not a ValidationError'))

    def test_required_fields_error(self):
        # Arrange
        collection_error = None

        # Act
        try:
            SomeModel()
        except ValidationError as e:
            collection_error = wrap_error(e)

        if collection_error is None:
            raise AssertionError('The `ValidationError` exception was not raised')

        # Assert
        self.assertIsInstance(collection_error, CollectionError)
        self.assertEqual(len(collection_error.errors), 4)
        self.assertTrue(all(isinstance(err, BaseError) for err in collection_error.errors))
        self.assertSetEqual(
            set(self.correct_required_fields_data.keys()),
            {err.field_name for err in collection_error.errors},
            'The required fields of the model do not match the expected required fields',
        )

    def test_enum_error(self):
        # Arrange
        collection_error = None

        # Act
        try:
            SomeModel(**{**self.correct_required_fields_data, 'enum_field': 'incorrect_value'})
        except ValidationError as e:
            collection_error = wrap_error(e)

        if collection_error is None:
            raise AssertionError('The `ValidationError` exception was not raised')

        # Assert
        self.assertIsInstance(collection_error, CollectionError)
        self.assertEqual(len(collection_error.errors), 1)
        self.assertTrue(all(isinstance(err, BaseError) for err in collection_error.errors))
        self.assertEqual('enum_field', collection_error.errors[0].field_name)

    def test_nested_model_error(self):
        # Arrange
        collection_error = None

        # Act
        try:
            SomeModel(**{**self.correct_required_fields_data, 'nested_model_field': {'int_field': 'incorrect_value'}})
        except ValidationError as e:
            collection_error = wrap_error(e)

        if collection_error is None:
            raise AssertionError('The `ValidationError` exception was not raised')

        # Assert
        self.assertIsInstance(collection_error, CollectionError)
        self.assertEqual(len(collection_error.errors), 1)
        self.assertTrue(all(isinstance(err, BaseError) for err in collection_error.errors))
        self.assertEqual('nested_model_field.int_field', collection_error.errors[0].field_name)
