"""
Comprehensive test suite for src/pyvider/cty/values/base.py to address
coverage gaps, particularly for comparison operators and canonical sorting.
"""
import pytest

from pyvider.cty import (
    CtyBool,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
    CtyTuple,
    CtyValue,
)
from pyvider.cty.types.capsule import CtyCapsule


class TestCtyValueComparisonOperators:
    """Tests for __lt__, __le__, __gt__, __ge__ dunder methods."""

    def test_number_comparisons(self) -> None:
        n5 = CtyNumber().validate(5)
        n10 = CtyNumber().validate(10)
        assert (n5 < n10) is True
        assert (n10 > n5) is True
        assert (n5 <= n10) is True
        assert (n10 >= n5) is True
        assert (n5 <= n5) is True
        assert (n5 >= n5) is True
        assert (n10 < n5) is False

    def test_string_comparisons(self) -> None:
        s_a = CtyString().validate("a")
        s_b = CtyString().validate("b")
        assert (s_a < s_b) is True
        assert (s_b > s_a) is True
        assert (s_a <= s_b) is True
        assert (s_b >= s_a) is True
        assert (s_a <= s_a) is True
        assert (s_a >= s_a) is True
        assert (s_b < s_a) is False

    def test_comparisons_with_invalid_types(self) -> None:
        """Verify comparisons raise TypeError for non-comparable or mismatched types."""
        n5 = CtyNumber().validate(5)
        s_a = CtyString().validate("a")
        b_true = CtyBool().validate(True)

        with pytest.raises(TypeError, match="Cannot compare CtyValues of different types"):
            _ = n5 < s_a
        with pytest.raises(TypeError, match="Value of type bool is not comparable"):
            _ = b_true > CtyBool().validate(False)

    def test_comparisons_with_null_or_unknown(self) -> None:
        """Verify comparisons raise TypeError for null or unknown values."""
        n5 = CtyNumber().validate(5)
        null_n = CtyValue.null(CtyNumber())
        unknown_n = CtyValue.unknown(CtyNumber())

        with pytest.raises(TypeError, match="Cannot compare null or unknown values"):
            _ = n5 < null_n
        with pytest.raises(TypeError, match="Cannot compare null or unknown values"):
            _ = unknown_n > n5
        with pytest.raises(TypeError, match="Cannot compare CtyValue with str"):
            _ = n5 > "not-a-cty-value"


class TestCanonicalSortKey:
    """Tests the internal _canonical_sort_key method for go-cty compatibility."""

    def test_canonical_sorting_order(self) -> None:
        """
        Verifies the precise sorting order of different CtyValue types and values.
        Order: null, unknown, known (by type rank, then by value).
        """
        class Opaque: pass
        capsule_type = CtyCapsule("Opaque", Opaque)

        # Type order: Number(0), String(1), Bool(2), Tuple(3), Set(4), List(5), Map(6), Object(7), Capsule(8)
        values_to_sort = [
            CtyString().validate("b"),
            CtyValue.null(CtyNumber()),
            CtyList(element_type=CtyString()).validate(["a"]),
            CtyNumber().validate(10),
            CtyValue.unknown(CtyString()),
            CtyBool().validate(False),
            CtySet(element_type=CtyNumber()).validate({1, 2}),
            CtyMap(element_type=CtyString()).validate({"key": "value"}),
            CtyNumber().validate(5),
            CtyString().validate("a"),
            CtyBool().validate(True),
            capsule_type.validate(Opaque()),
            CtyObject({"attr": CtyString()}).validate({"attr": "val"}),
            CtyTuple((CtyNumber(),)).validate((1,)),
        ]

        # Sort the list using the canonical key
        sorted_values = sorted(values_to_sort, key=lambda v: v._canonical_sort_key())

        # Define the expected order of types and values
        expected_order = [
            CtyValue.null(CtyNumber()),
            CtyValue.unknown(CtyString()),
            CtyNumber().validate(5),
            CtyNumber().validate(10),
            CtyString().validate("a"),
            CtyString().validate("b"),
            CtyBool().validate(False),
            CtyBool().validate(True),
            CtyTuple((CtyNumber(),)).validate((1,)),
            CtySet(element_type=CtyNumber()).validate({1, 2}),
            CtyList(element_type=CtyString()).validate(["a"]),
            CtyMap(element_type=CtyString()).validate({"key": "value"}),
            CtyObject({"attr": CtyString()}).validate({"attr": "val"}),
            # Capsule is last, we'll check it separately
        ]

        # Assert the order is correct by comparing the CtyValue objects
        assert len(sorted_values) == len(expected_order) + 1
        for i in range(len(expected_order)):
            assert sorted_values[i] == expected_order[i]
        
        # Check the last element is the capsule
        assert isinstance(sorted_values[-1].type, CtyCapsule)
