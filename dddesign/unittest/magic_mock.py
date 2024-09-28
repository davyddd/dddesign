from unittest.mock import MagicMock as OriginalMagicMock

from pydantic import BaseModel

from dddesign.utils.annotation_helpers import is_subclass
from dddesign.utils.sequence_helpers import get_safe_element


class MagicMock(OriginalMagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        class_type = (
            get_safe_element(args, 0)  # spec
            or get_safe_element(args, 5)  # spec_set
            or kwargs.get('spec')
            or kwargs.get('spec_set')
        )
        if is_subclass(class_type, BaseModel):
            self._copy_and_set_values.return_value = self  # some magic
