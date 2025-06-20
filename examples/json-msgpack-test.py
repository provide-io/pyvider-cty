#!/usr/bin/env python3
# example-json-msgpack-conversion.py
"""
Example demonstrating JSON and MessagePack conversion with complex nested structures.
Tests various edge cases and shows proper error handling.
"""

import json
from decimal import Decimal
from typing import Any

from pyvider.cty import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtyString,
    CtyTuple,
    CtyValue,
)
from pyvider.cty.conversion import WireFormatType, marshal, unmarshal
from pyvider.cty.exceptions import CtyValidationError
from pyvider.cty.marks import CtyMark


def test_basic_types():
    """Test serialization of basic types."""
    print("🧪 Testing Basic Types Serialization\n")
    
    test_cases = [
        ("String", CtyString(), "Hello, World!"),
        ("Number (int)", CtyNumber(), 42),
        ("Number (float)", CtyNumber(), 3.14159),
        ("Number (Decimal)", CtyNumber(), Decimal("123.456")),
        ("Boolean (true)", CtyBool(), True),
        ("Boolean (false)", CtyBool(), False),
    ]
    
    for name, cty_type, value in test_cases:
        try:
            # Create and validate value
            cty_val = cty_type.validate(value)
            
            # Test JSON
            json_data = marshal(cty_val, format_kind=WireFormatType.JSON)
            json_decoded = unmarshal(json_data, format_kind=WireFormatType.JSON, expected_type=cty_type)
            json_match = json_decoded.value == cty_val.value
            
            # Test MessagePack
            msgpack_data = marshal(cty_val, format_kind=WireFormatType.MSGPACK)
            msgpack_decoded = unmarshal(msgpack_data, format_kind=WireFormatType.MSGPACK, expected_type=cty_type)
            msgpack_match = msgpack_decoded.value == cty_val.value
            
            print(f"✅ {name}: JSON={'✓' if json_match else '✗'}, MessagePack={'✓' if msgpack_match else '✗'}")
            
        except Exception as e:
            print(f"❌ {name}: {type(e).__name__}: {e}")
    
    print()


def test_collection_types():
    """Test serialization of collection types."""
    print("🧪 Testing Collection Types Serialization\n")
    
    # List of strings
    list_type = CtyList(element_type=CtyString())
    list_val = list_type.validate(["apple", "banana", "cherry"])
    
    # Map of numbers
    map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())
    map_val = map_type.validate({"one": 1, "two": 2, "three": 3})
    
    # Set of numbers (if supported)
    # Note: Sets might serialize as lists in JSON
    
    test_cases = [
        ("List[String]", list_type, list_val),
        ("Map[String, Number]", map_type, map_val),
    ]
    
    for name, expected_type, cty_val in test_cases:
        try:
            # Test JSON
            json_data = marshal(cty_val, format_kind=WireFormatType.JSON)
            json_decoded = unmarshal(json_data, format_kind=WireFormatType.JSON, expected_type=expected_type)
            
            # Test MessagePack
            msgpack_data = marshal(cty_val, format_kind=WireFormatType.MSGPACK)
            msgpack_decoded = unmarshal(msgpack_data, format_kind=WireFormatType.MSGPACK, expected_type=expected_type)
            
            print(f"✅ {name}: Both formats successful")
            
        except Exception as e:
            print(f"❌ {name}: {type(e).__name__}: {e}")
    
    print()


def test_nested_structures():
    """Test deeply nested structures."""
    print("🧪 Testing Nested Structures\n")
    
    # Define a complex nested structure
    address_type = CtyObject({
        "street": CtyString(),
        "city": CtyString(),
        "coordinates": CtyTuple((CtyNumber(), CtyNumber())),
    })
    
    person_type = CtyObject({
        "name": CtyString(),
        "age": CtyNumber(),
        "addresses": CtyList(element_type=address_type),
        "phone_numbers": CtyMap(key_type=CtyString(), value_type=CtyString()),
    })
    
    company_type = CtyObject({
        "name": CtyString(),
        "employees": CtyList(element_type=person_type),
        "departments": CtyMap(
            key_type=CtyString(),
            value_type=CtyObject({
                "head": CtyString(),
                "budget": CtyNumber(),
            })
        ),
    })
    
    # Create test data
    company_data = {
        "name": "TechCorp",
        "employees": [
            {
                "name": "Alice",
                "age": 30,
                "addresses": [
                    {
                        "street": "123 Main St",
                        "city": "Seattle",
                        "coordinates": (47.6062, -122.3321),
                    }
                ],
                "phone_numbers": {
                    "home": "555-1234",
                    "work": "555-5678",
                },
            },
            {
                "name": "Bob",
                "age": 25,
                "addresses": [
                    {
                        "street": "456 Oak Ave",
                        "city": "Portland",
                        "coordinates": (45.5152, -122.6784),
                    }
                ],
                "phone_numbers": {
                    "mobile": "555-9999",
                },
            },
        ],
        "departments": {
            "engineering": {
                "head": "Alice",
                "budget": Decimal("1000000"),
            },
            "sales": {
                "head": "Bob",
                "budget": Decimal("500000"),
            },
        },
    }
    
    try:
        # Validate
        company_val = company_type.validate(company_data)
        print("✅ Complex structure validated successfully")
        
        # Test JSON serialization
        json_data = marshal(company_val, format_kind=WireFormatType.JSON)
        json_decoded = unmarshal(json_data, format_kind=WireFormatType.JSON, expected_type=company_type)
        print("✅ JSON serialization/deserialization successful")
        print(f"   JSON size: {len(json_data)} bytes")
        
        # Test MessagePack serialization
        msgpack_data = marshal(company_val, format_kind=WireFormatType.MSGPACK)
        msgpack_decoded = unmarshal(msgpack_data, format_kind=WireFormatType.MSGPACK, expected_type=company_type)
        print("✅ MessagePack serialization/deserialization successful")
        print(f"   MessagePack size: {len(msgpack_data)} bytes")
        print(f"   Size reduction: {100 * (1 - len(msgpack_data)/len(json_data)):.1f}%")
        
        # Verify data integrity
        alice = json_decoded['employees'].value[0]
        assert alice['name'].value == "Alice"
        assert alice['addresses'].value[0]['city'].value == "Seattle"
        print("✅ Data integrity verified")
        
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    
    print()


def test_special_values():
    """Test special values like null and unknown."""
    print("🧪 Testing Special Values\n")
    
    # Object with optional fields
    optional_type = CtyObject(
        attribute_types={
            "required": CtyString(),
            "optional": CtyString(),
        },
        optional_attributes=frozenset(["optional"]),
    )
    
    test_cases = [
        ("Null String", CtyValue.null(CtyString())),
        ("Unknown Number", CtyValue.unknown(CtyNumber())),
        ("Object with null optional", optional_type.validate({"required": "yes"})),
    ]
    
    for name, cty_val in test_cases:
        try:
            # Get the type for deserialization
            val_type = cty_val.type
            
            # Test JSON
            json_data = marshal(cty_val, format_kind=WireFormatType.JSON)
            json_decoded = unmarshal(json_data, format_kind=WireFormatType.JSON, expected_type=val_type)
            
            # Test MessagePack
            msgpack_data = marshal(cty_val, format_kind=WireFormatType.MSGPACK)
            msgpack_decoded = unmarshal(msgpack_data, format_kind=WireFormatType.MSGPACK, expected_type=val_type)
            
            print(f"✅ {name}: Both formats successful")
            
        except Exception as e:
            print(f"❌ {name}: {type(e).__name__}: {e}")
    
    print()


def test_marked_values():
    """Test values with marks."""
    print("🧪 Testing Marked Values\n")
    
    # Create marked values
    sensitive_password = CtyString().validate("super-secret").mark(CtyMark("sensitive"))
    tracked_value = CtyNumber().validate(42).mark(CtyMark("audit")).mark(CtyMark("important"))
    
    test_cases = [
        ("Sensitive string", sensitive_password),
        ("Multi-marked number", tracked_value),
    ]
    
    for name, cty_val in test_cases:
        try:
            val_type = cty_val.type
            
            # Test JSON
            json_data = marshal(cty_val, format_kind=WireFormatType.JSON)
            json_decoded = unmarshal(json_data, format_kind=WireFormatType.JSON, expected_type=val_type)
            
            # Check marks preserved
            if hasattr(json_decoded, 'marks'):
                marks_preserved = len(json_decoded.marks) == len(cty_val.marks)
            else:
                marks_preserved = False
            
            print(f"{'✅' if marks_preserved else '⚠️'} {name}: Marks {'preserved' if marks_preserved else 'lost'} in JSON")
            
        except Exception as e:
            print(f"❌ {name}: {type(e).__name__}: {e}")
    
    print()


def test_error_cases():
    """Test various error conditions."""
    print("🧪 Testing Error Cases\n")
    
    # Type mismatch
    try:
        string_val = CtyString().validate("hello")
        json_data = marshal(string_val, format_kind=WireFormatType.JSON)
        # Try to deserialize as wrong type
        unmarshal(json_data, format_kind=WireFormatType.JSON, expected_type=CtyNumber())
        print("❌ Type mismatch should have failed")
    except Exception as e:
        print(f"✅ Type mismatch caught: {type(e).__name__}")
    
    # Invalid structure
    try:
        obj_type = CtyObject({"name": CtyString(), "age": CtyNumber()})
        # Missing required field
        obj_type.validate({"name": "Alice"})
        print("❌ Missing required field should have failed")
    except CtyValidationError:
        print("✅ Missing required field caught")
    
    # Deep nesting limit (if any)
    try:
        # Create very deep nesting
        deep_type = CtyString()
        for i in range(100):
            deep_type = CtyList(element_type=deep_type)
        
        # This might fail at type creation or validation
        deep_val = deep_type.validate([[[[[["deep"]]]]]])
        print("⚠️  Very deep nesting allowed (might impact performance)")
    except Exception as e:
        print(f"✅ Deep nesting limit: {type(e).__name__}")
    
    print()


def main():
    """Run all tests."""
    print("🌟 JSON/MessagePack Conversion Test Suite\n")
    print("=" * 60)
    
    test_basic_types()
    test_collection_types()
    test_nested_structures()
    test_special_values()
    test_marked_values()
    test_error_cases()
    
    print("=" * 60)
    print("\n✨ Test suite completed!")
    
    # Note about MessagePack compatibility
    print("\n📝 Note: MessagePack compatibility with go-cty may have issues.")
    print("   For critical cross-language communication, use JSON format.")


if __name__ == "__main__":
    main()
