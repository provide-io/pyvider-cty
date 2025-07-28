from pyvider.cty import CtyString, CtyObject, CtyNumber, CtyValue, CtyMap

# Accessing the Raw Value
string_val = CtyString().validate("hello")
raw_string = string_val.raw_value
assert raw_string == "hello"
print("Successfully accessed raw value.")

# Special Values: Null and Unknown
profile_type = CtyObject(
    attribute_types={
        "username": CtyString(),
        "age": CtyNumber(),
    },
)
unknown_value = CtyValue.unknown(profile_type)
null_value = CtyValue.null(profile_type)
print(f"Unknown Value: Is Unknown? {unknown_value.is_unknown}, Is Null? {unknown_value.is_null}")
print(f"Null Value:    Is Unknown? {null_value.is_unknown}, Is Null? {null_value.is_null}")
try:
    _ = null_value["username"]
except TypeError as e:
    print(f"Attempting to access null value property failed as expected: {e}")

# Immutable Updates with Helper Methods
config_type = CtyMap(element_type=CtyNumber())
config_val = config_type.validate({"timeout": 30})
new_config_val = config_val.with_key("batch_size", 500).with_key("timeout", 60)
final_config_val = new_config_val.without_key("timeout")
print(f"Original: {config_val.raw_value}")
print(f"Updated:  {new_config_val.raw_value}")
print(f"Final:    {final_config_val.raw_value}")
