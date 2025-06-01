#!/usr/bin/env python3
# tests/values/test_cty_values_factory.py

import pytest
import asyncio
from decimal import Decimal

from pyvider.cty import (
    CtyBool, CtyNumber, CtyString,
    CtyList, CtyMap, CtySet, CtyObject, CtyTuple,
    CtyValue
)

class TestCtyValueFactoryMethods:
    """Tests for CtyValue factory methods."""
    
    @pytest.fixture
    def setup_types(self):
        """Set up Cty types."""
        self.str_type = CtyString()
        self.num_type = CtyNumber()
        self.bool_type = CtyBool()
    
    @pytest.mark.asyncio
    async def test_bool_factory(self, setup_types):
        """Test bool factory method."""
        # Create a boolean value
        value = CtyValue.bool(True)
        
        # Verify result
        assert isinstance(value, CtyValue)
        assert isinstance(value.type, CtyBool)
        assert value.value is True
        
        # Create false value
        value = CtyValue.bool(False)
        assert value.value is False
    
    @pytest.mark.asyncio
    async def test_string_factory(self, setup_types):
        """Test string factory method."""
        # Create a string value
        value = CtyValue.string("test")
        
        # Verify result
        assert isinstance(value, CtyValue)
        assert isinstance(value.type, CtyString)
        assert value.value == "test"
        
        # Empty string
        value = CtyValue.string("")
        assert value.value == ""
    
    @pytest.mark.asyncio
    async def test_number_factory(self, setup_types):
        """Test number factory method."""
        # Create an integer value
        value = CtyValue.number(42)
        
        # Verify result
        assert isinstance(value, CtyValue)
        assert isinstance(value.type, CtyNumber)
        assert value.value == 42
        
        # Create float value
        value = CtyValue.number(3.14)
        assert value.value == 3.14
        
        # Create decimal value
        value = CtyValue.number(Decimal("3.14159265359"))
        assert isinstance(value.value, Decimal)
        assert value.value == Decimal("3.14159265359")
    
    @pytest.mark.asyncio
    async def test_list_factory(self, setup_types):
        """Test list factory method."""
        # Create a list value
        value = CtyValue.list(self.str_type, ["a", "b", "c"])
        
        # Verify result
        assert isinstance(value, CtyValue)
        assert isinstance(value.type, CtyList)
        assert len(value.value) == 3
        
        # Check elements
        assert all(isinstance(item, CtyValue) for item in value.value)
        assert all(isinstance(item.type, CtyString) for item in value.value)
        assert [item.value for item in value.value] == ["a", "b", "c"]
        
        # Empty list
        value = CtyValue.list(self.str_type, [])
        assert isinstance(value, CtyValue)
        assert isinstance(value.type, CtyList)
        assert len(value.value) == 0
    
    @pytest.mark.asyncio
    async def test_map_factory(self, setup_types):
        """Test map factory method."""
        # Create a map value
        value = CtyValue.map(self.str_type, self.num_type, {"a": 1, "b": 2})
        
        # Verify result
        assert isinstance(value, CtyValue)
        assert isinstance(value.type, CtyMap)
        assert len(value.value) == 2
        
        # Check keys and values
        for k, v in value.value.items():
            assert isinstance(k, str)
            # For key type, we rely on CtyMap validation. Here k is Python str.
            assert isinstance(v, CtyValue)
            assert isinstance(v.type, CtyNumber)
            assert k in ["a", "b"]  # k is a str, so no .value
            if k == "a":  # k is a str
                assert v.value == 1
            elif k == "b":  # k is a str
                assert v.value == 2
        
        # Empty map
        value = CtyValue.map(self.str_type, self.num_type, {})
        assert isinstance(value, CtyValue)
        assert isinstance(value.type, CtyMap)
        assert len(value.value) == 0
    
    @pytest.mark.asyncio
    async def test_set_factory(self, setup_types):
        """Test set factory method."""
        # Create a set value
        value = CtyValue.set(self.num_type, {1, 2, 3})
        
        # Verify result
        assert isinstance(value, CtyValue)
        assert isinstance(value.type, CtySet)
        assert len(value.value) == 3
        
        # Check elements
        values = set()
        for item in value.value:
            assert isinstance(item, CtyValue)
            assert isinstance(item.type, CtyNumber)
            values.add(item.value)
        assert values == {1, 2, 3}
        
        # Empty set
        value = CtyValue.set(self.num_type, set())
        assert isinstance(value, CtyValue)
        assert isinstance(value.type, CtySet)
        assert len(value.value) == 0
    
    @pytest.mark.asyncio
    async def test_tuple_factory(self, setup_types):
        """Test tuple factory method."""
        # Create a tuple value
        value = CtyValue.tuple((self.str_type, self.num_type), ("test", 42))
        
        # Verify result
        assert isinstance(value, CtyValue)
        assert isinstance(value.type, CtyTuple)
        assert len(value.value) == 2
        
        # Check elements
        assert isinstance(value.value[0], CtyValue)
        assert isinstance(value.value[0].type, CtyString)
        assert value.value[0].value == "test"
        
        assert isinstance(value.value[1], CtyValue)
        assert isinstance(value.value[1].type, CtyNumber)
        assert value.value[1].value == 42
        
        # Empty tuple
        value = CtyValue.tuple((), ())
        assert isinstance(value, CtyValue)
        assert isinstance(value.type, CtyTuple)
        assert len(value.value) == 0
    
    @pytest.mark.asyncio
    async def test_object_factory(self, setup_types):
        """Test object factory method."""
        # Create an object value
        value = CtyValue.object(
            {"name": self.str_type, "age": self.num_type},
            {"name": "Alice", "age": 30}
        )
        
        # Verify result
        assert isinstance(value, CtyValue)
        assert isinstance(value.type, CtyObject)
        
        # Check attributes
        assert "name" in value
        assert "age" in value
        assert value["name"].value == "Alice"
        assert value["age"].value == 30
        
        # Empty object
        value = CtyValue.object({}, {})
        assert isinstance(value, CtyValue)
        assert isinstance(value.type, CtyObject)
    
    @pytest.mark.asyncio
    async def test_unknown_factory(self, setup_types):
        """Test unknown factory method."""
        # Create unknown values of different types
        unknown_str = CtyValue.unknown(self.str_type)
        unknown_num = CtyValue.unknown(self.num_type)
        unknown_bool = CtyValue.unknown(self.bool_type)
        
        # Verify results
        assert unknown_str.is_unknown
        assert unknown_num.is_unknown
        assert unknown_bool.is_unknown
        
        assert isinstance(unknown_str.type, CtyString)
        assert isinstance(unknown_num.type, CtyNumber)
        assert isinstance(unknown_bool.type, CtyBool)
    
    @pytest.mark.asyncio
    async def test_null_factory(self, setup_types):
        """Test null factory method."""
        # Create null values of different types
        null_str = CtyValue.null(self.str_type)
        null_num = CtyValue.null(self.num_type)
        null_bool = CtyValue.null(self.bool_type)
        
        # Verify results
        assert null_str.is_null
        assert null_num.is_null
        assert null_bool.is_null
        
        assert isinstance(null_str.type, CtyString)
        assert isinstance(null_num.type, CtyNumber)
        assert isinstance(null_bool.type, CtyBool)
