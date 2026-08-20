#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`jsondecode` refuses an object key that is not already NFC-normalized.

go-cty decodes a JSON document twice: `ImpliedType` builds an object type from
the keys as written, and `Unmarshal` then looks each attribute up by a
normalized name. For a key the two passes spell differently, they disagree, and
go-cty reports `unsupported attribute`. This package's `CtyObject.validate`
normalizes both sides before looking an attribute up, so it decoded those
documents happily -- and a provider that accepted one would build state
Terraform refuses, which is the same argument that makes `csvdecode` as strict
as Go's reader here.

The rule is exactly NFC, measured rather than assumed. Three keys that NFC
changes are refused by go-cty and three it leaves alone are accepted, including
the `fi` ligature -- which *NFKC* would change and NFC does not -- so the
boundary is the normal form and not "looks unusual".

Found on 2026-08-20 by `tests/compatibility/test_stdlib_fuzz.py` on a fresh
seed, from `{"\\uf900": null}`. Every expectation was read from
`soup-go cty call jsondecode` against go-cty v1.19.0; these run without a Go
toolchain.

Keys are written as escapes throughout. Written as literals they are normalized
in transit by editors and shells, which is exactly the confusion this rule is
about -- an early version of this check appeared to pass for that reason.
"""

from __future__ import annotations

import json
import unicodedata

import pytest

from pyvider.cty import CtyString
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import STDLIB

S = CtyString()

# NFC leaves these alone, and go-cty accepts them.
STABLE = [
    ("plain ascii", "a"),
    ("a precomposed e-acute", "é"),
    ("the fi ligature, which only NFKC touches", "ﬁ"),
    ("an already-composed CJK ideograph", "豈"),
    ("an emoji", "\U0001f600"),
]

# NFC rewrites these, and go-cty refuses them.
CHANGED = [
    ("e followed by a combining acute", "é"),
    ("the ohm sign, which NFC maps to omega", "Ω"),
    ("a CJK compatibility ideograph", "豈"),
    ("an angstrom sign", "Å"),
]


def document(key: str) -> str:
    return "{" + json.dumps(key) + ": null}"


def decode(key: str) -> object:
    return STDLIB["jsondecode"](S.validate(document(key)))


@pytest.mark.parametrize(("label", "key"), CHANGED, ids=[case[0] for case in CHANGED])
def test_a_key_that_nfc_rewrites_is_refused(label: str, key: str) -> None:
    assert unicodedata.normalize("NFC", key) != key, f"{label} is not actually a changing key"

    with pytest.raises(CtyFunctionError, match="unsupported attribute"):
        decode(key)


@pytest.mark.parametrize(("label", "key"), STABLE, ids=[case[0] for case in STABLE])
def test_a_key_nfc_leaves_alone_still_decodes(label: str, key: str) -> None:
    assert unicodedata.normalize("NFC", key) == key, f"{label} is not actually a stable key"

    decoded = decode(key)

    assert list(decoded.type.attribute_types) == [key], label  # type: ignore[attr-defined]


def test_the_refusal_reaches_a_nested_object() -> None:
    """`ImpliedType` walks the whole document, so the disagreement is not only
    a top-level one."""
    nested = json.dumps({"outer": {"豈": None}})

    with pytest.raises(CtyFunctionError, match="unsupported attribute"):
        STDLIB["jsondecode"](S.validate(nested))


def test_a_key_inside_an_array_is_reached_too() -> None:
    nested = json.dumps([{"Ω": None}])

    with pytest.raises(CtyFunctionError, match="unsupported attribute"):
        STDLIB["jsondecode"](S.validate(nested))


def test_a_string_value_is_normalized_on_both_sides() -> None:
    """Which is *why* only the key case diverged.

    go-cty normalizes a decoded string to NFC, and so does this package -- an
    `e` plus a combining acute comes back as a single composed code point from
    both. That is what makes the key behaviour asymmetric: `Unmarshal`
    normalizes, `ImpliedType` does not, so a key survives one pass in one form
    and the other pass in another. The value path has no such split, so there is
    nothing to disagree about and nothing here to fix.

    Built from `chr` rather than written as a literal: an unnormalized literal
    is composed in transit by editors and shells, and an earlier version of this
    test asserted against a literal that had been.
    """
    combining = chr(0x65) + chr(0x301)
    composed = chr(0xE9)
    assert unicodedata.normalize("NFC", combining) == composed

    decoded = STDLIB["jsondecode"](S.validate(json.dumps({"a": combining})))

    assert decoded.value["a"].value == composed


def test_an_ordinary_document_is_unchanged() -> None:
    decoded = STDLIB["jsondecode"](S.validate('{"name": "web", "port": 8080}'))

    assert decoded.value["name"].value == "web"


# 🌊🪢🔚
