#
# tests/capsule/test_cty_capsule_base.py
#

import pytest
import unittest
import pickle
from unittest.mock import MagicMock

import pytest

from pyvider.cty.exceptions import ValidationError, CapsuleError
from pyvider.cty.types.capsule import CtyCapsule
from pyvider.cty.capsule import capsule_type, capsule_val, capsule_type_with_ops
from pyvider.cty.values import CtyValue


class TestCtyCapsuleType(unittest.TestCase):
    """Test CtyCapsule type functionality."""
    
    def setUp(self):
        """Set up test fixtures before each test."""
        # Define test classes
        class TestObj:
            def __init__(self, name):
                self.name = name
                
            def __eq__(self, other):
                if not isinstance(other, TestObj):
                    return False
                return self.name == other.name
        
        self.TestObj = TestObj
        
        # Create test values
        self.test_obj = TestObj("test")
        
        # Create capsule types
        self.obj_type = capsule_type("test_obj", TestObj)
        
        # Create operations
        def test_op(value):
            return value.name.upper()
            
        # Create capsule type with operations
        self.ops_type = capsule_type_with_ops(
            "test_ops",
            TestObj,
            {"uppercase": test_op}
        )
    
    def test_capsule_type_creation(self):
        """Test creating a capsule type."""
        # Basic type creation
        capsule = capsule_type("test", str)
        self.assertEqual(capsule.friendly_name, "test")
        self.assertEqual(capsule.encapsulated_type, str)
        
        # With operations
        ops_capsule = capsule_type_with_ops(
            "test_ops",
            dict,
            {"test_op": lambda x: x}
        )
        self.assertEqual(ops_capsule.friendly_name, "test_ops")
        self.assertEqual(ops_capsule.encapsulated_type, dict)
        self.assertIn("test_op", ops_capsule.operations)
    
    def test_capsule_type_validation(self):
        """Test validation errors during type creation."""
        # Empty friendly name
        with self.assertRaises(ValidationError):
            capsule_type("", str)
            
        # None encapsulated type
        with self.assertRaises(ValidationError):
            capsule_type("test", None)
            
        # Invalid operation
        with self.assertRaises(ValidationError):
            capsule_type_with_ops("test", str, {"invalid": "not_callable"})
    
    def test_capsule_type_equality(self):
        """Test that capsule types compare by identity."""
        type1 = capsule_type("same", str)
        type2 = capsule_type("same", str)
        
        # Different instances with same params should NOT be equal
        self.assertFalse(type1.equal(type2))
        
        # Same instance should be equal to itself
        self.assertTrue(type1.equal(type1))
    
    def test_capsule_value_creation(self):
        """Test creating capsule values."""
        # Valid value
        val = capsule_val(self.obj_type, self.test_obj)
        self.assertEqual(val.type, self.obj_type)
        self.assertEqual(val.value, self.test_obj)
        
        # None is always valid
        null_val = capsule_val(self.obj_type, None)
        self.assertEqual(null_val.type, self.obj_type)
        self.assertTrue(null_val.is_null)
        
        # Invalid type
        with self.assertRaises(ValidationError):
            capsule_val(self.obj_type, "not_an_obj")
    
    def test_encapsulated_value_access(self):
        """Test accessing the encapsulated value."""
        val = capsule_val(self.obj_type, self.test_obj)
        
        # Get encapsulated value
        encapsulated = val.encapsulated_value()
        self.assertEqual(encapsulated, self.test_obj)
        
        # Test with null value
        null_val = capsule_val(self.obj_type, None)
        self.assertIsNone(null_val.encapsulated_value())
        
        # Test with unknown value
        unknown_val = CtyValue(type_=self.obj_type, is_unknown=True)
        with self.assertRaises(ValueError):
            unknown_val.encapsulated_value()
    
    def test_operations(self):
        """Test custom operations on capsule types."""
        # Create a value with the operations type
        val = capsule_val(self.ops_type, self.test_obj)
        
        # Get the operation
        uppercase_op = self.ops_type.get_operation("uppercase")
        self.assertIsNotNone(uppercase_op)
        
        # Execute the operation
        result = uppercase_op(val.value)
        self.assertEqual(result, "TEST")
        
        # Check operation existence
        self.assertTrue(self.ops_type.has_operation("uppercase"))
        self.assertFalse(self.ops_type.has_operation("nonexistent"))


class TestCapsuleSerialization(unittest.TestCase):
    """Test capsule serialization and deserialization."""
    
    def setUp(self):
        """Set up test fixtures before each test."""
        # Define test classes
        class TestObj:
            def __init__(self, name, value):
                self.name = name
                self.value = value
                
        self.TestObj = TestObj
        
        # Create test values
        self.test_obj = TestObj("test", 42)
        
        # Create capsule types
        self.obj_type = capsule_type("test_obj", TestObj)
        
        # Create capsule values
        self.obj_val = capsule_val(self.obj_type, self.test_obj)
    
    def test_json_serialization(self):
        """Test JSON serialization of capsule values."""
        from pyvider.cty.encoding import serialize, deserialize
        
        # Serialize to JSON
        serialized = serialize(self.obj_val, "json")
        self.assertIsInstance(serialized, bytes)
        
        # Deserialize from JSON
        deserialized = deserialize(serialized, "json")
        
        # Verify the result
        self.assertIsInstance(deserialized, CtyValue)
        self.assertEqual(deserialized.type.friendly_name, self.obj_type.friendly_name)
        
        # Verify encapsulated value
        encapsulated = deserialized.encapsulated_value()
        self.assertEqual(encapsulated.name, self.test_obj.name)
        self.assertEqual(encapsulated.value, self.test_obj.value)
    
    def test_msgpack_serialization(self):
        """Test MessagePack serialization of capsule values."""
        from pyvider.cty.encoding import serialize, deserialize
        
        # Serialize to MessagePack
        serialized = serialize(self.obj_val, "msgpack")
        self.assertIsInstance(serialized, bytes)
        
        # Deserialize from MessagePack
        deserialized = deserialize(serialized, "msgpack")
        
        # Verify the result
        self.assertIsInstance(deserialized, CtyValue)
        self.assertEqual(deserialized.type.friendly_name, self.obj_type.friendly_name)
        
        # Verify encapsulated value
        encapsulated = deserialized.encapsulated_value()
        self.assertEqual(encapsulated.name, self.test_obj.name)
        self.assertEqual(encapsulated.value, self.test_obj.value)
    
    def test_non_serializable_value(self):
        """Test handling of non-serializable values."""
        from pyvider.cty.encoding import serialize
        
        # Create a non-serializable object
        class NonSerializable:
            def __reduce__(self):
                raise TypeError("Not serializable")
        
        # Create a capsule type and value
        non_serializable_type = capsule_type("non_serializable", NonSerializable)
        non_serializable_val = capsule_val(non_serializable_type, NonSerializable())
        
        # Try to serialize
        from pyvider.cty.exceptions import CapsuleSerializationError
        with self.assertRaises(CapsuleSerializationError):
            serialize(non_serializable_val, "json")
