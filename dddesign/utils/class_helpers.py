import inspect
from typing import Any


def get_origin_class_of_method(cls: Any, method_name: str):
    for base in inspect.getmro(cls):
        if method_name in base.__dict__:
            return base
