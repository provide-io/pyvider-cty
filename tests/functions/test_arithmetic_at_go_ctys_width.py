#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Arithmetic computes at go-cty's width, not at `Decimal`'s default.

go-cty holds every number in a 512-bit `big.Float` and computes in it. A
`Decimal` computes in the ambient context, and this package took its default of
**28 significant digits**, so every arithmetic function quietly rounded there:

    add(2**100, 1)  ->  1267650600228229401496703205000

Four digits invented and one dropped, in a value that goes straight to Terraform
state. `subtract`, `multiply`, `divide`, `abs` and `negate` did the same --
Python's unary minus and `abs` are context operations too -- and `modulo` did
something worse, raising `DivisionImpossible` out of the implementation, which
the function framework reports as a *panic*, where go-cty simply answers.

Computing at 155 significant digits -- `floor(512 * log10 2) + 1`, the widest a
512-bit float can spell -- agrees with go-cty wherever go-cty is exact and rounds
where it rounds. `add(1e200, 1)` is `1e200` on both sides, because the exact
answer needs 201 significant digits and neither model has them.

Two smaller things, both about the sign of a zero, which is a real distinction
in both models and reaches the wire:

  * `negate(0)` is `-0` in go-cty, because negating a `big.Float` flips the sign
    bit. Python's `-Decimal(0)` is the *arithmetic* `0 - 0`, which the decimal
    specification defines as `+0`, so this answered the wrong zero.
  * `int(-0.5)` is `+0` in go-cty, because truncation goes through a `big.Int`
    and that has no signed zero. Truncating a `Decimal` leaves `-0`.

All of it found on 2026-08-19 by `tests/compatibility/test_stdlib_fuzz.py`, on
its first run, from arguments no hand-written row had used. The differential
cases live there; these run without a Go toolchain and state the rule directly.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

from pyvider.cty import CtyNumber
from pyvider.cty.functions import STDLIB

N = CtyNumber()

# Every answer here was read from the oracle -- `soup-go cty call <fn> ...`
# against go-cty v1.19.0 -- rather than worked out from the source.
EXACT: list[tuple[str, list[Any], str]] = [
    ("add", [2**100, 1], "1267650600228229401496703205377"),
    ("subtract", [2**100 + 1, 1], "1267650600228229401496703205376"),
    ("multiply", [10**40, 10**40], "1" + "0" * 80),
    ("divide", [2**100, 2], "633825300114114700748351602688"),
    ("modulo", [2**100 + 7, 10], "3"),
    ("abs", [-(2**100) - 1], "1267650600228229401496703205377"),
    ("negate", [2**100 + 1], "-1267650600228229401496703205377"),
]


@pytest.mark.parametrize(("func", "args", "expected"), EXACT, ids=[case[0] for case in EXACT])
def test_a_result_wider_than_the_default_context_keeps_its_digits(
    func: str, args: list[Any], expected: str
) -> None:
    """31 to 81 significant digits, all of them inside the width both models hold."""
    answer = STDLIB[func](*[N.validate(arg) for arg in args])

    assert format(answer.value, "f") == expected


def test_modulo_answers_where_it_used_to_raise() -> None:
    """The worst of them: a panic-class error where go-cty answers 3.

    `Decimal.__mod__` refuses when the integer quotient does not fit the
    context, and `DivisionImpossible` is not a `CtyError`, so it escaped the
    taxonomy as `CtyFunctionPanicError` -- an unhandled Python exception
    reaching a provider from a function whose contract is to answer or refuse.
    """
    assert STDLIB["modulo"](N.validate(2**100 + 7), N.validate(10)).value == Decimal(3)


def test_a_quotient_that_needs_a_wider_context_than_the_model_still_answers() -> None:
    """Past go-cty's own width, `modulo` widens rather than raising.

    The two disagree about the *answer* out here -- go-cty's `big.Float` has run
    out of bits and says 0 where the exact remainder is 1 -- which is the
    representation divergence recorded against `divide(1,3)` in the sweep. What
    matters is that this is an answer rather than a panic.
    """
    assert STDLIB["modulo"](N.validate(Decimal("1E+200")), N.validate(3)).value == Decimal(1)


def test_an_answer_past_the_models_width_rounds_the_way_go_cty_rounds() -> None:
    """`1e200 + 1` needs 201 significant digits, and neither model has them."""
    answer = STDLIB["add"](N.validate(Decimal("1E+200")), N.validate(1))

    assert answer.value == Decimal("1E+200")


class TestTheSignOfAZero:
    def test_negating_zero_gives_negative_zero(self) -> None:
        answer = STDLIB["negate"](N.validate(0))

        assert answer.value.is_zero()
        assert answer.value.is_signed(), "go-cty's negate(0) is -0"

    def test_truncating_a_negative_fraction_gives_positive_zero(self) -> None:
        answer = STDLIB["int"](N.validate(Decimal("-0.5")))

        assert answer.value.is_zero()
        assert not answer.value.is_signed(), "go-cty truncates through a big.Int, which has no -0"

    def test_a_negative_zero_that_is_already_whole_is_returned_untouched(self) -> None:
        """go-cty's `if bf.IsInt() { return args[0] }` -- the sign survives."""
        answer = STDLIB["int"](N.validate(Decimal("-0.0")))

        assert answer.value.is_zero()
        assert answer.value.is_signed()

    @pytest.mark.parametrize(
        ("func", "argument"),
        [("ceil", "-0.0"), ("floor", "-0.0"), ("ceil", "-0.5"), ("floor", "0.5")],
    )
    def test_rounding_to_zero_gives_positive_zero(self, func: str, argument: str) -> None:
        """`ceil` and `floor` have no already-whole shortcut, so every answer of
        theirs comes back through a `big.Int` -- and `ceil(-0.0)` is `0`."""
        answer = STDLIB[func](N.validate(Decimal(argument)))

        assert answer.value.is_zero()
        assert not answer.value.is_signed()

    def test_a_zero_remainder_is_positive_whatever_the_dividend_was(self) -> None:
        """go-cty computes `a - b*trunc(a/b)`, and a `big.Float` subtraction of
        equal magnitudes is `+0`; `Decimal.__mod__` takes the dividend's sign."""
        answer = STDLIB["modulo"](N.validate(-1), N.validate(1))

        assert answer.value.is_zero()
        assert not answer.value.is_signed()

    def test_a_non_zero_remainder_still_takes_the_dividends_sign(self) -> None:
        assert STDLIB["modulo"](N.validate(-7), N.validate(3)).value == Decimal(-1)


class TestWhatDidNotChange:
    """Ordinary arithmetic, which was never wrong and must stay exact."""

    @pytest.mark.parametrize(
        ("func", "args", "expected"),
        [
            ("add", [1, 2], "3"),
            ("subtract", ["1.5", "0.25"], "1.25"),
            ("multiply", [3, "0.5"], "1.5"),
            ("divide", [1, 8], "0.125"),
            ("modulo", [7, 3], "1"),
            ("divide", [1, 0], "Infinity"),
            ("divide", [-1, 0], "-Infinity"),
        ],
    )
    def test_a_small_exact_answer_is_unchanged(self, func: str, args: list[Any], expected: str) -> None:
        answer = STDLIB[func](*[N.validate(arg) for arg in args])

        assert answer.value == Decimal(expected)

    def test_a_non_terminating_quotient_is_still_a_recorded_divergence(self) -> None:
        """Widening the context did not close it and could not.

        go-cty's answer ends `...335` because it is a 512-bit *binary* float
        printed exactly; a decimal division ends `...333` at any precision. The
        sweep holds the case; this only asserts that the answer is now as wide
        as the model rather than 28 digits wide.
        """
        answer = STDLIB["divide"](N.validate(1), N.validate(3))

        assert len(format(answer.value, "f").removeprefix("0.")) == 155


# 🌊🪢🔚
