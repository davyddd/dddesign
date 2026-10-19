# DDDesign

[![pypi](https://img.shields.io/pypi/v/dddesign.svg)](https://pypi.python.org/pypi/dddesign)
[![downloads](https://static.pepy.tech/badge/dddesign/month)](https://pepy.tech/project/dddesign)
[![versions](https://img.shields.io/pypi/pyversions/dddesign.svg)](https://github.com/davyddd/dddesign)
[![codecov](https://codecov.io/gh/davyddd/dddesign/branch/main/graph/badge.svg)](https://app.codecov.io/github/davyddd/dddesign)
[![license](https://img.shields.io/github/license/davyddd/dddesign.svg)](https://github.com/davyddd/dddesign/blob/main/LICENSE)

**DDDesign** is a Python library designed to implement Domain-Driven Design (DDD) principles in software projects. 
It provides a set of tools and structures to help developers apply DDD architecture. 
This library is built on top of [Pydantic](https://docs.pydantic.dev/latest/), 
ensuring data validation and settings management using Python type annotations.

## Installation

Install the library using pip:
```bash
pip install dddesign
```

## Compatibility

Python 3.11 to 3.14, `pydantic>=2.1,<2.14`, `ddutils>=0.3.0`. What changed in each release, breaking changes
included, is in the [GitHub releases](https://github.com/davyddd/dddesign/releases).

## Development

The project runs entirely in Docker. The tests need no external services. Requires Docker and [Fabric](https://www.fabfile.org/) on the host:

```bash
fab build      # build the dev image
fab tests      # run pytest
fab linters    # run ruff (with --fix), ty and complexipy
fab shell      # IPython inside the container
fab bash       # bash inside the container
```

This project was generated from [dd-lib-stub](https://github.com/davyddd/dd-lib-stub);
run `uvx copier update` to pull in template updates.

## DDD Components

Every component is a pydantic model. The structural ones are frozen, so an instance declared at module level
(`profile_app_impl = ProfileApp()`) is shared safely; the domain ones are mutable with validation on assignment.

| Component | Import | Config |
|---|---|---|
| `Application` | `dddesign.structure.applications` | frozen |
| `InternalAdapter` | `dddesign.structure.infrastructure.adapters.internal` | frozen |
| `ExternalAdapter` | `dddesign.structure.infrastructure.adapters.external` | frozen |
| `Repository` | `dddesign.structure.infrastructure.repositories` | frozen, method names restricted |
| `Service` | `dddesign.structure.services` | frozen, abstract `handle()` |
| `DataTransferObject` | `dddesign.structure.domains.dto` | frozen |
| `ValueObject` | `dddesign.structure.domains.value_objects` | frozen |
| `Entity` | `dddesign.structure.domains.entities` | `validate_assignment` |
| `Aggregate` | `dddesign.structure.domains.aggregates` | `validate_assignment` |

All of them allow arbitrary field types. A default value of a field is shared between instances when it is
hashable, which a frozen component is; a mutable default is deep-copied by pydantic for every instance.

### Application

**Application** is a programmatic interface for accessing business logic. 
It serves as the primary entry point for all domain operations.

#### Entry points:
- **Ports**: HTTP interfaces, background tasks, CLI commands, and other interaction points.  
- **Other Applications**: Within the same **Context**, leading and subordinate **Applications** may coexist, creating a layered structure. Leading **Applications** manage core business logic, while subordinate **Applications** handle narrower delegated tasks.

This approach ensures clear separation of responsibilities and helps maintain a well-organized architecture.

### Adapter

**Adapter** is a component designed to retrieve data from external sources. 
Based on the **Adapter Pattern** described in "Gang of Four" (GoF), 
it bridges the interface of a system with the one expected by another.

#### Characteristics:
- Belongs to the infrastructure layer and isolates interactions with external interfaces.
- Divided into integration with internal (`InternalAdapter`) and third-party (`ExternalAdapter`) services.

By encapsulating external dependencies, **Adapter** keeps the core application logic decoupled and modular.

### Repository

**Repository**, a subtype of **Adapter**, is a specialized infrastructure layer component introduced in "Domain-Driven Design" by _Eric Evans_. 
It isolates interactions with data storage systems (e.g., PostgreSQL, ClickHouse, Redis, and others) 
and provides an abstraction for managing persistence.

#### Characteristics:
- **Single Responsibility**: Each **Repository** is typically designed to work with a single table (**Entity**).
- **Separation of Concerns**: Keeps domain logic independent of storage implementations.  
- **Application Usage**: If an **Application** uses more than one **Repository**, this indicates a design issue. In such cases, consider creating another **Application**.

This abstraction ensures that persistence logic is modular and aligns with DDD principles.

#### Method names

A `Repository` subclass may only define methods from `BASE_ALLOWED_METHODS`: `get`, `get_by_filters`, `get_list`,
`get_map`, `create`, `update`, `delete`, `bulk_create`, `bulk_update`, `bulk_delete`, `update_by_filters`,
`delete_by_filters`, `exists`, `count`. Any other function, static or class method, private helpers included, raises
`TypeError` at class definition; dunder methods are exempt. Extra names are opened with `EXTERNAL_ALLOWED_METHODS`,
declared as a field, not a `ClassVar`:

```python
from dddesign.structure.infrastructure.repositories import Repository


class ProfileRepository(Repository):
    EXTERNAL_ALLOWED_METHODS: set[str] | None = {'get_by_email'}

    async def get(self, profile_id: ProfileId) -> Profile | None: ...
    async def get_by_email(self, email: str) -> Profile | None: ...
```

### Service

**Service** is used to handle business logic not tied to a specific domain object.  

#### Characteristics:
- **Purpose**: Used when a method spans multiple domain objects.
- **Clear Naming**: The name should clearly describe its purpose, as it always implements a single `handle` method.
- **Input / Output**: Can return a new object or modify an input object in place.  
- **Dependency Management**: Relies only on provided inputs, avoiding direct infrastructure dependencies, ensuring easy unit testing.

### Data Transfer Object (DTO)

**Data Transfer Object** is a simple, immutable data structure used for transferring data between application layers. 
Introduced by _Martin Fowler_ in "Patterns of Enterprise Application Architecture", it acts as a data contract.

#### Characteristics:
- **Data Contracts**: Defines clear structures for exchanging data between layers.  
- **Immutability**: DTOs cannot be modified after creation.  
- **Application Access**: Any additional data fetching required to fulfill a contract should be handled by the **Application**, as it has access to **Repositories** or subordinate **Applications**.

### Value Object

**Value Object** is an object defined solely by its properties and has no unique identifier. 
Originating in object-oriented programming, it was refined by _Eric Evans_ in "Domain-Driven Design" to reduce domain model complexity.

#### Characteristics:
- **No Identity**: Identified by attributes, not a unique identifier.  
- **Immutability**: Cannot be modified after creation, ensuring consistency.  
- **Equality**: Two **Value Objects** are equal if all their properties match.

#### Examples:
- **Address**: street, city, postal code, country.  
- **Money**: amount, currency.

### Entity

**Entity** is a domain object identified by a unique property (typically a primary key in the database). 
It represents a single record in a table and encapsulates related data and behavior.

#### Characteristics:
- **Unique Identity**: Ensures one-to-one correspondence with a database record.  
- **Field Consistency**: Fields in the **Entity** should align with the database schema.  

#### Notes:
- Fields such as `created_at` and `updated_at`, often managed by ORMs, can be omitted from the **Entity** if they are not required in the business logic. 
- Ideally, each **Entity** should have a dedicated **Repository** and possibly its own **Application**.
- `entity.update(data, exclude_fields=None)` copies the fields set on another model (`model_dump(exclude_unset=True)`)
  onto the entity, assigning only the ones it has and whose value differs, so a DTO from a request can be applied in one call.

### Aggregate

**Aggregate** is a collection of related **Entity** objects that work together within a single bounded context.  
By exposing controlled methods for interaction, it ensures consistency and atomicity of operations under shared rules.

#### Characteristics:
- **Consistency**: Ensures domain rules are followed by exposing public methods for interaction, ensuring all internal **Entities** remain in valid states.
- **Atomicity**: Treats operations on the aggregate as a single unit, ensuring consistent changes across all entities.

#### Usage:
- **Ports** create a **DTO**, which is passed to the **Application**. The **Application** builds **Entities** and groups them into an **Aggregate**, validating rules and contracts.  
- **Aggregates** can also act as simple containers for related **Entities** within a single HTTP request, avoiding the need for multiple REST calls, thereby reducing network overhead.

### Component Interaction Flowchart

<img src="https://public-media.adapty.io/project-structure.png" alt="Component Interaction Flowchart" width="600">

## Factories

### ApplicationFactory

Facilitates creating application instances with specific dependencies.
Useful when multiple interfaces with different dependencies share the same application logic.

`ApplicationFactory(application_class, dependency_mappers=(), reuse_implementations=True)`. Each
`ApplicationDependencyMapper(application_attribute_name, request_attribute_value_map, request_attribute_name=None)`
maps the members of one `BaseEnum` to the dependency the application attribute receives: an instance or a class of
`Application`, `InternalAdapter`, `ExternalAdapter`, `Repository` or `Service`. The request attribute defaults to the
snake_case of the enum class name (`SocialDriver` → `social_driver`). The factory validates at construction that
every enum member is mapped, the values are dependencies and not all the same, the mappers use distinct enums,
attribute names and request names, and every required attribute of the application is covered.

`get(**kwargs)` takes the request attributes as enum members or their raw values and builds the application, or
returns the one built before for the same combination (`reuse_implementations`). A missing attribute raises
`RequestAttributeNotProvideError` (400), a value outside of the enum `RequestAttributeValueError` (404); both are
`BaseError`s. `request_attributes` lists the names and enums the factory expects.

**Example**:
```python
from dddesign.structure.applications import Application, ApplicationDependencyMapper, ApplicationFactory

from app.account_context.applications.account import AccountApp, account_app_impl
from app.account_context.applications.social_account import SocialAccountApp, social_account_app_impl
from app.account_context.domains.constants import SocialDriver
from app.account_context.infrastructure.adapters.external import social


class AuthSocialApp(Application):
    account_app: AccountApp = account_app_impl
    social_account_app: SocialAccountApp = social_account_app_impl
    social_adapter: social.SocialAdapterInterface
    
    ...


auth_social_app_factory = ApplicationFactory[AuthSocialApp](
    application_class=AuthSocialApp,
    dependency_mappers=(
        ApplicationDependencyMapper(
            application_attribute_name='social_adapter',
            request_attribute_value_map={
                SocialDriver.APPLE: social.apple_id_adapter_impl,
                SocialDriver.GOOGLE: social.google_adapter_impl,
                SocialDriver.FACEBOOK: social.facebook_adapter_impl,
            },
        ),
    ),
)

# the argument name is the snake_case of the enum class name unless `request_attribute_name` says otherwise
auth_apple_app_impl = auth_social_app_factory.get(social_driver=SocialDriver.APPLE)
```

### AggregateListFactory

Converts a list of **Entity** into **Aggregate** objects: loads the related objects of every entity through the
getters of the dependency mappers, in bulk where the getter accepts a sequence, and builds one aggregate per entity.

`AggregateDependencyMapper(method_getter, entity_attribute_name, aggregate_attribute_name, method_extra_arguments={})`
reads the related id from `entity.<entity_attribute_name>` and puts what the getter returns into
`aggregate.<aggregate_attribute_name>`. The getter is introspected through its annotations, so:

- it must be a plain `def` with annotations, `create_list` is synchronous and calls it directly;
- besides the keys of `method_extra_arguments` it takes exactly one argument, the related id: a plain type for a
  one-by-one getter, a sequence of it (`tuple[MediaId, ...]`) for a bulk getter, never `Optional` or another union;
- a bulk getter returns `dict[K, V]` with `K` the sequence element type; the return annotation is required;
- the aggregate attribute is annotated with the getter's return type, `Optional` on either side is ignored;
- `entity_attribute_name` and `aggregate_attribute_name` must be declared in the `__annotations__` of the entity and
  aggregate class themselves, not inherited.

A bulk getter is called once with the set of distinct ids; ids that are `None` or falsy are skipped and the aggregate
attribute is left `None`, so annotate it `Optional`.

```python
from dddesign.structure.infrastructure.adapters.internal import InternalAdapter

from app.account_context.domains.dto.media import Media, MediaId
from app.media_context.applications.media import MediaApp, media_app_impl


class MediaAdapter(InternalAdapter):
    media_app: MediaApp = media_app_impl
    
    def get(self, media_id: MediaId) -> Media | None:
        medias = self.get_map((media_id,))
        return next(iter(medias.values()), None)

    def get_map(self, media_ids: tuple[MediaId, ...]) -> dict[MediaId, Media]:
        if not media_ids:
            return {}

        medias = self.media_app.get_list(media_ids=media_ids)
        return {MediaId(media.media_id): Media(**media.model_dump()) for media in medias}


media_adapter_impl = MediaAdapter()
```

```python
from dddesign.structure.domains.aggregates import Aggregate
from pydantic import model_validator

from app.account_context.domains.dto.media import Media
from app.account_context.domains.entities.profile import Profile


class ProfileAggregate(Aggregate):
    profile: Profile
    icon: Media | None = None

    @model_validator(mode='after')
    def validate_consistency(self):
        if self.profile.icon_id:
            if self.icon is None:
                raise ValueError('`icon` field is required when `profile` has `icon_id`')
            if self.profile.icon_id != self.icon.media_id:
                raise ValueError('`profile.icon_id` is not equal to `icon.media_id`')
        elif self.icon is not None:
            raise ValueError('`icon` field is not allowed when `profile` has no `icon_id`')

        return self
```

**Example 1**: Retrieving multiple related objects
```python
from dddesign.structure.domains.aggregates import AggregateDependencyMapper, AggregateListFactory

from app.account_context.domains.aggregates.profile import ProfileAggregate
from app.account_context.infrastructure.adapters.internal.media import media_adapter_impl


aggregate_list_factory = AggregateListFactory[ProfileAggregate](
    aggregate_class=ProfileAggregate,
    aggregate_entity_attribute_name='profile',
    dependency_mappers=(
        AggregateDependencyMapper(
            method_getter=media_adapter_impl.get_map,
            entity_attribute_name='icon_id',
            aggregate_attribute_name='icon',
        ),
    ),
)

aggregates: list[ProfileAggregate] = aggregate_list_factory.create_list([...])  # list of Profile Entity
```

**Example 2**: Retrieving a single related object
```python
from dddesign.structure.domains.aggregates import AggregateDependencyMapper, AggregateListFactory

from app.account_context.domains.aggregates.profile import ProfileAggregate
from app.account_context.infrastructure.adapters.internal.media import media_adapter_impl


aggregate_list_factory = AggregateListFactory[ProfileAggregate](
    aggregate_class=ProfileAggregate,
    aggregate_entity_attribute_name='profile',
    dependency_mappers=(
        AggregateDependencyMapper(
            method_getter=media_adapter_impl.get,
            entity_attribute_name='icon_id',
            aggregate_attribute_name='icon',
        ),
    ),
)

aggregates: list[ProfileAggregate] = aggregate_list_factory.create_list([...])  # list of Profile Entity
```

## Enums

### BaseEnum

`BaseEnum` (`dddesign.structure.domains.constants`) is a foundational enum class that should be used across the application. 
It extends the standard Python Enum and provides additional functionality:
- `__str__` returns `str(member.value)`, so a member formats as its value in logs and responses rather than as `Kind.A`.
- `has_value(value)` class method: Allows you to check whether a specific value is defined in the enum. This is particularly useful for validation purposes.

### ChoiceEnum

`ChoiceEnum` is an extension of `BaseEnum` designed for scenarios where enumerations need both a machine-readable value 
and a human-readable title: `member.get_title()` is the member name with underscores replaced by spaces, in title case
(`NOT_FOUND` → `Not Found`), and `get_choices()` returns `((value, title), ...)` for every member.

## Error Handling

### BaseError

`BaseError` (`dddesign.structure.domains.errors`) is a foundational exception class that standardizes error handling by providing structured information for errors. 
It simplifies the creation of domain-specific exceptions and ensures consistency across the application.

An error carries `message`, `error_code`, `status_code` and `field_name`. A subclass declares them as class
attributes and `__init__(message=None, error_code=None, status_code=None, field_name=None, **kwargs)` falls back
to them: `message` is required one way or the other (`ValueError` otherwise), `error_code` defaults to the
snake_case of the class name, `status_code` to 400. The `{name}` placeholders of the message are filled from
`kwargs`, every placeholder must be provided (`ValueError`), and the kwargs are not stored otherwise. `str(error)`
is its repr with the four attributes.

```python
from dddesign.structure.domains.errors import BaseError


class ProfileNotFoundError(BaseError):
    message = 'Profile `{profile_id}` not found'
    status_code = 404


raise ProfileNotFoundError(profile_id=profile_id)  # error_code 'profile_not_found_error'
```

### CollectionError

`CollectionError` is an exception class designed to aggregate multiple instances of `BaseError`. 
It simplifies error handling in scenarios where multiple errors need to be captured and processed together:
`add(error)` appends a `BaseError` (`TypeError` for anything else), `errors` is the list, iterating the collection
iterates the list, and `bool(collection)` tells whether anything was added, so validation code can collect and
raise only when `if errors:`.

### Errors

`Errors` (`dddesign.components.domains.dto`) is a Data Transfer Object that transforms a `CollectionError` into a structured format for 4XX HTTP responses. 
It ensures domain-level errors are serialized and returned to the client in a meaningful way, avoiding 500 responses.
`Errors.factory(collection_error)` builds it from a non-empty collection, `errors` is a list of `Error` value
objects (`dddesign.components.domains.value_objects`) with the four attributes of a `BaseError`, and `status_code`
is the status of the single error or 400 when there are several.

### AutoUUID

`AutoUUID` (`dddesign.components.domains.value_objects`) is a `uuid.UUID` that generates a random UUID4 when
constructed without arguments and accepts another `UUID` instance; otherwise identical to `UUID`. Pydantic validates
it from a UUID, a string, bytes or an int. The pattern for typed identifiers:

```python
from pydantic import Field

from dddesign.components.domains.value_objects import AutoUUID
from dddesign.structure.domains.entities import Entity


class ProfileId(AutoUUID): ...


class Profile(Entity):
    profile_id: ProfileId = Field(default_factory=ProfileId)
```

### wrap_error

`wrap_error(error: ValidationError) -> CollectionError` (`dddesign.utils.base_model`) converts a Pydantic `ValidationError` into a `CollectionError`, 
enabling a standardized way of handling and aggregating validation errors. Every pydantic error becomes a `BaseError`
with `field_name` the dotted location (`address.city`) and `message` the pydantic message, or the messages an error
created with `create_pydantic_error_instance` carries.

### create_pydantic_error_instance

`create_pydantic_error_instance(base_error, message, code=None, context=None)` (`dddesign.utils.base_model`) is a utility function for dynamically creating custom `PydanticErrorMixin` instances, 
allowing to define detailed and context-aware Pydantic validation errors to raise from validators. `message` is
formatted with `context`; a `context['__messages__']` list (`CONTEXT_MESSAGES_PARAM`) is what `wrap_error` reports
instead of the single message.

### flatten_model_dump

`flatten_model_dump(model, separator='.', **model_dump_kwargs)` (`dddesign.utils.base_model`) is `model_dump` with
nested dicts flattened into dotted keys: `{'address': {'city': 'Oslo'}}` becomes `{'address.city': 'Oslo'}`.

## Testing and State Management

### MagicMock

`MagicMock` (`dddesign.unittest.magic_mock`) is an enhanced version of `unittest.mock.MagicMock` that adds compatibility with `BaseModel`. 
When the `spec` or `spec_set` is a pydantic model it makes `_copy_and_set_values` return the mock itself, so
`model_copy` and validation on assignment do not replace the mock with a copy.

### TrackChangesMixin

`TrackChangesMixin` (`dddesign.utils.base_model`) is a mixin for `BaseModel` that tracks changes made to model fields. 
It takes a deep copy of every field in `__init__` and compares against it: `has_changed`, `changed_fields`,
`changed_data` (field to current value), `diffs` (field to `(initial, current)`), `initial_state`;
`update_initial_state(fields=None)` takes a new snapshot of the given fields or of all of them, for example after
a save. Meant for mutable models such as an `Entity`; on a frozen model nothing ever changes.
