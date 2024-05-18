import ast
import builtins
import inspect
import textwrap
from importlib import import_module
from typing import Any, Callable, Dict, Generator, Optional, Tuple, Type

from pydantic import BaseModel, Field, validator

from dddesign.utils.module_getter import get_module

UNDEFINED_VALUE = object()


class ExceptionInfo(BaseModel):
    exception_class: Type[Exception]
    args: Tuple[Any, ...] = Field(default_factory=tuple)
    kwargs: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        allow_mutation = False

    @validator('args')
    def validate_args(cls, value):
        return tuple(_v.value if isinstance(_v, ast.Constant) else UNDEFINED_VALUE for _v in value)

    @validator('kwargs')
    def validate_kwargs(cls, value):
        return {_k: _v.value if isinstance(_v, ast.Constant) else UNDEFINED_VALUE for _k, _v in value.items()}

    def get_kwargs(self):
        annotations = tuple(
            argument_name
            for argument_name in inspect.signature(self.exception_class.__init__).parameters
            if argument_name not in ('self', 'args', 'kwargs')
        )
        kwargs = {
            **{attribute_name: self.args[item] for item, attribute_name in enumerate(annotations[: len(self.args)])},
            **{_k: _v for _k, _v in self.kwargs.items() if _k in annotations},
        }
        for annotation in annotations:
            if annotation not in kwargs:
                kwargs[annotation] = UNDEFINED_VALUE

        return kwargs

    def get_exception_instance(self):
        kwargs = {k: f'<{k}>' if v is UNDEFINED_VALUE else v for k, v in self.get_kwargs().items()}
        return self.exception_class(**kwargs)


def _get_node_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute):
        return f'{_get_node_name(node.value)}.{node.attr}'
    elif isinstance(node, ast.Call):
        return _get_node_name(node.func)
    else:
        raise TypeError(f'Unsupported node type: {type(node)}')


def extract_function_exceptions(func: Callable) -> Generator[ExceptionInfo, None, None]:
    source = textwrap.dedent(inspect.getsource(func))
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.Raise):
            if node.exc is None:
                continue

            try:
                exception_name: str = _get_node_name(node.exc)
                exception_args: Tuple[Any, ...] = ()
                exception_kwargs: Dict[str, Any] = {}
            except TypeError:
                continue

            if isinstance(node.exc, ast.Call):
                exception_args = tuple(node.exc.args)
                exception_kwargs = {kw.arg: kw.value for kw in node.exc.keywords if isinstance(kw.arg, str)}

            exception_name_slices = exception_name.split('.')
            class_name = exception_name_slices[-1]
            sub_modules = exception_name_slices[:-1]

            exception_module = get_module(import_module(func.__module__), sub_modules)

            exception_class: Optional[Type[Exception]] = getattr(exception_module, class_name, None)
            if exception_class is None and hasattr(builtins, exception_name):
                exception_class = getattr(builtins, exception_name)

            if exception_class is None:
                continue

            yield ExceptionInfo(exception_class=exception_class, args=exception_args, kwargs=exception_kwargs)
