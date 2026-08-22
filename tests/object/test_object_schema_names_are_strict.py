#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""A `CtyObject` schema's attribute names are checked at construction.

The value side already refuses non-string keys and two keys that normalize to
the same NFC string. The schema side did not: `CtyObject({1: CtyString()})`
constructed and then failed inside `validate` with a bare `TypeError` from
`unicodedata.normalize`, and a schema naming the same attribute in NFC and NFD
spelling had two attributes that one input key filled.
"""

import unicodedata

import pytest

from pyvider.cty import CtyObject, CtyString
from pyvider.cty.exceptions import InvalidTypeError

NFC = unicodedata.normalize("NFC", "é")
NFD = unicodedata.normalize("NFD", "é")


def test_non_string_attribute_name_is_refused_at_construction() -> None:
    with pytest.raises(InvalidTypeError, match="must be strings"):
        CtyObject({1: CtyString()})  # type: ignore[dict-item]


def test_nfc_colliding_attribute_names_are_refused_at_construction() -> None:
    with pytest.raises(InvalidTypeError, match="normalize to the same NFC string"):
        CtyObject({NFC: CtyString(), NFD: CtyString()})


def test_nfd_spelled_schema_name_still_matches_nfc_value_key() -> None:
    """A single name in either spelling is fine; only a *pair* collides."""
    obj = CtyObject({NFD: CtyString()})
    assert obj.validate({NFC: "x"}).value[NFD].value == "x"
