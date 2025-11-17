#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Final hardening test suite to address all remaining coverage gaps, bringing
the library to a production-ready state of test coverage."""

from decimal import Decimal

import pytest

from pyvider.cty import (
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtyString,
    CtyValue,
    convert,
)
from pyvider.cty.exceptions import CtyConversionError
from pyvider.cty.functions import coalesce, greater_than, less_than
from pyvider.cty.values.markers import RefinedUnknownValue


def refined_unknown_num(
    lower_bound: tuple[Decimal, bool] | None = None,
    upper_bound: tuple[Decimal, bool] | None = None,
) -> CtyValue:
    return CtyValue.unknown(
        CtyNumber(),
        value=RefinedUnknownValue(number_lower_bound=lower_bound, number_upper_bound=upper_bound),
    )


class TestFinalCoverageSuite:
    """A single suite to cover all remaining untested lines."""

    # --- Coverage for: src/pyvider/cty/functions/comparison_functions.py ---
    def test_comparison_refined_known_boundary_cases(self) -> None:
        """Covers boundary checks for refined vs. known value comparisons."""
        # Case: a_unknown < b_known, where b_known == a_upper and inclusive=False
        # (unknown < 20) < 20 -> should be True
        unknown_lt_20 = refined_unknown_num(upper_bound=(Decimal("20"), False))
        known_20 = CtyNumber().validate(20)
        assert less_than(unknown_lt_20, known_20).value is True

        # Case: a_known > b_unknown, where a_known == b_lower and inclusive=False
        # 50 > (unknown > 50) -> should be False
        known_50 = CtyNumber().validate(50)
        unknown_gt_50 = refined_unknown_num(lower_bound=(Decimal("50"), False))
        assert greater_than(known_50, unknown_gt_50).value is False

    # --- Coverage for: src/pyvider/cty/conversion/explicit.py ---
    def test_convert_object_to_object_missing_required_attribute(self) -> None:
        """Covers the error path for a missing required attribute during object conversion."""
        source_type = CtyObject(attribute_types={"name": CtyString()})
        target_type = CtyObject(attribute_types={"name": CtyString(), "age": CtyNumber()})
        source_val = source_type.validate({"name": "Alice"})

        with pytest.raises(CtyConversionError, match="Missing required attribute 'age'"):
            convert(source_val, target_type)

    # --- Coverage for: src/pyvider/cty/values/base.py ---
    def test_value_comparison_on_malformed_value(self) -> None:
        """Covers internal TypeErrors for comparisons on malformed CtyValues."""
        # Create a CtyValue that should be comparable but whose internal .value is not
        malformed_number = CtyValue(vtype=CtyNumber(), value="not-a-decimal")
        n5 = CtyNumber().validate(5)

        # The comparison should fail inside the CtyValue dunder method, raising a Python TypeError
        # because it cannot compare a string to a Decimal.
        with pytest.raises(
            TypeError,
            match=r"'<' not supported between instances of 'str' and 'decimal\.Decimal'",
        ):
            _ = malformed_number < n5

    def test_collection_helpers_on_malformed_value(self) -> None:
        """Covers internal TypeErrors for helper methods on malformed CtyValues."""
        malformed_map = CtyValue(vtype=CtyMap(element_type=CtyString()), value=123)
        with pytest.raises(TypeError, match="Internal value of CtyMap must be a dict"):
            malformed_map.with_key("a", "b")

        malformed_list = CtyValue(vtype=CtyList(element_type=CtyString()), value=123)
        with pytest.raises(TypeError, match="Internal value of CtyList must be a list or tuple"):
            malformed_list.append("a")

    # --- Coverage for: src/pyvider/cty/codec.py ---
    def test_ext_hook_for_other_codes(self) -> None:
        """Covers the case where an unknown msgpack extension code is received."""
        from pyvider.cty.codec import _ext_hook
        from pyvider.cty.values.markers import UNREFINED_UNKNOWN

        # Any code other than 0 or 12 should be treated as an unrefined unknown
        assert _ext_hook(99, b"some-data") is UNREFINED_UNKNOWN

    # --- Coverage for: src/pyvider/cty/functions/structural_functions.py ---
    def test_coalesce_with_unknown(self) -> None:
        """Covers coalesce returning the first non-null, non-unknown value."""
        null_val = CtyValue.null(CtyString())
        unknown_val = CtyValue.unknown(CtyString())
        real_val = CtyString().validate("hello")
        # The presence of an unknown value before the real value should not
        # prevent the real value from being found.
        assert coalesce(null_val, unknown_val, real_val) == real_val


# 🌊🪢🔚
