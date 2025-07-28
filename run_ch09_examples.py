from pyvider.cty import CtyCapsule

# The CtyCapsule Type
file_handle_type = CtyCapsule("FileHandle", object)
print("CtyCapsule example successful.")

# Create a dummy file handle object
class FileHandle:
    def __init__(self, path):
        self.path = path

file_handle = FileHandle("/path/to/file")

# Encapsulate the file handle in a CtyCapsule value
cty_file_handle = file_handle_type.validate(file_handle)
print("Encapsulation successful.")

# Access the encapsulated object
encapsulated_handle = cty_file_handle.raw_value
assert encapsulated_handle.path == "/path/to/file"
print("Access successful.")

# Type Safety
try:
    file_handle_type.validate("not a file handle")
except Exception as e:
    print(f"Validation failed as expected: {e}")
