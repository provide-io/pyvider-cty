#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from __future__ import annotations

from collections.abc import Iterable
from typing import Any, ClassVar, cast
import unicodedata

from attrs import define, field

from pyvider.cty.conversion._utils import _attrs_to_dict_safe
from pyvider.cty.exceptions import (
    CtyAttributeValidationError,
    CtyTypeMismatchError,
    CtyValidationError,
    InvalidTypeError,
)
from pyvider.cty.path import CtyPath, GetAttrStep
from pyvider.cty.types.base import (
    CtyType,
    equal_iteratively,
    hash_iteratively,
    usable_as_iteratively,
)
from pyvider.cty.validation.recursion import with_recursion_detection
from pyvider.cty.values import CtyValue
from pyvider.cty.values.frozen import FrozenDict


def _to_frozenset(names: Iterable[str]) -> frozenset[str]:
    """Copy an iterable of attribute names into a frozenset."""
    return frozenset(names)


@define(frozen=True, slots=True)
class CtyObject(CtyType[dict[str, object]]):
    ctype: ClassVar[str] = "object"
    _type_order: ClassVar[int] = 7
    # Copied into a FrozenDict at construction, as go-cty's `cty.Object()` copies
    # its map: `__hash__` reads this, so a caller's dict that kept changing would
    # change the hash of a type already used as a key.
    attribute_types: dict[str, CtyType[Any]] = field(factory=dict, converter=FrozenDict)
    # `frozenset` itself would work at runtime, but attrs derives the __init__
    # parameter type from the converter, and the class's overloads resolve to
    # `Iterable[_T_co]` with an unbound TypeVar -- which rejects every concrete
    # argument, `frozenset[str]` included, under a strict type checker.
    optional_attributes: frozenset[str] = field(factory=frozenset, converter=_to_frozenset)

    def __attrs_post_init__(self) -> None:
        # The same two rules `validate` applies to a value's keys, applied to the
        # schema's names: a non-string name made `validate` fail later with a bare
        # `TypeError` from `unicodedata.normalize`, and two names that are one
        # attribute spelled two ways were two attributes that one input key filled.
        seen: dict[str, str] = {}
        for name, attr_type in self.attribute_types.items():
            if not isinstance(name, str):
                raise InvalidTypeError(
                    f"Object attribute names must be strings, but got name of type {type(name).__name__}",
                    invalid_type=name,
                )
            normalized = unicodedata.normalize("NFC", name)
            if normalized in seen:
                raise InvalidTypeError(
                    f"Attribute names {seen[normalized]!r} and {name!r} normalize to the same NFC string",
                    invalid_type=name,
                )
            seen[normalized] = name
            if not isinstance(attr_type, CtyType):
                raise InvalidTypeError(
                    f"Attribute '{name}' must be a CtyType, but got {type(attr_type).__name__}"
                )
        unknown_optionals = self.optional_attributes - set(self.attribute_types)
        if unknown_optionals:
            raise CtyAttributeValidationError(
                f"Unknown optional attributes: {', '.join(sorted(unknown_optionals))}"
            )

    def __repr__(self) -> str:
        # Provide a safe representation that doesn't recurse infinitely
        attr_keys = sorted(self.attribute_types.keys())
        optional_list = sorted(self.optional_attributes)
        if len(attr_keys) > 5:
            # Truncate long attribute lists
            attr_display = f"{attr_keys[:5]}...+{len(attr_keys) - 5} more"
        else:
            attr_display = str(attr_keys)

        optional_display = f", optional={optional_list}" if optional_list else ""
        return f"CtyObject(attributes={attr_display}{optional_display})"

    @with_recursion_detection
    def validate(self, value: object) -> CtyValue[dict[str, Any]]:  # noqa: C901
        if isinstance(value, CtyValue):
            if self.equal(value.type) and isinstance(value.value, dict):
                return cast(CtyValue[dict[str, Any]], value)  # Fast path
            if value.is_unknown:
                return self.unknown_like(value)
            if value.is_null:
                return CtyValue.null(self)
            value = value.value

        if value is None:
            return CtyValue.null(self)

        if (unknown_marker := self.unknown_marker(value)) is not None:
            return unknown_marker

        if hasattr(type(value), "__attrs_attrs__"):
            value = _attrs_to_dict_safe(value)
        if not isinstance(value, dict):
            raise CtyAttributeValidationError(
                f"Expected a dictionary for CtyObject, got {type(value).__name__}"
            )

        # Keys are strings (CtyMap already refused anything else; `str(k)` here
        # let `{1: ...}` satisfy an attribute named "1"), normalized to NFC so the
        # two spellings of an accented name are one attribute -- and two keys that
        # are the *same* attribute spelled two ways are refused rather than the
        # later one silently winning.
        normalized: dict[str, Any] = {}
        for raw_key, v in cast(dict[object, Any], value).items():
            if not isinstance(raw_key, str):
                raise CtyAttributeValidationError(
                    f"Object attribute names must be strings, but got key of type {type(raw_key).__name__}"
                )
            key = unicodedata.normalize("NFC", raw_key)
            if key in normalized:
                raise CtyAttributeValidationError(
                    f"Attribute names {raw_key!r} and {key!r} normalize to the same NFC string"
                )
            normalized[key] = v
        value = normalized

        validated_attrs: dict[str, CtyValue[Any]] = {}
        # Normalize attribute_types keys to NFC for consistent comparison
        all_expected_attrs = {unicodedata.normalize("NFC", k) for k in self.attribute_types}
        unknown = set(value.keys()) - all_expected_attrs
        if unknown:
            raise CtyAttributeValidationError(f"Unknown attributes: {', '.join(sorted(list(unknown)))}")

        for name, attr_type in self.attribute_types.items():
            # Normalize the attribute name for lookup in the NFC-normalized value dict
            normalized_name = unicodedata.normalize("NFC", name)
            path = CtyPath(steps=[GetAttrStep(name)])
            if normalized_name not in value:
                if name in self.optional_attributes:
                    validated_attrs[name] = CtyValue.null(attr_type)
                    continue
                raise CtyAttributeValidationError("Missing required attribute", value=None, path=path)

            raw_attr_value = value.get(normalized_name)
            try:
                # Marks on raw_attr_value survive this call. Leaf types get that
                # from @preserves_marks; the recursing types get it from inside
                # @with_recursion_detection, which restores marks on every exit
                # including its early ones. A type carrying neither would
                # silently drop them here.
                validated_attr = attr_type.validate(raw_attr_value)
            except CtyValidationError as e:
                new_path = CtyPath(steps=(GetAttrStep(name), *(e.path.steps if e.path else ())))
                raise CtyAttributeValidationError(
                    e.message,
                    value=raw_attr_value,
                    path=new_path,
                    original_exception=e,
                ) from e

            # A null is a value of every type, so there is deliberately no check
            # here that a non-optional attribute is non-null. go-cty has none --
            # nullability is not part of an object type there -- and Terraform
            # relies on it: everything crossing the provider protocol is
            # marshalled with `ImpliedType()`, which strips optional attributes
            # recursively, so the type a provider receives has none at all and
            # nulls arrive for unset attributes constantly. Restoring the check
            # here would reject state go-cty itself writes.
            #
            # Required-ness is therefore the *caller's* to enforce, and cannot be
            # delegated back: `optional_attributes` records optionality, which is
            # a wire-format concern, and nothing in a CtyObject records intent.
            # An earlier version of this comment named the one pyvider method
            # that does the check, which read as a guarantee and was not one --
            # four of pyvider's five validation paths reach this function without
            # passing through it. cty cannot make that promise on another
            # package's behalf, so it no longer appears to.
            validated_attrs[name] = validated_attr

        # Don't mark the entire object as unknown just because some fields are unknown
        # Terraform expects field-level unknown tracking, not object-level
        # The object itself is only unknown if explicitly passed as unknown
        return CtyValue(vtype=self, value=FrozenDict(validated_attrs), is_unknown=False)

    def get_attribute(self, obj_value: CtyValue[Any], name: str) -> CtyValue[Any]:
        if not isinstance(obj_value, CtyValue):
            raise CtyTypeMismatchError("get_attribute requires a CtyValue object")
        if not self.has_attribute(name):
            raise CtyAttributeValidationError(f"Object has no attribute '{name}'", path=CtyPath.get_attr(name))
        if obj_value.is_unknown:
            return CtyValue.unknown(self.attribute_types[name])
        if obj_value.is_null:
            return CtyValue.null(self.attribute_types[name])
        if isinstance(obj_value.value, dict):
            return obj_value.value.get(name, CtyValue.null(self.attribute_types[name]))  # type: ignore
        raise CtyTypeMismatchError("CtyObject value is not a dict")

    def has_attribute(self, name: str) -> bool:
        return name in self.attribute_types

    def equal(self, other: CtyType[Any]) -> bool:
        return equal_iteratively(self, other)

    def _structure(self) -> tuple[Any, tuple[Any, ...]] | None:
        # Sorted, because the token has to be the same for two equal objects and
        # declaration order is a property of how each was written.
        names = tuple(sorted(self.attribute_types))
        return (
            (self.ctype, names, self.optional_attributes),
            tuple(self.attribute_types[name] for name in names),
        )

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
        if not isinstance(other, CtyObject):
            return None
        other_attrs = set(other.attribute_types.keys())
        self_attrs = set(self.attribute_types.keys())
        if not other_attrs.issubset(self_attrs):
            return None
        self_required = self_attrs - self.optional_attributes
        other_required = other_attrs - other.optional_attributes
        if not other_required.issubset(self_required):
            return None
        return tuple(
            (self.attribute_types[name], other_type) for name, other_type in other.attribute_types.items()
        )

    def _to_wire_json(self) -> Any:
        # Sort attributes alphabetically to match go-cty behavior for consistent wire format
        attrs_json = {
            name: attr_type._to_wire_json() for name, attr_type in sorted(self.attribute_types.items())
        }
        if not self.optional_attributes:
            return [self.ctype, attrs_json]
        # go-cty's third element is the list of attributes that may be omitted.
        # Dropping it makes every attribute of every nested object REQUIRED as far as
        # terraform is concerned: a `map(object({run, shell, image}))` where only `run`
        # is meant to be needed rejects the configuration with `attribute "image" is
        # required`, and no provider-side change can fix that, because the constraint
        # is being sent from here.
        return [self.ctype, attrs_json, sorted(self.optional_attributes)]

    def is_primitive_type(self) -> bool:
        return False


# 🌊🪢🔚
