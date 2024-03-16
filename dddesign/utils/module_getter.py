from types import ModuleType
from typing import List


def get_module(module: ModuleType, sub_modules: List[str]) -> ModuleType:
    if not module:
        raise ValueError('Argument `module` is required')
    elif not isinstance(sub_modules, list):
        raise ValueError('Argument `sub_modules` must be a list of strings')

    if len(sub_modules) == 0:
        return module

    sub_module = sub_modules.pop(0)

    if hasattr(module, sub_module):
        module = getattr(module, sub_module)
        return get_module(module, sub_modules)
    else:
        raise ValueError(f'Module {sub_module} not found in {module.__name__}')
