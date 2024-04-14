from typing import List, NewType, Tuple
from unittest import TestCase

from parameterized import parameterized

from dddesign.structure.domains.aggregates.aggregate import Aggregate
from dddesign.structure.domains.aggregates.aggregate_list_factory import AggregateDependencyMapper, AggregateListFactory
from dddesign.structure.domains.entities import Entity

ImageId = NewType('ImageId', int)


class Image(Entity):
    image_id: ImageId


class ProfileSingleRelated(Entity):
    profile_id: int
    icon_id: ImageId


class ProfileSingleRelatedAggregate(Aggregate):
    profile: ProfileSingleRelated
    icon: Image


class ProfileMultipleRelated(Entity):
    profile_id: int
    icon_ids: Tuple[ImageId, ...]


class ProfileMultipleRelatedAggregate(Aggregate):
    profile: ProfileMultipleRelated
    icons: Tuple[Image, ...]


def get_image(image_id: ImageId) -> Image:
    return Image(image_id=image_id)


def get_images(image_ids: List[ImageId]) -> List[Image]:
    return [Image(image_id=image_id) for image_id in image_ids]


class TestAggregateListFactory(TestCase):
    @parameterized.expand((get_image, get_images))
    def test_correct_state_for_single_related(self, method_getter):
        # Act
        aggregate_list_factory = AggregateListFactory(
            aggregate_class=ProfileSingleRelatedAggregate,
            aggregate_entity_attribute_name='profile',
            dependency_mappers=(
                AggregateDependencyMapper(
                    entity_attribute_name='icon_id', aggregate_attribute_name='icon', method_getter=method_getter
                ),
            ),
        )
        profiles = [
            ProfileSingleRelated(profile_id=1, icon_id=ImageId(1)),
            ProfileSingleRelated(profile_id=2, icon_id=ImageId(2)),
        ]
        profile_aggregates = aggregate_list_factory.create_list(profiles)

        for profile_aggregate in profile_aggregates:
            self.assertIsInstance(profile_aggregate, ProfileSingleRelatedAggregate)
            self.assertIsInstance(profile_aggregate.icon, Image)
            self.assertIsInstance(profile_aggregate.profile, ProfileSingleRelated)

    @parameterized.expand((get_image, get_images))
    def test_correct_state_for_multiple_related(self, method_getter):
        # Act
        aggregate_list_factory = AggregateListFactory(
            aggregate_class=ProfileMultipleRelatedAggregate,
            aggregate_entity_attribute_name='profile',
            dependency_mappers=(
                AggregateDependencyMapper(
                    entity_attribute_name='icon_ids', aggregate_attribute_name='icons', method_getter=method_getter
                ),
            ),
        )
        profiles = [
            ProfileMultipleRelated(profile_id=1, icon_ids=(ImageId(1), ImageId(2))),
            ProfileMultipleRelated(profile_id=2, icon_ids=(ImageId(2), ImageId(3))),
        ]
        profile_aggregates = aggregate_list_factory.create_list(profiles)

        for profile_aggregate in profile_aggregates:
            self.assertIsInstance(profile_aggregate, ProfileMultipleRelatedAggregate)
            self.assertIsInstance(profile_aggregate.icons, tuple)
            self.assertTrue(all(isinstance(icon, Image) for icon in profile_aggregate.icons))
            self.assertIsInstance(profile_aggregate.profile, ProfileMultipleRelated)
