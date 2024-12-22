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

## DDD Components

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

# note: the argument name must match the lowercase version of the Enum class name
auth_apple_app_impl = auth_social_app_factory.get(social_driver=SocialDriver.APPLE)
```

### AggregateListFactory

Converts a list of **Entity** into **Aggregate** objects.

```python
from dddesign.structure.infrastructure.adapters.internal import InternalAdapter

from app.account_context.domains.dto.media import Media, MediaId
from app.media_context.applications.media import MediaApp, media_app_impl


class MediaAdapter(InternalAdapter):
    media_app: MediaApp = media_app_impl
    
    def get(self, media_id: MediaId | None) -> Media | None:
        if media_id is None:
            return None

        medias = self.get_map((media_id,))
        return next(iter(medias.values()), None)

    def get_map(self, media_ids: tuple[str, ...]) -> dict[str, Media]:
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

`BaseEnum` is a foundational enum class that should be used across the application. 
It extends the standard Python Enum and provides additional functionality:
- `__str__` method: Converts the enum’s value to a string representation, making it more readable in logs, responses, or debugging output.
- `has_value` class method: Allows you to check whether a specific value is defined in the enum. This is particularly useful for validation purposes.

### ChoiceEnum

`ChoiceEnum` is an extension of `BaseEnum` designed for scenarios where enumerations need both a machine-readable value 
and a human-readable title. It adds utility methods for creating user-friendly choices.

## Error Handling

### BaseError

`BaseError` is a foundational exception class that standardizes error handling by providing structured information for errors. 
It simplifies the creation of domain-specific exceptions and ensures consistency across the application.

### CollectionError

`CollectionError` is an exception class designed to aggregate multiple instances of `BaseError`. 
It simplifies error handling in scenarios where multiple errors need to be captured and processed together.

### Errors

`Errors` is a Data Transfer Object that transforms a `CollectionError` into a structured format for 4XX HTTP responses. 
It ensures domain-level errors are serialized and returned to the client in a meaningful way, avoiding 500 responses.

### wrap_error

`wrap_error` is a utility function designed to convert a Pydantic `ValidationError` into a `CollectionError`, 
enabling a standardized way of handling and aggregating validation errors. 
It ensures that detailed error information is preserved while providing a structured format for further processing.

### create_pydantic_error_instance

`create_pydantic_error_instance` is a utility function for dynamically creating custom `PydanticErrorMixin` instances, 
allowing to define detailed and context-aware Pydantic validation errors.

## Testing and State Management

### MagicMock

`MagicMock` is an enhanced version of `unittest.mock.MagicMock` that adds compatibility with `BaseModel`. 
It streamlines testing by handling Pydantic models more effectively in mocked environments.

### TrackChangesMixin

`TrackChangesMixin` is a mixin for `BaseModel` that tracks changes made to model fields. 
It allows to monitor field modifications, compare current and initial values, and manage the state of the model.
