"""
Implementation of the public `convert` and `unify` functions for explicit
CTY-to-CTY type conversion.
"""

from collections.abc import Iterable
from typing import Any

from ..exceptions import CtyConversionError, CtyValidationError
from ..types import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyNumber,
    CtySet,
    CtyString,
    CtyTuple,
    CtyType,
)
from ..values import CtyValue


def convert(value: CtyValue, target_type: CtyType) -> CtyValue[Any]:
    """
    Converts a CtyValue to a new CtyValue of the target CtyType.
    """
    if value.type.equal(target_type):
        return value

    if value.is_null:
        return CtyValue.null(target_type)
    if value.is_unknown:
        return CtyValue.unknown(target_type)

    # Conversion to Dynamic is always a pass-through of the original value
    if isinstance(target_type, CtyDynamic):
        return value.with_marks(value.marks)

    # Primitive conversions
    if isinstance(target_type, CtyString):
        raw = value.value
        if isinstance(raw, bool):
            new_val = "true" if raw else "false"
        else:
            new_val = str(raw)
        return CtyValue(target_type, new_val).with_marks(value.marks)

    if isinstance(target_type, CtyNumber):
        try:
            # Rely on the target type's own validation logic for conversion
            validated = target_type.validate(value.value)
            return validated.with_marks(value.marks)
        except CtyValidationError as e:
            raise CtyConversionError(
                f"Cannot convert {value.type} to {target_type}: {e.message}",
                source_value=value,
                target_type=target_type,
            ) from e

    if isinstance(target_type, CtyBool):
        # Explicit bool conversion is stricter than validation
        if isinstance(value.type, CtyString):
            s = str(value.value).lower()
            if s == "true":
                return CtyValue(target_type, True).with_marks(value.marks)
            if s == "false":
                return CtyValue(target_type, False).with_marks(value.marks)
        # Any other conversion to bool is invalid
        raise CtyConversionError(
            f"Cannot convert {value.type} to bool",
            source_value=value,
            target_type=target_type,
        )

    # Collection conversions
    if isinstance(target_type, CtySet) and isinstance(value.type, CtyList | CtyTuple):
        return target_type.validate(value.value).with_marks(value.marks)

    if isinstance(target_type, CtyList) and isinstance(value.type, CtySet | CtyTuple):
        return target_type.validate(value.value).with_marks(value.marks)

    if isinstance(target_type, CtyList) and isinstance(value.type, CtyList):
        if target_type.element_type.equal(value.type.element_type):
            return value
        if isinstance(target_type.element_type, CtyDynamic):
            return target_type.validate(value.value).with_marks(value.marks)

    raise CtyConversionError(
        f"Cannot convert from {value.type} to {target_type}",
        source_value=value,
        target_type=target_type,
    )


def unify(types: Iterable[CtyType]) -> CtyType[Any]:
    """
    Finds a single common CtyType that all of the given types can convert to.
    """
    type_set = set(types)
    if not type_set:
        return CtyDynamic()
    if len(type_set) == 1:
        return type_set.pop()

    # Check for list unification
    if all(isinstance(t, CtyList) for t in type_set):
        element_types = {t.element_type for t in type_set}
        unified_element_type = unify(element_types)
        return CtyList(element_type=unified_element_type)

    # Fallback for all other cases
    return CtyDynamic()
