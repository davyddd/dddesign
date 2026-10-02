from typing import TypeVar, cast

from pydantic.errors import PydanticErrorMixin

BaseError = TypeVar('BaseError', bound=Exception)


CONTEXT_MESSAGES_PARAM = '__messages__'


def create_pydantic_error_instance(
    base_error: type[BaseError], message: str, code: str | None = None, context: dict | None = None
) -> BaseError:
    _class = type('PydanticError', (PydanticErrorMixin, base_error), {})

    if isinstance(context, dict):
        message = message.format(**context)

    instance = _class(message=message, code=code)  # ty: ignore[invalid-argument-type]

    if isinstance(context, dict) and CONTEXT_MESSAGES_PARAM in context:
        instance.__dict__[CONTEXT_MESSAGES_PARAM] = context[CONTEXT_MESSAGES_PARAM]

    return cast('BaseError', instance)


__all__ = ('create_pydantic_error_instance', 'CONTEXT_MESSAGES_PARAM')
