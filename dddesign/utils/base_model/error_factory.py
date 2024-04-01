from typing import Optional, Type, TypeVar

from pydantic.errors import PydanticErrorMixin

BaseError = TypeVar('BaseError', bound=Exception)


def create_pydantic_error_instance(
    base_error: Type[BaseError], code: str, msg_template: str, context: Optional[dict] = None
) -> BaseError:
    _class = type('PydanticError', (PydanticErrorMixin, base_error), {'code': code, 'msg_template': msg_template})
    if isinstance(context, dict):
        return _class(**context)
    else:
        return _class()
