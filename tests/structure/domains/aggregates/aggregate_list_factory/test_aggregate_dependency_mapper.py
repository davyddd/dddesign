from typing import Dict, List, NewType
from unittest import TestCase

from ddutils.annotation_helpers import get_complex_sequence_element_annotation, is_complex_sequence
from pydantic import ValidationError

from dddesign.structure.domains.aggregates.aggregate_list_factory import AggregateDependencyMapper
from dddesign.structure.domains.entities import Entity

ImageId = NewType('ImageId', int)


class Image(Entity):
    image_id: ImageId
    app_id: int = 1


def get_image(image_id: ImageId) -> Image:
    return Image(image_id=image_id)


def get_image_with_multiple_arguments(app_id: int, image_id: ImageId) -> Image:
    return Image(app_id=app_id, image_id=image_id)


def get_image_without_return_annotation(image_id: ImageId):
    return Image(image_id=image_id)


def get_image_without_arguments() -> Image:
    return Image(app_id=1, image_id=ImageId(1))


def get_images(image_ids: List[ImageId]) -> Dict[ImageId, Image]:
    return {image_id: Image(image_id=image_id) for image_id in image_ids}


def get_images_with_list_return_annotation(image_ids: List[ImageId]) -> List[Image]:
    return [Image(image_id=image_id) for image_id in image_ids]


def get_images_with_not_typed_dict_return_annotation(image_ids: List[ImageId]) -> dict:
    return {image_id: Image(image_id=image_id) for image_id in image_ids}


def get_images_with_incorrect_typed_dict_return_annotation(image_ids: List[ImageId]) -> Dict[int, Image]:
    return {image_id: Image(image_id=image_id) for image_id in image_ids}


class TestAggregateDependencyMapper(TestCase):
    def test_correct_state_for_single_getter(self):
        # Act
        mapper = AggregateDependencyMapper(
            entity_attribute_name='icon_id', aggregate_attribute_name='icon', method_getter=get_image
        )
        method_related_argument = mapper.method_related_argument
        method_return_argument_annotation = mapper.method_return_argument_annotation

        # Assert
        self.assertEqual(method_related_argument.name, 'image_id')
        self.assertEqual(method_related_argument.annotation, ImageId)
        self.assertEqual(method_return_argument_annotation, Image)

        self.assertFalse(is_complex_sequence(method_related_argument.annotation))

    def test_correct_state_for_single_getter_with_multiple_arguments(self):
        # Act
        mapper = AggregateDependencyMapper(
            entity_attribute_name='icon_id',
            aggregate_attribute_name='icon',
            method_getter=get_image_with_multiple_arguments,
            method_extra_arguments={'app_id': 2},
        )
        method_related_argument = mapper.method_related_argument
        method_return_argument_annotation = mapper.method_return_argument_annotation

        # Assert
        self.assertEqual(method_related_argument.name, 'image_id')
        self.assertEqual(method_related_argument.annotation, ImageId)
        self.assertEqual(method_return_argument_annotation, Image)

        self.assertFalse(is_complex_sequence(method_related_argument.annotation))

    def test_incorrect_state_for_single_getter_with_multiple_arguments(self):
        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            AggregateDependencyMapper(
                entity_attribute_name='icon_id',
                aggregate_attribute_name='icon',
                method_getter=get_image_with_multiple_arguments,
            )
        error = context.exception.errors()[0]['ctx']['error']
        self.assertEqual(error.code, 'method_must_have_one_related_argument')

    def test_incorrect_state_for_single_getter_without_arguments(self):
        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            AggregateDependencyMapper(
                entity_attribute_name='icon_id', aggregate_attribute_name='icon', method_getter=get_image_without_arguments
            )
        error = context.exception.errors()[0]['ctx']['error']
        self.assertEqual(error.code, 'method_must_have_one_related_argument')

    def test_method_getter_not_have_return_annotation(self):
        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            AggregateDependencyMapper(
                entity_attribute_name='icon_id',
                aggregate_attribute_name='icon',
                method_getter=get_image_without_return_annotation,
            )
        error = context.exception.errors()[0]['ctx']['error']
        self.assertEqual(error.code, 'method_must_have_return_annotation')

    def test_correct_state_with_multiple_getter(self):
        # Act
        mapper = AggregateDependencyMapper(
            entity_attribute_name='icon_id', aggregate_attribute_name='icon', method_getter=get_images
        )
        method_related_argument = mapper.method_related_argument
        method_return_argument_annotation = mapper.method_return_argument_annotation

        # Assert
        self.assertEqual(method_related_argument.name, 'image_ids')
        self.assertEqual(method_related_argument.annotation, List[ImageId])
        self.assertEqual(method_return_argument_annotation, Dict[ImageId, Image])

        self.assertTrue(is_complex_sequence(method_related_argument.annotation))
        self.assertEqual(get_complex_sequence_element_annotation(method_related_argument.annotation), ImageId)

    def test_multiple_getter_with_list_return_annotation(self):
        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            AggregateDependencyMapper(
                entity_attribute_name='icon_id',
                aggregate_attribute_name='icon',
                method_getter=get_images_with_list_return_annotation,
            )
        error = context.exception.errors()[0]['ctx']['error']
        self.assertEqual(error.code, 'method_return_annotation_must_be_dict')

    def test_multiple_getter_with_not_typed_dict_return_annotation(self):
        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            AggregateDependencyMapper(
                entity_attribute_name='icon_id',
                aggregate_attribute_name='icon',
                method_getter=get_images_with_not_typed_dict_return_annotation,
            )
        error = context.exception.errors()[0]['ctx']['error']
        self.assertEqual(error.code, 'method_return_annotation_must_have_key')

    def test_multiple_getter_with_incorrect_typed_dict_return_annotation(self):
        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            AggregateDependencyMapper(
                entity_attribute_name='icon_id',
                aggregate_attribute_name='icon',
                method_getter=get_images_with_incorrect_typed_dict_return_annotation,
            )
        error = context.exception.errors()[0]['ctx']['error']
        self.assertEqual(error.code, 'key_annotation_must_be_the_same_as_method_argument_annotation')
