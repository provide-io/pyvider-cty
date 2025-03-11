
# tests/integration/cty/function/test_stdlib.py

"""
Integration tests for CTY standard library functions.

These tests verify that the standard library functions work correctly with other
parts of the CTY system, including types, values, and conversions.
"""

import asyncio
import os
import tempfile
from decimal import Decimal
from pathlib import Path

import pytest

from pyvider.cty.types.primitives import CtyString, CtyNumber, CtyBool
from pyvider.cty.types.collections import CtyList, CtyMap, CtySet
from pyvider.cty.types.structural import CtyObject, CtyDynamic
from pyvider.cty.values.base import Value
from pyvider.cty.function.base import registry
from pyvider.cty.function.stdlib import *  # Import to register functions

class TestStdlibFunctions:
    """Test the CTY standard library functions."""
    
    @pytest.mark.asyncio
    async def test_string_functions(self):
        """Test string manipulation functions."""
        # upper
        upper_fn = registry.get("upper")
        assert upper_fn is not None
        
        result = await upper_fn(Value(type_=CtyString(), value="hello"))
        assert result.value == "HELLO"
        
        # lower
        lower_fn = registry.get("lower")
        assert lower_fn is not None
        
        result = await lower_fn(Value(type_=CtyString(), value="HELLO"))
        assert result.value == "hello"
        
        # title
        title_fn = registry.get("title")
        assert title_fn is not None
        
        result = await title_fn(Value(type_=CtyString(), value="hello world"))
        assert result.value == "Hello World"
        
        # trim
        trim_fn = registry.get("trim")
        assert trim_fn is not None
        
        result = await trim_fn(Value(type_=CtyString(), value="  hello  "))
        assert result.value == "hello"
        
        # substr
        substr_fn = registry.get("substr")
        assert substr_fn is not None
        
        result = await substr_fn(
            Value(type_=CtyString(), value="hello world"),
            Value(type_=CtyNumber(), value=6),
            Value(type_=CtyNumber(), value=5)
        )
        assert result.value == "world"
        
        # Test substr with negative offset
        result = await substr_fn(
            Value(type_=CtyString(), value="hello world"),
            Value(type_=CtyNumber(), value=-5),
            Value(type_=CtyNumber(), value=5)
        )
        assert result.value == "world"
        
        # replace
        replace_fn = registry.get("replace")
        assert replace_fn is not None
        
        result = await replace_fn(
            Value(type_=CtyString(), value="hello world"),
            Value(type_=CtyString(), value="world"),
            Value(type_=CtyString(), value="terraform")
        )
        assert result.value == "hello terraform"
        
        # format
        format_fn = registry.get("format")
        assert format_fn is not None
        
        result = await format_fn(
            Value(type_=CtyString(), value="Hello, {0}!"),
            Value(type_=CtyString(), value="world")
        )
        assert result.value == "Hello, world!"
        
        # Test format with multiple arguments
        result = await format_fn(
            Value(type_=CtyString(), value="{0} {1} {2}"),
            Value(type_=CtyString(), value="Hello"),
            Value(type_=CtyString(), value="Terraform"),
            Value(type_=CtyString(), value="World")
        )
        assert result.value == "Hello Terraform World"
        
    @pytest.mark.asyncio
    async def test_numeric_functions(self):
        """Test numeric functions."""
        # abs
        abs_fn = registry.get("abs")
        assert abs_fn is not None
        
        result = await abs_fn(Value(type_=CtyNumber(), value=-42))
        assert result.value == 42
        
        # ceil
        ceil_fn = registry.get("ceil")
        assert ceil_fn is not None
        
        result = await ceil_fn(Value(type_=CtyNumber(), value=4.3))
        assert result.value == 5
        
        # floor
        floor_fn = registry.get("floor")
        assert floor_fn is not None
        
        result = await floor_fn(Value(type_=CtyNumber(), value=4.7))
        assert result.value == 4
        
        # max
        max_fn = registry.get("max")
        assert max_fn is not None
        
        result = await max_fn(
            Value(type_=CtyNumber(), value=1),
            Value(type_=CtyNumber(), value=5),
            Value(type_=CtyNumber(), value=3)
        )
        assert result.value == 5
        
        # min
        min_fn = registry.get("min")
        assert min_fn is not None
        
        result = await min_fn(
            Value(type_=CtyNumber(), value=1),
            Value(type_=CtyNumber(), value=5),
            Value(type_=CtyNumber(), value=3)
        )
        assert result.value == 1
        
        # Test with Decimal values
        result = await min_fn(
            Value(type_=CtyNumber(), value=Decimal("1.1")),
            Value(type_=CtyNumber(), value=Decimal("1.2")),
            Value(type_=CtyNumber(), value=Decimal("1.3"))
        )
        assert result.value == Decimal("1.1")
        
    @pytest.mark.asyncio
    async def test_collection_functions(self):
        """Test collection functions."""
        # length
        length_fn = registry.get("length")
        assert length_fn is not None
        
        # Test with string
        result = await length_fn(Value(type_=CtyString(), value="hello"))
        assert result.value == 5
        
        # Test with list
        result = await length_fn(Value(
            type_=CtyList(element_type=CtyString()),
            value=["a", "b", "c"]
        ))
        assert result.value == 3
        
        # Test with map
        result = await length_fn(Value(
            type_=CtyMap(key_type=CtyString(), value_type=CtyString()),
            value={"a": "A", "b": "B", "c": "C"}
        ))
        assert result.value == 3
        
        # element
        element_fn = registry.get("element")
        assert element_fn is not None
        
        result = await element_fn(
            Value(
                type_=CtyList(element_type=CtyString()),
                value=["a", "b", "c"]
            ),
            Value(type_=CtyNumber(), value=1)
        )
        assert result.value == "b"
        
        # Test element with negative index
        result = await element_fn(
            Value(
                type_=CtyList(element_type=CtyString()),
                value=["a", "b", "c"]
            ),
            Value(type_=CtyNumber(), value=-1)
        )
        assert result.value == "c"
        
        # contains
        contains_fn = registry.get("contains")
        assert contains_fn is not None
        
        # Test with list
        result = await contains_fn(
            Value(
                type_=CtyList(element_type=CtyString()),
                value=["a", "b", "c"]
            ),
            Value(type_=CtyString(), value="b")
        )
        assert result.value is True
        
        # Test with map (checks keys)
        result = await contains_fn(
            Value(
                type_=CtyMap(key_type=CtyString(), value_type=CtyString()),
                value={"a": "A", "b": "B", "c": "C"}
            ),
            Value(type_=CtyString(), value="b")
        )
        assert result.value is True
        
        # Test with string
        result = await contains_fn(
            Value(type_=CtyString(), value="hello world"),
            Value(type_=CtyString(), value="world")
        )
        assert result.value is True
        
        # keys
        keys_fn = registry.get("keys")
        assert keys_fn is not None
        
        result = await keys_fn(Value(
            type_=CtyMap(key_type=CtyString(), value_type=CtyString()),
            value={"a": "A", "b": "B", "c": "C"}
        ))
        assert isinstance(result.value, list)
        assert set(result.value) == {"a", "b", "c"}
        
        # values
        values_fn = registry.get("values")
        assert values_fn is not None
        
        result = await values_fn(Value(
            type_=CtyMap(key_type=CtyString(), value_type=CtyString()),
            value={"a": "A", "b": "B", "c": "C"}
        ))
        assert isinstance(result.value, list)
        assert set(result.value) == {"A", "B", "C"}
        
        # merge
        merge_fn = registry.get("merge")
        assert merge_fn is not None
        
        result = await merge_fn(
            Value(
                type_=CtyMap(key_type=CtyString(), value_type=CtyString()),
                value={"a": "A", "b": "B"}
            ),
            Value(
                type_=CtyMap(key_type=CtyString(), value_type=CtyString()),
                value={"b": "BB", "c": "C"}
            )
        )
        assert result.value == {"a": "A", "b": "BB", "c": "C"}
        
    @pytest.mark.asyncio
    async def test_conversion_functions(self):
        """Test conversion functions."""
        # tostring
        tostring_fn = registry.get("tostring")
        assert tostring_fn is not None
        
        # Test with number
        result = await tostring_fn(Value(type_=CtyNumber(), value=42))
        assert result.value == "42"
        
        # Test with bool
        result = await tostring_fn(Value(type_=CtyBool(), value=True))
        assert result.value == "True"
        
        # Test with list
        result = await tostring_fn(Value(
            type_=CtyList(element_type=CtyString()),
            value=["a", "b", "c"]
        ))
        assert result.value == '["a", "b", "c"]' or result.value == '["a","b","c"]'
        
        # tonumber
        tonumber_fn = registry.get("tonumber")
        assert tonumber_fn is not None
        
        # Test with string
        result = await tonumber_fn(Value(type_=CtyString(), value="42"))
        assert result.value == 42
        
        # Test with bool
        result = await tonumber_fn(Value(type_=CtyBool(), value=True))
        assert result.value == 1
        
        # Test with invalid string
        result = await tonumber_fn(Value(type_=CtyString(), value="not a number"))
        assert result.is_null
        
        # tobool
        tobool_fn = registry.get("tobool")
        assert tobool_fn is not None
        
        # Test with string "true"
        result = await tobool_fn(Value(type_=CtyString(), value="true"))
        assert result.value is True
        
        # Test with string "false"
        result = await tobool_fn(Value(type_=CtyString(), value="false"))
        assert result.value is False
        
        # Test with number 1
        result = await tobool_fn(Value(type_=CtyNumber(), value=1))
        assert result.value is True
        
        # Test with number 0
        result = await tobool_fn(Value(type_=CtyNumber(), value=0))
        assert result.value is False
        
        # Test with invalid string
        result = await tobool_fn(Value(type_=CtyString(), value="not a bool"))
        assert result.is_null
        
    @pytest.mark.asyncio
    async def test_filesystem_functions(self):
        """Test filesystem functions."""
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write("Hello, Terraform!")
            temp_path = temp_file.name
        
        try:
            # file
            file_fn = registry.get("file")
            assert file_fn is not None
            
            result = await file_fn(Value(type_=CtyString(), value=temp_path))
            assert result.value == "Hello, Terraform!"
            
            # fileexists
            fileexists_fn = registry.get("fileexists")
            assert fileexists_fn is not None
            
            result = await fileexists_fn(Value(type_=CtyString(), value=temp_path))
            assert result.value is True
            
            result = await fileexists_fn(Value(type_=CtyString(), value=temp_path + ".nonexistent"))
            assert result.value is False
            
            # dirname
            dirname_fn = registry.get("dirname")
            assert dirname_fn is not None
            
            result = await dirname_fn(Value(type_=CtyString(), value=temp_path))
            assert result.value == os.path.dirname(temp_path)
            
            # basename
            basename_fn = registry.get("basename")
            assert basename_fn is not None
            
            result = await basename_fn(Value(type_=CtyString(), value=temp_path))
            assert result.value == os.path.basename(temp_path)
            
        finally:
            # Clean up
            try:
                os.unlink(temp_path)
            except:
                pass
                
    @pytest.mark.asyncio
    async def test_crypto_functions(self):
        """Test crypto functions."""
        # base64encode
        base64encode_fn = registry.get("base64encode")
        assert base64encode_fn is not None
        
        result = await base64encode_fn(Value(type_=CtyString(), value="Hello, Terraform!"))
        assert result.value == "SGVsbG8sIFRlcnJhZm9ybSE="
        
        # base64decode
        base64decode_fn = registry.get("base64decode")
        assert base64decode_fn is not None
        
        result = await base64decode_fn(Value(type_=CtyString(), value="SGVsbG8sIFRlcnJhZm9ybSE="))
        assert result.value == "Hello, Terraform!"
        
        # md5
        md5_fn = registry.get("md5")
        assert md5_fn is not None
        
        result = await md5_fn(Value(type_=CtyString(), value="Hello, Terraform!"))
        assert result.value == "cbe9f1b62e7cf99eebc43d7641900656"
        
        # sha1
        sha1_fn = registry.get("sha1")
        assert sha1_fn is not None
        
        result = await sha1_fn(Value(type_=CtyString(), value="Hello, Terraform!"))
        assert result.value == "d963e2a3a3b2e76b9219470ea8c4a1fa0c9f112b"
        
        # sha256
        sha256_fn = registry.get("sha256")
        assert sha256_fn is not None
        
        result = await sha256_fn(Value(type_=CtyString(), value="Hello, Terraform!"))
        assert result.value == "37c3422fccd0a84d0a9a4c45d19a2223fa5731e11bd9875840b79074622e1d78"
        
    @pytest.mark.asyncio
    async def test_null_and_unknown_handling(self):
        """Test that functions handle null and unknown values correctly."""
        # Test with null
        upper_fn = registry.get("upper")
        result = await upper_fn(Value(type_=CtyString(), is_null=True))
        assert result.is_null
        
        # Test with unknown
        result = await upper_fn(Value(type_=CtyString(), is_unknown=True))
        assert result.is_unknown
        
        # Test with multiple arguments where one is null
        replace_fn = registry.get("replace")
        result = await replace_fn(
            Value(type_=CtyString(), value="hello world"),
            Value(type_=CtyString(), value="world"),
            Value(type_=CtyString(), is_null=True)
        )
        assert result.is_null
        
        # Test with multiple arguments where one is unknown
        result = await replace_fn(
            Value(type_=CtyString(), value="hello world"),
            Value(type_=CtyString(), is_unknown=True),
            Value(type_=CtyString(), value="terraform")
        )
        assert result.is_unknown