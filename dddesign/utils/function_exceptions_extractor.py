import ast
import builtins
import inspect
import textwrap
from importlib import import_module
from typing import Any, Callable, Dict, Generator, Optional, Tuple, Type

from pydantic import BaseModel, Field, validator

from dddesign.utils.module_getter import get_module


class ExceptionInfo(BaseModel):
    exception_class: Type[Exception]
    args: Tuple[Any, ...] = Field(default_factory=tuple)
    kwargs: Dict[str, Any] = Field(default_factory=dict)

    @validator('args')
    def validate_args(cls, value):
        return tuple(_v.value if isinstance(_v, ast.Constant) else None for _v in value)

    @validator('kwargs')
    def validate_kwargs(cls, value):
        return {_k: _v.value if isinstance(_v, ast.Constant) else None for _k, _v in value.items()}

    def get_kwargs(self):
        annotations = tuple(
            argument_name
            for argument_name in inspect.signature(self.exception_class.__init__).parameters
            if argument_name not in ('self', 'args', 'kwargs')
        )

        return {
            **{attribute_name: self.args[item] for item, attribute_name in enumerate(annotations[: len(self.args)])},
            **self.kwargs,
        }

    def get_exception_instance(self):
        kwargs = {k: f'<{k}>' if v is None else v for k, v in self.get_kwargs().items()}
        return self.exception_class(**kwargs)


def extract_function_exceptions(func: Callable) -> Generator[ExceptionInfo, None, None]:
    source = textwrap.dedent(inspect.getsource(func))
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.Raise):
            exception_name: Optional[str] = None
            exception_args: Tuple[Any, ...] = ()
            exception_kwargs: Dict[str, Any] = {}

            if isinstance(node.exc, ast.Call):
                exception_name = ast.unparse(node.exc.func)
                exception_args = tuple(node.exc.args)
                exception_kwargs = {kw.arg: kw.value for kw in node.exc.keywords if isinstance(kw.arg, str)}
            elif isinstance(node.exc, (ast.Attribute, ast.Name)):
                exception_name = ast.unparse(node.exc)

            if not exception_name:
                continue

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
