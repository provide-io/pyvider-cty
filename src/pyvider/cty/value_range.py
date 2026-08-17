#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""go-cty's `Value.Range()` and `ValueRange`.

The read side of refinements. `refine()` records what is known about a value
that is not yet known; this asks. A known value has a range too — a degenerate
one containing exactly itself — so a caller can ask the same questions of both
and stop branching on `is_unknown`.

`includes()` is the reason the rest exists, and it is **three-valued**: yes, no,
or "cannot say yet". That third answer is the honest one for an unknown whose
refinements neither admit nor exclude the candidate, and returning a plain bool
there is how comparisons come to assert more than they know. `equality.py`
records exactly this gap — go-cty disqualifies some comparisons early from an
unknown's bounds, and without a range to consult, everything fell through to
"unknown".

Where go-cty panics for asking a type-inappropriate question — a string prefix
of a number — this raises. Asking for a bound on a `dynamic` is *not* an error
in either: nothing is known about the type yet, so the answer is the widest one.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, cast

from attrs import define

from pyvider.cty.types import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtySet,
    CtyString,
    CtyType,
)
from pyvider.cty.values import CtyValue
from pyvider.cty.values.markers import RefinedUnknownValue

__all__ = ["ValueRange", "value_range"]

_COLLECTIONS = (CtyList, CtySet, CtyMap)
_UNBOUNDED_LENGTH = -1
"""`length_upper_bound()` when nothing bounds it. go-cty uses maxint; this says so."""


def value_range(value: CtyValue[Any], /) -> ValueRange:
    """What is known about `value`, whether or not the value itself is."""
    refinement = value.value if isinstance(value.value, RefinedUnknownValue) else None
    return ValueRange(value=value, refinement=refinement)


@define(frozen=True, slots=True)
class ValueRange:
    """The set of values a `CtyValue` could turn out to be."""

    value: CtyValue[Any]
    refinement: RefinedUnknownValue | None

    # -- nullness ---------------------------------------------------------

    @property
    def type_constraint(self) -> CtyType[Any]:
        return self.value.type

    def could_be_null(self) -> bool:
        """True unless the value is definitely non-null."""
        if not self.value.is_unknown:
            return bool(self.value.is_null)
        if self.refinement is None:
            return True
        return self.refinement.is_known_null is not False

    def definitely_not_null(self) -> bool:
        return not self.could_be_null()

    # -- numbers ----------------------------------------------------------

    def number_lower_bound(self) -> tuple[CtyValue[Any], bool]:
        """The lower bound, and whether it is inclusive.

        An unknown number is returned when nothing bounds it, matching go-cty --
        at which point the inclusive flag is meaningless.
        """
        self._require_number()
        if not self.value.is_unknown and not self.value.is_null:
            return self.value, True
        bound = self.refinement.number_lower_bound if self.refinement else None
        return self._bound(bound)

    def number_upper_bound(self) -> tuple[CtyValue[Any], bool]:
        self._require_number()
        if not self.value.is_unknown and not self.value.is_null:
            return self.value, True
        bound = self.refinement.number_upper_bound if self.refinement else None
        return self._bound(bound)

    # -- strings ----------------------------------------------------------

    def string_prefix(self) -> str:
        """The known leading characters, or `""` if none are known."""
        if isinstance(self.value.type, CtyDynamic):
            return ""  # Not even known to be a string yet.
        if not isinstance(self.value.type, CtyString):
            raise TypeError(f"string_prefix for {self.value.type.ctype}")
        if not self.value.is_unknown and not self.value.is_null:
            return str(self.value.value)
        return (self.refinement.string_prefix if self.refinement else None) or ""

    # -- collections ------------------------------------------------------

    def length_lower_bound(self) -> int:
        if isinstance(self.value.type, CtyDynamic):
            return 0
        self._require_collection()
        if not self.value.is_unknown and not self.value.is_null:
            return len(cast("Any", self.value.value or ()))
        lower = self.refinement.collection_length_lower_bound if self.refinement else None
        return lower or 0

    def length_upper_bound(self) -> int:
        if isinstance(self.value.type, CtyDynamic):
            return _UNBOUNDED_LENGTH
        self._require_collection()
        if not self.value.is_unknown and not self.value.is_null:
            return len(cast("Any", self.value.value or ()))
        upper = self.refinement.collection_length_upper_bound if self.refinement else None
        return _UNBOUNDED_LENGTH if upper is None else upper

    # -- the question the rest exists to answer ---------------------------

    def includes(self, candidate: CtyValue[Any], /) -> CtyValue[Any]:
        """Whether `candidate` could be this value: true, false, or unknown.

        Three-valued deliberately. "Unknown" means the refinements neither admit
        nor exclude it, and collapsing that to false would claim knowledge the
        range does not have -- which in a plan means reporting a difference that
        may not exist.
        """
        nullness = self._includes_by_nullness(candidate)
        if nullness is not None:
            return nullness
        if isinstance(candidate.type, CtyDynamic) or isinstance(self.value.type, CtyDynamic):
            # Nothing further can be tested without knowing the type.
            return CtyValue.unknown(CtyBool())
        if not candidate.type.equal(self.value.type):
            return CtyBool().validate(False)
        if candidate.is_unknown:
            return CtyValue.unknown(CtyBool())
        return self._includes_known(candidate)

    def _includes_by_nullness(self, candidate: CtyValue[Any]) -> CtyValue[Any] | None:
        if self.definitely_not_null():
            return CtyBool().validate(False) if candidate.is_null else None
        if not self.value.is_unknown and self.value.is_null:
            return CtyBool().validate(bool(candidate.is_null))
        if candidate.is_null:
            # The range admits null and the candidate is null, so it fits.
            return CtyBool().validate(True)
        return None

    def _includes_known(self, candidate: CtyValue[Any]) -> CtyValue[Any]:
        if isinstance(self.value.type, CtyString):
            fits = str(candidate.value).startswith(self.string_prefix())
            return CtyBool().validate(fits) if not fits else self._undecided()
        if isinstance(self.value.type, CtyNumber):
            return self._includes_number(candidate)
        if isinstance(self.value.type, _COLLECTIONS):
            length = len(cast("Any", candidate.value or ()))
            upper = self.length_upper_bound()
            outside = length < self.length_lower_bound() or (upper != _UNBOUNDED_LENGTH and length > upper)
            return CtyBool().validate(False) if outside else self._undecided()
        return self._undecided()

    def _includes_number(self, candidate: CtyValue[Any]) -> CtyValue[Any]:
        number = cast("Decimal", candidate.value)
        lower, lower_inclusive = self.number_lower_bound()
        upper, upper_inclusive = self.number_upper_bound()
        if not lower.is_unknown:
            limit = cast("Decimal", lower.value)
            if number < limit or (number == limit and not lower_inclusive):
                return CtyBool().validate(False)
        if not upper.is_unknown:
            limit = cast("Decimal", upper.value)
            if number > limit or (number == limit and not upper_inclusive):
                return CtyBool().validate(False)
        return self._undecided()

    def _undecided(self) -> CtyValue[Any]:
        """Within the bounds is not the same as equal to the value.

        A known value's range contains only itself, so there the answer is
        definite; for an unknown, passing every bound only means the candidate
        has not been ruled out.
        """
        if not self.value.is_unknown:
            return CtyBool().validate(True)
        return CtyValue.unknown(CtyBool())

    # -- guards -----------------------------------------------------------

    def _bound(self, bound: tuple[Decimal, bool] | None) -> tuple[CtyValue[Any], bool]:
        if bound is None:
            return CtyValue.unknown(CtyNumber()), False
        return CtyNumber().validate(bound[0]), bound[1]

    def _require_number(self) -> None:
        if isinstance(self.value.type, CtyDynamic):
            return
        if not isinstance(self.value.type, CtyNumber):
            raise TypeError(f"number bound for {self.value.type.ctype}")

    def _require_collection(self) -> None:
        if not isinstance(self.value.type, _COLLECTIONS):
            raise TypeError(f"length bound for {self.value.type.ctype}")


# 🌊🪢🔚
