#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""This test suite specifically targets the remaining coverage gaps in
src/pyvider/cty/values/base.py to harden the CtyValue object against
internal inconsistencies and edge cases."""

import pytest

from pyvider.cty import CtyList, CtyMap, CtyNumber, CtyString, CtyValue


class TestCtyValueCoverage:
    """Targeted tests for CtyValue error paths and dunder methods."""

    def test_check_comparable_raises_on_non_cty_value(self) -> None:
        """Covers the initial type check in _check_comparable."""
        val = CtyNumber().validate(1)
        with pytest.raises(TypeError, match="Cannot compare CtyValue with int"):
            val._check_comparable(123)

    def test_check_comparable_raises_on_different_types(self) -> None:
        """Covers the type equality check in _check_comparable."""
        val1 = CtyNumber().validate(1)
        val2 = CtyString().validate("1")
        with pytest.raises(TypeError, match="Cannot compare CtyValues of different types"):
            val1._check_comparable(val2)

    def test_check_comparable_raises_on_non_comparable_type(self) -> None:
        """Covers the final check for comparable types (Number or String)."""
        val = CtyList(element_type=CtyString()).validate([])
        # CORRECTED: The error message uses the string representation of the type,
        # which is 'list(string)', not the class name 'CtyList'. The parentheses
        # must be escaped for the regex match.
        with pytest.raises(TypeError, match="Value of type list\\(string\\) is not comparable"):
            val._check_comparable(val)

    def test_comparison_dunders_on_malformed_internal_value(self) -> None:
        """
        Covers the TypeError raised if the internal .value does not support
        the comparison operation (e.g., '<').
        """
        # Create a CtyValue that should be comparable but has a bad internal value.
        malformed_number = CtyValue(vtype=CtyNumber(), value="not-a-number")
        n5 = CtyNumber().validate(5)

        with pytest.raises(TypeError, match="'<' not supported"):
            _ = malformed_number < n5
        with pytest.raises(TypeError, match="'<=' not supported"):
            _ = malformed_number <= n5
        with pytest.raises(TypeError, match="'>' not supported"):
            _ = malformed_number > n5
        with pytest.raises(TypeError, match="'>=' not supported"):
            _ = malformed_number >= n5

    def test_contains_on_null_and_unknown(self) -> None:
        """Covers __contains__ branches for null and unknown values."""
        null_val = CtyValue.null(CtyList(element_type=CtyString()))
        unknown_val = CtyValue.unknown(CtyList(element_type=CtyString()))
        item = CtyString().validate("a")

        assert (item in null_val) is False
        assert (item in unknown_val) is False

    def test_iter_on_non_iterable_type(self) -> None:
        """Covers the final TypeError in __iter__ for non-iterable types."""
        val = CtyString().validate("a")
        with pytest.raises(TypeError, match="is not iterable"):
            list(iter(val))

    def test_collection_helpers_on_malformed_internal_values(self) -> None:
        """
        Covers TypeErrors in collection helpers when the internal .value
        is not of the expected container type (dict, list, tuple).
        """
        malformed_map = CtyValue(vtype=CtyMap(element_type=CtyString()), value=123)
        with pytest.raises(TypeError, match="Internal value of CtyMap must be a dict"):
            malformed_map.with_key("a", "b")
        with pytest.raises(TypeError, match="Internal value of CtyMap must be a dict"):
            malformed_map.without_key("a")

        malformed_list = CtyValue(vtype=CtyList(element_type=CtyString()), value=123)
        with pytest.raises(TypeError, match="Internal value of CtyList must be a list or tuple"):
            malformed_list.append("a")
        with pytest.raises(TypeError, match="Internal value of CtyList must be a list or tuple"):
            malformed_list.with_element_at(0, "a")

    def test_without_key_on_missing_key(self) -> None:
        """Covers the branch where the key to be removed does not exist."""
        map_val = CtyMap(element_type=CtyString()).validate({"a": "b"})
        # This should be a no-op and return the same value.
        new_val = map_val.without_key("non-existent-key")
        assert new_val is map_val


# 🌊🪢🔚
