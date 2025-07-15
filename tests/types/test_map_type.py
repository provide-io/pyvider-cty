import pytest
from pyvider.cty.types import CtyMap, CtyString, CtyNumber, CtyType
from pyvider.cty.values import CtyValue
from pyvider.cty.exceptions import CtyValidationError, InvalidTypeError

class TestCtyMap:
    def test_map_creation_and_type_equality(self):
        """Tests that a CtyMap can be created with an element_type."""
        map_type = CtyMap(element_type=CtyString())
        assert isinstance(map_type.element_type, CtyType)
        assert map_type.equal(CtyMap(element_type=CtyString()))
        assert not map_type.equal(CtyMap(element_type=CtyNumber()))

    def test_map_validation_success(self):
        map_type = CtyMap(element_type=CtyNumber())
        value = map_type.validate({"a": 1, "b": 100})
        assert isinstance(value, CtyValue)
        # CORRECTED: CtyValue.__eq__ is defined to compare the underlying values.
        # We compare the returned CtyValue with an expected CtyValue.
        assert value.value["a"] == CtyNumber().validate(1)

    def test_map_validation_type_mismatch_fails(self):
        map_type = CtyMap(element_type=CtyNumber())
        with pytest.raises(CtyValidationError):
            map_type.validate({"a": 1, "b": "not-a-number"})
    
    def test_map_creation_with_invalid_type_fails(self):
        """Ensures the constructor raises an error for invalid element types."""
        with pytest.raises(InvalidTypeError):
            CtyMap(element_type="not a cty type")
