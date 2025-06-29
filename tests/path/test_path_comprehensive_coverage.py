import pytest
from decimal import Decimal
from pyvider.cty import (
    CtyBool, CtyDynamic, CtyList, CtyMap, CtyNumber, CtyObject, CtyString, CtyTuple, CtyValue
)
from pyvider.cty.path import CtyPath, GetAttrStep, IndexStep, KeyStep
from pyvider.cty.exceptions import AttributePathError, CtyTypeMismatchError, CtyValidationError

class TestPathComprehensiveCoverage:
    """Comprehensive tests to improve coverage for pyvider.cty.path.base."""

    @pytest.fixture
    def list_val(self):
        return CtyList(element_type=CtyString()).validate(["a", "b", "c"])

    @pytest.fixture
    def map_val(self):
        return CtyMap(value_type=CtyString()).validate({"a": "x", "b": "y"})
        
    def test_getattr_on_null_value(self):
        """Test GetAttrStep.apply on a null value."""
        step = GetAttrStep("name")
        obj_type = CtyObject({"name": CtyString()})
        null_value = CtyValue.null(obj_type)
        with pytest.raises(AttributePathError, match="Cannot get attribute 'name' from null value"):
            step.apply(null_value)

    def test_getattr_on_map_with_non_string_key(self):
        """Test GetAttrStep on a map where the attribute name is not a valid key type."""
        step = GetAttrStep("123") # Key is string "123"
        # Map requires CtyNumber keys. CtyString "123" is not a valid CtyNumber.
        map_type = CtyMap(key_type=CtyNumber(), value_type=CtyString())
        map_value = map_type.validate({1: "one"})
        with pytest.raises(AttributePathError, match=r"Unexpected error getting key '123'"):
            step.apply(map_value)

    def test_indexstep_negative_out_of_bounds(self, list_val):
        """Test IndexStep with a negative index that is still out of bounds."""
        step = IndexStep(-4)
        with pytest.raises(AttributePathError, match="Index out of bounds"):
            step.apply(list_val)

    def test_keystep_on_dynamic_with_invalid_key_type(self):
        """Test KeyStep on a CtyDynamic value with an unsupported key type."""
        step = KeyStep(b"bytes_key") # bytes is not a supported raw key type
        value = CtyDynamic().validate({"a": "b"})
        with pytest.raises(AttributePathError, match="Unsupported key type for raw dictionary lookup"):
            step.apply(value)

    def test_keystep_on_map_with_null_or_unknown_key(self, map_val):
        """Test KeyStep on a map with a null or unknown key."""
        null_key_step = KeyStep(CtyValue.null(CtyString()))
        unknown_key_step = KeyStep(CtyValue.unknown(CtyString()))
        
        with pytest.raises(AttributePathError, match="Map key in path cannot be null or unknown"):
            null_key_step.apply(map_val)
        
        with pytest.raises(AttributePathError, match=r"Map key in path cannot be null or unknown"):
            unknown_key_step.apply(map_val)

    def test_keystep_on_map_with_unsupported_key_type(self, map_val):
        """Test KeyStep on a map with an unsupported raw key type."""
        unsupported_key_step = KeyStep(b"unsupported")
        with pytest.raises(AttributePathError, match="Unsupported key type for map lookup"):
            unsupported_key_step.apply(map_val)
