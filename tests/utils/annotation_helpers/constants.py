from typing import Dict, List, NewType as NewTypeTyping

from typing_extensions import NewType as NewTypeTypingExtensions

COMMON_PYTHON_TYPES = (bool, int, float, str, tuple, list, dict)

# List annotations

ListAnnotationNative = list[int]
ListAnnotationNotNative = List[int]

CustomListNativeTyping = NewTypeTyping('CustomListNativeTyping', ListAnnotationNative)
CustomListNotNativeTyping = NewTypeTyping('CustomListNotNativeTyping', ListAnnotationNotNative)

CustomListNativeTypingExtensions = NewTypeTypingExtensions('CustomListNativeTypingExtensions', ListAnnotationNative)
CustomListNotNativeTypingExtensions = NewTypeTypingExtensions('CustomListNotNativeTypingExtensions', ListAnnotationNotNative)

GENERIC_LIST_ANNOTATIONS = (
    ListAnnotationNative,
    ListAnnotationNotNative,
    CustomListNativeTyping,
    CustomListNotNativeTyping,
    CustomListNativeTypingExtensions,
    CustomListNotNativeTypingExtensions,
)

# Dict annotations

DictAnnotationNative = dict[str, int]
DictAnnotationNotNative = Dict[str, int]

CustomDictNativeTyping = NewTypeTyping('CustomDictNativeTyping', DictAnnotationNative)
CustomDictNotNativeTyping = NewTypeTyping('CustomDictNotNativeTyping', DictAnnotationNotNative)

CustomDictNativeTypingExtensions = NewTypeTypingExtensions('CustomDictNativeTypingExtensions', DictAnnotationNative)
CustomDictNotNativeTypingExtensions = NewTypeTypingExtensions('CustomDictNotNativeTypingExtensions', DictAnnotationNotNative)

GENERIC_DICT_ANNOTATIONS = (
    DictAnnotationNative,
    DictAnnotationNotNative,
    CustomDictNativeTyping,
    CustomDictNotNativeTyping,
    CustomDictNativeTypingExtensions,
    CustomDictNotNativeTypingExtensions,
)
