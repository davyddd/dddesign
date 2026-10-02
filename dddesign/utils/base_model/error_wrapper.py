from pydantic import ValidationError
from pydantic.errors import PydanticErrorMixin
from pydantic_core import ErrorDetails

from dddesign.structure.domains.errors import BaseError, CollectionError
from dddesign.utils.base_model.error_instance_factory import CONTEXT_MESSAGES_PARAM


def _get_error_messages(error_details: ErrorDetails) -> list[str]:
    original_error: Exception | None = error_details.get('ctx', {}).get('error')
    if not original_error:
        return [error_details['msg']]
    if not isinstance(original_error, PydanticErrorMixin):
        return [str(original_error)]

    messages = getattr(original_error, CONTEXT_MESSAGES_PARAM, None)
    if isinstance(messages, list):
        return messages
    return [original_error.message]


def wrap_error(error: ValidationError) -> CollectionError:
    if not isinstance(error, ValidationError):
        raise TypeError('`exception` must be an instance of `pydantic.ValidationError`')

    errors = CollectionError()

    for error_details in error.errors():
        field_name: str | None = '.'.join(str(item) for item in error_details['loc']) or None
        for message in _get_error_messages(error_details):
            errors.add(BaseError(message=message, field_name=field_name))

    return errors


__all__ = ('wrap_error',)
