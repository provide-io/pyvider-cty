#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


import pytest

from pyvider.cty import CtyBool, CtyNumber, CtyString
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import to_bool, to_number, to_string


def test_to_string() -> None:
    assert to_string(CtyNumber().validate(123)).value == "123"
    assert to_string(CtyBool().validate(True)).value == "true"


def test_to_number() -> None:
    assert to_number(CtyString().validate("123")).value == 123
    with pytest.raises(CtyFunctionError):
        to_number(CtyString().validate("abc"))


def test_to_bool() -> None:
    assert to_bool(CtyString().validate("true")).value is True
    assert to_bool(CtyString().validate("false")).value is False
    with pytest.raises(CtyFunctionError):
        to_bool(CtyString().validate("abc"))


# 🌊🪢🔚
