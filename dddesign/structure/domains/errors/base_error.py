from typing import Any, Optional

from ddutils.convertors import convert_camel_case_to_snake_case, convert_to_repr


class BaseError(Exception):
    message: str
    error_code: str
    status_code: int
    field_name: Optional[str]

    def __init__(
        self,
        message: Optional[str] = None,
        error_code: Optional[str] = None,
        status_code: Optional[int] = None,
        field_name: Optional[str] = None,
        **kwargs: Any,
    ):
        message = message or getattr(self, 'message', None)
        if not message:
            raise ValueError('Field `message` is required')
        self.message = message.format(**kwargs)

        self.error_code = error_code or getattr(self, 'error_code', None) or self.get_error_code()

        self.status_code = status_code or getattr(self, 'status_code', None) or 400

        self.field_name = field_name or getattr(self, 'field_name', None)

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return convert_to_repr(self)

    @classmethod
    def get_error_code(cls) -> str:
        return convert_camel_case_to_snake_case(cls.__name__)


__all__ = ('BaseError',)
