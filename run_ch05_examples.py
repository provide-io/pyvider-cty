from pyvider.cty import CtyString, CtyNumber, CtyBool

# CtyString
string_type = CtyString()
cty_string = string_type.validate("hello")
assert cty_string.raw_value == "hello"
print("CtyString example successful.")
try:
    string_type.validate(123)
except Exception as e:
    print(f"CtyString validation failed as expected: {e}")

# CtyNumber
number_type = CtyNumber()
cty_int = number_type.validate(123)
assert cty_int.raw_value == 123
cty_float = number_type.validate(3.14)
assert cty_float.raw_value == 3.14
print("CtyNumber examples successful.")
try:
    number_type.validate("hello")
except Exception as e:
    print(f"CtyNumber validation failed as expected: {e}")

# CtyBool
bool_type = CtyBool()
cty_true = bool_type.validate(True)
assert cty_true.raw_value is True
print("CtyBool example successful.")
try:
    bool_type.validate(1)
except Exception as e:
    print(f"CtyBool validation failed as expected: {e}")
