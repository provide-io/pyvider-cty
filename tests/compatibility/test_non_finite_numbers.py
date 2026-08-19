#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Infinity and NaN, where go-cty's `big.Float` and a `Decimal` part company.

go-cty holds a number in a `big.Float`. That type has `+Inf` and `-Inf` and
**no NaN at all** -- `SetFloat64` panics on one -- so `cty.NumberVal` cannot
carry a NaN and every string that parses to one is refused. A `Decimal` carries
both, which is where the two implementations diverge.

Two separate questions, answered differently on purpose.

**The wire is closed.** A NaN used to serialize, as the msgpack string `"NaN"`,
and go-cty reading those bytes answers `number is required` -- a value this
package could put on the wire that Terraform's own library could not read back.
Both codecs refuse it now. Infinity is untouched: go-cty writes it as a float64
and reads ours, so it round-trips on both sides. JSON refuses an infinity on
both sides, because JSON has no spelling for one.

**Input acceptance is recorded, not matched.** go-cty parses a string with Go's
`big.ParseFloat` grammar, which takes `inf`, `+Inf` and `-Inf` and nothing else;
`Decimal` also takes `Infinity`, `infinity` and `INF`. Matching that exactly
means narrowing what `convert(string, number)` accepts, which is a breaking
change for a config that spells it the long way, and there is no wire
consequence -- every spelling this package accepts produces the same `+Inf` that
go-cty writes and reads. So it stays, and the xfail below is what keeps it from
being forgotten.

Found 2026-08-19 by the generated conversion property, which drew the string
`"NaN"` at 800 examples where 60 had not reached it.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from pyvider.cty import CtyNumber, CtyString
from pyvider.cty.codec import cty_from_msgpack, cty_to_msgpack
from pyvider.cty.conversion import convert
from pyvider.cty.exceptions import SerializationError
from pyvider.cty.json_codec import CtyJsonError, cty_to_json
from tests.compatibility._oracle import run, type_spec

pytestmark = pytest.mark.compat

N = CtyNumber()
S = CtyString()


def go_converts(text: str) -> bool:
    """Whether go-cty converts `text` from string to number."""
    reported = run("cty", "convert-value", "--from", type_spec(S), "--to", type_spec(N), f'"{text}"')
    return bool(reported.get("ok"))


class TestTheWireRefusesANaN:
    def test_msgpack_refuses_it(self) -> None:
        """Was the string `"NaN"`, which go-cty reads as `number is required`."""
        with pytest.raises(SerializationError, match="NaN"):
            cty_to_msgpack(N.validate(Decimal("NaN")), N)

    def test_json_refuses_it_and_says_so(self) -> None:
        """The message used to say `infinity` for a NaN."""
        with pytest.raises(CtyJsonError, match="NaN"):
            cty_to_json(N.validate(Decimal("NaN")), N)

    def test_go_cty_refuses_the_bytes_this_package_used_to_write(self) -> None:
        """The reason the refusal is at the codec rather than at construction."""
        import base64

        reported = run(
            "cty", "msgpack", "decode", "--type", type_spec(N), base64.b64encode(b"\xa3NaN").decode()
        )

        assert not reported.get("ok")
        assert "number is required" in str(reported.get("error"))


class TestInfinityIsUntouched:
    @pytest.mark.parametrize("literal", ["Infinity", "-Infinity"])
    def test_it_round_trips_through_msgpack_on_both_sides(self, literal: str) -> None:
        value = N.validate(Decimal(literal))
        encoded = cty_to_msgpack(value, N)

        assert cty_from_msgpack(encoded, N).value == value.value

        theirs = run("cty", "msgpack", "encode", "--type", type_spec(N), f'{{"$number":"{literal}"}}')
        assert theirs["hex"] == encoded.hex(), "go-cty writes the same float64"

    def test_json_refuses_an_infinity_on_both_sides(self) -> None:
        with pytest.raises(CtyJsonError, match="infinity"):
            cty_to_json(N.validate(Decimal("Infinity")), N)

        theirs = run("cty", "json", "marshal", '{"$number":"Infinity"}', "--type", type_spec(N))
        assert not theirs.get("ok")


class TestStringParsing:
    @pytest.mark.parametrize("spelling", ["inf", "+Inf", "-Inf"])
    def test_go_ctys_own_spellings_convert_on_both_sides(self, spelling: str) -> None:
        assert go_converts(spelling), f"go-cty should accept {spelling}"
        assert not convert(S.validate(spelling), N).value.is_finite()

    @pytest.mark.parametrize("spelling", ["NaN", "nan", "Infinity", "-Infinity", "infinity", "INF"])
    def test_go_cty_refuses_the_spellings_decimal_also_takes(self, spelling: str) -> None:
        """Pinned so a change to `big.ParseFloat`'s grammar shows up here."""
        assert not go_converts(spelling), f"go-cty should refuse {spelling}"

    @pytest.mark.xfail(
        strict=True,
        reason="Decimal parses more non-finite spellings than Go's big.ParseFloat; "
        "accepted divergence, no wire consequence",
    )
    @pytest.mark.parametrize("spelling", ["Infinity", "-Infinity"])
    def test_this_package_would_ideally_refuse_them_too(self, spelling: str) -> None:
        """The recorded half. Narrowing this is a breaking change for a config
        that spells infinity the long way, and every spelling accepted here
        produces the same `+Inf` go-cty writes -- so the divergence is in what
        is *accepted*, never in what is sent."""
        with pytest.raises(Exception, match="number"):
            convert(S.validate(spelling), N)


# 🌊🪢🔚
