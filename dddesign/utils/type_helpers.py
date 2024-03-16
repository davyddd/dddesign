import inspect
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from ipaddress import IPv4Address, IPv6Address
from types import CodeType, FunctionType
from typing import Any, Callable, Optional, Type, Union, get_args
from uuid import UUID

PythonType = Union[str, float, bool, bytes, int, dict, date, time, datetime, timedelta, UUID, Decimal, IPv4Address, IPv6Address]


def is_subclass_smart(class_type: Any, *base_types: Any) -> bool:
    class_type = getattr(class_type, '__origin__', class_type)
    return inspect.isclass(class_type) and issubclass(class_type, base_types)


def get_type_without_optional(class_type: Any) -> Any:
    return get_args(class_type)[0] if type(None) in get_args(class_type) else class_type


def get_origin_class_of_method(cls: Any, method_name: str):
    for base in inspect.getmro(cls):
        if method_name in base.__dict__:
            return base


def _is_python_type(type_) -> bool:
    return is_subclass_smart(type_, getattr(PythonType, '__args__', None))


def get_python_type(type_) -> Type[PythonType]:
    if hasattr(type_, '__supertype__'):
        return get_python_type(type_.__supertype__)
    elif hasattr(type_, '__origin__'):
        return get_python_type(type_.__args__[0])
    elif hasattr(type_, '__bases__'):
        next_type = type_.__bases__[0]
        if _is_python_type(type_) and not _is_python_type(next_type):
            return type_
        else:
            return get_python_type(next_type)
    else:
        raise TypeError(f'Unknown type: {type(type_)}')


def get_new_function(func: Callable, new_name: Optional[str] = None) -> Callable:
    base_code = func.__code__
    func_name = new_name or base_code.co_name
    new_code = CodeType(
        base_code.co_argcount,
        base_code.co_posonlyargcount,
        base_code.co_kwonlyargcount,
        base_code.co_nlocals,
        base_code.co_stacksize,
        base_code.co_flags,
        base_code.co_code,
        base_code.co_consts,
        base_code.co_names,
        base_code.co_varnames,
        base_code.co_filename,
        func_name,
        base_code.co_firstlineno,
        base_code.co_lnotab,
        base_code.co_freevars,
        base_code.co_cellvars,
    )
    return FunctionType(new_code, func.__globals__)
