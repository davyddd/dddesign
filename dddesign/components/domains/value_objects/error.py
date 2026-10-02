from dddesign.structure.domains.value_objects import ValueObject


class Error(ValueObject):
    message: str
    error_code: str
    status_code: int
    field_name: str | None


__all__ = ('Error',)
