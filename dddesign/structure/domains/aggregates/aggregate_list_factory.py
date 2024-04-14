from typing import Any, Callable, Dict, Generic, Iterable, List, NamedTuple, Tuple, Type, TypeVar, get_args

from pydantic import BaseModel, Field, PrivateAttr, root_validator

from dddesign.structure.domains.aggregates.aggregate import Aggregate
from dddesign.structure.domains.entities import Entity
from dddesign.utils.base_model import create_pydantic_error_instance
from dddesign.utils.type_helpers import get_type_without_optional

RelatedObject = Any
RelatedObjectId = Any

AggregateT = TypeVar('AggregateT', bound=Aggregate)


class MethodArgument(NamedTuple):
    name: str
    argument_class: Any

    @classmethod
    def factory(cls, name: str, argument_class: Any) -> 'MethodArgument':
        return cls(name, get_type_without_optional(argument_class))

    @property
    def is_iterable(self) -> bool:
        return hasattr(getattr(self.argument_class, '__origin__', self.argument_class), '__iter__')


class AggregateDependencyMapper(BaseModel):
    entity_attribute_name: str
    aggregate_attribute_name: str

    method_getter: Callable
    method_extra_arguments: Dict[str, Any] = Field(default_factory=dict)

    _method_related_object_id_argument: MethodArgument = PrivateAttr()
    _related_object_id_attribute_name: str = PrivateAttr()

    class Config:
        allow_mutation = False

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self._method_related_object_id_argument = self._get_method_related_object_id_argument(
            method_getter=self.method_getter, method_extra_arguments=self.method_extra_arguments
        )
        self._related_object_id_attribute_name = self._get_related_object_id_attribute_name(
            method_getter=self.method_getter, method_related_object_id_argument=self._method_related_object_id_argument
        )

    @property
    def method_related_object_id_argument(self) -> MethodArgument:
        return self._method_related_object_id_argument

    @property
    def related_object_id_attribute_name(self) -> str:
        return self._related_object_id_attribute_name

    @root_validator
    def validate_consistency(cls, values):
        method_getter = values['method_getter']
        method_extra_arguments = values['method_extra_arguments']

        method_related_object_id_argument = cls._get_method_related_object_id_argument(
            method_getter=method_getter, method_extra_arguments=method_extra_arguments
        )
        cls._get_related_object_id_attribute_name(
            method_getter=method_getter, method_related_object_id_argument=method_related_object_id_argument
        )

        return values

    @staticmethod
    def _get_method_related_object_id_argument(
        method_getter: Callable, method_extra_arguments: Dict[str, Any]
    ) -> MethodArgument:
        argument_name, argument_class = None, None
        for _argument_name, _argument_class in method_getter.__annotations__.items():
            if _argument_name in method_extra_arguments or _argument_name == 'return':
                continue

            if argument_name and argument_class:
                raise create_pydantic_error_instance(
                    base_error=ValueError,
                    code='method_getter_have_multiple_related_arguments',
                    msg_template='`method_getter` must have only one related argument',
                )

            argument_name, argument_class = _argument_name, _argument_class

        if not (argument_name and argument_class):
            raise create_pydantic_error_instance(
                base_error=ValueError,
                code='method_getter_not_have_related_argument',
                msg_template='`method_getter` must have one related argument',
            )

        return MethodArgument.factory(argument_name, argument_class)

    @staticmethod
    def _get_related_object_id_attribute_name(
        method_getter: Callable, method_related_object_id_argument: MethodArgument
    ) -> str:
        related_object_class = get_type_without_optional(method_getter.__annotations__.get('return'))
        if not related_object_class:
            raise create_pydantic_error_instance(
                base_error=ValueError,
                code='method_getter_not_have_return_annotation',
                msg_template='`method_getter` must have return annotation',
            )

        related_object_id_attribute_class = method_related_object_id_argument.argument_class

        if method_related_object_id_argument.is_iterable:
            related_object_class = get_type_without_optional(get_args(related_object_class)[0])
            related_object_id_attribute_class = get_type_without_optional(get_args(related_object_id_attribute_class)[0])

        return {value: key for key, value in related_object_class.__annotations__.items()}[related_object_id_attribute_class]


class AggregateListFactory(BaseModel, Generic[AggregateT]):
    aggregate_class: Type[AggregateT]
    aggregate_entity_attribute_name: str
    dependency_mappers: Tuple[AggregateDependencyMapper, ...]

    class Config:
        allow_mutation = False

    @root_validator
    def validate_consistency(cls, values):
        aggregate_class = values['aggregate_class']
        aggregate_entity_attribute_name = values['aggregate_entity_attribute_name']
        dependency_mappers = values['dependency_mappers']

        if aggregate_entity_attribute_name not in aggregate_class.__annotations__:
            raise ValueError(f"The aggregate class doesn't have `{aggregate_entity_attribute_name}` attribute")

        if any(dependency.aggregate_attribute_name not in aggregate_class.__annotations__ for dependency in dependency_mappers):
            raise ValueError("The aggregate class doesn't have a attribute from some declared dependency")

        entity_class = get_type_without_optional(aggregate_class.__annotations__[aggregate_entity_attribute_name])

        if any(dependency.entity_attribute_name not in entity_class.__annotations__ for dependency in dependency_mappers):
            raise ValueError("The entity class doesn't have a attribute from some declared dependency")

        return values

    def create_list(self, entities: List[Entity]) -> List[AggregateT]:
        dependency_related_object_ids_map: Dict[int, Tuple[RelatedObjectId, ...]] = {}
        for dependency_item, dependency in enumerate(self.dependency_mappers):
            _related_object_ids: List[RelatedObjectId] = []
            for entity in entities:
                related_value = getattr(entity, dependency.entity_attribute_name)
                if isinstance(related_value, Iterable):
                    _related_object_ids.extend(related_value)
                else:
                    _related_object_ids.append(related_value)

            dependency_related_object_ids_map[dependency_item] = tuple(set(_related_object_ids))

        dependency_related_object_map: Dict[int, Dict[RelatedObjectId, RelatedObject]] = {}
        for dependency_item, related_object_ids in dependency_related_object_ids_map.items():
            dependency = self.dependency_mappers[dependency_item]

            if dependency.method_related_object_id_argument.is_iterable:
                related_objects = dependency.method_getter(
                    **{
                        dependency.method_related_object_id_argument.name: related_object_ids,
                        **dependency.method_extra_arguments,
                    }
                )
            else:
                related_objects = []
                for related_object_id in related_object_ids:
                    related_object = dependency.method_getter(
                        **{
                            dependency.method_related_object_id_argument.name: related_object_id,
                            **dependency.method_extra_arguments,
                        }
                    )
                    if related_object is not None:
                        related_objects.append(related_object)

            related_object_map: Dict[RelatedObjectId, RelatedObject] = {
                getattr(related_object, dependency.related_object_id_attribute_name): related_object
                for related_object in related_objects
            }
            dependency_related_object_map[dependency_item] = related_object_map

        aggregates: List[AggregateT] = []
        for entity in entities:
            aggregate_init: Dict[str, Any] = {self.aggregate_entity_attribute_name: entity}
            for dependency_item, dependency in enumerate(self.dependency_mappers):
                related_object_id = getattr(entity, dependency.entity_attribute_name)
                if hasattr(related_object_id, '__iter__'):
                    aggregate_init[dependency.aggregate_attribute_name] = tuple(
                        dependency_related_object_map[dependency_item].get(related_object_id)
                        for related_object_id in related_object_id
                    )
                else:
                    aggregate_init[dependency.aggregate_attribute_name] = dependency_related_object_map[dependency_item].get(
                        related_object_id
                    )

            aggregate = self.aggregate_class(**aggregate_init)
            aggregates.append(aggregate)

        return aggregates
