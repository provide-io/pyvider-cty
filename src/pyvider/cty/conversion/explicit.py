#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from __future__ import annotations

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
    ERR_MAP_MISSING_REQUIRED_ATTRIBUTE,
    ERR_MISSING_REQUIRED_ATTRIBUTE,
    ERR_SOURCE_OBJECT_NOT_DICT,
    ERR_TUPLE_LENGTH_MISMATCH,
)
from pyvider.cty.exceptions import CtyConversionError, CtyValidationError
from pyvider.cty.types import (
    CtyBool,
    CtyCapsule,
    CtyCapsuleWithOps,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
    CtyTuple,
    CtyType,
)
from pyvider.cty.values import CtyValue

"""
Implementation of the public `convert` function and its type-level companion
`can_convert_unsafe`, for explicit CTY-to-CTY conversion. Unification lives in
`pyvider.cty.conversion.unify` and is defined in terms of both.
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


def _ordered_elements(value: CtyValue[Any]) -> list[CtyValue[Any]]:
    """A sequence value's elements, as CtyValues, in a stable order.

    A set carries its canonical order in the payload itself, so it needs no
    sorting here. It used to hold a frozenset, whose iteration order varies
    between processes, and the sort below was what stopped converting the same
    set to a list twice from producing two different lists. The `frozenset`
    branch is kept because a CtyValue can still be hand-built around one.

    Elements are validated against the source's own element type on the way
    out, because a CtyValue can legitimately be built around a raw Python
    payload and the caller here needs values it can convert one at a time.
    """
    source_type = value.type
    element_type: CtyType[Any] | None = None
    if isinstance(source_type, CtyList | CtySet):
        element_type = source_type.element_type

    raw = value.value
    elements = sorted(raw, key=_sort_key) if isinstance(raw, frozenset) else list(cast(tuple[Any, ...], raw))
    return [
        element
        if isinstance(element, CtyValue)
        else (element_type.validate(element) if element_type is not None else CtyDynamic().validate(element))
        for element in elements
    ]


def _sort_key(element: Any) -> Any:
    return element._canonical_sort_key() if isinstance(element, CtyValue) else (0, str(element))


@lru_cache(maxsize=1024)
def can_convert_unsafe(source: CtyType[Any], target: CtyType[Any]) -> bool:  # noqa: C901
    """Whether `convert` might succeed from `source` to `target`, on types alone.

    go-cty's `GetConversionUnsafe` as a predicate. "Unsafe" is go-cty's word for
    a conversion that depends on the value as well as the type: every string has
    a number type available to it, but only some strings are numbers. Type
    unification asks this question, so it must answer for exactly the
    conversions `convert` performs -- a divergence either way means unification
    proposes a type that cannot be reached, or refuses one that can.
    """
    if isinstance(target, CtyDynamic) or isinstance(source, CtyDynamic):
        return True
    if source.equal(target):
        return True
    if isinstance(source, CtyCapsuleWithOps) and source.convert_fn is not None:
        # Whether a capsule converts is its own `convert_fn`'s decision, and
        # that needs the value. Optimistic, matching the "unsafe" contract.
        return True
    if isinstance(target, CtyCapsuleWithOps) and target.convert_to_fn is not None:
        # The other direction: a capsule declaring `convert_to_fn` can receive a
        # value. go-cty splits ConversionFrom and ConversionTo for exactly this,
        # and without the second half a capsule can be converted out of and
        # never into -- which is also what blocks capsule-to-capsule.
        return True
    if isinstance(source, CtyCapsule) or isinstance(target, CtyCapsule):
        return False

    if isinstance(target, CtyString):
        return isinstance(source, CtyBool | CtyNumber)
    if isinstance(target, CtyNumber | CtyBool):
        return isinstance(source, CtyString)

    if isinstance(target, CtyList | CtySet):
        if isinstance(source, CtyList | CtySet):
            return can_convert_unsafe(source.element_type, target.element_type)
        if isinstance(source, CtyTuple):
            return all(can_convert_unsafe(element, target.element_type) for element in source.element_types)
        return False

    if isinstance(target, CtyTuple):
        if isinstance(source, CtyTuple) and len(source.element_types) == len(target.element_types):
            return all(
                can_convert_unsafe(have, want)
                for have, want in zip(source.element_types, target.element_types, strict=True)
            )
        return False

    if isinstance(target, CtyMap):
        if isinstance(source, CtyMap):
            return can_convert_unsafe(source.element_type, target.element_type)
        if isinstance(source, CtyObject):
            return all(
                can_convert_unsafe(attribute, target.element_type)
                for attribute in source.attribute_types.values()
            )
        return False

    if isinstance(target, CtyObject) and isinstance(source, CtyMap):
        # Unsafe only, and go-cty says why: "we don't know if all the map keys
        # will correspond to object attributes". Which keys a map holds is a
        # property of the value, so the type can only be optimistic. A required
        # attribute whose type the map's elements cannot reach still rules it
        # out here; an optional one does not, because the map may simply not
        # carry that key.
        return all(
            can_convert_unsafe(source.element_type, want)
            for name, want in target.attribute_types.items()
            if name not in target.optional_attributes
        )

    if isinstance(target, CtyObject) and isinstance(source, CtyObject):
        # Unsafe conversion permits a target that is a *subset* of the source:
        # dropping attributes nobody asked for is legal. Unification is
        # deliberately stricter and does not use this -- see `_unify_objects`.
        for name, want in target.attribute_types.items():
            have = source.attribute_types.get(name)
            if have is None:
                if name not in target.optional_attributes:
                    return False
            elif not can_convert_unsafe(have, want):
                return False
        return True

    return False


def _collection_target(
    target: CtyList[Any] | CtySet[Any], source: CtyList[Any] | CtySet[Any] | CtyTuple
) -> CtyList[Any] | CtySet[Any]:
    """The collection type a conversion actually produces.

    A `dynamic` element type in the *target* is not a request for a collection
    of dynamics -- it is the absence of a constraint, and go-cty resolves it
    from the source rather than storing it. `list(any)` given a `list(string)`
    yields a `list(string)`, because converting each element to dynamic is the
    identity and `ListVal` then infers the element type from what it was handed.

    Producing `list(dynamic)` instead puts a *type constraint* in a value's
    type, which is a distinction go-cty is careful about, and it reaches the
    wire: a provider returning `list(any)` would tell Terraform nothing about
    its elements.
    """
    if not isinstance(target.element_type, CtyDynamic):
        return target

    if isinstance(source, CtyTuple):
        if not source.element_types:
            # Nothing to infer from. go-cty keeps the dynamic here too.
            return target
        # go-cty unifies the tuple's element types (conversion_collection.go's
        # conversionTupleToList), and refuses when they have no common type.
        from pyvider.cty.conversion.unify import unify

        unified = unify(list(source.element_types))
        if unified is None or isinstance(unified, CtyDynamic):
            return target
        return type(target)(element_type=unified)

    return type(target)(element_type=source.element_type)


def _without_optional(cty_type: CtyType[Any]) -> CtyType[Any]:
    """go-cty's `Type.WithoutOptionalAttributesDeep`.

    Optionality is a property of a type *constraint* -- "you need not supply
    this" -- and says nothing about a value, which either has the attribute or
    has null for it. go-cty is careful never to let one reach a value's type,
    and `Convert` strips it both when deciding a conversion is unnecessary and
    when building the result.

    It matters on the wire: a schema declaring `b` optional and a value whose
    type still says so are different documents, and the second is a type
    constraint claiming to be a value.
    """
    match cty_type:
        case CtyObject():
            return CtyObject(
                attribute_types={
                    name: _without_optional(attribute) for name, attribute in cty_type.attribute_types.items()
                },
                optional_attributes=frozenset(),
            )
        case CtyList():
            return CtyList(element_type=_without_optional(cty_type.element_type))
        case CtySet():
            return CtySet(element_type=_without_optional(cty_type.element_type))
        case CtyMap():
            return CtyMap(element_type=_without_optional(cty_type.element_type))
        case CtyTuple():
            return CtyTuple(element_types=tuple(_without_optional(e) for e in cty_type.element_types))
    return cty_type


def _map_to_object(value: CtyValue[Any], target_type: CtyObject) -> CtyValue[Any]:
    """go-cty's `conversionMapToObject`."""
    items = cast(dict[str, CtyValue[Any]], value.value or {})
    attributes: dict[str, CtyValue[Any]] = {}
    for name, want in target_type.attribute_types.items():
        if name in items:
            attributes[name] = convert(items[name], want)
        elif name in target_type.optional_attributes:
            attributes[name] = CtyValue.null(want)
        else:
            raise CtyConversionError(
                ERR_MAP_MISSING_REQUIRED_ATTRIBUTE.format(name=name),
                source_value=value,
                target_type=target_type,
            )
    concrete = cast(CtyObject, _without_optional(target_type))
    return cast("CtyValue[Any]", concrete.validate(attributes).with_marks(set(value.marks)))


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
        # Early exit cases. Compared against the target with its optionality
        # stripped, which is go-cty's `in.Type().Equals(want.WithoutOptional
        # AttributesDeep())`: a value whose type already matches needs no
        # conversion, and whether the *constraint* marked an attribute optional
        # has no bearing on that.
        if value.type.equal(target_type) or value.type.equal(_without_optional(target_type)):
            return value

        # A null or an unknown still has to be *convertible*: nullness is not
        # part of a cty type, so "null of list(string)" is no more a string
        # than a populated list is. This used to return a null of the target
        # type for any target at all, so `tostring(null_of_list)` produced a
        # null string where go-cty refuses the conversion outright.
        if value.is_null or value.is_unknown:
            if not can_convert_unsafe(value.type, target_type):
                error_message = ERR_CANNOT_CONVERT_GENERAL.format(
                    value_type=value.type, target_type=target_type
                )
                raise CtyConversionError(error_message, source_value=value, target_type=target_type)
            return CtyValue.null(target_type) if value.is_null else CtyValue.unknown(target_type)

        # Into a capsule that declares how to receive a value. The target's
        # `ConversionTo` is tried before the source's `ConversionFrom`, which is
        # go-cty's order (`convert/conversion.go:172-184`) and matters only when
        # both ends are capsules -- there, the destination decides first.
        if isinstance(target_type, CtyCapsuleWithOps) and target_type.convert_to_fn:
            received = target_type.convert_to_fn(value, target_type)
            if received is not None:
                return target_type.validate(received)

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

        # Collection conversions, element by element. `target_type.validate` on
        # its own was not enough: it checks each element against the element
        # type rather than converting it, so `list(number)` to `list(string)`
        # -- exactly what unification asks for once it can widen primitives --
        # was refused. A conversion `can_convert_unsafe` admits has to be one
        # `convert` performs, or unification promises a type nothing can reach.
        if isinstance(target_type, CtySet | CtyList) and isinstance(value.type, CtyList | CtySet | CtyTuple):
            collection = _collection_target(target_type, value.type)
            element_type = collection.element_type
            elements = [convert(element, element_type) for element in _ordered_elements(value)]
            converted: CtyValue[Any] = collection.validate(elements).with_marks(set(value.marks))
            return converted

        # Tuple *from a tuple only*. go-cty's table has no list-to-tuple or
        # set-to-tuple conversion at all -- a collection's length is a property
        # of the value and a tuple's is part of its type, so the conversion
        # would be one that type-checking cannot decide. This accepted both,
        # while `can_convert_unsafe` above said it could not, so `convert`
        # performed a conversion its own predicate denied: unification could
        # refuse a type that `convert` would in fact have reached.
        if isinstance(target_type, CtyTuple) and isinstance(value.type, CtyTuple):
            source_elements = _ordered_elements(value)
            if len(source_elements) != len(target_type.element_types):
                error_message = ERR_TUPLE_LENGTH_MISMATCH.format(
                    got=len(source_elements), want=len(target_type.element_types)
                )
                raise CtyConversionError(error_message, source_value=value, target_type=target_type)
            converted = target_type.validate(
                tuple(
                    convert(element, element_type)
                    for element, element_type in zip(source_elements, target_type.element_types, strict=True)
                )
            ).with_marks(set(value.marks))
            return converted

        # An object is map-shaped data that happens to carry per-attribute
        # types, so it converts to a map whose element type every attribute
        # reaches. Unification leans on this whenever two objects have different
        # attribute names.
        if isinstance(target_type, CtyMap) and isinstance(value.type, CtyMap | CtyObject):
            source_items = value.value
            if not isinstance(source_items, dict):
                error_message = ERR_SOURCE_OBJECT_NOT_DICT
                raise CtyConversionError(error_message)
            items = cast(dict[str, CtyValue[Any]], source_items)
            converted = target_type.validate(
                {name: convert(item, target_type.element_type) for name, item in items.items()}
            ).with_marks(set(value.marks))
            return converted

        # A map converts to an object, and only unsafely: which keys a map holds
        # is a property of the value, so the type cannot promise the attributes
        # will be there. Keys the object does not declare are *skipped* rather
        # than refused, a missing optional attribute becomes null, and a missing
        # required one is the error. All three are go-cty's rules
        # (`conversionMapToObject`), and without any of it a provider decoding
        # `map(string)` config into a schema object was simply refused.
        if isinstance(target_type, CtyObject) and isinstance(value.type, CtyMap):
            return _map_to_object(value, target_type)

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
            concrete = cast(CtyObject, _without_optional(target_type))
            converted = concrete.validate(new_attrs).with_marks(set(value.marks))
            return converted

        # Fallback - no conversion available
        error_message = ERR_CANNOT_CONVERT_GENERAL.format(value_type=value.type, target_type=target_type)
        raise CtyConversionError(
            error_message,
            source_value=value,
            target_type=target_type,
        )


# 🌊🪢🔚
