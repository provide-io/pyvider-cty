#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Refusing a conversion is an ordinary answer, and has to cost like one.

`convert` was wrapped in an `error_boundary` that logs with `exc_info=True`.
Rendering that traceback cost a flat **88 ms per failed conversion**, measured,
independent of the value's size -- so a hundred of them took nearly nine
seconds, and the cost was paid on a path that is not an error at all.

A failed conversion is expected here. `can_convert_unsafe` and everything built
on it -- unification, the function framework's argument coercion -- ask exactly
this question and take "no" for an answer. Charging a full traceback render and
an ERROR log for a routine "these two types are incompatible" is not a
diagnostic; it is a denial of service reachable from any decoded value.

The boundary also wrapped a function that recurses into every element and
attribute, so each of them entered a boundary and stringified both types.
"""

from __future__ import annotations

import time

import pytest

from pyvider.cty import CtyBool, CtyList, CtyNumber, CtyString
from pyvider.cty.conversion.explicit import convert
from pyvider.cty.exceptions import CtyConversionError

# The defect this guards against cost 88 ms per refusal. The budget only has to
# sit clearly below that while staying above anything a loaded machine can do to
# a sub-millisecond operation -- and it has to hold on a shared CI runner under
# `pytest -n auto`, where wall-clock for a fast operation is mostly scheduler
# noise. 5 ms was too tight and went red on macOS at 5.5 ms; 25 ms is still
# three and a half times under the defect and does not measure the runner.
BUDGET_PER_REFUSAL_MS = 25.0
REPEATS = 40


def _refuse() -> None:
    source = CtyList(element_type=CtyString()).validate(["x"] * 10)
    with pytest.raises(CtyConversionError):
        convert(source, CtyList(element_type=CtyBool()))


class TestARefusalIsCheap:
    def test_repeated_refusals_stay_within_budget(self) -> None:
        _refuse()  # warm anything one-time

        started = time.perf_counter()
        for _ in range(REPEATS):
            _refuse()
        per_refusal_ms = (time.perf_counter() - started) / REPEATS * 1000

        assert per_refusal_ms < BUDGET_PER_REFUSAL_MS, f"{per_refusal_ms:.2f} ms per refusal"

    def test_the_cost_does_not_grow_with_the_value(self) -> None:
        """It never did -- the render was flat -- but a future diagnostic that
        walks the value would show up here rather than in production.

        Measured as a ratio against a small value rather than as an absolute, so
        what is asserted is the *shape* of the cost curve and not the speed of
        the machine. A single timing sample of a sub-millisecond operation on a
        shared runner is mostly scheduler noise, so both ends are the best of
        several attempts.
        """

        def best_refusal_over(count: int) -> float:
            source = CtyList(element_type=CtyString()).validate(["x"] * count)
            target = CtyList(element_type=CtyBool())

            def once() -> float:
                started = time.perf_counter()
                with pytest.raises(CtyConversionError):
                    convert(source, target)
                return time.perf_counter() - started

            once()  # warm this size
            return min(once() for _ in range(5))

        small = best_refusal_over(10)
        large = best_refusal_over(2000)

        # A diagnostic that walked the value would be 200x here, not 20x. The
        # floor keeps a near-zero `small` from making the ratio meaningless.
        assert large < max(small * 20, BUDGET_PER_REFUSAL_MS / 1000)


class TestTheRefusalItselfIsUnchanged:
    def test_it_still_raises_a_conversion_error(self) -> None:
        with pytest.raises(CtyConversionError):
            convert(CtyString().validate("x"), CtyBool())

    def test_the_message_still_names_both_types(self) -> None:
        with pytest.raises(CtyConversionError, match="string"):
            convert(CtyString().validate("x"), CtyBool())

    def test_a_conversion_that_should_work_still_works(self) -> None:
        converted = convert(CtyNumber().validate(1), CtyString())

        assert converted.value == "1"

    def test_a_nested_conversion_still_works(self) -> None:
        source = CtyList(element_type=CtyNumber()).validate([1, 2])
        converted = convert(source, CtyList(element_type=CtyString()))

        assert [element.value for element in converted.value] == ["1", "2"]  # type: ignore[union-attr]


# 🌊🪢🔚
