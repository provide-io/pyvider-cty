
# pyvider/cty/values/refinement.py

from typing import Any, Optional, List
from decimal import Decimal

from pyvider.cty.values import CtyValue

class ValueRefinement:
    """Base class for all value refinements."""
    pass

class NotNullRefinement(ValueRefinement):
    """Refinement indicating a value is not null."""
    pass

class StringPrefixRefinement(ValueRefinement):
    """Refinement indicating a string has a specific prefix."""

    def __init__(self, prefix: str):
        self.prefix = prefix

class NumberRangeRefinement(ValueRefinement):
    """Refinement constraining a number to a range."""

    def __init__(self,
                 min_value: Optional[Decimal] = None,
                 max_value: Optional[Decimal] = None,
                 min_inclusive: bool = True,
                 max_inclusive: bool = True):
        self.min_value = min_value
        self.max_value = max_value
        self.min_inclusive = min_inclusive
        self.max_inclusive = max_inclusive

class ValueRefinementBuilder:
    """Builder for creating refined values."""

    def __init__(self, value: CtyValue):
        self._value = value
        self._refinements: List[ValueRefinement] = []

    def not_null(self) -> 'ValueRefinementBuilder':
        """Add a not-null refinement."""
        self._refinements.append(NotNullRefinement())
        return self

    def string_prefix(self, prefix: str) -> 'ValueRefinementBuilder':
        """Add a string prefix refinement."""
        from pyvider.cty.types.primitives import CtyString
        if not isinstance(self._value.type, CtyString):
            raise TypeError("string_prefix can only be applied to string values")

        self._refinements.append(StringPrefixRefinement(prefix))
        return self

    def number_range_inclusive(self, min_val: Any, max_val: Any) -> 'ValueRefinementBuilder':
        """Add a number range refinement with inclusive bounds."""
        from pyvider.cty.types.primitives import CtyNumber
        if not isinstance(self._value.type, CtyNumber):
            raise TypeError("number_range_inclusive can only be applied to number values")

        min_decimal = Decimal(str(min_val)) if min_val is not None else None
        max_decimal = Decimal(str(max_val)) if max_val is not None else None

        self._refinements.append(
            NumberRangeRefinement(
                min_value=min_decimal,
                max_value=max_decimal,
                min_inclusive=True,
                max_inclusive=True
            )
        )
        return self

    def new_value(self) -> CtyValue:
        """Create the refined value."""
        # If value is already known, check if it satisfies refinements
        if self._value.is_known and not self._value.is_null:
            # Check each refinement
            # for refinement in self._refinements:
            #     # Validation logic based on refinement type
            #     # ...

            # # If all refinements are satisfied, return the original value with marks
            return self._value

        # For unknown values, create a new unknown with refinements
        return CtyValue(
            type_=self._value.type,
            is_unknown=True,
            marks=self._value._marks,
            refinements=self._refinements
        )
