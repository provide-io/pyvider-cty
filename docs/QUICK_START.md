# Quick Start Guide

Get up and running with pyvider.cty in 5 minutes!

## Installation

```bash
pip install pyvider-cty==0.1.0-preview1
```

## Basic Usage

### 1. Import Required Types

```python
from pyvider.cty import (
    CtyString, CtyNumber, CtyBool, CtyList, CtyObject, CtyDynamic,
    CtyValue
)
# For specific exceptions if you want to catch them
from pyvider.cty.exceptions import CtyValidationError
from decimal import Decimal # Often useful with CtyNumber
```

### 2. Define a Type Schema

```python
# Simple types are instantiated
name_type = CtyString()
age_type = CtyNumber()
active_type = CtyBool()

# Collection type: CtyList requires element_type to be specified with an instance of a CtyType
tags_type = CtyList(element_type=CtyString())

# Complex object type: A dictionary mapping attribute names to CtyType instances
person_schema_dict = {
    "name": CtyString(),
    "age": CtyNumber(),
    "active": CtyBool(),
    "tags": CtyList(element_type=CtyString())
}
person_type = CtyObject(person_schema_dict) # Create a CtyObject type from the schema dictionary
```

### 3. Create Values

```python
# Define the data using native Python types
person_data_native = {
    "name": "Alice",
    "age": 30,
    "active": True,
    "tags": ["developer", "python"] # Native list of native strings
}

# Create the CtyValue object using the CtyObject type (person_type) and native data.
# The library will validate and convert native types based on the person_type schema.
# Alternatively, the schema dictionary (person_schema_dict) can be passed instead of person_type.
person = CtyValue.object(person_type, person_data_native)

# You can also create individual CtyValues directly if needed:
name_only_val = CtyValue.string("Bob")
age_only_val = CtyValue.number(25) # Creates a CtyValue with a Decimal
# For lists, provide the element type (instance) and a list of native or CtyValues:
specific_tags_list = CtyValue.list(CtyString(), ["tag1", "tag2"])
```

### 4. Access Values

```python
# Access the underlying native Python values using the .value property
print(f"Name: {person['name'].value}")  # Expected: "Alice" (str)
# For CtyNumber, .value is typically a Decimal instance
print(f"Age: {person['age'].value}")   # Expected: Decimal('30')

# Iterate lists: .value on a CtyList CtyValue returns a Python list of CtyValue instances
print("Hobbies:")
for tag_cty_value in person['tags'].value: # tag_cty_value is a CtyValue(CtyString)
    print(f"- {tag_cty_value.value}") # Access .value on each element to get native string

# Check properties (these are properties, not methods)
print(f"Is person null? {person.is_null}")      # False
print(f"Is person unknown? {person.is_unknown}")   # False
```

### 5. Serialize/Deserialize

```python
# person is a CtyValue instance (created in step 3)
# person_type is the CtyObject schema instance defined in step 2

# To JSON string (this is a method on a CtyValue instance)
json_str = person.to_json_string()
print(f"Serialized JSON: {json_str}")

# From JSON string (this is a classmethod on the CtyValue class)
# Provide the target CtyType (e.g., person_type which is our CtyObject instance)
loaded_person = CtyValue.from_json_string(json_str, person_type)

# Verify deserialized data (accessing .value for native types)
assert loaded_person['name'].value == "Alice"
assert loaded_person['age'].value == Decimal(30) # Compare with Decimal
deserialized_tags = [t.value for t in loaded_person['tags'].value]
assert deserialized_tags == ["developer", "python"]
print("Deserialization successful.")
```

## Common Patterns

### Working with Unknown Values

```python
# person_type is the CtyObject schema instance defined earlier

# Create an unknown value of person_type
unknown_person = CtyValue.unknown(person_type)
print(f"Is unknown_person unknown? {unknown_person.is_unknown}") # True

# Check before attempting to access attributes
if not unknown_person.is_unknown:
    # This block will be skipped
    name = unknown_person["name"].value
    print(f"Name from unknown_person: {name}")
else:
    print("unknown_person is unknown, cannot access attributes directly.")
```

### Handling Null Values

```python
# person_type is the CtyObject schema instance defined earlier

# Create a null value of person_type
null_person = CtyValue.null(person_type)
print(f"Is null_person null? {null_person.is_null}") # True

# IMPORTANT: Accessing an attribute on a CtyValue that represents a null object
# (e.g., null_person["name"]) will raise a TypeError.
try:
    name_from_null = null_person["name"].value # This line will raise TypeError
except TypeError as e:
    print(f"Caught expected error when accessing attribute of null object: {e}")

# Safe access pattern: always check is_null before trying to use attributes
if null_person.is_null:
    print("Person data is null (as in null_person).")
else:
    # This block will be skipped for null_person
    print(f"Name: {null_person['name'].value}")

# To demonstrate with the non-null 'person' instance:
if person.is_null: # person was created with actual data
    print("This should not print: 'person' instance is not null.")
else:
    print(f"Name from 'person' (which is not null): {person['name'].value}")
```

### Type Validation

```python
# person_type is the CtyObject schema instance defined earlier

try:
    # This data has a 'name' attribute that is a number, but person_type expects a string.
    invalid_person_data = {
        "name": 123,  # Incorrect type!
        "age": 30,
        "active": True,
        "tags": ["testing"]
    }
    # This will raise a CtyValidationError because 'name' is not a string
    bad_person = CtyValue.object(person_type, invalid_person_data)
except CtyValidationError as e:
    print(f"Successfully caught expected validation error: {e}")
except Exception as e:
    print(f"An unexpected error occurred during type validation test: {e}")
```

### Dynamic Types

```python
from pyvider.cty import CtyDynamic # Ensure it's imported

# Define a schema dictionary where 'data' can be of any type
flexible_schema_dict = {
    "id": CtyString(),
    "data": CtyDynamic()
}
# flexible_type = CtyObject(flexible_schema_dict) # Optional: create CtyObject type

# Create an instance with string data
config1_data = {"id": "config-1", "data": "text data"}
config1 = CtyValue.object(flexible_schema_dict, config1_data) # Pass schema dict
print(f"Config1 'data' type: {config1['data'].type!r}, value: {config1['data'].value}")

# Create an instance with number data
config2_data = {"id": "config-2", "data": 42}
config2 = CtyValue.object(flexible_schema_dict, config2_data) # Pass schema dict
print(f"Config2 'data' type: {config2['data'].type!r}, value: {config2['data'].value}") # .value is Decimal
```

## Next Steps

- Read the [full documentation](README.md) <!-- TODO: Verify this link. Does it point to docs/README.md or main README.md? -->
- Explore [examples](../examples/)
- Learn about [migration from go-cty](MIGRATION_FROM_GO_CTY.md)
- Check out [API reference](api/) <!-- TODO: Verify this link, docs/api/ was not found -->

## Need Help?

- 📧 Email: code@provide.io
- 🐛 [GitHub Issues](https://github.com/provide/pyvider-cty/issues)
- 💬 [GitHub Discussions](https://github.com/provide/pyvider-cty/discussions)
