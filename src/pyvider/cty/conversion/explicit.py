"""
Implementation of the public `convert` and `unify` functions for explicit
CTY-to-CTY type conversion.
"""

from collections.abc import Iterable
from typing import Any

from ..exceptions import CtyConversionError, CtyValidationError
from ..types import (
    CtyBool,
    CtyCapsule,
    CtyCapsuleWithOps,
    CtyDynamic,
    CtyList,
    CtyNumber,
    CtyObject,
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

    if isinstance(value.type, CtyCapsuleWithOps) and value.type.convert_fn:
        result = value.type.convert_fn(value.value, target_type)
        if result is None:
            raise CtyConversionError(
                f"Capsule type {value.type} cannot be converted to {target_type}",
                source_value=value,
                target_type=target_type,
            )
        if not isinstance(result, CtyValue):
            raise CtyConversionError(
                "Custom capsule converter returned a non-CtyValue object",
                source_value=value,
                target_type=target_type,
            )
        if not result.type.equal(target_type):
            raise CtyConversionError(
                f"Custom capsule converter returned a value of the wrong type "
                f"(got {result.type}, want {target_type})",
                source_value=value,
                target_type=target_type,
            )
        return result.with_marks(value.marks)

    if isinstance(target_type, CtyDynamic):
        return value.with_marks(value.marks)

    if isinstance(target_type, CtyString):
        if not isinstance(value.type, CtyCapsule):
            raw = value.value
            if isinstance(raw, bool):
                new_val = "true" if raw else "false"
            else:
                new_val = str(raw)
            return CtyValue(target_type, new_val).with_marks(value.marks)

    if isinstance(target_type, CtyNumber):
        try:
            validated = target_type.validate(value.value)
            return validated.with_marks(value.marks)
        except CtyValidationError as e:
            raise CtyConversionError(
                f"Cannot convert {value.type} to {target_type}: {e.message}",
                source_value=value,
                target_type=target_type,
            ) from e

    if isinstance(target_type, CtyBool):
        if isinstance(value.type, CtyString):
            s = str(value.value).lower()
            if s == "true":
                return CtyValue(target_type, True).with_marks(value.marks)
            if s == "false":
                return CtyValue(target_type, False).with_marks(value.marks)
        raise CtyConversionError(
            f"Cannot convert {value.type} to bool",
            source_value=value,
            target_type=target_type,
        )

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

    if all(isinstance(t, CtyList) for t in type_set):
        element_types = {t.element_type for t in type_set}
        unified_element_type = unify(element_types)
        return CtyList(element_type=unified_element_type)

    if all(isinstance(t, CtyObject) for t in type_set):
        if any(not t.attribute_types for t in type_set):
            return CtyObject({})

        all_object_attrs = [set(t.attribute_types.keys()) for t in type_set]
        common_keys = set.intersection(*all_object_attrs)

        if not common_keys:
            return CtyDynamic()

        all_optional_keys = set().union(*(t.optional_attributes for t in type_set))
        unified_attrs = {}
        for key in common_keys:
            attr_types_to_unify = [t.attribute_types[key] for t in type_set]
            unified_attrs[key] = unify(attr_types_to_unify)
        
        final_optional_attrs = common_keys.intersection(all_optional_keys)

        return CtyObject(
            attribute_types=unified_attrs,
            optional_attributes=frozenset(final_optional_attrs),
        )

    return CtyDynamic()
