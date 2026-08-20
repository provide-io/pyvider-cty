#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from __future__ import annotations

from typing import Any, ClassVar, Generic, TypeVar, cast
import unicodedata

from attrs import define, field

from pyvider.cty.exceptions import (
    CtyMapValidationError,
    CtyTypeMismatchError,
    CtyValidationError,
    InvalidTypeError,
)
from pyvider.cty.path import CtyPath, KeyStep
from pyvider.cty.types.base import (
    CtyType,
    equal_iteratively,
    hash_iteratively,
    render_iteratively,
    usable_as_iteratively,
)
from pyvider.cty.validation.recursion import with_recursion_detection
from pyvider.cty.values import CtyValue
from pyvider.cty.values.frozen import FrozenDict

V = TypeVar("V")


@define(frozen=True, slots=True)
class CtyMap(CtyType[dict[str, V]], Generic[V]):
    ctype: ClassVar[str] = "map"
    _type_order: ClassVar[int] = 6
    element_type: CtyType[V] = field(kw_only=True)

    def __attrs_post_init__(self) -> None:
        if not isinstance(self.element_type, CtyType):
            raise InvalidTypeError(
                f"element_type must be a CtyType instance, got {type(self.element_type).__name__}"
            )

    def _short_circuit(self, value: object) -> tuple[CtyValue[dict[str, V]] | None, object]:
        """The answers that need no validation: a value already of this exact type,
        null, and unknown in either shape. Returns (answer, value-to-validate)."""
        if isinstance(value, CtyValue):
            if self.equal(value.type) and isinstance(value.value, dict):
                return cast(CtyValue[dict[str, V]], value), value  # Fast path
            if value.is_null:
                return CtyValue.null(self), value
            if value.is_unknown:
                return self.unknown_like(value), value
            value = value.value
        if value is None:
            return CtyValue.null(self), value
        return self.unknown_marker(value), value

    @with_recursion_detection
    def validate(self, value: object) -> CtyValue[dict[str, V]]:
        answer, value = self._short_circuit(value)
        if answer is not None:
            return answer

        if not isinstance(value, dict):
            raise CtyMapValidationError(f"Input must be a dictionary, got {type(value).__name__}.")
        validated_map: dict[str, CtyValue[V]] = {}
        for k, v in value.items():
            if not isinstance(k, str):
                raise CtyMapValidationError(
                    f"Map keys must be strings, but got key of type {type(k).__name__}"
                )

            normalized_key = unicodedata.normalize("NFC", k)

            try:
                validated_map[normalized_key] = self.element_type.validate(v)
            except CtyValidationError as e:
                new_path = CtyPath(steps=(KeyStep(normalized_key), *(e.path.steps if e.path else ())))
                raise CtyMapValidationError(e.message, value=v, path=new_path, original_exception=e) from e

        # Known map, undecided element -- see the note in CtyList.validate.
        return CtyValue(vtype=self, value=FrozenDict(validated_map))

    def get(
        self,
        map_value: CtyValue[dict[str, V]],
        key: object,
        default: CtyValue[V] | None = None,
    ) -> CtyValue[V]:
        if not isinstance(map_value, CtyValue) or not isinstance(map_value.type, CtyMap):
            raise CtyTypeMismatchError("get operation called on non-map CtyValue")
        if map_value.is_null or map_value.is_unknown:
            return default if default is not None else CtyValue.null(self.element_type)
        internal_dict = map_value.value
        if not isinstance(internal_dict, dict):
            raise CtyMapValidationError(
                f"Internal error: CtyValue of CtyMap type does not wrap a dict, got {type(internal_dict).__name__}"
            )

        normalized_key = unicodedata.normalize("NFC", str(key))
        internal_dict_cast = cast(dict[str, CtyValue[V]], internal_dict)
        result = internal_dict_cast.get(normalized_key)

        if result is not None:
            return self.element_type.validate(result)
        return default if default is not None else CtyValue.null(self.element_type)

    def equal(self, other: CtyType[Any]) -> bool:
        return equal_iteratively(self, other)

    def _structure(self) -> tuple[Any, tuple[Any, ...]] | None:
        return ((self.ctype,), (self.element_type,))

    def __eq__(self, other: object) -> bool:
        # Written out rather than left to attrs, which generates a field-by-field
        # comparison that recurses once per level of nesting. `equal` walks.
        # attrs' `auto_detect` leaves both of these alone because they are here.
        return self.equal(other) if isinstance(other, CtyType) else NotImplemented

    def __hash__(self) -> int:
        return hash_iteratively(self)

    def usable_as(self, other: CtyType[Any]) -> bool:
        return usable_as_iteratively(self, other)

    def _usable_shallow(self, other: Any) -> tuple[tuple[Any, Any], ...] | None:
        from pyvider.cty.types.structural import CtyDynamic

        if isinstance(other, CtyDynamic):
            return ()
        if not isinstance(other, CtyMap):
            return None
        return ((self.element_type, other.element_type),)

    def _to_wire_json(self) -> Any:
        return [self.ctype, self.element_type._to_wire_json()]

    def _render(self, children: list[str]) -> str:
        return f"map({children[0]})"

    def __str__(self) -> str:
        return render_iteratively(self)


# 🌊🪢🔚
