from typing import Optional, Type, TypeVar

from pydantic.errors import PydanticErrorMixin

BaseError = TypeVar('BaseError', bound=Exception)


CONTEXT_MESSAGES_PARAM = '__messages__'


def create_pydantic_error_instance(
    base_error: Type[BaseError], message: str, code: Optional[str] = None, context: Optional[dict] = None
) -> BaseError:
    _class = type('PydanticError', (PydanticErrorMixin, base_error), {})

    if isinstance(context, dict):
        message = message.format(**context)

    instance = _class(message=message, code=code)

    if isinstance(context, dict) and CONTEXT_MESSAGES_PARAM in context:
        instance.__dict__[CONTEXT_MESSAGES_PARAM] = context[CONTEXT_MESSAGES_PARAM]

    return instance


__all__ = ('create_pydantic_error_instance', 'CONTEXT_MESSAGES_PARAM')
