import sys
from typing import Dict, List, NewType as NewTypeTyping, Optional, Union

from typing_extensions import NewType as NewTypeTypingExtensions

COMMON_PYTHON_TYPES = (bool, int, float, str, tuple, list, dict)

OPTIONAL_INT_ANNOTATIONS = [(Optional[int],), (Union[int, None],)]

if sys.version_info >= (3, 10):
    OPTIONAL_INT_ANNOTATIONS.append((int | None,))

# List annotations

ListAnnotationNotNative = List[int]
CustomListNotNativeTyping = NewTypeTyping('CustomListNotNativeTyping', ListAnnotationNotNative)
CustomListNotNativeTypingExtensions = NewTypeTypingExtensions('CustomListNotNativeTypingExtensions', ListAnnotationNotNative)

GENERIC_LIST_ANNOTATIONS = [(ListAnnotationNotNative,), (CustomListNotNativeTyping,), (CustomListNotNativeTypingExtensions,)]

if sys.version_info >= (3, 10):
    ListAnnotationNative = list[int]
    CustomListNativeTyping = NewTypeTyping('CustomListNativeTyping', ListAnnotationNative)
    CustomListNativeTypingExtensions = NewTypeTypingExtensions('CustomListNativeTypingExtensions', ListAnnotationNative)

    GENERIC_LIST_ANNOTATIONS += [(ListAnnotationNative,), (CustomListNativeTyping,), (CustomListNativeTypingExtensions,)]

# Dict annotations

DictAnnotationNotNative = Dict[str, int]
CustomDictNotNativeTyping = NewTypeTyping('CustomDictNotNativeTyping', DictAnnotationNotNative)
CustomDictNotNativeTypingExtensions = NewTypeTypingExtensions('CustomDictNotNativeTypingExtensions', DictAnnotationNotNative)

GENERIC_DICT_ANNOTATIONS = [(DictAnnotationNotNative,), (CustomDictNotNativeTyping,), (CustomDictNotNativeTypingExtensions,)]


if sys.version_info >= (3, 10):
    DictAnnotationNative = dict[str, int]
    CustomDictNativeTyping = NewTypeTyping('CustomDictNativeTyping', DictAnnotationNative)
    CustomDictNativeTypingExtensions = NewTypeTypingExtensions('CustomDictNativeTypingExtensions', DictAnnotationNative)

    GENERIC_DICT_ANNOTATIONS += [(DictAnnotationNative,), (CustomDictNativeTyping,), (CustomDictNativeTypingExtensions,)]
