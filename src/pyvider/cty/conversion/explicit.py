#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal
from functools import lru_cache
from typing import Any, cast

from provide.foundation.errors import error_boundary

from pyvider.cty.config.defaults import (
    ERR_CANNOT_CONVERT_BOOL_CASE,
    ERR_CANNOT_CONVERT_GENERAL,
    ERR_CANNOT_CONVERT_TO_BOOL,
    ERR_CANNOT_CONVERT_VALIDATION,
    ERR_CAPSULE_CANNOT_CONVERT,
    ERR_CUSTOM_CONVERTER_NON_CTYVALUE,
    ERR_CUSTOM_CONVERTER_WRONG_TYPE,
    ERR_DYNAMIC_VALUE_NOT_CTYVALUE,
    ERR_MISSING_REQUIRED_ATTRIBUTE,
    ERR_SOURCE_OBJECT_NOT_DICT,
)
from pyvider.cty.exceptions import CtyConversionError, CtyValidationError
from pyvider.cty.types import (
    CtyBool,
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
from pyvider.cty.values import CtyValue

"""
Implementation of the public `convert` and `unify` functions for explicit
CTY-to-CTY type conversion.
"""


def _number_to_string(raw: Any) -> str:
    """A number as go-cty renders it: plain decimal, never exponent notation.

    go-cty formats with `big.Float.Text('f', -1)`, which has no exponent form
    and no trailing zeros. `str(Decimal)` has both -- a number that arrived as
    `1e2` stringified as `"1E+2"` where go-cty says `"100"`, and a `Decimal`
    keeps the trailing zeros of `1.50` where a `big.Float` never had them.
    `normalize()` strips the zeros, and `format(..., "f")` undoes the exponent
    that normalizing an integral value introduces.
    """
    if isinstance(raw, Decimal) and raw.is_finite():
        return format(raw.normalize(), "f")
    return str(raw)


def convert(value: CtyValue[Any], target_type: CtyType[Any]) -> CtyValue[Any]:  # noqa: C901
    """
    Converts a CtyValue to a new CtyValue of the target CtyType.
    """
    with error_boundary(
        context={
            "operation": "cty_value_conversion",
            "source_type": str(value.type),
            "target_type": str(target_type),
            "value_is_null": value.is_null,
            "value_is_unknown": value.is_unknown,
        }
    ):
        # Early exit cases
        if value.type.equal(target_type):
            return value

        if value.is_null:
            return CtyValue.null(target_type)
        if value.is_unknown:
            return CtyValue.unknown(target_type)

        # Capsule conversion with operations
        if isinstance(value.type, CtyCapsuleWithOps) and value.type.convert_fn:
            result = value.type.convert_fn(value.value, target_type)
            if result is None:
                error_message = ERR_CAPSULE_CANNOT_CONVERT.format(
                    value_type=value.type, target_type=target_type
                )
                raise CtyConversionError(
                    error_message,
                    source_value=value,
                    target_type=target_type,
                )
            if not isinstance(result, CtyValue):
                error_message = ERR_CUSTOM_CONVERTER_NON_CTYVALUE
                raise CtyConversionError(
                    error_message,
                    source_value=value,
                    target_type=target_type,
                )
            if not result.type.equal(target_type):
                error_message = ERR_CUSTOM_CONVERTER_WRONG_TYPE.format(
                    result_type=result.type, target_type=target_type
                )
                raise CtyConversionError(
                    error_message,
                    source_value=value,
                    target_type=target_type,
                )
            return result.with_marks(set(value.marks))

        # Dynamic type handling
        if isinstance(value.type, CtyDynamic):
            if not isinstance(value.value, CtyValue):
                error_message = ERR_DYNAMIC_VALUE_NOT_CTYVALUE
                raise CtyConversionError(error_message, source_value=value)
            return convert(value.value, target_type)

        if isinstance(target_type, CtyDynamic):
            return value.with_marks(set(value.marks))

        # String conversion. go-cty's table (cty/convert/conversion_primitive.go)
        # defines exactly two conversions to string -- from number and from bool
        # -- and nothing else. This used to convert *anything* non-capsule with
        # `str(raw)`, and `raw` for a collection is the internal tuple of
        # CtyValues, so `convert(list, string)` returned the text of a repr:
        # "(CtyValue(vtype=CtyString(), value='a', ...),)". A plausible-looking
        # string, headed for Terraform state.
        if isinstance(target_type, CtyString):
            if isinstance(value.type, CtyBool):
                text = "true" if value.value else "false"
                return CtyValue(target_type, text).with_marks(set(value.marks))
            if isinstance(value.type, CtyNumber):
                return CtyValue(target_type, _number_to_string(value.value)).with_marks(set(value.marks))

        # Number conversion. Only from a string, or from a number of course.
        # This used to hand the payload to CtyNumber().validate, which accepts a
        # bool because a Python bool *is* an int -- so `convert(true, number)`
        # returned 1 where go-cty has no bool-to-number conversion at all.
        if isinstance(target_type, CtyNumber) and isinstance(value.type, CtyString | CtyNumber):
            try:
                validated = target_type.validate(value.value)
                return validated.with_marks(set(value.marks))
            except CtyValidationError as e:
                error_message = ERR_CANNOT_CONVERT_VALIDATION.format(
                    value_type=value.type, target_type=target_type, message=e.message
                )
                raise CtyConversionError(
                    error_message,
                    source_value=value,
                    target_type=target_type,
                ) from e

        # Boolean conversion. go-cty accepts "true"/"1" and "false"/"0", and
        # refuses any other casing with a message that says so; this lowercased
        # first, so "TRUE" converted here and is refused there.
        if isinstance(target_type, CtyBool):
            if isinstance(value.type, CtyString):
                text = str(value.value)
                if text in ("true", "1"):
                    return CtyValue(target_type, True).with_marks(set(value.marks))
                if text in ("false", "0"):
                    return CtyValue(target_type, False).with_marks(set(value.marks))
                lowered = text.lower()
                if lowered in ("true", "false"):
                    error_message = ERR_CANNOT_CONVERT_BOOL_CASE.format(text=text, lowered=lowered)
                    raise CtyConversionError(
                        error_message,
                        source_value=value,
                        target_type=target_type,
                    )
            error_message = ERR_CANNOT_CONVERT_TO_BOOL.format(value_type=value.type)
            raise CtyConversionError(
                error_message,
                source_value=value,
                target_type=target_type,
            )

        # Collection conversions
        if isinstance(target_type, CtySet) and isinstance(value.type, CtyList | CtyTuple):
            converted: CtyValue[Any] = target_type.validate(value.value).with_marks(set(value.marks))
            return converted

        if isinstance(target_type, CtyList) and isinstance(value.type, CtySet | CtyTuple):
            converted = target_type.validate(value.value).with_marks(set(value.marks))
            return converted

        # A list of anything widens to a list of dynamic. There is deliberately
        # no same-element-type case: `CtyList.equal` *is* element-type equality,
        # so two lists with equal element types are equal lists and the identity
        # exit at the top of this function has already returned. The branch that
        # used to test for it could not run.
        if (
            isinstance(target_type, CtyList)
            and isinstance(value.type, CtyList)
            and isinstance(target_type.element_type, CtyDynamic)
        ):
            converted = target_type.validate(value.value).with_marks(set(value.marks))
            return converted

        # Object conversion
        if isinstance(target_type, CtyObject) and isinstance(value.type, CtyObject):
            new_attrs = {}
            source_attrs = value.value
            if not isinstance(source_attrs, dict):
                error_message = ERR_SOURCE_OBJECT_NOT_DICT
                raise CtyConversionError(error_message)
            source_attrs_dict = cast(dict[str, CtyValue[Any]], source_attrs)
            for name, target_attr_type in target_type.attribute_types.items():
                if name in source_attrs_dict:
                    new_attrs[name] = convert(source_attrs_dict[name], target_attr_type)
                elif name in target_type.optional_attributes:
                    new_attrs[name] = CtyValue.null(target_attr_type)
                else:
                    error_message = ERR_MISSING_REQUIRED_ATTRIBUTE.format(name=name)
                    raise CtyConversionError(error_message)
            converted = target_type.validate(new_attrs).with_marks(set(value.marks))
            return converted

        # Fallback - no conversion available
        error_message = ERR_CANNOT_CONVERT_GENERAL.format(value_type=value.type, target_type=target_type)
        raise CtyConversionError(
            error_message,
            source_value=value,
            target_type=target_type,
        )


@lru_cache(maxsize=1024)
def _unify_frozen(types: frozenset[CtyType[Any]]) -> CtyType[Any]:
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
        # `obj_types` cannot be empty here: an empty `type_set` returned above,
        # and the guard on this branch says every remaining member is a
        # CtyObject. Filtering again is what convinces the type checker, not a
        # case that can occur.
        obj_types = [t for t in type_set if isinstance(t, CtyObject)]

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


def unify(types: Iterable[CtyType[Any]]) -> CtyType[Any]:
    """
    Finds a single common CtyType that all of the given types can convert to.
    This is a wrapper that enables caching by converting input to a frozenset.
    """
    return _unify_frozen(frozenset(types))


# 🌊🪢🔚
