
# tests/path/test_path.py

"""
Integration tests for the Cty path system.

These tests verify that paths can navigate through nested Cty values,
including objects, lists, tuples, and maps.
"""

import pytest

from pyvider.cty.types.primitives import CtyString, CtyNumber, CtyBool
from pyvider.cty.types.collections import CtyList, CtyMap
from pyvider.cty.types.structural import CtyObject, CtyTuple
from pyvider.cty import CtyValue
from pyvider.cty.path import (
    CtyPath,
)
from pyvider.cty.exceptions import AttributePathError

class TestPathSystem:
    """Test the Cty path system."""

    @pytest.mark.asyncio
    async def test_attribute_paths(self):
        """Test paths with attribute access."""
        # Create an object type
        person_type = CtyObject(attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
            "address": CtyObject(attribute_types={
                "street": CtyString(),
                "city": CtyString(),
                "zip": CtyString()
            })
        })

        # Create a properly wrapped object value
        person = CtyValue(
            vtype=person_type, 
            value={
                "name": CtyValue(vtype=CtyString(), value="Alice"),
                "age": CtyValue(vtype=CtyNumber(), value=30),
                "address": CtyValue(
                    vtype=CtyObject(attribute_types={
                        "street": CtyString(),
                        "city": CtyString(),
                        "zip": CtyString()
                    }),
                    value={
                        "street": CtyValue(vtype=CtyString(), value="123 Main St"),
                        "city": CtyValue(vtype=CtyString(), value="Anytown"),
                        "zip": CtyValue(vtype=CtyString(), value="12345")
                    }
                )
            }
        )

        # Test direct attribute access
        name_path = CtyPath.get_attr("name")
        name_result = name_path.apply_path(person)
        assert isinstance(name_result, CtyValue)
        assert isinstance(name_result.type, CtyString)
        assert name_result.value == "Alice"

        # Test nested attribute access
        street_path = CtyPath.get_attr("address").child("street")
        street_result = street_path.apply_path(person)
        assert isinstance(street_result, CtyValue)
        assert isinstance(street_result.type, CtyString)
        assert street_result.value == "123 Main St"

        # Test invalid attribute
        invalid_path = CtyPath.get_attr("invalid")
        with pytest.raises(AttributePathError):
            invalid_path.apply_path(person)

        # Test type checking
        name_type = name_path.apply_path_type(person_type)
        assert isinstance(name_type, CtyString)

        street_type = street_path.apply_path_type(person_type)
        assert isinstance(street_type, CtyString)

        # Create an unknown value
        unknown_person = CtyValue(vtype=person_type, is_unknown=True)

        # Test path to attribute should return unknown value of correct type
        unknown_name_result = name_path.apply_path(unknown_person)
        assert unknown_name_result.is_unknown
        assert isinstance(unknown_name_result.type, CtyString)

    @pytest.mark.asyncio
    async def test_index_paths(self):
        """Test paths with index access."""
        # Create a list type
        numbers_type = CtyList(element_type=CtyNumber())

        # Create a properly wrapped list value
        numbers = CtyValue(
            vtype=numbers_type, 
            value=[
                CtyValue(vtype=CtyNumber(), value=10),
                CtyValue(vtype=CtyNumber(), value=20),
                CtyValue(vtype=CtyNumber(), value=30),
                CtyValue(vtype=CtyNumber(), value=40),
                CtyValue(vtype=CtyNumber(), value=50)
            ]
        )

        # Test index access
        second_path = CtyPath.index(1)
        second_result = second_path.apply_path(numbers)
        assert isinstance(second_result, CtyValue)
        assert second_result.value == 20

        # Test negative index
        last_path = CtyPath.index(-1)
        last_result = last_path.apply_path(numbers)
        assert isinstance(last_result, CtyValue)
        assert last_result.value == 50

        # Test out of bounds
        out_of_bounds_path = CtyPath.index(10)
        with pytest.raises(AttributePathError):
            out_of_bounds_path.apply_path(numbers)

        # Test type checking
        element_type = second_path.apply_path_type(numbers_type)
        assert isinstance(element_type, CtyNumber)

        # Test with tuple
        tuple_type = CtyTuple(element_types=(CtyString(), CtyNumber(), CtyBool()))
        tuple_value = CtyValue(
            vtype=tuple_type, 
            value=(
                CtyValue(vtype=CtyString(), value="hello"),
                CtyValue(vtype=CtyNumber(), value=42),
                CtyValue(vtype=CtyBool(), value=True)
            )
        )

        middle_path = CtyPath.index(1)
        middle_result = middle_path.apply_path(tuple_value)
        assert isinstance(middle_result, CtyValue)
        assert middle_result.value == 42

        # Test tuple type checking
        middle_type = middle_path.apply_path_type(tuple_type)
        assert isinstance(middle_type, CtyNumber)

    @pytest.mark.asyncio
    async def test_key_paths(self):
        """Test paths with key access."""
        # Create a map type
        scores_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())

        # Create a properly wrapped map value
        # Create a properly wrapped map value by validating a Python dict with string keys
        raw_scores_data = {
            "Alice": 95,
            "Bob": 87,
            "Charlie": 92,
            "Dave": 78
        }
        scores = scores_type.validate(raw_scores_data)

        # Test key access
        bob_path = CtyPath.key("Bob")
        bob_result = bob_path.apply_path(scores)
        assert isinstance(bob_result, CtyValue)
        assert bob_result.value == 87

        # Test invalid key
        invalid_path = CtyPath.key("Eve")
        with pytest.raises(AttributePathError):
            invalid_path.apply_path(scores)

        # Test type checking
        value_type = bob_path.apply_path_type(scores_type)
        assert isinstance(value_type, CtyNumber)

    @pytest.mark.asyncio
    async def test_complex_paths(self):
        """Test complex paths with multiple step types."""
        # Create a complex nested structure
        # List of users, each with a name and a map of scores
        user_type = CtyObject(attribute_types={
            "name": CtyString(),
            "scores": CtyMap(key_type=CtyString(), value_type=CtyNumber())
        })
        users_type = CtyList(element_type=user_type)

        # Create properly wrapped values
        # Create properly wrapped values by validating Python dicts/lists
        raw_users_data = [
            {
                "name": "Alice",
                "scores": {"math": 95, "science": 92, "history": 88}
            },
            {
                "name": "Bob",
                "scores": {"math": 87, "science": 85, "history": 92}
            },
            {
                "name": "Charlie",
                "scores": {"math": 78, "science": 90, "history": 85}
            }
        ]
        users = users_type.validate(raw_users_data)

        # Test complex path: second user's math score
        # users[1].scores["math"]
        path = CtyPath.index(1).child("scores").key_step("math")
        result = path.apply_path(users)
        assert isinstance(result, CtyValue)
        assert result.value == 87

        # Test another complex path: first user's name
        # users[0].name
        path = CtyPath.index(0).child("name")
        result = path.apply_path(users)
        assert isinstance(result, CtyValue)
        assert result.value == "Alice"

        # Test path type checking
        name_type = path.apply_path_type(users_type)
        assert isinstance(name_type, CtyString)

    @pytest.mark.asyncio
    async def test_null_and_unknown_handling(self):
        """Test paths with null and unknown values."""

        # Create an object type
        person_type = CtyObject(attribute_types={
            "name": CtyString(),
            "age": CtyNumber()
        })

        # Create a null value
        null_person = CtyValue(vtype=person_type, is_null=True)

        # Path to attribute should fail for null
        name_path = CtyPath.get_attr("name")
        with pytest.raises(AttributePathError):
            name_path.apply_path(null_person)

        # Create an unknown value
        unknown_person = CtyValue(vtype=person_type, is_unknown=True)

        # Path to attribute should return unknown value of correct type
        name_result = name_path.apply_path(unknown_person)
        assert name_result.is_unknown
        assert isinstance(name_result.type, CtyString)

        # Test with null value in a nested structure
        address_type = CtyObject(attribute_types={
            "street": CtyString(),
            "city": CtyString()
        })
        person_with_address_type = CtyObject(attribute_types={
            "name": CtyString(),
            "address": address_type
        })

        person_with_null_address = CtyValue(
            vtype=person_with_address_type, 
            value={
                "name": CtyValue(vtype=CtyString(), value="Alice"),
                "address": CtyValue(vtype=address_type, is_null=True)
            }
        )

        # Path to street should fail because address is null
        street_path = CtyPath.get_attr("address").child("street")
        with pytest.raises(AttributePathError):
            street_path.apply_path(person_with_null_address)

        # Test with unknown value in a nested structure
        person_with_unknown_address = CtyValue(
            vtype=person_with_address_type, 
            value={
                "name": CtyValue(vtype=CtyString(), value="Alice"),
                "address": CtyValue(vtype=address_type, is_unknown=True)
            }
        )

        # Path to street should return unknown value of correct type
        street_result = street_path.apply_path(person_with_unknown_address)
        assert street_result.is_unknown
        assert isinstance(street_result.type, CtyString)

    @pytest.mark.asyncio
    async def test_path_string_representation(self):
        """Test string representation of paths."""
        # Empty path
        empty_path = CtyPath.empty()
        assert str(empty_path) == "(empty path)"

        # Attribute path
        attr_path = CtyPath.get_attr("name")
        assert str(attr_path) == ".name"

        # Index path
        index_path = CtyPath.index(1)
        assert str(index_path) == "[1]"

        # Key path
        key_path = CtyPath.key("foo")
        assert str(key_path) == "['foo']"

        # Complex path
        complex_path = CtyPath.index(0).child("scores").key_step("math")
        assert str(complex_path) == "[0].scores['math']"
