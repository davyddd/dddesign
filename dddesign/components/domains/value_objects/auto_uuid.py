from uuid import UUID, SafeUUID, uuid4


class AutoUUID(UUID):
    """
    Drop-in replacement for uuid.UUID:
    - AutoUUID() with no arguments -> generates a random UUID4.
    - AutoUUID(x) with arguments -> identical to UUID(x).
    Compatible with Pydantic (v1 and v2) for use as a field type.
    Allows for the following:
    class CustomerId(AutoUUID): ...
    class Customer(BaseModel):
        customer_id: CustomerId = Field(default_factory=CustomerId)
        name: str
    Customer(name='John Doe')
    This does not raise and satisfies type checkers
    """

    def __init__(self, *args, **kwargs):
        # If no args/kwargs, generate a new random UUID4
        if not args and not kwargs:
            rand_uuid = uuid4()
            object.__setattr__(self, 'int', rand_uuid.int)
            # Preserve is_safe attribute if available (Python 3.7+)
            object.__setattr__(self, 'is_safe', getattr(rand_uuid, 'is_safe', SafeUUID.unknown))
        # If a UUID instance is passed, convert it (not handled by base UUID)
        elif len(args) == 1 and isinstance(args[0], UUID):
            base_uuid = args[0]
            object.__setattr__(self, 'int', base_uuid.int)
            object.__setattr__(self, 'is_safe', getattr(base_uuid, 'is_safe', SafeUUID.unknown))
        else:
            # Delegate to base class for all other cases (hex, int, bytes, etc.)
            super().__init__(*args, **kwargs)

    @classmethod
    def __get_validators__(cls):
        """Pydantic v1: yield validators for parsing input."""
        yield cls._validate

    @classmethod
    def _validate(cls, value):
        # Already a AutoUUID instance
        if isinstance(value, cls):
            return value
        # Any UUID (base UUID or another subclass) -> convert to AutoUUID
        if isinstance(value, UUID):
            # Convert base UUID to AutoUUID (preserve value)
            return cls(value)
        # Acceptable input types: str, bytes, bytearray, int
        if isinstance(value, (bytes, bytearray)):
            try:
                return cls(bytes=value)  # parse from 16-byte sequence
            except Exception as e:  # noqa: BLE001
                raise ValueError(f'Invalid UUID bytes: {e}') from e
        if isinstance(value, str):
            try:
                return cls(value)  # parse from hex string (with or without hyphens)
            except Exception as e:  # noqa: BLE001
                raise ValueError(f'Invalid UUID string: {e}') from e
        if isinstance(value, int):
            try:
                return cls(int=value)  # parse from integer
            except Exception as e:  # noqa: BLE001
                raise ValueError(f'Invalid UUID integer: {e}') from e
        # If it's none of the above, it's an error
        raise TypeError('UUID type required')

    @classmethod
    def __modify_schema__(cls, field_schema):
        """Pydantic v1: Customize JSON schema output."""
        field_schema.update(type='string', format='uuid')  # represent as a UUID string

    # Pydantic v2 core schema hook:
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        """Pydantic v2: Define how to validate AutoUUID (wrap built-in UUID schema)."""
        # Import pydantic_core utilities
        from pydantic_core import core_schema

        # Get the core schema for standard UUID, then wrap it with a post-validator
        base_schema = handler(UUID)  # core schema for a standard UUID
        # After validation, call AutoUUID (cls) to construct our subclass instance
        return core_schema.no_info_after_validator_function(cls, base_schema)

    # Pydantic v2 JSON schema hook:
    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        """Pydantic v2: Customize JSON schema generation."""
        json_schema = handler(core_schema)
        # Ensure the schema is represented as a string with format uuid
        json_schema.update(type='string', format='uuid')
        return json_schema
