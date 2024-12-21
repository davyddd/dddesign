from functools import cached_property
from typing import Any, Callable, Dict, Generic, List, NamedTuple, Sequence, Tuple, Type, TypeVar

from ddutils.annotation_helpers import (
    get_annotation_origin,
    get_annotation_without_optional,
    get_complex_sequence_element_annotation,
    get_dict_items_annotation,
    is_complex_sequence,
    is_subclass,
)
from pydantic import BaseModel, ConfigDict, Field, model_validator

from dddesign.structure.domains.aggregates import Aggregate
from dddesign.structure.domains.entities import Entity
from dddesign.utils.base_model import create_pydantic_error_instance

AggregateT = TypeVar('AggregateT', bound=Aggregate)

RelatedObject = Any
RelatedObjectId = Any


class MethodArgument(NamedTuple):
    name: str
    annotation: Any


class AggregateDependencyMapper(BaseModel):
    model_config = ConfigDict(frozen=True)

    entity_attribute_name: str
    aggregate_attribute_name: str

    method_getter: Callable
    method_extra_arguments: Dict[str, Any] = Field(default_factory=dict)

    @cached_property
    def method_related_argument(self) -> MethodArgument:
        declared_arguments = {*self.method_extra_arguments.keys(), 'return'}
        not_declared_arguments = {
            name: annotation
            for name, annotation in self.method_getter.__annotations__.items()
            if name not in declared_arguments
        }
        if len(not_declared_arguments) != 1:
            raise create_pydantic_error_instance(
                base_error=ValueError,
                code='method_must_have_one_related_argument',
                message='Method must have one related argument',
            )

        name, annotation = next(iter(not_declared_arguments.items()))
        if is_subclass(annotation, dict):
            raise create_pydantic_error_instance(
                base_error=ValueError,
                code='method_related_argument_must_be_simple_type',
                message='Method related argument must be a simple type',
            )

        return MethodArgument(name=name, annotation=annotation)

    @cached_property
    def method_return_argument_annotation(self) -> Any:
        method_return_argument_annotation = self.method_getter.__annotations__.get('return')
        if method_return_argument_annotation is None:
            raise create_pydantic_error_instance(
                base_error=ValueError, code='method_must_have_return_annotation', message='Method must have return annotation'
            )
        return method_return_argument_annotation

    @model_validator(mode='after')
    def validate_consistency(self):
        # wurm up properties because they are cached
        property_names = ('method_related_argument', 'method_return_argument_annotation')
        for property_name in property_names:
            if getattr(self, property_name) is None:
                raise create_pydantic_error_instance(
                    base_error=ValueError,
                    code='property_not_initialized',
                    message=f'Property `{property_name}` must be initialized',
                )

        if is_complex_sequence(self.method_related_argument.annotation):
            # If the method accepts a list of related object IDs,
            # it should return a map where the key is the ID of the related object
            try:
                key_annotation, _ = get_dict_items_annotation(self.method_return_argument_annotation)
            except TypeError as err:
                raise create_pydantic_error_instance(
                    base_error=ValueError,
                    code='method_return_annotation_must_be_dict',
                    message='Return annotation of method must be a dict',
                ) from err
            except ValueError as err:
                raise create_pydantic_error_instance(
                    base_error=ValueError,
                    code='method_return_annotation_must_have_key',
                    message='Dict return annotation must have an annotation of key',
                ) from err

            sequence_element_annotation = get_complex_sequence_element_annotation(self.method_related_argument.annotation)
            if key_annotation != sequence_element_annotation:
                raise create_pydantic_error_instance(
                    base_error=ValueError,
                    code='key_annotation_must_be_the_same_as_method_argument_annotation',
                    message='Key annotation of dict must be the same as the method argument annotation',
                )

        return self


class AggregateListFactory(BaseModel, Generic[AggregateT]):
    model_config = ConfigDict(frozen=True)

    aggregate_class: Type[AggregateT]
    aggregate_entity_attribute_name: str
    dependency_mappers: Tuple[AggregateDependencyMapper, ...]

    @model_validator(mode='after')
    def validate_consistency(self):
        if self.aggregate_entity_attribute_name not in self.aggregate_class.__annotations__:
            raise create_pydantic_error_instance(
                base_error=ValueError,
                code='aggregate_class_does_not_have_entity_attribute',
                message=f'The aggregate class does not have `{self.aggregate_entity_attribute_name}` attribute',
            )

        entity_class = get_annotation_origin(self.aggregate_class.__annotations__[self.aggregate_entity_attribute_name])

        for dependency in self.dependency_mappers:
            if dependency.aggregate_attribute_name not in self.aggregate_class.__annotations__:
                raise create_pydantic_error_instance(
                    base_error=ValueError,
                    code='aggregate_class_does_not_have_attribute',
                    message=f'The aggregate class does not have `{dependency.aggregate_attribute_name}` attribute',
                )

            if dependency.entity_attribute_name not in entity_class.__annotations__:
                raise create_pydantic_error_instance(
                    base_error=ValueError,
                    code='entity_class_does_not_have_attribute',
                    message=f'The entity class does not have `{dependency.entity_attribute_name}` attribute',
                )

            aggregate_target_attribute_annotation = get_annotation_without_optional(
                self.aggregate_class.__annotations__[dependency.aggregate_attribute_name]
            )
            dependency_return_object_annotation = dependency.method_return_argument_annotation

            if is_complex_sequence(dependency.method_related_argument.annotation):
                _, dependency_return_object_annotation = get_dict_items_annotation(dependency_return_object_annotation)

            dependency_return_object_annotation = get_annotation_without_optional(dependency_return_object_annotation)

            if aggregate_target_attribute_annotation != dependency_return_object_annotation:
                raise create_pydantic_error_instance(
                    base_error=ValueError,
                    code='aggregate_attribute_annotation_must_be_the_same_as_method_return_annotation',
                    message='Aggregate attribute annotation must be the same as the method return annotation',
                )

        return self

    def create_list(self, entities: List[Entity]) -> List[AggregateT]:
        dependency_related_object_map: Dict[int, Dict[RelatedObjectId, RelatedObject]] = {}
        for dependency_item, dependency in enumerate(self.dependency_mappers):
            related_objects: Dict[RelatedObjectId, RelatedObject] = {}
            if is_complex_sequence(dependency.method_related_argument.annotation):
                annotation_origin = get_annotation_origin(dependency.method_related_argument.annotation)
                related_object_ids: Sequence[RelatedObjectId] = annotation_origin(
                    {
                        related_object_id
                        for entity in entities
                        if (
                            (related_object_id := getattr(entity, dependency.entity_attribute_name))
                            and related_object_id is not None
                        )
                    }
                )
                related_objects = dependency.method_getter(
                    **{dependency.method_related_argument.name: related_object_ids, **dependency.method_extra_arguments}
                )
            else:
                for entity in entities:
                    related_object_id = getattr(entity, dependency.entity_attribute_name)
                    if related_object_id is not None and related_object_id not in related_objects:
                        related_object = dependency.method_getter(
                            **{dependency.method_related_argument.name: related_object_id, **dependency.method_extra_arguments}
                        )
                        related_objects[related_object_id] = related_object

            dependency_related_object_map[dependency_item] = related_objects

        aggregates: List[AggregateT] = []
        for entity in entities:
            aggregate_init: Dict[str, Any] = {self.aggregate_entity_attribute_name: entity}
            for dependency_item, dependency in enumerate(self.dependency_mappers):
                related_object_id = getattr(entity, dependency.entity_attribute_name)
                aggregate_init[dependency.aggregate_attribute_name] = dependency_related_object_map[dependency_item].get(
                    related_object_id
                )

            aggregate = self.aggregate_class(**aggregate_init)
            aggregates.append(aggregate)

        return aggregates


__all__ = ('AggregateListFactory', 'AggregateDependencyMapper', 'MethodArgument')
