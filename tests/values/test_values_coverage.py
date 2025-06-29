import pytest
from decimal import Decimal
from pyvider.cty import (
    CtyBool, CtyList, CtyMap, CtyNumber, CtyObject, CtySet, CtyString, CtyTuple, CtyValue, CtyDynamic
)
from pyvider.cty.marks import CtyMark
from pyvider.cty.exceptions import CtyValidationError

class TestCtyValueCoverage:
    """Targeted tests to improve code coverage for pyvider.cty.values.base."""

    def test_post_init_consistency_checks(self):
        """Covers the internal state correction in __attrs_post_init__."""
        # Test that an unknown value cannot also be null or have a value.
        val = CtyValue(vtype=CtyString(), value="a", is_unknown=True, is_null=True)
        assert val.is_unknown
        assert not val.is_null
        assert val._value is None

        # Test that a null value cannot have a value.
        val_null = CtyValue(vtype=CtyString(), value="a", is_null=True)
        assert val_null.is_null
        assert val_null._value is None

    def test_len_on_non_container(self):
        """Covers the __len__ TypeError for non-container types."""
        val = CtyNumber().validate(123)
        with pytest.raises(TypeError, match="has no len()"):
            len(val)

    def test_iter_on_non_container(self):
        """Covers the __iter__ TypeError for non-container types."""
        val = CtyBool().validate(True)
        with pytest.raises(TypeError, match="is not iterable"):
            iter(val)

    def test_getitem_error_paths(self):
        """Covers TypeError paths for __getitem__."""
        # On null and unknown values
        list_type = CtyList(element_type=CtyString())
        null_val = CtyValue.null(list_type)
        unknown_val = CtyValue.unknown(list_type)
        with pytest.raises(TypeError, match="Cannot index into unknown or null value"):
            _ = null_val[0]
        with pytest.raises(TypeError, match="Cannot index into unknown or null value"):
            _ = unknown_val[0]

        # On object with non-string key
        obj_type = CtyObject({"name": CtyString()})
        obj_val = obj_type.validate({"name": "test"})
        with pytest.raises(TypeError, match="Object attribute name must be a string"):
            _ = obj_val[123]
        
        # On a non-subscriptable type
        num_val = CtyNumber().validate(42)
        with pytest.raises(TypeError, match="is not subscriptable"):
            _ = num_val[0]

    def test_hash_of_unhashable_value(self):
        """Covers the fallback hashing mechanism for unhashable internal values."""
        list_val = CtyList(element_type=CtyString()).validate(["a"])
        try:
            h = hash(list_val)
            assert isinstance(h, int)
        except TypeError:
            pytest.fail("CtyValue.__hash__ failed to handle unhashable internal value.")

    def test_equality_branches(self):
        """Covers all branches of the __eq__ method."""
        str_val = CtyString().validate("a")
        num_val = CtyNumber().validate(1)
        marked_val = str_val.mark(CtyMark("test"))

        assert (str_val == num_val) is False
        assert (CtyValue.unknown(CtyString()) == str_val) is False
        assert (CtyValue.null(CtyString()) == str_val) is False
        assert (marked_val == str_val) is False
        assert (str_val == "not a cty value") is False

    def test_contains_branches(self):
        """Covers edge cases in the __contains__ method."""
        map_type = CtyMap(value_type=CtyString())
        map_val = map_type.validate({"a": "b"})
        assert (CtyValue.null(CtyString()) in map_val) is False

        list_val = CtyList(element_type=CtyNumber()).validate([1, 2, 3])
        assert ("a" in list_val) is False

        class UnhashableContains:
            def __contains__(self, item):
                raise TypeError("Simulating unhashable item check")
        val = CtyValue(vtype=CtyDynamic(), value=UnhashableContains())
        assert (1 in val) is False
        
        # Test contains on a non-container primitive
        assert ("a" in CtyString().validate("abc")) is True
        assert ("d" in CtyString().validate("abc")) is False

    def test_bool_and_empty_checks_on_dynamic(self):
        """Covers boolean and empty checks on CtyDynamic values."""
        dyn_type = CtyDynamic()
        
        true_val = CtyValue(dyn_type, CtyBool().validate(True))
        false_val = CtyValue(dyn_type, CtyBool().validate(False))
        non_bool_val = CtyValue(dyn_type, CtyString().validate("text"))
        
        assert true_val.is_true()
        assert not true_val.is_false()
        assert false_val.is_false()
        assert not false_val.is_true()
        assert not non_bool_val.is_true()
        assert not non_bool_val.is_false()
        
        empty_val = CtyValue(dyn_type, CtyList(element_type=CtyString()).validate([]))
        non_empty_val = CtyValue(dyn_type, CtyList(element_type=CtyString()).validate(["a"]))
        
        assert empty_val.is_empty()
        assert not non_empty_val.is_empty()
