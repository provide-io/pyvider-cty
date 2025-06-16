#!/usr/bin/env python3
# tests/values/test_cty_values_containers.py

import pytest
import asyncio

from pyvider.cty import (
    CtyBool, CtyNumber, CtyString,
    CtyList, CtyMap, CtySet, CtyObject, CtyTuple,
    CtyValue
)

class TestCtyListValueOperations:
    """Tests focused on list container operations."""
    
    @pytest.fixture
    def setup_values(self):
        """Set up test fixtures."""
        # Create string list type
        self.str_type = CtyString()
        self.list_type = CtyList(element_type=self.str_type)
        
        # Create sample list value
        self.list_val = self.list_type.validate(["a", "b", "c"])
    
    @pytest.mark.asyncio
    async def test_list_direct_access(self, setup_values):
        """Test direct access to list elements."""
        # Get element directly 
        element = self.list_val.value[0]
        
        # Verify it's a CtyValue with expected type and value
        assert isinstance(element, CtyValue)
        assert isinstance(element.type, CtyString)
        assert element.value == "a"
    
    @pytest.mark.asyncio
    async def test_list_element_at(self, setup_values):
        """Test element_at method."""
        # Get element at index 1
        element = self.list_val.element_at(1)
        
        # Verify result
        assert isinstance(element, CtyValue)
        assert isinstance(element.type, CtyString)
        assert element.value == "b"
        
        # Test negative index
        element = self.list_val.element_at(-1)
        assert element.value == "c"
        
        # Test out of bounds
        with pytest.raises(IndexError):
            self.list_val.element_at(99)
    
    @pytest.mark.asyncio
    async def test_list_getitem(self, setup_values):
        """Test __getitem__ for indexing."""
        # Get element via indexing
        element = self.list_val[0]
        
        # Verify result
        assert isinstance(element, CtyValue)
        assert isinstance(element.type, CtyString)
        assert element.value == "a"
    
    @pytest.mark.asyncio
    async def test_list_slicing(self, setup_values):
        """Test list slicing."""
        # Get slice [1:3]
        sliced = self.list_val[1:3]
        
        # Verify slice is a CtyValue with list type
        assert isinstance(sliced, CtyValue)
        assert isinstance(sliced.type, CtyList)
        
        # Verify slice contents
        assert len(sliced.value) == 2
        assert sliced.value[0].value == "b"
        assert sliced.value[1].value == "c"
    
    @pytest.mark.asyncio
    async def test_list_contains(self, setup_values):
        """Test membership testing."""
        # Test in operator with raw value
        assert "a" in self.list_val
        assert "z" not in self.list_val

    @pytest.mark.asyncio
    async def test_list_iteration(self, setup_values):
        """Test iteration over list elements."""
        values = []
        for element in self.list_val:
            values.append(element.value)
        
        assert values == ["a", "b", "c"]
    
    @pytest.mark.asyncio
    async def test_list_length(self, setup_values):
        """Test length operation."""
        assert len(self.list_val) == 3

class TestCtyMapValueOperations:
    """Tests focused on map container operations."""
    
    @pytest.fixture
    def setup_values(self):
        """Set up test fixtures."""
        # Create map type
        self.str_type = CtyString()
        self.num_type = CtyNumber()
        self.map_type = CtyMap(key_type=self.str_type, value_type=self.num_type)
        
        # Create sample map value
        self.map_val = self.map_type.validate({"a": 1, "b": 2, "c": 3})
    
    @pytest.mark.asyncio
    async def test_map_get(self, setup_values):
        """Test get method for map."""
        # Get element by key
        element = self.map_val.get("a")
        
        # Verify result
        assert isinstance(element, CtyValue)
        assert isinstance(element.type, CtyNumber)
        assert element.value == 1
        
        # Test missing key
        missing_result = self.map_val.get("z")
        assert missing_result is not None, "Result for missing key should be a CtyValue, not Python None"
        assert missing_result.is_null, "Result for missing key should be null"
        assert missing_result.type.equal(self.map_type.value_type), "Null result type should match map's value_type"
        
        # Test with default
        default = CtyValue(vtype=self.num_type, value=999)
        assert self.map_val.get("z", default) is default
    
    @pytest.mark.asyncio
    async def test_map_getitem(self, setup_values):
        """Test indexing into a map."""
        # Access by key
        element = self.map_val["a"]
        
        # Verify result
        assert isinstance(element, CtyValue)
        assert isinstance(element.type, CtyNumber)
        assert element.value == 1
        
        # Test missing key
        with pytest.raises((KeyError, TypeError)):
            _ = self.map_val["z"]
    
    @pytest.mark.asyncio
    async def test_map_set_method(self, setup_values):
        """Test setting a key in a map."""
        # Original map items (Python dict of CtyValues)
        # Accessing .value on a CtyMap CtyValue gives the Python dict.
        original_py_dict = {}
        if not self.map_val.is_null and not self.map_val.is_unknown:
            original_py_dict = self.map_val.value

        # Create items for the new map, ensuring values are raw Python types for the factory
        new_items_data_for_d = {k: v.value for k, v in original_py_dict.items()}
        new_items_data_for_d["d"] = 4 # Add/update "d" with raw Python value

        new_map = CtyValue.map(self.map_type.key_type, self.map_type.value_type, new_items_data_for_d)
        
        # Verify result
        assert isinstance(new_map, CtyValue)
        assert isinstance(new_map.type, CtyMap)
        assert "d" in new_map.value # Check in the inner dict
        
        # Value is correctly set
        element = new_map.value["d"] # Access inner dict
        assert element.value == 4
        
        # Original map is unchanged (check its inner dict)
        assert "d" not in original_py_dict
        
        # Update existing key "a"
        updated_items_data_for_a = {k: v.value for k, v in original_py_dict.items()}
        updated_items_data_for_a["a"] = 10

        updated_map = CtyValue.map(self.map_type.key_type, self.map_type.value_type, updated_items_data_for_a)
        assert updated_map.value["a"].value == 10
        assert original_py_dict["a"].value == 1  # Original unchanged
    
    @pytest.mark.asyncio
    async def test_map_delete_method(self, setup_values):
        """Test deleting a key from a map."""
        # Delete a key
        new_map = self.map_val.delete("b")
        
        # Verify result
        assert isinstance(new_map, CtyValue)
        assert isinstance(new_map.type, CtyMap)
        assert "b" not in new_map
        assert "a" in new_map
        assert "c" in new_map
        
        # Original map is unchanged
        assert "b" in self.map_val
        
        # Deleting a non-existent key returns the same map
        same_map = new_map.delete("z")
        assert same_map == new_map
    
    @pytest.mark.asyncio
    async def test_map_contains(self, setup_values):
        """Test membership testing for map."""
        # Test in operator with raw value
        assert "a" in self.map_val
        assert "z" not in self.map_val

class TestCtyObjectValueOperations:
    """Tests focused on object container operations."""
    
    @pytest.fixture
    def setup_values(self):
        """Set up test fixtures."""
        # Create object type
        self.str_type = CtyString()
        self.num_type = CtyNumber()
        self.obj_type = CtyObject(attribute_types={
            "name": self.str_type,
            "height": self.str_type,
            "age": self.num_type,
        })
        
        # Create sample object value
        self.obj_val = self.obj_type.validate({
            "name": "Alice",
            "height": "5ft 9in",
            "age": 30,
        })
    
    @pytest.mark.asyncio
    async def test_object_getitem(self, setup_values):
        """Test indexing into an object."""
        # Access by attribute name
        element = self.obj_val["name"]
        
        # Verify result
        assert isinstance(element, CtyValue)
        assert isinstance(element.type, CtyString)
        assert element.value == "Alice"
        
        # Test missing attribute
        from pyvider.cty.exceptions import CtyAttributeValidationError # Ensure import
        with pytest.raises(CtyAttributeValidationError):
            _ = self.obj_val["non_existent_attr"]
    
    @pytest.mark.asyncio
    async def test_object_get_method(self, setup_values):
        """Test get method on an object."""
        # Get attribute by name
        element = self.obj_val.get("age")
        
        # Verify result
        assert isinstance(element, CtyValue)
        assert isinstance(element.type, CtyNumber)
        assert element.value == 30
        
        # Test missing attribute
        assert self.obj_val.get("height").value == "5ft 9in" # "height" is a present attribute
        
        # Test with default for a missing attribute
        default = CtyValue(vtype=self.num_type, value=0) # Default CtyValue for a number
        assert self.obj_val.get("non_existent_attr", default) is default
    
    @pytest.mark.asyncio
    async def test_object_contains(self, setup_values):
        """Test membership testing for object."""
        # Test in operator with attribute name
        assert "name" in self.obj_val
        assert "height" in self.obj_val # "height" is an attribute

class TestCtyTupleValueOperations:
    """Tests focused on tuple container operations."""
    
    @pytest.fixture
    def setup_values(self):
        """Set up test fixtures."""
        # Create tuple type
        self.str_type = CtyString()
        self.num_type = CtyNumber()
        self.tuple_type = CtyTuple(element_types=(self.str_type, self.num_type))
        
        # Create sample tuple value
        self.tuple_val = self.tuple_type.validate(("Alice", 30))
    
    @pytest.mark.asyncio
    async def test_tuple_getitem(self, setup_values):
        """Test indexing into a tuple."""
        # Access by index
        element0 = self.tuple_val[0]
        element1 = self.tuple_val[1]
        
        # Verify results
        assert isinstance(element0, CtyValue)
        assert isinstance(element0.type, CtyString)
        assert element0.value == "Alice"
        
        assert isinstance(element1, CtyValue)
        assert isinstance(element1.type, CtyNumber)
        assert element1.value == 30
        
        # Test out of bounds
        with pytest.raises(IndexError):
            _ = self.tuple_val[2]
    
    @pytest.mark.asyncio
    async def test_tuple_element_at(self, setup_values):
        """Test element_at method on a tuple."""
        # Get element at index
        element = self.tuple_val.element_at(1)
        
        # Verify result
        assert isinstance(element, CtyValue)
        assert isinstance(element.type, CtyNumber)
        assert element.value == 30
        
        # Test negative index
        element = self.tuple_val.element_at(-1)
        assert element.value == 30
        
        # Test out of bounds
        with pytest.raises(IndexError):
            self.tuple_val.element_at(2)
    
    @pytest.mark.asyncio
    async def test_tuple_slicing(self, setup_values):
        """Test slicing a tuple."""
        # Get full slice
        sliced = self.tuple_val[0:2]
        
        # Verify result
        assert isinstance(sliced, CtyValue)
        assert len(sliced.value) == 2
        assert sliced.value[0].value == "Alice"
        assert sliced.value[1].value == 30
    
    @pytest.mark.asyncio
    async def test_tuple_length(self, setup_values):
        """Test length operation."""
        assert len(self.tuple_val) == 2
    
    @pytest.mark.asyncio
    async def test_tuple_iteration(self, setup_values):
        """Test iteration over tuple elements."""
        elements = list(self.tuple_val)
        assert len(elements) == 2
        assert elements[0].value == "Alice"
        assert elements[1].value == 30

class TestCtySetValueOperations:
    """Tests focused on set container operations."""
    
    @pytest.fixture
    def setup_values(self):
        """Set up test fixtures."""
        # Create set type
        self.num_type = CtyNumber()
        self.set_type = CtySet(element_type=self.num_type)
        
        # Create sample set value
        self.set_val = self.set_type.validate({1, 2, 3})
    
    @pytest.mark.asyncio
    async def test_set_contains(self, setup_values):
        """Test membership testing."""
        # Test in operator
        assert 1 in self.set_val
        assert 99 not in self.set_val
    
    @pytest.mark.asyncio
    async def test_set_length(self, setup_values):
        """Test length operation."""
        assert len(self.set_val) == 3
    
    @pytest.mark.asyncio
    async def test_set_iteration(self, setup_values):
        """Test iteration over set elements."""
        values = set()
        for element in self.set_val:
            values.add(element.value)
        
        assert values == {1, 2, 3}

class TestSpecialValues:
    """Tests focused on special value behavior."""
    
    @pytest.fixture
    def setup_values(self):
        """Set up test fixtures."""
        # Create types
        self.str_type = CtyString()
        self.list_type = CtyList(element_type=self.str_type)
        self.map_type = CtyMap(key_type=self.str_type, value_type=CtyString())
        
        # Create special values
        self.unknown_str = CtyValue.unknown(self.str_type)
        self.null_str = CtyValue.null(self.str_type)
        self.unknown_list = CtyValue.unknown(self.list_type)
        self.null_list = CtyValue.null(self.list_type)
    
    @pytest.mark.asyncio
    async def test_unknown_value_operations(self, setup_values):
        """Test operations on unknown values."""
        # Attempt operations on unknown values
        with pytest.raises(TypeError):
            _ = self.unknown_list[0]
            
        with pytest.raises(TypeError):
            _ = "x" in self.unknown_list
            
        with pytest.raises(ValueError):
            _ = self.unknown_str.value
            
        with pytest.raises(TypeError):
            _ = len(self.unknown_list)
    
    @pytest.mark.asyncio
    async def test_null_value_operations(self, setup_values):
        """Test operations on null values."""
        # Attempt operations on null values
        with pytest.raises(TypeError):
            _ = self.null_list[0]
            
        with pytest.raises(TypeError):
            _ = "x" in self.null_list
            
        # Null value access returns None
        assert self.null_str.value is None
        
        # Length of a null list should be 0, not raise TypeError
        assert len(self.null_list) == 0