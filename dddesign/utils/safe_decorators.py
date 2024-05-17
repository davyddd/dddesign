import logging
from functools import wraps
from typing import Any, Callable, Optional, Tuple, Type

logger = logging.getLogger(__name__)


def safe_call(
    func: Optional[Callable] = None,
    capture_exception: bool = True,
    default_result: Optional[Any] = None,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
) -> Callable:
    if func is None:
        return lambda _func: safe_call(
            func=_func, capture_exception=capture_exception, default_result=default_result, exceptions=exceptions
        )

    @wraps(func)
    def wrapped_func(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except exceptions as error:
            if capture_exception:
                logger.exception(error)

            result = default_result

        return result

    return wrapped_func


def retry_once_after_exception(
    func: Optional[Callable] = None, capture_exception: bool = True, exceptions: Tuple[Type[Exception], ...] = (Exception,)
) -> Callable:
    if func is None:
        return lambda _func: retry_once_after_exception(func=_func, capture_exception=capture_exception, exceptions=exceptions)

    @wraps(func)
    def wrapped_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except exceptions as error:
            if capture_exception:
                logger.exception(error)

            return func(*args, **kwargs)

    return wrapped_func
