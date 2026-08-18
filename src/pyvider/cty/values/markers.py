#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from __future__ import annotations

from decimal import Decimal

from attrs import define

# pyvider/cty/values/markers.py
"""
This module contains simple marker classes to break import cycles.
"""


class UnknownValue:
    """A base marker class for all unknown value types."""


class UnrefinedUnknownValue(UnknownValue):
    """A marker class for a simple, unrefined unknown value."""

    def __repr__(self) -> str:
        return "UNREFINED_UNKNOWN"


@define(frozen=True, slots=True, auto_attribs=True, match_args=True)
class RefinedUnknownValue(UnknownValue):
    """Represents an unknown value with additional constraints."""

    is_known_null: bool | None = None
    string_prefix: str | None = None
    number_lower_bound: tuple[Decimal, bool] | None = None
    number_upper_bound: tuple[Decimal, bool] | None = None
    collection_length_lower_bound: int | None = None
    collection_length_upper_bound: int | None = None

    def for_type(self, target: object) -> RefinedUnknownValue | UnrefinedUnknownValue:
        """This refinement with everything the target type cannot carry removed.

        A refinement is only meaningful against the type it constrains: a string
        prefix on a number is not a weaker fact, it is a malformed one. go-cty
        refuses such a value at the msgpack door ("string prefix refinement for
        non-string type"), so carrying one across a type change produces bytes
        Terraform cannot decode -- a protocol failure rather than a diff.

        Nullness survives every target, because "this will not be null" is a
        statement about the value rather than about its type, and it is the bit
        equality reasons from.
        """
        from pyvider.cty.types.collections import CtyList, CtyMap, CtySet
        from pyvider.cty.types.primitives import CtyNumber, CtyString

        keep_string = isinstance(target, CtyString)
        keep_number = isinstance(target, CtyNumber)
        keep_length = isinstance(target, CtyList | CtySet | CtyMap)

        ported = RefinedUnknownValue(
            is_known_null=self.is_known_null,
            string_prefix=self.string_prefix if keep_string else None,
            number_lower_bound=self.number_lower_bound if keep_number else None,
            number_upper_bound=self.number_upper_bound if keep_number else None,
            collection_length_lower_bound=(self.collection_length_lower_bound if keep_length else None),
            collection_length_upper_bound=(self.collection_length_upper_bound if keep_length else None),
        )
        if all(
            getattr(ported, field) is None
            for field in (
                "is_known_null",
                "string_prefix",
                "number_lower_bound",
                "number_upper_bound",
                "collection_length_lower_bound",
                "collection_length_upper_bound",
            )
        ):
            return UNREFINED_UNKNOWN
        return ported


# This singleton represents an unknown value with no refinements.
UNREFINED_UNKNOWN = UnrefinedUnknownValue()

# 🌊🪢🔚
