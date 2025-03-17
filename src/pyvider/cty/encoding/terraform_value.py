
# pyvider/cty/encoding/terraform_value.py

"""
Terraform Value Conversion Utilities

This module centralizes the logic for converting between Terraform's wire representation
and Pyvider's internal value structures. It handles the various formats that Terraform
might send, including serialized JSON, byte strings, CtyValue objects, and more.

This is particularly important for function arguments and return values, where Terraform
may send complex or partially unknown values.
"""

import json
import re
from typing import Any, List, Optional, Union

from pyvider.cty.logger import logger

def deserialize_tf_value(value: Any) -> Any:
    """
    Deserialize a value from Terraform's format to a Python value.
    
    This handles:
    - CtyValue objects (preserving unknown/null status)
    - String representations of JSON arrays/objects
    - Byte string representations
    - Terraform tuple format ["tuple", [values...]]
    - Regular Python values
    
    Args:
        value: The value to deserialize
        
    Returns:
        The deserialized value
    """
    logger.debug(f"🧰🔍🔄 Deserializing Terraform value: {value}")
    
    # Handle CtyValue-like objects (duck typing to avoid import cycles)
    if hasattr(value, 'is_known') and hasattr(value, 'value'):
        # Extract raw value for known values
        if getattr(value, 'is_known', False) and not getattr(value, 'is_null', False):
            raw_value = getattr(value, 'value')
            logger.debug(f"🧰🔍🔄 Extracted raw value from CtyValue: {raw_value}")
            return deserialize_tf_value(raw_value)
        
        # Return unknown/null values as-is
        logger.debug(f"🧰🔍🔄 Preserving unknown/null CtyValue")
        return value
    
    # Handle list/tuple collections by recursively deserializing elements
    if isinstance(value, (list, tuple)):
        logger.debug(f"🧰🔍🔄 Deserializing collection with {len(value)} items")
        return [deserialize_tf_value(item) for item in value]
    
    # Handle dict collections by recursively deserializing values
    if isinstance(value, dict):
        logger.debug(f"🧰🔍🔄 Deserializing dict with {len(value)} keys")
        return {k: deserialize_tf_value(v) for k, v in value.items()}
    
    # Already a primitive non-string value
    if not isinstance(value, str):
        return value
        
    # Handle serialized string formats
    if value.startswith('b\'[') or value.startswith('["'):
        try:
            # Clean the string for parsing
            clean_str = value
            if value.startswith('b\''):
                clean_str = value[2:-1].replace('\\', '')
            
            # Parse as JSON
            try:
                parsed = json.loads(clean_str)
                
                # Handle ["tuple",[values...]] format
                if isinstance(parsed, list) and len(parsed) > 1 and parsed[0] == "tuple":
                    logger.debug(f"🧰🔍🔄 Extracted tuple values: {parsed[1]}")
                    return parsed[1]  # Return the actual values
                
                logger.debug(f"🧰🔍🔄 Parsed JSON: {parsed}")
                return parsed
                
            except json.JSONDecodeError:
                # If JSON parsing fails, try regex pattern matching for tuples
                pattern = r'\["tuple",\[(.*)\]\]'
                match = re.search(pattern, clean_str)
                if match:
                    # Extract values from the tuple
                    values_str = match.group(1)
                    values = []
                    
                    # Parse individual items
                    for item in re.findall(r'"[^"]*"|\d+\.\d+|\d+|true|false', values_str):
                        if item.startswith('"') and item.endswith('"'):
                            values.append(item[1:-1])  # Remove quotes
                        elif item == "true":
                            values.append(True)
                        elif item == "false":
                            values.append(False)
                        elif "." in item:
                            values.append(float(item))
                        else:
                            values.append(int(item))
                    
                    logger.debug(f"🧰🔍🔄 Extracted values using regex: {values}")
                    return values
        except Exception as e:
            logger.error(f"🧰🔍❌ Error deserializing value: {e}", exc_info=True)
    
    # Return as is if we couldn't deserialize
    return value

def extract_collection_values(collection: Any) -> List[Any]:
    """
    Extract values from a collection that might be in Terraform's format.
    
    This is specialized for collections (lists, sets) where Terraform might
    send a complex representation that needs special handling.
    
    Args:
        collection: The collection to extract values from
        
    Returns:
        List of extracted values
    """
    logger.debug(f"🧰📝🔍 Extracting collection values from: {collection}")
    
    # Handle CtyValue-like objects
    if hasattr(collection, 'is_known') and hasattr(collection, 'value'):
        if getattr(collection, 'is_known', False) and not getattr(collection, 'is_null', False):
            # Extract and process the raw value
            raw_value = getattr(collection, 'value')
            logger.debug(f"🧰📝🔍 Extracting from CtyValue raw value: {raw_value}")
            return extract_collection_values(raw_value)
            
        # Return unknown/null values as empty list
        logger.debug(f"🧰📝🔍 Unknown/null CtyValue, returning empty list")
        return []
    
    # Already a list or tuple
    if isinstance(collection, (list, tuple)):
        result = []
        for item in collection:
            # Handle each item, which might itself be a complex value
            result.append(deserialize_tf_value(item))
        
        logger.debug(f"🧰📝✅ Extracted collection values: {result}")
        return result
    
    # For string representation of a collection
    if isinstance(collection, str) and (collection.startswith('b\'[') or collection.startswith('[')):
        # Try to extract from serialized form
        deserialized = deserialize_tf_value(collection)
        if isinstance(deserialized, list):
            return deserialized
    
    # For single values or unrecognized formats, wrap in a list
    logger.debug(f"🧰📝✅ Wrapping single value in list: {collection}")
    return [deserialize_tf_value(collection)]

# 🐍🏗️
