from typing import Any

from dddesign.structure.domains.constants import BaseEnum

SEPARATOR = '_'


class ChoiceEnum(BaseEnum):
    def get_title(self) -> str:
        _name = ' '.join(self.name.split(SEPARATOR))
        return _name.title()

    @classmethod
    def get_choices(cls) -> tuple[tuple[Any, str], ...]:
        return tuple((value.value, value.get_title()) for value in cls)


__all__ = ('ChoiceEnum',)
