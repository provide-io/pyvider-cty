"""
Implementation of the public `convert` and `unify` functions for explicit
CTY-to-CTY type conversion.
"""

from collections.abc import Iterable
from functools import lru_cache
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


def convert(value: "CtyValue[Any]", target_type: "CtyType[Any]") -> "CtyValue[Any]":  # noqa: C901
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
        return result.with_marks(set(value.marks))

    if isinstance(value.type, CtyDynamic):
        if not isinstance(value.value, CtyValue):
            raise CtyConversionError(
                "Dynamic value does not contain a CtyValue", source_value=value
            )
        return convert(value.value, target_type)

    if isinstance(target_type, CtyDynamic):
        return value.with_marks(set(value.marks))

    if isinstance(target_type, CtyString) and not isinstance(value.type, CtyCapsule):
        raw = value.value
        if isinstance(raw, bool):
            new_val = "true" if raw else "false"
        else:
            new_val = str(raw)
        return CtyValue(target_type, new_val).with_marks(set(value.marks))

    if isinstance(target_type, CtyNumber):
        try:
            validated = target_type.validate(value.value)
            return validated.with_marks(set(value.marks))
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
                return CtyValue(target_type, True).with_marks(set(value.marks))
            if s == "false":
                return CtyValue(target_type, False).with_marks(set(value.marks))
        raise CtyConversionError(
            f"Cannot convert {value.type} to bool",
            source_value=value,
            target_type=target_type,
        )

    if isinstance(target_type, CtySet) and isinstance(value.type, CtyList | CtyTuple):
        return target_type.validate(value.value).with_marks(set(value.marks))

    if isinstance(target_type, CtyList) and isinstance(value.type, CtySet | CtyTuple):
        return target_type.validate(value.value).with_marks(set(value.marks))

    if isinstance(target_type, CtyList) and isinstance(value.type, CtyList):
        if target_type.element_type.equal(value.type.element_type):
            return value
        if isinstance(target_type.element_type, CtyDynamic):
            return target_type.validate(value.value).with_marks(set(value.marks))

    if isinstance(target_type, CtyObject) and isinstance(value.type, CtyObject):
        new_attrs = {}
        source_attrs = value.value
        if not isinstance(source_attrs, dict):
            raise CtyConversionError("Source object is not a dictionary")
        for name, target_attr_type in target_type.attribute_types.items():
            if name in source_attrs:
                new_attrs[name] = convert(source_attrs[name], target_attr_type)
            elif name in target_type.optional_attributes:
                new_attrs[name] = CtyValue.null(target_attr_type)
            else:
                raise CtyConversionError(
                    f"Missing required attribute '{name}' for conversion"
                )
        return target_type.validate(new_attrs).with_marks(set(value.marks))

    raise CtyConversionError(
        f"Cannot convert from {value.type} to {target_type}",
        source_value=value,
        target_type=target_type,
    )


@lru_cache(maxsize=1024)
def _unify_frozen(types: frozenset["CtyType[Any]"]) -> "CtyType[Any]":
    """
    Memoized implementation of unify; operates on a hashable frozenset.
    """
    type_set = set(types)
    if not type_set:
        return CtyDynamic()
    if len(type_set) == 1:
        return type_set.pop()

    if CtyDynamic() in type_set:
        return CtyDynamic()

    if all(isinstance(t, CtyList) for t in type_set):
        element_types = {t.element_type for t in type_set if isinstance(t, CtyList)}
        unified_element_type = unify(element_types)
        return CtyList(element_type=unified_element_type)

    if all(isinstance(t, CtyObject) for t in type_set):
        obj_types = [t for t in type_set if isinstance(t, CtyObject)]
        if not obj_types:
            return CtyDynamic()

        key_sets = [set(t.attribute_types.keys()) for t in obj_types]
        # If key sets are not identical, unification results in CtyDynamic.
        if not all(ks == key_sets[0] for ks in key_sets):
            return CtyDynamic()

        common_keys = key_sets[0]
        unified_attrs = {}
        unified_optionals = set()

        for key in common_keys:
            attr_types_to_unify = {t.attribute_types[key] for t in obj_types}
            unified_attrs[key] = unify(attr_types_to_unify)
            if any(key in t.optional_attributes for t in obj_types):
                unified_optionals.add(key)

        return CtyObject(
            attribute_types=unified_attrs,
            optional_attributes=frozenset(unified_optionals),  # type: ignore
        )

    return CtyDynamic()


def unify(types: Iterable["CtyType[Any]"]) -> "CtyType[Any]":
    """
    Finds a single common CtyType that all of the given types can convert to.
    This is a wrapper that enables caching by converting input to a frozenset.
    """
    return _unify_frozen(frozenset(types))
