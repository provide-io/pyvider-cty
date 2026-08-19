#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from __future__ import annotations

from typing import Any, ClassVar

from attrs import define

from pyvider.cty.exceptions import CtyBoolValidationError
from pyvider.cty.types.base import CtyType
from pyvider.cty.validation.marks import preserves_marks
from pyvider.cty.values import CtyValue, UnknownValue


@define(frozen=True, slots=True)
class CtyBool(CtyType[bool]):
    ctype: ClassVar[str] = "bool"
    _type_order: ClassVar[int] = 2  # Correct go-cty order

    @preserves_marks
    def validate(self, value: object) -> CtyValue[bool]:  # noqa: C901
        if isinstance(value, UnknownValue):
            return self.unknown_like(value)

        if isinstance(value, CtyValue):
            if value.is_null:
                return CtyValue.null(self)
            if value.is_unknown:
                return self.unknown_like(value)
            raw_value = value.value
        else:
            raw_value = value

        if raw_value is None:
            return CtyValue.null(self)

        if isinstance(raw_value, bool):
            return CtyValue(vtype=self, value=raw_value)
        if isinstance(raw_value, str):
            if raw_value.lower() == "true":
                return CtyValue(vtype=self, value=True)
            if raw_value.lower() == "false":
                return CtyValue(vtype=self, value=False)
        if isinstance(raw_value, int | float):
            if raw_value == 1:
                return CtyValue(vtype=self, value=True)
            if raw_value == 0:
                return CtyValue(vtype=self, value=False)

        raise CtyBoolValidationError(f"Cannot convert {type(raw_value).__name__} to bool.")

    def equal(self, other: CtyType[Any]) -> bool:
        return isinstance(other, CtyBool)

    def usable_as(self, other: CtyType[Any]) -> bool:
        from pyvider.cty.types.structural import CtyDynamic

        return isinstance(other, CtyBool | CtyDynamic)

    def _to_wire_json(self) -> Any:
        return self.ctype

    def __str__(self) -> str:
        return "bool"

    def is_primitive_type(self) -> bool:
        return True


# 🌊🪢🔚
