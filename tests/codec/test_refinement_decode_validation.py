#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Refinement bytes arrive from the wire, so they are input, not data.

This is the one refinement path that does not go through RefinementBuilder,
whose stated purpose is to refuse an inconsistent refinement rather than record
one. Unchecked, a malformed field was stored verbatim and surfaced later as an
AttributeError from inside the encoder -- outside the CtyError taxonomy, so a
provider's `except CtyError` missed it and bad input read as a crash.
"""

from decimal import Decimal

import msgpack
from msgpack import ExtType
import pytest

from pyvider.cty import CtyList, CtyString
from pyvider.cty.codec import cty_from_msgpack
from pyvider.cty.exceptions import CtyError


def _refined(payload: dict[int, object]) -> bytes:
    return msgpack.packb(ExtType(12, msgpack.packb(payload)))


@pytest.mark.parametrize(
    ("payload", "why"),
    [
        ({2: 5}, "a string prefix that is not a string"),
        ({1: "notabool"}, "a nullness flag that is not a bool"),
        ({1: 1}, "a nullness flag that is an int, which bool would otherwise accept"),
        ({5: -3}, "a negative collection length"),
    ],
)
def test_a_malformed_refinement_is_refused_within_the_taxonomy(payload: dict[int, object], why: str) -> None:
    with pytest.raises(CtyError):
        cty_from_msgpack(_refined(payload), CtyList(element_type=CtyString()))


def test_well_formed_refinements_still_decode() -> None:
    """Validation must not become refusal: the legal forms are untouched."""
    assert cty_from_msgpack(_refined({2: "https://"}), CtyString()).value.string_prefix == "https://"
    assert cty_from_msgpack(_refined({1: True}), CtyString()).value.is_known_null is True


def test_python_json_literals_are_refused() -> None:
    """NaN, Infinity and -Infinity are Python extensions, not JSON.

    Go's encoding/json rejects them outright. Accepting one produced a value
    this package's own JSON encoder then refused, while the msgpack encoder
    wrote the string "NaN" into a number slot -- a document only one of two
    codecs would take.
    """
    from pyvider.cty import CtyNumber
    from pyvider.cty.json_codec import CtyJsonError, cty_from_json

    # CtyJsonError, not CtyError: this module's errors descend from
    # CtyValidationError and sit outside the CtyError branch entirely. That
    # split is a real wart, filed separately -- asserting the type this code
    # actually raises rather than the one it arguably should.
    for literal in (b"NaN", b"Infinity", b"-Infinity"):
        with pytest.raises(CtyJsonError):
            cty_from_json(literal, CtyNumber())


def test_ordinary_json_numbers_still_decode() -> None:
    from pyvider.cty import CtyNumber
    from pyvider.cty.json_codec import cty_from_json

    assert cty_from_json(b"1.5", CtyNumber()).value == Decimal("1.5")
