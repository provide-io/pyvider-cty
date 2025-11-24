#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
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

    def test_numeric_refined_propagation_coverage(self) -> None:
        """Covers various unexercised branches in refined unknown propagation."""
        # Case: add with one bound missing
        r1 = refined_unknown_num(lower_bound=(Decimal(10), True))
        r2 = refined_unknown_num(upper_bound=(Decimal(20), True))
        res_add = add(r1, r2)
        assert res_add.is_unknown and res_add.value.number_lower_bound is None

        # Case: subtract with known minuend
        known_100 = CtyNumber().validate(100)
        res_sub = subtract(known_100, r1)
        assert res_sub.is_unknown and res_sub.value.number_upper_bound is not None

        # Case: multiply with two refined unknowns (currently simplified, will be unknown)
        res_mul = multiply(r1, r2)
        assert res_mul.is_unknown and res_mul.value.number_lower_bound is None

    # --- Coverage for: src/pyvider/cty/conversion/explicit.py ---

    def test_convert_list_to_list_of_dynamic(self) -> None:
        """Covers converting a typed list to a list of dynamic."""
        source_val = CtyList(element_type=CtyString()).validate(["a", "b"])
        target_type = CtyList(element_type=CtyDynamic())
        result = convert(source_val, target_type)
        assert result.type.equal(target_type)
        assert result.value[0].type.is_dynamic_type()

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
