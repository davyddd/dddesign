import inspect
import sys
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from ipaddress import IPv4Address, IPv6Address
from types import CellType, CodeType, FunctionType
from typing import Any, Callable, Optional, Type, Union, get_args
from uuid import UUID

PythonType = Union[
    str, bool, int, float, bytes, tuple, list, dict, date, time, datetime, timedelta, UUID, Decimal, IPv4Address, IPv6Address
]


def is_subclass_smart(class_type: Any, *base_types: Any) -> bool:
    class_type = getattr(class_type, '__origin__', class_type)
    return inspect.isclass(class_type) and issubclass(class_type, base_types)


def get_type_without_optional(class_type: Any) -> Any:
    if type(None) in get_args(class_type) and len(get_args(class_type)) == 2:  # noqa: PLR2004
        for arg in get_args(class_type):
            if arg is not type(None):
                return arg
    else:
        return class_type


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
        return get_python_type(get_type_without_optional(type_))
    elif getattr(type_, '__bases__', None):
        next_type = type_.__bases__[0]
        if (
            type_ is bool  # because bool is a subclass of int
            or type_ is datetime  # because datetime is a subclass of date
            or (_is_python_type(type_) and not _is_python_type(next_type))
        ):
            return type_
        else:
            return get_python_type(next_type)
    else:
        raise TypeError(f'Unknown type: {type(type_)}')


def get_new_function(func: Callable, new_name: Optional[str] = None) -> Callable:
    base_code = func.__code__
    func_name = new_name or base_code.co_name

    if sys.version_info >= (3, 11):
        # for python 3.11 and newer
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
            func_name,
            base_code.co_firstlineno,
            base_code.co_lnotab,
            base_code.co_exceptiontable,
            base_code.co_freevars,
            base_code.co_cellvars,
        )
    else:
        # for python 3.10 and older
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

    closure = func.__closure__
    if closure:
        closure = tuple(CellType(cell.cell_contents) for cell in closure)

    return FunctionType(new_code, func.__globals__, func_name, func.__defaults__, closure)
