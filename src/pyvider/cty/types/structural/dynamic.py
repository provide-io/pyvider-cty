#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from __future__ import annotations

import json
from typing import Any, ClassVar, cast

from attrs import define

from pyvider.cty.exceptions import CtyValidationError, DeserializationError
from pyvider.cty.types.base import CtyType
from pyvider.cty.validation.recursion import with_recursion_detection
from pyvider.cty.values import CtyValue, UnknownValue


@define(frozen=True, slots=True)
class CtyDynamic(CtyType[object]):
    """Represents a dynamic type that can hold any CtyValue."""

    ctype: ClassVar[str] = "dynamic"
    _type_order: ClassVar[int] = 9

    @with_recursion_detection
    def validate(self, value: object) -> CtyValue[Any]:
        """
        Validates a raw Python value for a dynamic type. The result is always a
        CtyValue of type CtyDynamic, which wraps the inferred concrete value.
        """
        from pyvider.cty.conversion.raw_to_cty import infer_cty_type_from_raw
        from pyvider.cty.parser import parse_tf_type_to_ctytype

        if isinstance(value, CtyValue):
            if isinstance(value.type, CtyDynamic):
                return cast(CtyValue[Any], value)  # type: ignore[redundant-cast]
            return CtyValue(vtype=self, value=value)

        if value is None:
            return CtyValue.null(self)

        # An unknown that arrived without a type of its own. Terraform writes
        # exactly this for a dynamic-typed attribute whose value is unknown and
        # whose type is not yet determined -- `objchange` answers
        # `cty.UnknownVal(cty.DynamicPseudoType)` whenever the prior value was
        # unknown, and `jsondecode` of an unknown returns the same. There is
        # nothing here to infer a type from, and inference answered `dynamic`,
        # which called straight back into this method with the same marker until
        # the recursion detector stopped the whole validation -- flagging every
        # enclosing value unknown, so a resource's entire planned state was lost
        # for one unknown attribute. The root of a dynamic value never reached
        # this, because the codec handles it before `validate`; only a nested one
        # did.
        #
        # Answered totally unrefined, as go-cty does: its msgpack decoder ignores
        # the refinement map outright when the type is `DynamicPseudoType`
        # (`cty/msgpack/unknown.go`), and `Refine()` on `DynamicVal` echoes back
        # an unrefined `DynamicVal` (`cty/unknown_refinement.go`). A refinement
        # constrains a type, and this value does not have one yet.
        if isinstance(value, UnknownValue):
            return CtyValue.unknown(self)

        if isinstance(value, list) and len(value) == 2 and isinstance(value[0], bytes):
            try:
                type_spec = json.loads(value[0].decode("utf-8"))
                actual_type = parse_tf_type_to_ctytype(type_spec)
                concrete_value = actual_type.validate(value[1])
                return CtyValue(vtype=self, value=concrete_value)
            except json.JSONDecodeError as e:
                raise DeserializationError(
                    "Failed to decode dynamic value type spec from JSON during validation"
                ) from e
            except CtyValidationError as e:
                raise e

        inferred_type = infer_cty_type_from_raw(value)
        concrete_value = inferred_type.validate(value)
        return CtyValue(vtype=self, value=concrete_value)

    def equal(self, other: CtyType[Any]) -> bool:
        return isinstance(other, CtyDynamic)

    def usable_as(self, other: CtyType[Any]) -> bool:
        return isinstance(other, CtyDynamic)

    def _to_wire_json(self) -> Any:
        return self.ctype

    def is_dynamic_type(self) -> bool:
        return True

    def __str__(self) -> str:
        return "dynamic"


def unwrap_dynamic(value: CtyValue[Any], *, carry_marks: bool = False) -> CtyValue[Any]:
    """See through this package's `CtyDynamic` wrapper to the concrete value.

    go-cty has no such wrapper: a dynamic-typed *value* there is `cty.DynamicVal`,
    an unknown whose type is `DynamicPseudoType`, and a value that merely arrived
    through a dynamic-typed slot carries its own concrete type. Here a known
    dynamic value is a `CtyValue` whose type is `CtyDynamic` and whose payload is
    another `CtyValue`, so the wrapper has to be removed before any type check to
    ask go-cty's question rather than a different one. A value that is not a
    wrapper is returned as itself, identity preserved.

    What happens to the *wrapper's* marks is the caller's decision, and it is
    made explicit here because four private copies of this loop once disagreed
    about it silently:

    - `carry_marks=False` (the default) is the structural reading: the wrapper
      is transparent, and its marks stay where they are. `walk` wants this --
      it re-wraps a rebuilt value in the original wrapper, marks and all, so
      carrying them down would mark the same value twice; `flatten` wants it for
      the same reason, its result already carries the deep union; equality
      strips marks before comparing and has nothing to carry.

    - `carry_marks=True` moves each removed wrapper's marks onto what it
      wrapped. The function framework wants this for an *argument*: in go-cty
      the same marks would already be on the value itself, so dropping them
      would declassify a sensitive value merely for having arrived through a
      dynamic slot -- invisible for a parameter that strips marks, and a live
      leak for one that declares `allow_marked`.
    """
    while isinstance(value.type, CtyDynamic) and isinstance(value.value, CtyValue):
        wrapper_marks = value.marks if carry_marks else None
        value = value.value
        if wrapper_marks:
            value = value.with_marks(wrapper_marks)
    return value


# 🌊🪢🔚
