from typing import Any, Optional

from dddesign.utils.convertors import convert_camel_case_to_snake_case


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
        return (
            f'{self.__class__.__name__}(\n'
            f"    message='{self.message}',\n"
            f"    error_code='{self.error_code}',\n"
            f"    status_code='{self.status_code}',\n"
            f"    field_name='{self.field_name}'\n"
            ')'
        )

    def __repr__(self) -> str:
        return self.__str__()

    @classmethod
    def get_error_code(cls) -> str:
        return convert_camel_case_to_snake_case(cls.__name__)
