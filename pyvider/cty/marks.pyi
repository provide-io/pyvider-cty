from attrs import define, field
from typing import Any

@define(frozen=True, slots=True)
class CtyMark:
    name: str = field()
    details: frozenset[Any] | None = field(default=None, converter=_convert_details)
