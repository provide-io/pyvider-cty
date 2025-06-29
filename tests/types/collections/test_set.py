import pytest

from pyvider.cty.exceptions import CtySetValidationError
from pyvider.cty.types import (
    CtyDynamic,
    CtyList,
    CtyNumber,
    CtySet,
    CtyString,
)
from pyvider.cty.values import CtyValue


class TestCtySetInstantiation:
    def test_instantiation_valid_element_type(self) -> None:
        s = CtySet(element_type=CtyString())
        assert isinstance(s.element_type, CtyString)

    @pytest.mark.parametrize("invalid_type", ["foo", int, 123])
    def test_instantiation_invalid_element_type_raises_error(
        self, invalid_type
    ) -> None:
        with pytest.raises(
            CtySetValidationError, match="Expected CtyType for element_type"
        ):
            CtySet(element_type=invalid_type)

class TestCtySetValidate:
    def test_validate_list_input_with_unhashable_elements(self) -> None:
        set_type = CtySet(element_type=CtyDynamic())
        unhashable_input = [1, "two", {"three": 3}]
        with pytest.raises(
            CtySetValidationError,
            match="Input list/tuple could not be converted to set",
        ):
            set_type.validate(unhashable_input)

    def test_validate_set_with_mixed_validity_elements(self) -> None:
        set_type = CtySet(element_type=CtyNumber())
        mixed_validity_input = {10, "twenty"}
        with pytest.raises(CtySetValidationError) as excinfo:
            set_type.validate(mixed_validity_input)
        assert "Set validation failed:" in str(excinfo.value)
        assert "Cannot convert string 'twenty' to number" in str(excinfo.value)

class TestCtySetOperations:
    @pytest.fixture
    def set_type(self):
        return CtySet(element_type=CtyString())

    @pytest.fixture
    def set_val1(self, set_type):
        return set_type.validate({"a", "b", "c"})

    @pytest.fixture
    def set_val2(self, set_type):
        return set_type.validate({"b", "c", "d"})
        
    def test_union_operation(self, set_type, set_val1, set_val2):
        # FIX: Operations are called on the TYPE, not the VALUE
        result = set_type.union(set_val1, set_val2)
        expected = set_type.validate({"a", "b", "c", "d"})
        assert result == expected

    def test_intersection_operation(self, set_type, set_val1, set_val2):
        # FIX: Operations are called on the TYPE, not the VALUE
        result = set_type.intersection(set_val1, set_val2)
        expected = set_type.validate({"b", "c"})
        assert result == expected

    def test_difference_operation(self, set_type, set_val1, set_val2):
        # FIX: Operations are called on the TYPE, not the VALUE
        result = set_type.difference(set_val1, set_val2)
        expected = set_type.validate({"a"})
        assert result == expected
