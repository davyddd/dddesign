from typing import Any, Dict, Generic, NamedTuple, Optional, Tuple, Type, TypeVar, Union

from pydantic import BaseModel, PrivateAttr, root_validator, validator

from dddesign.structure.applications import Application
from dddesign.structure.domains.constants import BaseEnum
from dddesign.structure.domains.errors import BaseError
from dddesign.structure.infrastructure.adapters.external import ExternalAdapter
from dddesign.structure.infrastructure.adapters.internal import InternalAdapter
from dddesign.structure.infrastructure.repositories import Repository
from dddesign.structure.services.service import Service
from dddesign.utils.convertors import convert_camel_case_to_snake_case

ApplicationT = TypeVar('ApplicationT')

DependencyValue = Union[
    InternalAdapter,
    ExternalAdapter,
    Repository,
    Application,
    Service,
    Type[InternalAdapter],
    Type[ExternalAdapter],
    Type[Repository],
    Type[Application],
    Type[Service],
]

RequestAttributeName = str
RequestAttributeValue = Any
RequestAttributeValueCombination = Tuple[RequestAttributeValue, ...]


class RequestAttributeNotProvideError(BaseError):
    message = 'Request attribute `{attribute_name}` not provide'


class RequestAttributeValueError(BaseError):
    message = 'Request attribute `{attribute_name}` has invalid value `{attribute_value}`'
    status_code = 404


class RequestAttribute(NamedTuple):
    name: RequestAttributeName
    enum_class: Type[BaseEnum]


class ApplicationDependencyMapper(BaseModel):
    request_attribute_name: Optional[RequestAttributeName] = None
    request_attribute_value_map: Dict[RequestAttributeValue, DependencyValue]
    application_attribute_name: str

    class Config:
        allow_mutation = False
        arbitrary_types_allowed = True

    @staticmethod
    def _get_enum_class(mapping: Dict[RequestAttributeValue, DependencyValue]) -> Type[BaseEnum]:
        return next(iter(mapping.keys())).__class__

    @property
    def enum_class(self) -> Type[BaseEnum]:
        return self._get_enum_class(self.request_attribute_value_map)

    def get_request_attribute_name(self) -> RequestAttributeName:
        return self.request_attribute_name or convert_camel_case_to_snake_case(self.enum_class.__name__)

    @validator('request_attribute_value_map')
    def validate_request_attribute_value_map(cls, request_attribute_value_map):
        if len(request_attribute_value_map) == 0:
            raise ValueError('`request_attribute_value_map` must contain at least one element')

        enum_class = cls._get_enum_class(request_attribute_value_map)
        if set(enum_class) ^ set(request_attribute_value_map.keys()):
            raise ValueError(
                f'All elements of `{enum_class.__name__}` enum must announced as key in `request_attribute_value_map` attribute'
            )
        return request_attribute_value_map


class ApplicationFactory(BaseModel, Generic[ApplicationT]):
    dependency_mappers: Tuple[ApplicationDependencyMapper, ...] = ()
    application_class: Type[ApplicationT]
    reuse_implementations: bool = True

    # private attributes
    _request_attributes: Tuple[RequestAttribute, ...] = PrivateAttr()
    _application_implementations: Dict[RequestAttributeValueCombination, ApplicationT] = PrivateAttr()

    class Config:
        allow_mutation = False
        arbitrary_types_allowed = True

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self._request_attributes = self._get_request_attributes()
        self._application_implementations = {}

    def _get_request_attributes(self) -> Tuple[RequestAttribute, ...]:
        return tuple(
            RequestAttribute(name=mapper.get_request_attribute_name(), enum_class=mapper.enum_class)
            for mapper in self.dependency_mappers
        )

    @validator('dependency_mappers')
    def validate_dependency_mappers(cls, dependency_mappers):
        if len(dependency_mappers) != len({mapper.enum_class for mapper in dependency_mappers}):
            raise ValueError('`dependency_mappers` must contain unique enum classes')
        elif len(dependency_mappers) != len({mapper.application_attribute_name for mapper in dependency_mappers}):
            raise ValueError('`dependency_mappers` must contain unique `application_attribute_name`')
        elif len(dependency_mappers) != len({mapper.get_request_attribute_name() for mapper in dependency_mappers}):
            raise ValueError('`dependency_mappers` must contain unique `request_attribute_name`')

        return dependency_mappers

    @root_validator
    def validate_consistency(cls, values):
        application_class = values['application_class']
        dependency_mappers = values['dependency_mappers']

        application_required_attribute_names = {name for name, field in application_class.__fields__.items() if field.required}
        requested_dependency_attribute_names = {mapper.application_attribute_name for mapper in dependency_mappers}

        if not (application_required_attribute_names <= requested_dependency_attribute_names):
            raise ValueError('`dependency_mappers` must contain all required attributes of `application_class`')

        return values

    def _get_request_attribute_value_combination(self, **kwargs: RequestAttributeValue) -> RequestAttributeValueCombination:
        request_attribute_value_combination = []
        for attribute in self._request_attributes:
            if attribute.name in kwargs:
                try:
                    request_attribute_value_combination.append(attribute.enum_class(kwargs[attribute.name]))
                except ValueError as err:
                    raise RequestAttributeValueError(
                        attribute_name=attribute.name, attribute_value=kwargs[attribute.name]
                    ) from err
            else:
                raise RequestAttributeNotProvideError(attribute_name=attribute.name)

        return tuple(request_attribute_value_combination)

    def _get_application_implementation(self, **kwargs: RequestAttributeValue) -> ApplicationT:
        request_attribute_value_combination = self._get_request_attribute_value_combination(**kwargs)

        if request_attribute_value_combination in self._application_implementations:
            return self._application_implementations[request_attribute_value_combination]

        application_impl = self.application_class(
            **{
                self.dependency_mappers[index].application_attribute_name: dependency_value
                for index in range(len(request_attribute_value_combination))
                if (
                    dependency_value := self.dependency_mappers[index].request_attribute_value_map[
                        request_attribute_value_combination[index]
                    ]
                )
            }
        )
        if self.reuse_implementations:
            self._application_implementations[request_attribute_value_combination] = application_impl

        return application_impl

    @property
    def request_attributes(self) -> Tuple[RequestAttribute, ...]:
        return self._request_attributes

    def get(self, **kwargs: RequestAttributeValue) -> ApplicationT:
        return self._get_application_implementation(**kwargs)