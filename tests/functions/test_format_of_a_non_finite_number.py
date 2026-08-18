#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`format` on an infinity or a NaN.

A `CtyNumber` can hold one: msgpack decodes a float64 infinity straight into
`Decimal("Infinity")`, and `pow`, `log` and `divide` all produce one. `format`
had no branch for it, so three different things went wrong at once:

    format("%d", +Inf)  -> CtyFunctionPanicError from int(Decimal("Infinity"))
    format("%e", +Inf)  -> "Infinitye+01"
    format("%#v", +Inf) -> "Infinity", which is not JSON

Every expectation here was read off go-cty v1.19.0, and **every one of them is
now a row in the differential sweep**. JSON has no spelling for an infinity, so
a plain `{"type":"number","value":...}` cannot carry one -- which was taken to
mean the oracle could not express it at all, and these were first checked
against a hand-written Go program. That was wrong: the harness's rich dialect
takes `{"$number":"Infinity"}`, the text `big.Float.Text` itself produces, and
has round-tripped it since the dialect landed. The sweep rows replace the
program, and they agree:

    +Inf  %v     -> "+Inf"      +Inf  %08.2f  -> "    +Inf"
    +Inf  %f     -> "+Inf"      +Inf  %08v    -> "0000+Inf"
    +Inf  %e     -> "+Inf"      +Inf  % f     -> " Inf"
    +Inf  %d     -> ERR an integer is required
    list  %v     -> ERR cannot serialize infinity as JSON

`big.Float` cannot hold a NaN at all -- `SetFloat64` panics on one -- so the NaN
rows below are Go's `fmt`, which is where go-cty's float verbs delegate anyway.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from pyvider.cty import CtyList, CtyNumber, CtyString
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import format_fn

INF = Decimal("Infinity")
NINF = Decimal("-Infinity")
NAN = Decimal("NaN")


def fmt(template: str, number: Decimal) -> str:
    return str(format_fn(CtyString().validate(template), CtyNumber().validate(number)).value)


class TestTheFloatVerbsSpellItGoesWay:
    """`+Inf`, `-Inf` and `NaN` -- not `Infinity`, which is `str(Decimal)`."""

    @pytest.mark.parametrize("verb", ["%v", "%f", "%e", "%E", "%g", "%G", "%s", "%.3f"])
    def test_positive_infinity(self, verb: str) -> None:
        """The sign is always shown on a positive infinity, in every verb."""
        assert fmt(verb, INF) == "+Inf"

    @pytest.mark.parametrize("verb", ["%v", "%f", "%e", "%E", "%g", "%G", "%s", "%.3f"])
    def test_negative_infinity(self, verb: str) -> None:
        assert fmt(verb, NINF) == "-Inf"

    def test_the_exponent_verb_no_longer_appends_an_exponent(self) -> None:
        """`%e` produced "Infinitye+01": the mantissa path ran on an infinity."""
        assert fmt("%e", INF) == "+Inf"
        assert fmt("%e", NAN) == "NaN"

    def test_quoting_quotes_the_go_spelling(self) -> None:
        assert fmt("%q", INF) == '"+Inf"'


class TestSignFlags:
    """Go's `fmt` forces a sign onto an infinity and withholds one from a NaN."""

    def test_the_plus_flag_changes_nothing_for_an_infinity(self) -> None:
        assert fmt("%+f", INF) == "+Inf"
        assert fmt("%+f", NINF) == "-Inf"

    def test_the_space_flag_replaces_the_plus(self) -> None:
        assert fmt("% f", INF) == " Inf"

    def test_the_space_flag_does_not_touch_a_negative_infinity(self) -> None:
        assert fmt("% f", NINF) == "-Inf"

    def test_a_nan_is_unsigned_unless_a_sign_was_asked_for(self) -> None:
        assert fmt("%f", NAN) == "NaN"
        assert fmt("%+f", NAN) == "+NaN"
        assert fmt("% f", NAN) == " NaN"


class TestPadding:
    """Two padding rules, because two different code paths do the padding."""

    def test_a_float_verb_never_zero_pads(self) -> None:
        """ "infinities and NaN ... shouldn't be padded with '0'" -- Go's fmt.

        Zero-padding would read as a number: "0000+Inf" says nothing sensible.
        """
        assert fmt("%08.2f", INF) == "    +Inf"
        assert fmt("%08e", INF) == "    +Inf"
        assert fmt("%08.2f", NAN) == "     NaN"

    def test_a_float_verb_still_pads_and_still_left_aligns(self) -> None:
        assert fmt("%10.2f", INF) == "      +Inf"
        assert fmt("%-10.2f", INF) == "+Inf      "
        assert fmt("%12.4e", NINF) == "        -Inf"

    def test_the_v_and_s_verbs_do_zero_pad(self) -> None:
        """They go through go-cty's own `formatPadWidth`, which honours the flag.

        Not a tidying opportunity: `%08.2f` is "    +Inf" and `%08v` is
        "0000+Inf" in go-cty, because only the float verbs delegate to Go's fmt.
        """
        assert fmt("%08v", INF) == "0000+Inf"
        assert fmt("%08s", INF) == "0000+Inf"
        assert fmt("%5v", INF) == " +Inf"
        assert fmt("%-5v", INF) == "+Inf "

    def test_precision_is_ignored(self) -> None:
        """There are no digits to round."""
        assert fmt("%.0f", INF) == "+Inf"
        assert fmt("%.10e", NINF) == "-Inf"


class TestTheIntegerVerbsRefuse:
    """`bf.Int(nil)` is inexact for an infinity, which is go-cty's refusal."""

    @pytest.mark.parametrize("verb", ["%d", "%b", "%o", "%x", "%X"])
    @pytest.mark.parametrize("number", [INF, NINF, NAN], ids=["inf", "-inf", "nan"])
    def test_an_integer_verb_is_refused(self, verb: str, number: Decimal) -> None:
        """A refusal, not the `OverflowError` that `int(Decimal("Infinity"))` raises."""
        with pytest.raises(CtyFunctionError, match="an integer is required"):
            fmt(verb, number)


class TestJsonFallback:
    """`%#v`, and `%v` of anything that is not a bare number or string."""

    def test_the_sharp_flag_refuses_an_infinity(self) -> None:
        """It wrote the bare token "Infinity", which no JSON parser accepts."""
        with pytest.raises(CtyFunctionError, match="cannot serialize infinity as JSON"):
            fmt("%#v", INF)

    def test_a_collection_holding_an_infinity_is_refused(self) -> None:
        """`%v` only fast-paths a *bare* number; a list goes through JSON."""
        value = CtyList(element_type=CtyNumber()).validate([INF])
        with pytest.raises(CtyFunctionError, match="cannot serialize infinity as JSON"):
            format_fn(CtyString().validate("%v"), value)


class TestFiniteNumbersAreUnchanged:
    """The guard must not cost the ordinary path."""

    def test_the_float_verbs(self) -> None:
        assert fmt("%f", Decimal("1.5")) == "1.500000"
        assert fmt("%e", Decimal("1.5")) == "1.500000e+00"
        assert fmt("%08.2f", Decimal("-42")) == "-0042.00"
        assert fmt("%g", Decimal("0.00001")) == "1e-05"

    def test_the_integer_verbs(self) -> None:
        assert fmt("%d", Decimal(42)) == "42"
        assert fmt("%x", Decimal(255)) == "ff"

    def test_the_v_verb(self) -> None:
        assert fmt("%v", Decimal("1.5")) == "1.5"
        assert fmt("%#v", Decimal("1.5")) == "1.5"


# 🐍🏗️🔚
