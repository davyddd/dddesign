import sys
from types import CellType, CodeType, FunctionType
from typing import Callable, Optional


def create_new_function(base_func: Callable, new_name: Optional[str] = None) -> Callable:
    base_code = base_func.__code__
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

    closure = base_func.__closure__
    if closure:
        closure = tuple(CellType(cell.cell_contents) for cell in closure)

    return FunctionType(new_code, base_func.__globals__, func_name, base_func.__defaults__, closure)
