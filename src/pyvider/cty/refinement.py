#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""go-cty's `Value.Refine()` builder and `ctystrings.SafeKnownPrefix`.

The refinement *data model* already existed here — `RefinedUnknownValue` carries
all six of go-cty's keys, and the msgpack `0x0c` wire codec reads and writes
them. What was missing is the part that makes them trustworthy: a builder that
**refuses** an inconsistent refinement rather than recording it.

That is the point of this module, and the tracker says so: the validation is the
work, not the API shape. A refinement is a *promise* about a value that is not
yet known, and Terraform plans on it. A promise that contradicts the value, or
contradicts an earlier promise, is worse than no refinement at all — it produces
a plan that cannot apply, and the contradiction is discovered at apply time by a
practitioner rather than at refine time by the provider.

Refinements only ever narrow. go-cty panics on a widening; this raises, which is
the same decision expressed the way Python expresses it.

One behaviour that surprises on first reading and is deliberate: refining can
produce a **known** value. An unknown refined to "not null, and between 5 and 5
inclusive" is 5. An unknown collection refined to "length 0" is the empty
collection. go-cty collapses these in `NewValue()`, and so does this.
"""

from __future__ import annotations

from collections.abc import Sized
from decimal import Decimal
from typing import Any, Self, cast
import unicodedata

from pyvider.cty._unicode import iter_clusters
from pyvider.cty.exceptions import CtyValidationError
from pyvider.cty.types import CtyList, CtyMap, CtyNumber, CtySet, CtyString
from pyvider.cty.values import CtyValue
from pyvider.cty.values.markers import RefinedUnknownValue

__all__ = ["CtyRefinementError", "RefinementBuilder", "refine", "safe_known_prefix"]

_COLLECTIONS = (CtyList, CtySet, CtyMap)


class CtyRefinementError(CtyValidationError):
    """A refinement that contradicts the value, or an earlier refinement."""


def safe_known_prefix(prefix: str, /) -> str:
    """The longest prefix that cannot change when more characters are appended.

    go-cty's `ctystrings.SafeKnownPrefix`. The final grapheme cluster is dropped
    because a later character may *combine* with it: `"hello"` is not a safe
    known prefix, since the full string could turn out to be `"hellö"` — the
    `o` was never final. Its own documentation uses that example.

    Always NFC-normalized first, matching how cty stores strings, so the prefix
    is comparable with the values it will be checked against.
    """
    normalized = unicodedata.normalize("NFC", prefix)
    clusters = list(iter_clusters(normalized))
    return "".join(clusters[:-1])


def refine(value: CtyValue[Any], /) -> RefinementBuilder:
    """Begin refining `value`. Finish with `.new_value()`."""
    return RefinementBuilder(value)


class RefinementBuilder:
    """Accumulates refinements, checking each against the value and the rest."""

    def __init__(self, value: CtyValue[Any]) -> None:
        self._value = value
        self._marks = value.marks
        existing = value.value if isinstance(value.value, RefinedUnknownValue) else None
        self._is_known_null: bool | None = existing.is_known_null if existing else None
        self._prefix: str | None = existing.string_prefix if existing else None
        self._lower = existing.number_lower_bound if existing else None
        self._upper = existing.number_upper_bound if existing else None
        self._min_len = existing.collection_length_lower_bound if existing else None
        self._max_len = existing.collection_length_upper_bound if existing else None

    # -- nullness ---------------------------------------------------------

    def not_null(self) -> Self:
        if self._value.is_null:
            raise CtyRefinementError("refining a null value as non-null")
        if self._is_known_null is True:
            raise CtyRefinementError("refining a null value as non-null")
        self._is_known_null = False
        return self

    def null(self) -> Self:
        if (not self._value.is_unknown) and not self._value.is_null:
            raise CtyRefinementError("refining a non-null value as null")
        if self._is_known_null is False:
            raise CtyRefinementError("refining a non-null value as null")
        self._is_known_null = True
        return self

    # -- numbers ----------------------------------------------------------

    def number_range_lower_bound(self, minimum: Decimal | int, *, inclusive: bool = True) -> Self:
        self._require(CtyNumber, "numeric bounds")
        bound = Decimal(minimum)
        self._check_known_number(lambda known: known >= bound if inclusive else known > bound, bound)
        if self._lower is None or bound > self._lower[0] or (bound == self._lower[0] and not inclusive):
            self._lower = (bound, inclusive)
        self._check_number_bounds()
        return self

    def number_range_upper_bound(self, maximum: Decimal | int, *, inclusive: bool = True) -> Self:
        self._require(CtyNumber, "numeric bounds")
        bound = Decimal(maximum)
        self._check_known_number(lambda known: known <= bound if inclusive else known < bound, bound)
        if self._upper is None or bound < self._upper[0] or (bound == self._upper[0] and not inclusive):
            self._upper = (bound, inclusive)
        self._check_number_bounds()
        return self

    def number_range_inclusive(self, minimum: Decimal | int, maximum: Decimal | int) -> Self:
        return self.number_range_lower_bound(minimum).number_range_upper_bound(maximum)

    # -- collections ------------------------------------------------------

    def collection_length_lower_bound(self, minimum: int) -> Self:
        self._require(_COLLECTIONS, "collection length bounds")
        self._check_known_length(lambda known: known >= minimum, f"lower bound {minimum}")
        self._min_len = minimum if self._min_len is None else max(self._min_len, minimum)
        self._check_length_bounds()
        return self

    def collection_length_upper_bound(self, maximum: int) -> Self:
        self._require(_COLLECTIONS, "collection length bounds")
        self._check_known_length(lambda known: known <= maximum, f"upper bound {maximum}")
        self._max_len = maximum if self._max_len is None else min(self._max_len, maximum)
        self._check_length_bounds()
        return self

    def collection_length(self, length: int) -> Self:
        return self.collection_length_lower_bound(length).collection_length_upper_bound(length)

    # -- strings ----------------------------------------------------------

    def string_prefix(self, prefix: str) -> Self:
        """Refine by a prefix, shortened so a later character cannot change it."""
        return self.string_prefix_full(safe_known_prefix(prefix))

    def string_prefix_full(self, prefix: str) -> Self:
        """Refine by a prefix taken literally.

        Only safe when the caller controls every character that follows and can
        guarantee none of them combines with the prefix's last character. Use
        `string_prefix` otherwise.
        """
        self._require(CtyString, "string prefix")
        normalized = unicodedata.normalize("NFC", prefix)
        if (not self._value.is_unknown) and not self._value.is_null:
            known = str(self._value.value)
            if not known.startswith(normalized):
                raise CtyRefinementError("refined prefix is inconsistent with known value")
        if self._prefix is not None:
            longer, shorter = sorted((self._prefix, normalized), key=len, reverse=True)
            if not longer.startswith(shorter):
                raise CtyRefinementError("refined prefix is inconsistent with previous refined prefix")
            normalized = longer
        self._prefix = normalized
        return self

    # -- finish -----------------------------------------------------------

    def new_value(self) -> CtyValue[Any]:
        """The refined value, collapsed to a known one where the bounds decide it."""
        if not self._value.is_unknown:
            # go-cty returns the original untouched: a refinement of a known
            # value is a claim to be *checked*, which the builder already did,
            # not information to be recorded.
            return self._value

        collapsed = self._collapsed()
        if collapsed is not None:
            return collapsed.with_marks(self._marks)

        refined = RefinedUnknownValue(
            is_known_null=self._is_known_null,
            string_prefix=self._prefix,
            number_lower_bound=self._lower,
            number_upper_bound=self._upper,
            collection_length_lower_bound=self._min_len,
            collection_length_upper_bound=self._max_len,
        )
        return CtyValue(vtype=self._value.type, value=refined, is_unknown=True, marks=self._marks)

    def _collapsed(self) -> CtyValue[Any] | None:
        """A known value, where the refinements have narrowed to exactly one."""
        if self._is_known_null is True:
            # There is only one null of each type, so this is now known.
            return CtyValue.null(self._value.type)
        if self._is_known_null is not False:
            return None
        if (
            isinstance(self._value.type, CtyNumber)
            and self._lower is not None
            and self._upper is not None
            and self._lower[1]
            and self._upper[1]
            and self._lower[0] == self._upper[0]
        ):
            return CtyValue(vtype=self._value.type, value=self._lower[0])
        if (
            isinstance(self._value.type, _COLLECTIONS)
            and self._min_len is not None
            and self._min_len == self._max_len == 0
        ):
            empty: Any = {} if isinstance(self._value.type, CtyMap) else []
            return cast("CtyValue[Any]", self._value.type.validate(empty))
        return None

    # -- checks -----------------------------------------------------------

    def _require(self, kinds: Any, what: str) -> None:
        if not isinstance(self._value.type, kinds):
            raise CtyRefinementError(f"cannot refine {what} for a {self._value.type.ctype} value")

    def _check_known_number(self, holds: Any, bound: Decimal) -> None:
        if (not self._value.is_unknown) and not self._value.is_null and not holds(self._value.value):
            raise CtyRefinementError(f"refining {self._value.value} against bound {bound}")

    def _check_known_length(self, holds: Any, described: str) -> None:
        if (not self._value.is_unknown) and not self._value.is_null:
            length = len(cast("Sized", self._value.value or ()))
            if not holds(length):
                raise CtyRefinementError(f"refining collection of length {length} with {described}")

    def _check_number_bounds(self) -> None:
        if self._lower is not None and self._upper is not None and self._lower[0] > self._upper[0]:
            raise CtyRefinementError(
                f"number lower bound {self._lower[0]} is greater than upper bound {self._upper[0]}"
            )

    def _check_length_bounds(self) -> None:
        if self._min_len is not None and self._max_len is not None and self._max_len < self._min_len:
            raise CtyRefinementError(
                f"collection length upper bound {self._max_len} is less than lower bound {self._min_len}"
            )


# 🌊🪢🔚
