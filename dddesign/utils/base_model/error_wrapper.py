from typing import Optional

from pydantic import ValidationError

from dddesign.structure.domains.errors import BaseError, CollectionError

CONTEXT_MESSAGES_PARAM = '__messages__'


def wrap_error(error: ValidationError) -> CollectionError:
    if not isinstance(error, ValidationError):
        raise TypeError('`exception` must be an instance of `pydantic.ValidationError`')

    errors = CollectionError()

    for _error in error.errors():
        field_name: Optional[str] = '.'.join(str(item) for item in _error['loc'])
        if field_name == '__root_validator__':
            field_name = None

        if 'ctx' in _error and CONTEXT_MESSAGES_PARAM in _error['ctx']:
            for msg in _error['ctx'][CONTEXT_MESSAGES_PARAM]:
                errors.add(BaseError(message=msg, field_name=field_name))
        else:
            errors.add(BaseError(message=_error['msg'], field_name=field_name))

    return errors
