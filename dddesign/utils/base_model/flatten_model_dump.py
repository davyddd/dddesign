from typing import Any, Dict

from pydantic import BaseModel


def _flatten_dict(data: Dict[str, Any], prefix: str, separator: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in data.items():
        full_key = f'{prefix}{separator}{key}' if prefix else key
        if isinstance(value, dict):
            result.update(_flatten_dict(value, prefix=full_key, separator=separator))
        else:
            result[full_key] = value
    return result


def flatten_model_dump(data: BaseModel, separator: str = '.', **model_dump_kwargs) -> Dict[str, Any]:
    return _flatten_dict(data.model_dump(**model_dump_kwargs), prefix='', separator=separator)


__all__ = ('flatten_model_dump',)
