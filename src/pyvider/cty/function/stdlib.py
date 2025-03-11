#!/usr/bin/env python3
# pyvider/cty/function/stdlib.py

"""
Standard library of functions for CTY.

This module provides a set of standard functions that can be used in
Terraform expressions. It implements the core set of functions that
are available in Terraform's HCL language.

The functions are organized into categories:
- String manipulation
- Numeric operations
- Collection operations
- Type conversion
- Logical operations
- Filesystem operations

Each function is registered with the global function registry.
"""

import asyncio
import os
import re
import hashlib
import base64
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Union

from pyvider.telemetry import logger
from pyvider.cty.types.base import CtyType
from pyvider.cty.types.primitives import CtyString, CtyNumber, CtyBool
from pyvider.cty.types.collections import CtyList, CtyMap, CtySet
from pyvider.cty.types.structural import CtyObject, CtyDynamic, CtyTuple
from pyvider.cty.values.base import Value
from pyvider.cty.function.base import (
    Parameter,
    VariadicParameter,
    FunctionSpec,
    Function,
    registry,
)

#
# Type Helpers
#

def return_type_number(args: List[Value]) -> CtyType:
    """Always returns CtyNumber type."""
    return CtyNumber()
    
def return_type_string(args: List[Value]) -> CtyType:
    """Always returns CtyString type."""
    return CtyString()
    
def return_type_bool(args: List[Value]) -> CtyType:
    """Always returns CtyBool type."""
    return CtyBool()
    
def return_type_first_arg(args: List[Value]) -> CtyType:
    """Returns the type of the first argument."""
    if not args:
        return CtyDynamic()
    return args[0].type
    
def return_type_list_of(args: List[Value]) -> CtyType:
    """Returns a list type with element type from the first argument."""
    if not args:
        return CtyList(element_type=CtyDynamic())
    return CtyList(element_type=args[0].type)

#
# String Functions
#

def fn_upper(args: List[Value], return_type: CtyType) -> Value:
    """Convert string to uppercase."""
    if args[0].is_null:
        return Value(type_=return_type, is_null=True)
        
    if args[0].is_unknown:
        return Value(type_=return_type, is_unknown=True)
        
    result = str(args[0].value).upper()
    return Value(type_=return_type, value=result)
    
def fn_lower(args: List[Value], return_type: CtyType) -> Value:
    """Convert string to lowercase."""
    if args[0].is_null:
        return Value(type_=return_type, is_null=True)
        
    if args[0].is_unknown:
        return Value(type_=return_type, is_unknown=True)
        
    result = str(args[0].value).lower()
    return Value(type_=return_type, value=result)
    
def fn_title(args: List[Value], return_type: CtyType) -> Value:
    """Convert string to title case."""
    if args[0].is_null:
        return Value(type_=return_type, is_null=True)
        
    if args[0].is_unknown:
        return Value(type_=return_type, is_unknown=True)
        
    result = str(args[0].value).title()
    return Value(type_=return_type, value=result)
    
def fn_trim(args: List[Value], return_type: CtyType) -> Value:
    """Trim whitespace from string."""
    if args[0].is_null:
        return Value(type_=return_type, is_null=True)
        
    if args[0].is_unknown:
        return Value(type_=return_type, is_unknown=True)
        
    result = str(args[0].value).strip()
    return Value(type_=return_type, value=result)
    
def fn_substr(args: List[Value], return_type: CtyType) -> Value:
    """Extract substring."""
    if any(arg.is_null for arg in args):
        return Value(type_=return_type, is_null=True)
        
    if any(arg.is_unknown for arg in args):
        return Value(type_=return_type, is_unknown=True)
        
    s = str(args[0].value)
    offset = int(args[1].value)
    length = int(args[2].value) if len(args) > 2 else len(s) - offset
    
    # Adjust negative offset
    if offset < 0:
        offset = len(s) + offset
        
    # Bounds checking
    if offset < 0 or offset >= len(s):
        return Value(type_=return_type, value="")
        
    # Extract substring
    result = s[offset:offset + length]
    return Value(type_=return_type, value=result)
    
def fn_replace(args: List[Value], return_type: CtyType) -> Value:
    """Replace substring."""
    if any(arg.is_null for arg in args):
        return Value(type_=return_type, is_null=True)
        
    if any(arg.is_unknown for arg in args):
        return Value(type_=return_type, is_unknown=True)
        
    s = str(args[0].value)
    search = str(args[1].value)
    replace = str(args[2].value)
    
    result = s.replace(search, replace)
    return Value(type_=return_type, value=result)
    
def fn_format(args: List[Value], return_type: CtyType) -> Value:
    """Format string using format specifiers."""
    if any(arg.is_null for arg in args):
        return Value(type_=return_type, is_null=True)
        
    if any(arg.is_unknown for arg in args):
        return Value(type_=return_type, is_unknown=True)
        
    format_str = str(args[0].value)
    format_args = [arg.value for arg in args[1:]]
    
    try:
        result = format_str.format(*format_args)
        return Value(type_=return_type, value=result)
    except Exception as e:
        logger.error(f"🧰🔧❌ Error formatting string: {e}")
        # Return original string on error
        return Value(type_=return_type, value=format_str)

#
# Numeric Functions
#

def fn_abs(args: List[Value], return_type: CtyType) -> Value:
    """Absolute value."""
    if args[0].is_null:
        return Value(type_=return_type, is_null=True)
        
    if args[0].is_unknown:
        return Value(type_=return_type, is_unknown=True)
        
    num = args[0].value
    if isinstance(num, Decimal):
        result = abs(num)
    else:
        result = abs(Decimal(str(num)))
        
    return Value(type_=return_type, value=result)
    
def fn_ceil(args: List[Value], return_type: CtyType) -> Value:
    """Ceiling function (round up)."""
    if args[0].is_null:
        return Value(type_=return_type, is_null=True)
        
    if args[0].is_unknown:
        return Value(type_=return_type, is_unknown=True)
        
    num = args[0].value
    if isinstance(num, Decimal):
        result = num.quantize(Decimal('1.'), rounding=ROUND_HALF_UP)
    else:
        result = Decimal(str(num)).quantize(Decimal('1.'), rounding=ROUND_HALF_UP)
        
    return Value(type_=return_type, value=result)
    
def fn_floor(args: List[Value], return_type: CtyType) -> Value:
    """Floor function (round down)."""
    if args[0].is_null:
        return Value(type_=return_type, is_null=True)
        
    if args[0].is_unknown:
        return Value(type_=return_type, is_unknown=True)
        
    num = args[0].value
    if isinstance(num, Decimal):
        result = num.to_integral_exact(rounding=ROUND_HALF_UP)
    else:
        result = Decimal(str(num)).to_integral_exact(rounding=ROUND_HALF_UP)
        
    return Value(type_=return_type, value=result)
    
def fn_max(args: List[Value], return_type: CtyType) -> Value:
    """Maximum value."""
    if any(arg.is_null for arg in args):
        return Value(type_=return_type, is_null=True)
        
    if any(arg.is_unknown for arg in args):
        return Value(type_=return_type, is_unknown=True)
        
    # Convert all to Decimal for consistency
    nums = []
    for arg in args:
        if isinstance(arg.value, Decimal):
            nums.append(arg.value)
        else:
            nums.append(Decimal(str(arg.value)))
            
    result = max(nums)
    return Value(type_=return_type, value=result)
    
def fn_min(args: List[Value], return_type: CtyType) -> Value:
    """Minimum value."""
    if any(arg.is_null for arg in args):
        return Value(type_=return_type, is_null=True)
        
    if any(arg.is_unknown for arg in args):
        return Value(type_=return_type, is_unknown=True)
        
    # Convert all to Decimal for consistency
    nums = []
    for arg in args:
        if isinstance(arg.value, Decimal):
            nums.append(arg.value)
        else:
            nums.append(Decimal(str(arg.value)))
            
    result = min(nums)
    return Value(type_=return_type, value=result)

#
# Collection Functions
#

def fn_length(args: List[Value], return_type: CtyType) -> Value:
    """Get length of a string or collection."""
    if args[0].is_null:
        return Value(type_=return_type, is_null=True)
        
    if args[0].is_unknown:
        return Value(type_=return_type, is_unknown=True)
        
    value = args[0].value
    
    if isinstance(value, (str, list, dict, set, tuple)):
        result = len(value)
    else:
        # Try to convert to string and get length
        result = len(str(value))
        
    return Value(type_=return_type, value=result)
    
def fn_element(args: List[Value], return_type: CtyType) -> Value:
    """Get element from list at specified index."""
    if any(arg.is_null for arg in args):
        return Value(type_=return_type, is_null=True)
        
    if any(arg.is_unknown for arg in args):
        return Value(type_=return_type, is_unknown=True)
        
    lst = args[0].value
    index = int(args[1].value)
    
    # Handle negative indices
    if index < 0:
        index = len(lst) + index
        
    # Bounds checking
    if not isinstance(lst, (list, tuple)) or index < 0 or index >= len(lst):
        return Value(type_=return_type, is_null=True)
        
    result = lst[index]
    return Value(type_=return_type, value=result)
    
def fn_contains(args: List[Value], return_type: CtyType) -> Value:
    """Check if list contains a value."""
    if any(arg.is_null for arg in args):
        return Value(type_=return_type, is_null=True)
        
    if any(arg.is_unknown for arg in args):
        return Value(type_=return_type, is_unknown=True)
        
    lst = args[0].value
    value = args[1].value
    
    # For dicts, check if key exists
    if isinstance(lst, dict):
        result = value in lst
    # For strings, check substring
    elif isinstance(lst, str):
        result = str(value) in lst
    # For collections, check membership
    elif isinstance(lst, (list, tuple, set)):
        result = value in lst
    else:
        result = False
        
    return Value(type_=return_type, value=result)
    
def fn_keys(args: List[Value], return_type: CtyType) -> Value:
    """Get keys from a map."""
    if args[0].is_null:
        return Value(type_=return_type, is_null=True)
        
    if args[0].is_unknown:
        return Value(type_=return_type, is_unknown=True)
        
    value = args[0].value
    
    if not isinstance(value, dict):
        return Value(type_=return_type, is_null=True)
        
    result = list(value.keys())
    return Value(type_=return_type, value=result)
    
def fn_values(args: List[Value], return_type: CtyType) -> Value:
    """Get values from a map."""
    if args[0].is_null:
        return Value(type_=return_type, is_null=True)
        
    if args[0].is_unknown:
        return Value(type_=return_type, is_unknown=True)
        
    value = args[0].value
    
    if not isinstance(value, dict):
        return Value(type_=return_type, is_null=True)
        
    result = list(value.values())
    return Value(type_=return_type, value=result)
    
def fn_merge(args: List[Value], return_type: CtyType) -> Value:
    """Merge maps."""
    if any(arg.is_null for arg in args):
        return Value(type_=return_type, is_null=True)
        
    if any(arg.is_unknown for arg in args):
        return Value(type_=return_type, is_unknown=True)
        
    # Ensure all args are dicts
    if not all(isinstance(arg.value, dict) for arg in args):
        return Value(type_=return_type, is_null=True)
        
    # Start with empty dict
    result = {}
    
    # Merge all dicts
    for arg in args:
        result.update(arg.value)
        
    return Value(type_=return_type, value=result)

#
# Conversion Functions
#

def fn_tostring(args: List[Value], return_type: CtyType) -> Value:
    """Convert to string."""
    if args[0].is_null:
        return Value(type_=return_type, is_null=True)
        
    if args[0].is_unknown:
        return Value(type_=return_type, is_unknown=True)
        
    value = args[0].value
    
    # Special handling for collections
    if isinstance(value, (list, dict, set)):
        try:
            result = json.dumps(value)
        except Exception:
            result = str(value)
    else:
        result = str(value)
        
    return Value(type_=return_type, value=result)
    
def fn_tonumber(args: List[Value], return_type: CtyType) -> Value:
    """Convert to number."""
    if args[0].is_null:
        return Value(type_=return_type, is_null=True)
        
    if args[0].is_unknown:
        return Value(type_=return_type, is_unknown=True)
        
    value = args[0].value
    
    try:
        if isinstance(value, bool):
            result = Decimal(1 if value else 0)
        elif isinstance(value, (int, float, Decimal)):
            result = Decimal(str(value))
        elif isinstance(value, str):
            result = Decimal(value)
        else:
            # Can't convert
            return Value(type_=return_type, is_null=True)
    except Exception:
        # Conversion failed
        return Value(type_=return_type, is_null=True)
        
    return Value(type_=return_type, value=result)
    
def fn_tobool(args: List[Value], return_type: CtyType) -> Value:
    """Convert to bool."""
    if args[0].is_null:
        return Value(type_=return_type, is_null=True)
        
    if args[0].is_unknown:
        return Value(type_=return_type, is_unknown=True)
        
    value = args[0].value
    
    if isinstance(value, bool):
        result = value
    elif isinstance(value, (int, float, Decimal)):
        result = bool(value)
    elif isinstance(value, str):
        lower = value.lower()
        if lower in ("true", "yes", "1"):
            result = True
        elif lower in ("false", "no", "0"):
            result = False
        else:
            # Can't convert
            return Value(type_=return_type, is_null=True)
    else:
        # Can't convert
        return Value(type_=return_type, is_null=True)
        
    return Value(type_=return_type, value=result)

#
# Filesystem Functions
#

def fn_file(args: List[Value], return_type: CtyType) -> Value:
    """Read file contents."""
    if args[0].is_null:
        return Value(type_=return_type, is_null=True)
        
    if args[0].is_unknown:
        return Value(type_=return_type, is_unknown=True)
        
    path = str(args[0].value)
    
    try:
        with open(path, "r") as f:
            content = f.read()
        return Value(type_=return_type, value=content)
    except Exception as e:
        logger.error(f"🧰🔧❌ Error reading file: {e}")
        return Value(type_=return_type, is_null=True)
        
def fn_fileexists(args: List[Value], return_type: CtyType) -> Value:
    """Check if file exists."""
    if args[0].is_null:
        return Value(type_=return_type, is_null=True)
        
    if args[0].is_unknown:
        return Value(type_=return_type, is_unknown=True)
        
    path = str(args[0].value)
    result = os.path.isfile(path)
    return Value(type_=return_type, value=result)
    
def fn_dirname(args: List[Value], return_type: CtyType) -> Value:
    """Get directory name from path."""
    if args[0].is_null:
        return Value(type_=return_type, is_null=True)
        
    if args[0].is_unknown:
        return Value(type_=return_type, is_unknown=True)
        
    path = str(args[0].value)
    result = os.path.dirname(path)
    return Value(type_=return_type, value=result)
    
def fn_basename(args: List[Value], return_type: CtyType) -> Value:
    """Get basename from path."""
    if args[0].is_null:
        return Value(type_=return_type, is_null=True)
        
    if args[0].is_unknown:
        return Value(type_=return_type, is_unknown=True)
        
    path = str(args[0].value)
    result = os.path.basename(path)
    return Value(type_=return_type, value=result)

#
# Crypto Functions
#

def fn_base64encode(args: List[Value], return_type: CtyType) -> Value:
    """Encode string as base64."""
    if args[0].is_null:
        return Value(type_=return_type, is_null=True)
        
    if args[0].is_unknown:
        return Value(type_=return_type, is_unknown=True)
        
    value = str(args[0].value).encode('utf-8')
    result = base64.b64encode(value).decode('utf-8')
    return Value(type_=return_type, value=result)
    
def fn_base64decode(args: List[Value], return_type: CtyType) -> Value:
    """Decode base64 string."""
    if args[0].is_null:
        return Value(type_=return_type, is_null=True)
        
    if args[0].is_unknown:
        return Value(type_=return_type, is_unknown=True)
        
    try:
        value = str(args[0].value).encode('utf-8')
        result = base64.b64decode(value).decode('utf-8')
        return Value(type_=return_type, value=result)
    except Exception as e:
        logger.error(f"🧰🔧❌ Error decoding base64: {e}")
        return Value(type_=return_type, is_null=True)
        
def fn_md5(args: List[Value], return_type: CtyType) -> Value:
    """Calculate MD5 hash."""
    if args[0].is_null:
        return Value(type_=return_type, is_null=True)
        
    if args[0].is_unknown:
        return Value(type_=return_type, is_unknown=True)
        
    value = str(args[0].value).encode('utf-8')
    result = hashlib.md5(value).hexdigest()
    return Value(type_=return_type, value=result)
    
def fn_sha1(args: List[Value], return_type: CtyType) -> Value:
    """Calculate SHA1 hash."""
    if args[0].is_null:
        return Value(type_=return_type, is_null=True)
        
    if args[0].is_unknown:
        return Value(type_=return_type, is_unknown=True)
        
    value = str(args[0].value).encode('utf-8')
    result = hashlib.sha1(value).hexdigest()
    return Value(type_=return_type, value=result)
    
def fn_sha256(args: List[Value], return_type: CtyType) -> Value:
    """Calculate SHA256 hash."""
    if args[0].is_null:
        return Value(type_=return_type, is_null=True)
        
    if args[0].is_unknown:
        return Value(type_=return_type, is_unknown=True)
        
    value = str(args[0].value).encode('utf-8')
    result = hashlib.sha256(value).hexdigest()
    return Value(type_=return_type, value=result)

#
# Register all functions
#

# String functions
registry.register(Function(FunctionSpec(
    name="upper",
    params=[Parameter(name="str", type=CtyString(), allow_null=False, allow_unknown=True)],
    return_type_fn=return_type_string,
    implementation=fn_upper,
    description="Converts a string to uppercase"
)))

registry.register(Function(FunctionSpec(
    name="lower",
    params=[Parameter(name="str", type=CtyString(), allow_null=False, allow_unknown=True)],
    return_type_fn=return_type_string,
    implementation=fn_lower,
    description="Converts a string to lowercase"
)))

registry.register(Function(FunctionSpec(
    name="title",
    params=[Parameter(name="str", type=CtyString(), allow_null=False, allow_unknown=True)],
    return_type_fn=return_type_string,
    implementation=fn_title,
    description="Converts a string to title case"
)))

registry.register(Function(FunctionSpec(
    name="trim",
    params=[Parameter(name="str", type=CtyString(), allow_null=False, allow_unknown=True)],
    return_type_fn=return_type_string,
    implementation=fn_trim,
    description="Removes whitespace from both ends of a string"
)))

registry.register(Function(FunctionSpec(
    name="substr",
    params=[
        Parameter(name="str", type=CtyString(), allow_null=False, allow_unknown=True),
        Parameter(name="offset", type=CtyNumber(), allow_null=False, allow_unknown=True),
        Parameter(name="length", type=CtyNumber(), allow_null=False, allow_unknown=True)
    ],
    return_type_fn=return_type_string,
    implementation=fn_substr,
    description="Extracts a substring from a string"
)))

registry.register(Function(FunctionSpec(
    name="replace",
    params=[
        Parameter(name="str", type=CtyString(), allow_null=False, allow_unknown=True),
        Parameter(name="search", type=CtyString(), allow_null=False, allow_unknown=True),
        Parameter(name="replace", type=CtyString(), allow_null=False, allow_unknown=True)
    ],
    return_type_fn=return_type_string,
    implementation=fn_replace,
    description="Replaces occurrences of a substring"
)))

registry.register(Function(FunctionSpec(
    name="format",
    params=[Parameter(name="format", type=CtyString(), allow_null=False, allow_unknown=True)],
    variadic_param=VariadicParameter(
        name="args",
        type=CtyDynamic(),
        allow_null=True,
        allow_unknown=True,
        allow_dynamic_type=True
    ),
    return_type_fn=return_type_string,
    implementation=fn_format,
    description="Formats a string according to a format specification"
)))

# Numeric functions
registry.register(Function(FunctionSpec(
    name="abs",
    params=[Parameter(name="num", type=CtyNumber(), allow_null=False, allow_unknown=True)],
    return_type_fn=return_type_number,
    implementation=fn_abs,
    description="Returns the absolute value of a number"
)))

registry.register(Function(FunctionSpec(
    name="ceil",
    params=[Parameter(name="num", type=CtyNumber(), allow_null=False, allow_unknown=True)],
    return_type_fn=return_type_number,
    implementation=fn_ceil,
    description="Returns the smallest integer greater than or equal to a number"
)))

registry.register(Function(FunctionSpec(
    name="floor",
    params=[Parameter(name="num", type=CtyNumber(), allow_null=False, allow_unknown=True)],
    return_type_fn=return_type_number,
    implementation=fn_floor,
    description="Returns the largest integer less than or equal to a number"
)))

registry.register(Function(FunctionSpec(
    name="max",
    params=[Parameter(name="first", type=CtyNumber(), allow_null=False, allow_unknown=True)],
    variadic_param=VariadicParameter(
        name="others",
        type=CtyNumber(),
        allow_null=False,
        allow_unknown=True,
        min_elements=0
    ),
    return_type_fn=return_type_number,
    implementation=fn_max,
    description="Returns the maximum value from a set of numbers"
)))

registry.register(Function(FunctionSpec(
    name="min",
    params=[Parameter(name="first", type=CtyNumber(), allow_null=False, allow_unknown=True)],
    variadic_param=VariadicParameter(
        name="others",
        type=CtyNumber(),
        allow_null=False,
        allow_unknown=True,
        min_elements=0
    ),
    return_type_fn=return_type_number,
    implementation=fn_min,
    description="Returns the minimum value from a set of numbers"
)))

# Collection functions
registry.register(Function(FunctionSpec(
    name="length",
    params=[Parameter(name="collection", type=CtyDynamic(), allow_null=False, allow_unknown=True)],
    return_type_fn=return_type_number,
    implementation=fn_length,
    description="Returns the length of a string, list, map, or set"
)))

registry.register(Function(FunctionSpec(
    name="element",
    params=[
        Parameter(name="list", type=CtyList(element_type=CtyDynamic()), allow_null=False, allow_unknown=True),
        Parameter(name="index", type=CtyNumber(), allow_null=False, allow_unknown=True)
    ],
    return_type_fn=return_type_first_arg,
    implementation=fn_element,
    description="Returns the element at a specific index in a list"
)))

registry.register(Function(FunctionSpec(
    name="contains",
    params=[
        Parameter(name="list", type=CtyDynamic(), allow_null=False, allow_unknown=True),
        Parameter(name="value", type=CtyDynamic(), allow_null=True, allow_unknown=True)
    ],
    return_type_fn=return_type_bool,
    implementation=fn_contains,
    description="Checks if a list, set, or map contains a specific value"
)))

registry.register(Function(FunctionSpec(
    name="keys",
    params=[Parameter(name="map", type=CtyMap(key_type=CtyString(), value_type=CtyDynamic()), allow_null=False, allow_unknown=True)],
    return_type_fn=lambda _: CtyList(element_type=CtyString()),
    implementation=fn_keys,
    description="Returns a list of keys in a map"
)))

registry.register(Function(FunctionSpec(
    name="values",
    params=[Parameter(name="map", type=CtyMap(key_type=CtyString(), value_type=CtyDynamic()), allow_null=False, allow_unknown=True)],
    return_type_fn=lambda _: CtyList(element_type=CtyDynamic()),
    implementation=fn_values,
    description="Returns a list of values in a map"
)))

registry.register(Function(FunctionSpec(
    name="merge",
    params=[Parameter(name="map1", type=CtyMap(key_type=CtyString(), value_type=CtyDynamic()), allow_null=False, allow_unknown=True)],
    variadic_param=VariadicParameter(
        name="maps",
        type=CtyMap(key_type=CtyString(), value_type=CtyDynamic()),
        allow_null=False,
        allow_unknown=True,
        min_elements=0
    ),
    return_type_fn=return_type_first_arg,
    implementation=fn_merge,
    description="Merges multiple maps into a single map"
)))

# Conversion functions
registry.register(Function(FunctionSpec(
    name="tostring",
    params=[Parameter(name="value", type=CtyDynamic(), allow_null=False, allow_unknown=True, allow_dynamic_type=True)],
    return_type_fn=return_type_string,
    implementation=fn_tostring,
    description="Converts a value to a string"
)))

registry.register(Function(FunctionSpec(
    name="tonumber",
    params=[Parameter(name="value", type=CtyDynamic(), allow_null=False, allow_unknown=True, allow_dynamic_type=True)],
    return_type_fn=return_type_number,
    implementation=fn_tonumber,
    description="Converts a value to a number"
)))

registry.register(Function(FunctionSpec(
    name="tobool",
    params=[Parameter(name="value", type=CtyDynamic(), allow_null=False, allow_unknown=True, allow_dynamic_type=True)],
    return_type_fn=return_type_bool,
    implementation=fn_tobool,
    description="Converts a value to a bool"
)))

# Filesystem functions
registry.register(Function(FunctionSpec(
    name="file",
    params=[Parameter(name="path", type=CtyString(), allow_null=False, allow_unknown=True)],
    return_type_fn=return_type_string,
    implementation=fn_file,
    description="Reads the contents of a file"
)))

registry.register(Function(FunctionSpec(
    name="fileexists",
    params=[Parameter(name="path", type=CtyString(), allow_null=False, allow_unknown=True)],
    return_type_fn=return_type_bool,
    implementation=fn_fileexists,
    description="Checks if a file exists"
)))

registry.register(Function(FunctionSpec(
    name="dirname",
    params=[Parameter(name="path", type=CtyString(), allow_null=False, allow_unknown=True)],
    return_type_fn=return_type_string,
    implementation=fn_dirname,
    description="Returns the directory portion of a path"
)))

registry.register(Function(FunctionSpec(
    name="basename",
    params=[Parameter(name="path", type=CtyString(), allow_null=False, allow_unknown=True)],
    return_type_fn=return_type_string,
    implementation=fn_basename,
    description="Returns the filename portion of a path"
)))

# Crypto functions
registry.register(Function(FunctionSpec(
    name="base64encode",
    params=[Parameter(name="str", type=CtyString(), allow_null=False, allow_unknown=True)],
    return_type_fn=return_type_string,
    implementation=fn_base64encode,
    description="Encodes a string as base64"
)))

registry.register(Function(FunctionSpec(
    name="base64decode",
    params=[Parameter(name="str", type=CtyString(), allow_null=False, allow_unknown=True)],
    return_type_fn=return_type_string,
    implementation=fn_base64decode,
    description="Decodes a base64-encoded string"
)))

registry.register(Function(FunctionSpec(
    name="md5",
    params=[Parameter(name="str", type=CtyString(), allow_null=False, allow_unknown=True)],
    return_type_fn=return_type_string,
    implementation=fn_md5,
    description="Computes the MD5 hash of a string"
)))

registry.register(Function(FunctionSpec(
    name="sha1",
    params=[Parameter(name="str", type=CtyString(), allow_null=False, allow_unknown=True)],
    return_type_fn=return_type_string,
    implementation=fn_sha1,
    description="Computes the SHA1 hash of a string"
)))

registry.register(Function(FunctionSpec(
    name="sha256",
    params=[Parameter(name="str", type=CtyString(), allow_null=False, allow_unknown=True)],
    return_type_fn=return_type_string,
    implementation=fn_sha256,
    description="Computes the SHA256 hash of a string"
)))

# Log initialization
logger.info(f"🧰📝✅ Registered {len(registry)} standard library functions")
