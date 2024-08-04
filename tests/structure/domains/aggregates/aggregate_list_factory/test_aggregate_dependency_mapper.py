from typing import List, NewType
from unittest import TestCase

from pydantic import ValidationError

from dddesign.structure.domains.aggregates.aggregate_list_factory import AggregateDependencyMapper
from dddesign.structure.domains.entities import Entity
from dddesign.utils.type_helpers import is_subclass_smart

ImageId = NewType('ImageId', int)


class Image(Entity):
    app_id: int = 1
    image_id: ImageId


def get_image(image_id: ImageId) -> Image:
    return Image(image_id=image_id)


def get_images(image_ids: List[ImageId]) -> List[Image]:
    return [Image(image_id=image_id) for image_id in image_ids]


def get_image_without_annotation(image_id: ImageId):
    return Image(image_id=image_id)


def get_image_with_multiple_arguments(app_id: int, image_id: ImageId) -> Image:
    return Image(app_id=app_id, image_id=image_id)


def get_image_without_arguments() -> Image:
    return Image(app_id=1, image_id=ImageId(1))


class TestAggregateDependencyMapper(TestCase):
    def test_correct_state_with_single_getter(self):
        # Act
        mapper = AggregateDependencyMapper(
            entity_attribute_name='icon_id', aggregate_attribute_name='icon', method_getter=get_image
        )
        method_related_object_id_argument = mapper.method_related_object_id_argument
        related_object_id_attribute_name = mapper.related_object_id_attribute_name  # pk in returned object

        # Assert
        self.assertEqual(method_related_object_id_argument.name, 'image_id')
        self.assertEqual(method_related_object_id_argument.argument_class, ImageId)
        self.assertEqual(method_related_object_id_argument.is_iterable, False)

        self.assertEqual(related_object_id_attribute_name, 'image_id')

    def test_correct_state_with_multiple_getter(self):
        # Act
        mapper = AggregateDependencyMapper(
            entity_attribute_name='icon_id', aggregate_attribute_name='icon', method_getter=get_images
        )
        method_related_object_id_argument = mapper.method_related_object_id_argument
        related_object_id_attribute_name = mapper.related_object_id_attribute_name  # pk in returned object

        # Assert
        self.assertEqual(method_related_object_id_argument.name, 'image_ids')
        assert is_subclass_smart(method_related_object_id_argument.argument_class, list)
        self.assertEqual(method_related_object_id_argument.argument_class.__args__[0], ImageId)
        self.assertEqual(method_related_object_id_argument.is_iterable, True)

        self.assertEqual(related_object_id_attribute_name, 'image_id')

    def test_method_getter_not_have_return_annotation(self):
        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            AggregateDependencyMapper(
                entity_attribute_name='icon_id', aggregate_attribute_name='icon', method_getter=get_image_without_annotation
            )
        error = context.exception.errors()[0]['ctx']['error']
        self.assertEqual(error.code, 'method_getter_not_have_return_annotation')

    def test_method_getter_have_multiple_related_arguments(self):
        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            AggregateDependencyMapper(
                entity_attribute_name='icon_id',
                aggregate_attribute_name='icon',
                method_getter=get_image_with_multiple_arguments,
            )
        error = context.exception.errors()[0]['ctx']['error']
        self.assertEqual(error.code, 'method_getter_have_multiple_related_arguments')

    def test_method_getter_not_have_related_argument(self):
        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            AggregateDependencyMapper(
                entity_attribute_name='icon_id', aggregate_attribute_name='icon', method_getter=get_image_without_arguments
            )
        error = context.exception.errors()[0]['ctx']['error']
        self.assertEqual(error.code, 'method_getter_not_have_related_argument')
