from pyvider.cty import CtyObject, CtyString, CtyNumber, CtyBool, CtyTuple

# CtyObject
user_type = CtyObject(
    attribute_types={
        "name": CtyString(),
        "age": CtyNumber(),
        "is_active": CtyBool(),
    },
    optional_attributes={"is_active"}
)
user_data = {"name": "Alice", "age": 30}
cty_user = user_type.validate(user_data)
active_val = cty_user["is_active"]
print(f"Active: {active_val.raw_value} (Is Null: {active_val.is_null})")
try:
    user_type.validate({"name": "Bob"}) # Missing 'age'
except Exception as e:
    print(f"\nValidation failed as expected: {e}")

# CtyTuple
tuple_type = CtyTuple(element_types=(
    CtyString(),
    CtyNumber(),
    CtyBool(),
))
tuple_data = ["hello", 123, True]
cty_tuple = tuple_type.validate(tuple_data)
assert cty_tuple.raw_value == ("hello", 123, True)
print("\nCtyTuple example successful.")
try:
    tuple_type.validate(["hello", 123])
except Exception as e:
    print(f"Validation failed as expected: {e}")
