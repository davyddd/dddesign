from typing import Optional

from pydantic import ValidationError
from pydantic.errors import PydanticErrorMixin

from dddesign.structure.domains.errors import BaseError, CollectionError
from dddesign.utils.base_model.error_instance_factory import CONTEXT_MESSAGES_PARAM


def wrap_error(error: ValidationError) -> CollectionError:
    if not isinstance(error, ValidationError):
        raise TypeError('`exception` must be an instance of `pydantic.ValidationError`')

    errors = CollectionError()

    for _error in error.errors():
        field_name: Optional[str] = '.'.join(str(item) for item in _error['loc']) or None

        original_error: Optional[Exception] = _error.get('ctx', {}).get('error')
        if original_error:
            if isinstance(original_error, PydanticErrorMixin):
                messages = getattr(original_error, CONTEXT_MESSAGES_PARAM, None)
                if isinstance(messages, list):
                    for message in messages:
                        errors.add(BaseError(message=message, field_name=field_name))
                else:
                    errors.add(BaseError(message=original_error.message, field_name=field_name))
            else:
                errors.add(BaseError(message=str(original_error), field_name=field_name))
        else:
            errors.add(BaseError(message=_error['msg'], field_name=field_name))

    return errors


__all__ = ('wrap_error',)
