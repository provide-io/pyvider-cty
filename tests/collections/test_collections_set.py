"""
Test module for CtySet implementation.

This module contains tests for the CtySet type, ensuring proper validation,
equality checking, and other operations.
"""
import pytest
from typing import Any, Set

from pyvider.cty.exceptions import ValidationError
from pyvider.cty.types import CtyBool, CtyNumber, CtySet, CtyString, CtyValue

class TestCtySetType:
    """Test suite for CtySet type."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.string_set = CtySet(element_type=CtyString())
        self.number_set = CtySet(element_type=CtyNumber())
        self.bool_set = CtySet(element_type=CtyBool())
    
    # -------------------- VALIDATION TESTS --------------------
    
    def test_validate_valid_string_set(self):
        """Test validation of a valid string set."""
        valid = {"apple", "banana", "cherry"}
        validated = self.string_set.validate(valid)
        assert set(validated.value) == valid
    
    def test_validate_valid_number_set(self):
        """Test validation of a valid number set."""
        valid = {1, 2, 3}
        validated = self.number_set.validate(valid)
        assert set(validated.value) == valid
    
    def test_validate_valid_bool_set(self):
        """Test validation of a valid boolean set."""
        valid = {True, False}
        validated = self.bool_set.validate(valid)
        assert set(validated.value) == valid
    
    def test_validate_invalid_element_type(self):
        """Test validation with invalid element type."""
        invalid = {"apple", 2, True}  # Mixed types
        with pytest.raises(ValidationError):
            self.string_set.validate(invalid)
    
    def test_validate_empty_set(self):
        """Test validation of an empty set."""
        empty = set()
        validated = self.string_set.validate(empty)
        assert len(validated.value) == 0
    
    def test_validate_none_value(self):
        """Test validation with None value."""
        validated = self.string_set.validate(None)
        assert len(validated.value) == 0
    
    def test_validate_non_iterable(self):
        """Test validation with non-iterable value."""
        with pytest.raises(ValidationError):
            self.string_set.validate(123)
    
    def test_validate_nested_set(self):
        """Test validation with nested set (should fail)."""
        nested = {{"nested"}}
        with pytest.raises(ValidationError):
            self.string_set.validate(nested)
    
    # -------------------- EQUALITY AND COMPARISON TESTS --------------------
    
    def test_set_equality(self):
        """Test equality of sets with same element type."""
        set1 = CtySet(element_type=CtyString())
        set2 = CtySet(element_type=CtyString())
        assert set1.equal(set2)
    
    def test_set_inequality(self):
        """Test inequality of sets with different element types."""
        assert not self.string_set.equal(self.number_set)
    
    def test_usable_as_same_type(self):
        """Test usable_as with same type."""
        set1 = CtySet(element_type=CtyString())
        set2 = CtySet(element_type=CtyString())
        assert set1.usable_as(set2)
    
    def test_usable_as_different_type(self):
        """Test usable_as with different type."""
        assert not self.string_set.usable_as(self.number_set)
    
    def test_usable_as_non_set_type(self):
        """Test usable_as with non-set type."""
        assert not self.string_set.usable_as(CtyString())
    
    # -------------------- OPERATION TESTS --------------------
    
    def test_add_valid_element(self):
        """Test adding a valid element to the set."""
        set_obj = self.string_set.validate({"apple", "banana"})
        set_obj.add("cherry")
        assert "cherry" in set_obj.value
    
    def test_add_invalid_element(self):
        """Test adding an invalid element to the set."""
        set_obj = self.string_set.validate({"apple", "banana"})
        with pytest.raises(ValidationError):
            set_obj.add(123)
    
    def test_remove_element(self):
        """Test removing an element from the set."""
        set_obj = self.string_set.validate({"apple", "banana", "cherry"})
        new_set = set_obj.remove("banana")
        assert "banana" not in new_set.value
        assert len(new_set.value) == 2
    
    def test_remove_nonexistent_element(self):
        """Test removing a nonexistent element from the set."""
        set_obj = self.string_set.validate({"apple", "banana"})
        new_set = set_obj.remove("cherry")
        assert len(new_set.value) == 2
    
    # -------------------- EDGE CASES --------------------
    
    def test_large_set(self):
        """Test validation of a large set."""
        large_set = {str(i) for i in range(1000)}
        validated = self.string_set.validate(large_set)
        assert len(validated.value) == 1000
    
    def test_string_representation(self):
        """Test string representation of CtySet."""
        assert str(self.string_set) == "set(CtyString)"
    
    def test_iteration(self):
        """Test iteration over set values."""
        set_obj = self.string_set.validate({"apple", "banana", "cherry"})
        items = set(iter(set_obj))
        assert items == {"apple", "banana", "cherry"}
