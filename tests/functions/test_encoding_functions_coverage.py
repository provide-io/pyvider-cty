#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TODO: Add module docstring."""

import pytest

from pyvider.cty import CtyNumber, CtyString, CtyValue
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import csvdecode, jsondecode, jsonencode


class TestEncodingFunctionsCoverage:
    def test_jsonencode_unknown(self) -> None:
        assert jsonencode(CtyValue.unknown(CtyString())).is_unknown

    def test_jsonencode_error(self, mocker) -> None:
        mocker.patch(
            "pyvider.cty.functions.encoding_functions.cty_to_native",
            side_effect=Exception("test error"),
        )
        with pytest.raises(CtyFunctionError):
            jsonencode(CtyString().validate("a"))

    def test_jsondecode_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            jsondecode(CtyNumber().validate(123))

    def test_jsondecode_null_unknown(self) -> None:
        assert jsondecode(CtyValue.null(CtyString())).is_unknown
        assert jsondecode(CtyValue.unknown(CtyString())).is_unknown

    def test_jsondecode_invalid_json(self) -> None:
        with pytest.raises(CtyFunctionError):
            jsondecode(CtyString().validate("{not json}"))

    def test_csvdecode_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            csvdecode(CtyNumber().validate(123))

    def test_csvdecode_null_unknown(self) -> None:
        assert csvdecode(CtyValue.null(CtyString())).is_unknown
        assert csvdecode(CtyValue.unknown(CtyString())).is_unknown

    def test_csvdecode_invalid_csv(self, mocker) -> None:
        mocker.patch("csv.DictReader", side_effect=Exception("test error"))
        with pytest.raises(CtyFunctionError):
            csvdecode(CtyString().validate("a,b\n1,2"))


# 🌊🪢🔚
