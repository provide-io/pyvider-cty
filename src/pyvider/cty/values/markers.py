# pyvider/cty/values/markers.py
"""
This module contains simple marker classes to break import cycles.
"""

from decimal import Decimal

from attrs import define


class UnknownValue:
    """A base marker class for all unknown value types."""

    pass


class UnrefinedUnknownValue(UnknownValue):
    """A marker class for a simple, unrefined unknown value."""

    pass


@define(frozen=True, slots=True, auto_attribs=True, match_args=True)
class RefinedUnknownValue(UnknownValue):
    """Represents an unknown value with additional constraints."""

    is_known_null: bool | None = None
    string_prefix: str | None = None
    number_lower_bound: tuple[Decimal, bool] | None = None
    number_upper_bound: tuple[Decimal, bool] | None = None
    collection_length_lower_bound: int | None = None
    collection_length_upper_bound: int | None = None


# This singleton represents an unknown value with no refinements.
UNREFINED_UNKNOWN = UnrefinedUnknownValue()
