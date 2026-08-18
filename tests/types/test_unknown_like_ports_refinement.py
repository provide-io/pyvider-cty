#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""A refinement must not outlive the type it constrains.

`unknown_like` receives bare markers straight off the wire: the msgpack decoder
rebuilds only the top-level value against the schema, so every nested unknown
arrives at its element type carrying whatever refinement the sender wrote. A
string prefix on a number is not a weaker fact but a malformed one, and go-cty
refuses the resulting bytes outright -- "string prefix refinement for
non-string type" -- which is a protocol failure rather than a plan diff.
"""

import msgpack
from msgpack import ExtType

from pyvider.cty import CtyList, CtyNumber, CtyString
from pyvider.cty.codec import cty_from_msgpack, cty_to_msgpack
from pyvider.cty.values.markers import UNREFINED_UNKNOWN

# One unknown element refined with a string prefix, as a sender would write it
# for a list of strings.
PREFIXED_UNKNOWN = msgpack.packb([ExtType(12, msgpack.packb({2: "https://"}))])


def test_a_string_prefix_does_not_survive_onto_a_number() -> None:
    decoded = cty_from_msgpack(PREFIXED_UNKNOWN, CtyList(element_type=CtyNumber()))

    element = decoded.value[0]
    assert element.type.equal(CtyNumber())
    assert element.value is UNREFINED_UNKNOWN


def test_the_re_encoded_bytes_are_ones_go_cty_accepts() -> None:
    """go-cty decodes 91d40000 as [unknown]; the prefixed form it rejects."""
    target = CtyList(element_type=CtyNumber())

    round_tripped = cty_to_msgpack(cty_from_msgpack(PREFIXED_UNKNOWN, target), target)

    assert round_tripped.hex() == "91d40000"


def test_a_string_prefix_survives_onto_a_string() -> None:
    """Narrowing must not become discarding: the legal case is untouched."""
    target = CtyList(element_type=CtyString())

    decoded = cty_from_msgpack(PREFIXED_UNKNOWN, target)

    assert decoded.value[0].value.string_prefix == "https://"
    assert cty_to_msgpack(decoded, target) == PREFIXED_UNKNOWN
