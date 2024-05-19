from typing import Any, Dict, Generator, Optional, Tuple

from pydantic import BaseModel, PrivateAttr

UNDEFINED_VALUE = object()


class TrackChangesMixin(BaseModel):
    _initial_state: Dict[str, Any] = PrivateAttr()

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self.update_initial_state()

    def _get_changed_fields(self) -> Generator[str, None, None]:
        for field, value in self.dict().items():
            if self._initial_state.get(field, UNDEFINED_VALUE) != value:
                yield field

    @property
    def has_changed(self) -> bool:
        return next(self._get_changed_fields(), None) is not None

    @property
    def changed_fields(self) -> Tuple[str, ...]:
        return tuple(self._get_changed_fields())

    @property
    def changed_data(self) -> Dict[str, Any]:
        return {field: getattr(self, field, None) for field in self._get_changed_fields()}

    @property
    def diffs(self) -> Dict[str, Tuple[Any, Any]]:
        return {field: (self._initial_state[field], getattr(self, field, None)) for field in self._get_changed_fields()}

    @property
    def initial_state(self) -> Dict[str, Any]:
        return self._initial_state

    def update_initial_state(self, fields: Optional[tuple] = None):
        _dict = self.dict()
        if fields:
            for field in fields:
                if field in _dict:
                    self._initial_state[field] = _dict[field]
        else:
            self._initial_state = _dict
