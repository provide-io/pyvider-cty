#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from __future__ import annotations

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
from pyvider.cty.types.base import CtyType, equal_iteratively
from pyvider.cty.validation.recursion import with_recursion_detection
from pyvider.cty.values import CtyValue
from pyvider.cty.values.frozen import FrozenDict


@define(frozen=True, slots=True)
class CtyObject(CtyType[dict[str, object]]):
    ctype: ClassVar[str] = "object"
    _type_order: ClassVar[int] = 7
    attribute_types: dict[str, CtyType[Any]] = field(factory=dict)
    optional_attributes: frozenset[str] = field(factory=frozenset, converter=frozenset)

    def __attrs_post_init__(self) -> None:
        for name, attr_type in self.attribute_types.items():
            if not isinstance(attr_type, CtyType):
                raise InvalidTypeError(
                    f"Attribute '{name}' must be a CtyType, but got {type(attr_type).__name__}"
                )

    def __hash__(self) -> int:
        # Use a recursive hashing approach that safely handles nested objects
        def safe_hash_type(cty_type: CtyType[Any]) -> int:
            if hasattr(cty_type, "ctype") and cty_type.ctype == "object":
                # For nested objects, use a simpler hash to avoid recursion
                obj_type = cast(CtyObject, cty_type)
                return hash((obj_type.ctype, tuple(sorted(obj_type.attribute_types.keys()))))
            return hash(cty_type)

        attr_hashes = tuple(
            (name, safe_hash_type(attr_type)) for name, attr_type in sorted(self.attribute_types.items())
        )
        return hash((self.ctype, attr_hashes, self.optional_attributes))

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

        unknown_optionals = self.optional_attributes - set(self.attribute_types.keys())
        if unknown_optionals:
            raise CtyAttributeValidationError(
                f"Unknown optional attributes: {', '.join(sorted(list(unknown_optionals)))}"
            )

        if hasattr(type(value), "__attrs_attrs__"):
            value = _attrs_to_dict_safe(value)
        if not isinstance(value, dict):
            raise CtyAttributeValidationError(
                f"Expected a dictionary for CtyObject, got {type(value).__name__}"
            )

        # Normalize keys to NFC before validation to ensure consistency.
        value_dict = cast(dict[str, Any], value)
        value = {unicodedata.normalize("NFC", str(k)): v for k, v in value_dict.items()}

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

    def _equal_shallow(self, other: Any) -> tuple[tuple[Any, Any], ...] | None:
        if not isinstance(other, CtyObject):
            return None
        if self.optional_attributes != other.optional_attributes:
            return None
        if self.attribute_types.keys() != other.attribute_types.keys():
            return None
        return tuple(
            (attr_type, other.attribute_types[name]) for name, attr_type in self.attribute_types.items()
        )

    def usable_as(self, other: CtyType[Any]) -> bool:
        from pyvider.cty.types.structural import CtyDynamic

        if isinstance(other, CtyDynamic):
            return True
        if not isinstance(other, CtyObject):
            return False
        other_attrs = set(other.attribute_types.keys())
        self_attrs = set(self.attribute_types.keys())
        if not other_attrs.issubset(self_attrs):
            return False
        self_required = self_attrs - self.optional_attributes
        other_required = other_attrs - other.optional_attributes
        if not other_required.issubset(self_required):
            return False
        return all(
            self.attribute_types[name].usable_as(other_type)
            for name, other_type in other.attribute_types.items()
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
