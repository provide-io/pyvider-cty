#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Test suite for datetime functions (formatdate, timeadd)."""

import pytest

from pyvider.cty import CtyNumber, CtyString, CtyValue
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import formatdate, timeadd


# Helper functions for creating CtyValues to improve test readability
def S(v):
    return CtyString().validate(v)


class TestDateTimeFunctions:
    def test_formatdate(self) -> None:
        ts = S("2020-02-03T04:05:06Z")
        assert formatdate(S("2006-01-02"), ts).value == "2020-02-03"

    def test_timeadd(self) -> None:
        ts = S("2020-01-02T03:04:05Z")
        dur = S("1h30m")
        assert "T04:34:05" in timeadd(ts, dur).value

    def test_formatdate_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            formatdate(CtyNumber().validate(123), S("..."))
        with pytest.raises(CtyFunctionError):
            formatdate(S("..."), CtyNumber().validate(123))

    def test_formatdate_null_unknown(self) -> None:
        spec = S("YYYY")
        ts = S("2020-01-01T00:00:00Z")
        assert formatdate(CtyValue.null(CtyString()), ts).is_unknown
        assert formatdate(CtyValue.unknown(CtyString()), ts).is_unknown
        assert formatdate(spec, CtyValue.null(CtyString())).is_unknown
        assert formatdate(spec, CtyValue.unknown(CtyString())).is_unknown

    def test_formatdate_invalid_timestamp(self) -> None:
        with pytest.raises(CtyFunctionError):
            formatdate(S("YYYY"), S("not a timestamp"))

    def test_timeadd_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            timeadd(CtyNumber().validate(123), S("1h"))
        with pytest.raises(CtyFunctionError):
            timeadd(S("..."), CtyNumber().validate(123))

    def test_timeadd_null_unknown(self) -> None:
        ts = S("2020-01-01T00:00:00Z")
        dur = S("1h")
        assert timeadd(CtyValue.null(CtyString()), dur).is_unknown
        assert timeadd(CtyValue.unknown(CtyString()), dur).is_unknown
        assert timeadd(ts, CtyValue.null(CtyString())).is_unknown
        assert timeadd(ts, CtyValue.unknown(CtyString())).is_unknown

    def test_timeadd_invalid_timestamp(self) -> None:
        with pytest.raises(CtyFunctionError):
            timeadd(S("not a timestamp"), S("1h"))

    def test_timeadd_invalid_duration(self) -> None:
        with pytest.raises(CtyFunctionError):
            timeadd(
                S("2020-01-01T00:00:00Z"),
                S("not a duration"),
            )


# 🌊🪢🔚
