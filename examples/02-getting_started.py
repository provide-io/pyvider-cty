#!/usr/bin/env python3

from pyvider.cty import (
    CtyString, CtyNumber, CtyBool, CtyList, CtyObject, CtyDynamic,
    CtyValue
)
from pyvider.cty.functions import jsonencode, jsondecode
from pyvider.cty.conversion import convert

# Define a complex object type for a user
person_type = CtyObject({
    "name": CtyString(),
    "age": CtyNumber(),
    "active": CtyBool(),
    "tags": CtyList(element_type=CtyString())
})

# Create a raw Python dictionary
user_data = {
    "name": "Alice",
    "age": 30,
    "active": True,
    "tags": ["developer", "python"]
}

# Validate the data
try:
    person_value = person_type.validate(user_data)
    print("Validation successful!")
except Exception as e:
    print(f"Validation failed: {e}")

# Access attributes of the object
print(f"Name: {person_value['name'].value}")
print(f"Age: {person_value['age'].value}")

# Iterate over the list
print("Tags:")
for tag_value in person_value['tags']:
    print(f"- {tag_value.value}")

# Serialize to JSON
json_representation = jsonencode(person_value)
print(f"\nJSON representation:\n{json_representation.value}")

# Deserialize from JSON
reconstructed_value = jsondecode(json_representation)
converted_value = convert(reconstructed_value, person_type)
assert converted_value.type.equal(person_type)
assert converted_value['name'].value == "Alice"
print("\nSuccessfully reconstructed value from JSON.")
