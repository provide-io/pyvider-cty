#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`CtyMarksSerializationError` is a `SerializationError`.

It was a direct `CtyError` subclass, so `except SerializationError` around
`cty_to_msgpack` let the one serialization failure a provider is most likely
to hit -- a marked value -- straight through, while the serialization guide
called it "the more specific" `SerializationError`.
"""

import pytest

from pyvider.cty import CtyString
from pyvider.cty.codec import cty_to_msgpack
from pyvider.cty.exceptions import (
    CtyError,
    CtyMarksSerializationError,
    EncodingError,
    SerializationError,
)


def test_hierarchy() -> None:
    assert issubclass(CtyMarksSerializationError, SerializationError)
    assert issubclass(CtyMarksSerializationError, EncodingError)
    assert issubclass(CtyMarksSerializationError, CtyError)


def test_except_serialization_error_catches_a_marked_value() -> None:
    marked = CtyString().validate("secret").mark("sensitive")
    with pytest.raises(SerializationError) as excinfo:
        cty_to_msgpack(marked, CtyString())
    assert isinstance(excinfo.value, CtyMarksSerializationError)


def test_message_path_and_code_are_unchanged() -> None:
    err = CtyMarksSerializationError(path="a.b")
    assert str(err).startswith("value has marks, so it cannot be serialized (at a.b)")
    assert err.path == "a.b"
    assert err.code == "CTY_MARKS_NOT_SERIALIZABLE"
