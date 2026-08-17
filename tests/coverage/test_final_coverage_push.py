#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Final test suite to address all significant remaining coverage gaps, bringing
the library to a production-ready state of test coverage."""

from decimal import Decimal

import pytest

from pyvider.cty import (
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyString,
    CtyValue,
    convert,
)
from pyvider.cty.functions import add, greater_than, less_than, multiply, subtract
from pyvider.cty.values.markers import RefinedUnknownValue


def refined_unknown_num(
    lower_bound: tuple[Decimal, bool] | None = None,
    upper_bound: tuple[Decimal, bool] | None = None,
) -> CtyValue:
    return CtyValue.unknown(
        CtyNumber(),
        value=RefinedUnknownValue(number_lower_bound=lower_bound, number_upper_bound=upper_bound),
    )


class TestFinalCoveragePush:
    """A single suite to cover all remaining untested lines."""

    # --- Coverage for: src/pyvider/cty/values/base.py ---

    def test_value_comparison_dunders_on_malformed_value(self) -> None:
        """Covers internal TypeErrors for comparisons on malformed CtyValues."""
        malformed_number = CtyValue(vtype=CtyNumber(), value="not-a-decimal")
        n5 = CtyNumber().validate(5)

        with pytest.raises(TypeError):
            _ = malformed_number < n5
        with pytest.raises(TypeError):
            _ = malformed_number <= n5
        with pytest.raises(TypeError):
            _ = malformed_number > n5
        with pytest.raises(TypeError):
            _ = malformed_number >= n5

    def test_value_comparison_dunders_on_non_comparable_type(self) -> None:
        """Covers TypeErrors when comparing uncomparable CtyValue types."""
        list_val = CtyList(element_type=CtyString()).validate([])
        with pytest.raises(TypeError, match="not comparable"):
            _ = list_val < list_val
        with pytest.raises(TypeError, match="not comparable"):
            _ = list_val <= list_val
        with pytest.raises(TypeError, match="not comparable"):
            _ = list_val > list_val
        with pytest.raises(TypeError, match="not comparable"):
            _ = list_val >= list_val

    def test_collection_helpers_on_malformed_value(self) -> None:
        """Covers internal TypeErrors for helper methods on malformed CtyValues."""
        malformed_map = CtyValue(vtype=CtyMap(element_type=CtyString()), value=123)
        with pytest.raises(TypeError, match="Internal value of CtyMap must be a dict"):
            malformed_map.without_key("a")

        malformed_list = CtyValue(vtype=CtyList(element_type=CtyString()), value=123)
        with pytest.raises(TypeError, match="Internal value of CtyList must be a list or tuple"):
            malformed_list.with_element_at(0, "a")

    # --- Coverage for: src/pyvider/cty/functions/comparison_functions.py ---

    def test_comparison_both_refined_can_resolve(self) -> None:
        """Covers comparison where two refined unknowns do not overlap."""
        # (unknown < 10) < (unknown > 20) -> should be True
        unknown_lt_10 = refined_unknown_num(upper_bound=(Decimal("10"), False))
        unknown_gt_20 = refined_unknown_num(lower_bound=(Decimal("20"), False))
        assert less_than(unknown_lt_10, unknown_gt_20).value is True
        assert greater_than(unknown_gt_20, unknown_lt_10).value is True

    # --- Coverage for: src/pyvider/cty/functions/numeric_functions.py ---

    def test_arithmetic_discards_a_refined_unknowns_bounds(self) -> None:
        """`subtract(100, unknown >= 10)` carried an upper bound until 2026-08-17.

        None of the arithmetic functions in go-cty's `stdlib/number.go` sets
        `AllowUnknown`, so none of them ever reaches its implementation with an
        unknown argument: `Function.Call` short-circuits at `function.go:314` and
        returns `cty.UnknownVal(cty.Number)` carrying only `refineNonNull`. The
        narrowing does exist in go-cty, on `cty.Value.Add` and friends
        (`value_ops.go:623`), which is a surface this package does not have.
        Verified against the oracle for `add`, `multiply`, `negate` and `abs`.

        Fully covered in `tests/functions/test_numeric_refined_unknowns.py`; kept
        here because this file drives the module by line.
        """
        r1 = refined_unknown_num(lower_bound=(Decimal(10), True))
        r2 = refined_unknown_num(upper_bound=(Decimal(20), True))
        only_not_null = RefinedUnknownValue(is_known_null=False)

        assert add(r1, r2).value == only_not_null
        assert subtract(CtyNumber().validate(100), r1).value == only_not_null
        assert multiply(r1, r2).value == only_not_null

    # --- Coverage for: src/pyvider/cty/conversion/explicit.py ---

    def test_convert_list_to_list_of_dynamic(self) -> None:
        """Covers converting a typed list to a list of dynamic."""
        source_val = CtyList(element_type=CtyString()).validate(["a", "b"])
        target_type = CtyList(element_type=CtyDynamic())
        result = convert(source_val, target_type)
        # A dynamic element type in the target is the absence of a constraint,
        # so the concrete element type survives. See test_explicit_conversion.
        assert result.type.equal(CtyList(element_type=CtyString()))
        assert not result.value[0].type.is_dynamic_type()

    # --- Coverage for: src/pyvider/cty/conversion/adapter.py ---

    def test_cty_to_native_with_malformed_set(self) -> None:
        """Covers cty_to_native with a CtySet whose internal value is not iterable."""
        from pyvider.cty import CtySet
        from pyvider.cty.conversion.adapter import cty_to_native

        malformed_set = CtyValue(vtype=CtySet(element_type=CtyString()), value=123)
        assert cty_to_native(malformed_set) == []

    # --- Coverage for: src/pyvider/cty/types/base.py ---

    def test_type_protocol_conformance_check(self) -> None:
        """Covers the runtime_checkable branches of the CtyTypeProtocol."""
        from pyvider.cty.types.base import CtyTypeProtocol

        class IncompleteType:
            def validate(self, value) -> None:
                pass

        assert not isinstance(IncompleteType(), CtyTypeProtocol)


# 🌊🪢🔚
