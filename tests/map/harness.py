# Simple test harness for CtyMap
from pyvider.cty import CtyString, CtyValue, CtyMap

# Create a basic map type
string_map = CtyMap(key_type=CtyString(), value_type=CtyString())

# Create keys and values
key1 = CtyValue(type_=CtyString(), value="key1")
val1 = CtyValue(type_=CtyString(), value="value1")
key2 = CtyValue(type_=CtyString(), value="key2")
val2 = CtyValue(type_=CtyString(), value="value2")

# Create map data
data = {key1: val1, key2: val2}

# Validate the map
result = string_map.validate(data)

# Check the result
print(f"Result type: {type(result)}")
print(f"Result value length: {len(result.value)}")
print(f"Value keys: {list(result.value.keys())}")
print(f"Key mapping: {getattr(result, '_key_mapping', {})}")

# Try accessing with get
val1_get = string_map.get(result, key1)
print(f"Get result: {val1_get}")
