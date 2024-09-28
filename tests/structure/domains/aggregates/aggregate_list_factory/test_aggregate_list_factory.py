from typing import Dict, List, NewType
from unittest import TestCase

from parameterized import parameterized
from pydantic import ValidationError

from dddesign.structure.domains.aggregates.aggregate import Aggregate
from dddesign.structure.domains.aggregates.aggregate_list_factory import AggregateDependencyMapper, AggregateListFactory
from dddesign.structure.domains.entities import Entity

ImageId = NewType('ImageId', int)


class Image(Entity):
    image_id: ImageId


class Profile(Entity):
    profile_id: int
    icon_id: ImageId


class ProfileAggregate(Aggregate):
    profile: Profile
    icon: Image


def get_image(image_id: ImageId) -> Image:
    return Image(image_id=image_id)


def get_images(image_ids: List[ImageId]) -> Dict[ImageId, Image]:
    return {image_id: Image(image_id=image_id) for image_id in image_ids}


class TestAggregateListFactory(TestCase):
    @parameterized.expand((get_image, get_images))
    def test_correct_state(self, method_getter):
        # Arrange
        profiles = [Profile(profile_id=1, icon_id=ImageId(1)), Profile(profile_id=2, icon_id=ImageId(2))]

        # Act
        aggregate_list_factory = AggregateListFactory(
            aggregate_class=ProfileAggregate,
            aggregate_entity_attribute_name='profile',
            dependency_mappers=(
                AggregateDependencyMapper(
                    entity_attribute_name='icon_id', aggregate_attribute_name='icon', method_getter=method_getter
                ),
            ),
        )
        profile_aggregates = aggregate_list_factory.create_list(profiles)

        # Assert
        for profile_aggregate in profile_aggregates:
            self.assertIsInstance(profile_aggregate, ProfileAggregate)
            self.assertIsInstance(profile_aggregate.icon, Image)
            self.assertIsInstance(profile_aggregate.profile, Profile)

    def test_aggregate_class_does_not_have_entity_attribute(self):
        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            AggregateListFactory(
                aggregate_class=ProfileAggregate,
                aggregate_entity_attribute_name='not_existing_attribute',
                dependency_mappers=(
                    AggregateDependencyMapper(
                        entity_attribute_name='icon_id', aggregate_attribute_name='icon', method_getter=get_image
                    ),
                ),
            )
        error = context.exception.errors()[0]['ctx']['error']
        self.assertEqual('aggregate_class_does_not_have_entity_attribute', error.code)

    def test_aggregate_class_does_not_have_dependency_attribute(self):
        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            AggregateListFactory(
                aggregate_class=ProfileAggregate,
                aggregate_entity_attribute_name='profile',
                dependency_mappers=(
                    AggregateDependencyMapper(
                        entity_attribute_name='icon_id',
                        aggregate_attribute_name='not_existing_attribute',
                        method_getter=get_image,
                    ),
                ),
            )
        error = context.exception.errors()[0]['ctx']['error']
        self.assertEqual('aggregate_class_does_not_have_attribute', error.code)

    def test_entity_class_does_not_have_dependency_attribute(self):
        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            AggregateListFactory(
                aggregate_class=ProfileAggregate,
                aggregate_entity_attribute_name='profile',
                dependency_mappers=(
                    AggregateDependencyMapper(
                        entity_attribute_name='not_existing_attribute', aggregate_attribute_name='icon', method_getter=get_image
                    ),
                ),
            )
        error = context.exception.errors()[0]['ctx']['error']
        self.assertEqual('entity_class_does_not_have_attribute', error.code)
