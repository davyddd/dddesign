from typing import Any, get_args


def get_type_without_optional(class_type: Any) -> Any:
    return get_args(class_type)[0] if type(None) in get_args(class_type) else class_type
