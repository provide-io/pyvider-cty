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
of a number, a range of a marked value — this raises. Asking for a bound on a
`dynamic` is *not* an error in either: nothing is known about the type yet, so
the answer is the widest one.

Every answer here is go-cty's answer, including the ones that look imprecise.
Three of them were originally written from `value_range.go`'s docstrings and
disagreed with the code underneath: an unbounded number range returns an
infinity rather than an unknown, `includes()` answers "cannot say" even for a
known value that equals the candidate, and its undecided answer is refined
not-null rather than a bare unknown. The first two were only found once a
harness could ask real go-cty, and the lesson is the same each time — a
reimplementation that is *more* decisive than its reference is still a
divergence, because a caller porting a comparison across the two gets a
different plan.
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

_NEGATIVE_INFINITY = Decimal("-Infinity")
_POSITIVE_INFINITY = Decimal("Infinity")


def value_range(value: CtyValue[Any], /) -> ValueRange:
    """What is known about `value`, whether or not the value itself is.

    Refuses a marked value, as go-cty does. A range describes what a value
    could be while saying nothing about the marks it carries, so answering here
    would hand a caller a description of a sensitive value with the reason it
    was flagged left behind.
    """
    if value.marks:
        raise ValueError("value_range on a marked value; unmark it first")
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

        Negative infinity when nothing bounds it, at which point the inclusive
        flag is meaningless. go-cty's docstring says it returns an unknown
        number there; `NumberLowerBound` returns `cty.NegativeInfinity`, and
        this follows the code.
        """
        self._require_number()
        if not self.value.is_unknown and not self.value.is_null:
            return self.value, True
        bound = self.refinement.number_lower_bound if self.refinement else None
        return self._bound(bound, _NEGATIVE_INFINITY)

    def number_upper_bound(self) -> tuple[CtyValue[Any], bool]:
        self._require_number()
        if not self.value.is_unknown and not self.value.is_null:
            return self.value, True
        bound = self.refinement.number_upper_bound if self.refinement else None
        return self._bound(bound, _POSITIVE_INFINITY)

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
            return self._known_length_lower_bound()
        lower = self.refinement.collection_length_lower_bound if self.refinement else None
        return lower or 0

    def _known_length_lower_bound(self) -> int:
        """How short a known collection could still turn out to be.

        For a list or a map, exactly as long as it is: an unknown element does
        not change the count. A SET is different, because it holds distinct
        values -- an unknown element may resolve to something already in the set
        and collapse into it. Reporting the stored count as an exact length let
        `equals` answer a definite False for two sets that may well be
        identical, where go-cty answers undecided, and a provider comparing
        planned against prior state plans a replacement on the strength of it.

        The upper bound needs no such care: every element resolving to something
        distinct is already the largest the set can be.
        """
        from pyvider.cty.types import CtySet

        elements = cast("Any", self.value.value or ())
        if not isinstance(self.value.type, CtySet):
            return len(elements)
        known = sum(1 for element in elements if not element.is_unknown)
        if known == len(elements):
            return known
        # Every unknown could collapse into a known one, but a set holding only
        # unknowns still has at least one element.
        return max(known, 1)

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
        from pyvider.cty.conformance import conformance_errors

        nullness = self._includes_by_nullness(candidate)
        if nullness is not None:
            return nullness

        # Conformance, not equality, and in this order: go-cty tests the
        # candidate's type against the *constraint*, so a dynamic candidate
        # against a concrete range is definitely not in it, while any candidate
        # against a dynamic range still has to be tested further down. Asking
        # `equal` instead answered "unknown" for the first of those.
        if conformance_errors(candidate.type, self.value.type):
            return CtyBool().validate(False)
        if isinstance(candidate.type, CtyDynamic):
            # An unknown value of an unknown type; nothing further to test.
            return self._undecided()
        if candidate.is_unknown:
            return self._undecided()
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
            # The candidate's length is itself a range, not a point: a known set
            # holding unknown elements may be shorter than it looks, because an
            # unknown can resolve to a value already present and collapse into
            # it. Comparing the stored count against this range excluded sets
            # that overlap it perfectly well, and equality reported a definite
            # difference where go-cty stays undecided.
            candidate_range = value_range(candidate)  # defined below in this module
            candidate_low = candidate_range.length_lower_bound()
            candidate_high = candidate_range.length_upper_bound()
            upper = self.length_upper_bound()
            disjoint = candidate_high < self.length_lower_bound() or (
                upper != _UNBOUNDED_LENGTH and candidate_low > upper
            )
            return CtyBool().validate(False) if disjoint else self._undecided()
        return self._undecided()

    def _includes_number(self, candidate: CtyValue[Any]) -> CtyValue[Any]:
        """Both bounds always hold a number now -- an infinity when unbounded.

        So there is no "no bound to check" branch: a comparison against an
        infinity excludes nothing, which is the same answer that branch gave.
        """
        number = cast("Decimal", candidate.value)
        lower, lower_inclusive = self.number_lower_bound()
        upper, upper_inclusive = self.number_upper_bound()

        low = cast("Decimal", lower.value)
        if number < low or (number == low and not lower_inclusive):
            return CtyBool().validate(False)
        high = cast("Decimal", upper.value)
        if number > high or (number == high and not upper_inclusive):
            return CtyBool().validate(False)
        return self._undecided()

    def _undecided(self) -> CtyValue[Any]:
        """Passing every bound only means the candidate has not been ruled out.

        Not even for a known value, whose range go-cty describes with synthetic
        refinements rather than with the value: a known `"hello"` has the prefix
        `"hello"`, and a candidate that starts with it has not been excluded but
        has not been shown equal either. go-cty says as much in `Includes`'
        docstring -- the rules "focus mainly on answering false, because
        disproving membership tends to be more useful".

        The answer is refined not-null, as go-cty's is. It costs nothing here
        and a caller that asks whether the answer could be null gets the same
        reply from both.
        """
        return CtyValue(
            vtype=CtyBool(),
            value=RefinedUnknownValue(is_known_null=False),
            is_unknown=True,
        )

    # -- guards -----------------------------------------------------------

    def _bound(self, bound: tuple[Decimal, bool] | None, unbounded: Decimal) -> tuple[CtyValue[Any], bool]:
        if bound is None:
            return CtyNumber().validate(unbounded), False
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
