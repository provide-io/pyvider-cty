#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


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

    def test_jsondecode_refuses_a_null_and_defers_an_unknown(self) -> None:
        with pytest.raises(CtyFunctionError):
            jsondecode(CtyValue.null(CtyString()))
        assert jsondecode(CtyValue.unknown(CtyString())).is_unknown

    def test_jsondecode_invalid_json(self) -> None:
        with pytest.raises(CtyFunctionError):
            jsondecode(CtyString().validate("{not json}"))

    def test_csvdecode_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            csvdecode(CtyNumber().validate(123))

    def test_csvdecode_refuses_a_null_and_defers_an_unknown(self) -> None:
        with pytest.raises(CtyFunctionError):
            csvdecode(CtyValue.null(CtyString()))
        assert csvdecode(CtyValue.unknown(CtyString())).is_unknown

    @pytest.mark.parametrize(
        ("document", "why"),
        [
            ("", "missing header line"),
            ("a,a\n1,2", "duplicate column name"),
            ("a,b\n1", "wrong number of fields"),
            ("a,b\n1,2,3", "wrong number of fields"),
        ],
    )
    def test_csvdecode_invalid_csv(self, document: str, why: str) -> None:
        """The inputs go-cty rejects.

        This used to mock csv.DictReader into raising, which tested that the
        try/except was present rather than that any real document is rejected --
        and it went on passing after the implementation stopped using DictReader
        at all.
        """
        with pytest.raises(CtyFunctionError, match=why):
            csvdecode(CtyString().validate(document))


# 🌊🪢🔚
