#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""A value in a `dynamic` position carries its concrete type across the wire.

go-cty writes `[type, value]` for *every* value at `cty.DynamicPseudoType`,
because the declared type says nothing and the envelope is the only thing
carrying what the value actually is. This package checked knownness first, so an
unknown-of-string went out as a bare `d40000` and a null-of-string as a bare
`c0`.

That is not a spelling difference. Asked to read those bytes at a dynamic
position, go-cty v1.19.0 answers `type=dynamic`, where its own bytes give
`type=string` -- measured directly rather than through the harness, whose rich
report does not carry an unknown's type and so cannot show it:

    ours: bare unknown d40000          type=dynamic   known=false
    go:   envelope + unknown           type=string    known=false

Deferring as `string` and deferring as `dynamic` are different answers to a
Terraform plan; the parity file already records that as the reason refinements
and types travel with an unknown.

**The unknown half is fixed. The null half is not, and it is a different bug**
one layer up: `CtyDynamic().validate(CtyValue.null(CtyString()))` collapses to a
bare dynamic null, discarding the inner type before the codec is ever reached.
The codec cannot write what it is not given, and retaining it changes what a
dynamic null *is* -- so it is recorded here as a strict xfail rather than
patched at the codec, which would only paper over the loss.

That half is also invisible to `test_differential_properties`, and instructively
so: that suite spells our value for the harness with `rich`/`dynamic_arg`, so
when this package drops information *before* the comparison, both sides are
handed the same lossy value and agree. A differential suite can only see what
survives into the value it compares. This file constructs go's side by hand for
exactly that reason.
"""

from __future__ import annotations

import pytest

from pyvider.cty import CtyDynamic, CtyString, CtyValue
from pyvider.cty.codec import cty_to_msgpack
from tests.compatibility._oracle import run

pytestmark = pytest.mark.compat

DYNAMIC = CtyDynamic()
# `["string", <value>]` with the type as a msgpack bin, which is go-cty's
# envelope. Written out rather than derived so a change to our own encoder
# cannot quietly move the expectation with it.
STRING_TYPE_ENVELOPE = "92c40822737472696e6722"


def go_encodes(spec: str) -> str:
    """go-cty's msgpack for a value at a dynamic position, as hex."""
    reported = run("cty", "msgpack", "encode", spec, "--type", '"dynamic"')
    assert reported.get("ok"), reported
    return str(reported["hex"])


class TestTheEnvelopeIsWritten:
    def test_a_known_value_carries_its_type(self) -> None:
        """The case that always worked, kept so a fix cannot trade one for the other."""
        ours = cty_to_msgpack(DYNAMIC.validate(CtyString().validate("x")), DYNAMIC).hex()

        assert ours.startswith(STRING_TYPE_ENVELOPE)
        assert ours == go_encodes('{"$dynamic":{"type":"string","value":"x"}}')

    def test_an_unknown_carries_its_type(self) -> None:
        """Was `d40000`, which go-cty reads back as an unknown of *dynamic*."""
        ours = cty_to_msgpack(DYNAMIC.validate(CtyValue.unknown(CtyString())), DYNAMIC).hex()

        assert ours.startswith(STRING_TYPE_ENVELOPE)
        assert ours == go_encodes('{"$dynamic":{"type":"string","value":{"$unknown":true}}}')

    def test_a_value_with_no_concrete_type_is_still_written_bare(self) -> None:
        """An unknown *of* dynamic has no type to carry, and go-cty writes it bare."""
        ours = cty_to_msgpack(CtyValue.unknown(DYNAMIC), DYNAMIC).hex()

        assert ours == "d40000"


@pytest.mark.xfail(
    strict=True,
    reason="CtyDynamic.validate discards a null's concrete type before the codec sees it",
)
def test_a_null_carries_its_type() -> None:
    """Recorded, not patched: the loss happens a layer above the codec.

    `CtyDynamic().validate(CtyValue.null(CtyString()))` returns a value whose
    payload is `None` rather than the string null it was handed, so there is no
    type left to write. Fixing it means changing what a dynamic null retains,
    which reaches equality and identity as well as the wire -- a deliberate
    change rather than a codec patch.
    """
    ours = cty_to_msgpack(DYNAMIC.validate(CtyValue.null(CtyString())), DYNAMIC).hex()

    assert ours == go_encodes('{"$dynamic":{"type":"string","value":{"$null":true}}}')


# 🌊🪢🔚
