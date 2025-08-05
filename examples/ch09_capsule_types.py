#!/usr/bin/env python3
from examples.example_utils import configure_for_example
from pyvider.cty.types import CtyCapsule

configure_for_example()


class FileHandle:
    def __init__(self, path: str) -> None:
        self.path = path


file_handle_type = CtyCapsule("FileHandle", FileHandle)

file_handle = FileHandle("/path/to/file")

cty_file_handle = file_handle_type.validate(file_handle)

encapsulated_handle = cty_file_handle.raw_value
assert encapsulated_handle.path == "/path/to/file"

try:
    file_handle_type.validate("not a file handle")
except Exception as e:
    print(f"Capsule validation failed as expected: {e}")

print("Capsule type examples ran successfully.")
