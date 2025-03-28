#!/usr/bin/env python3
# docs/examples/example-10-value-marking.py

from pyvider.cty import CtyObject, CtyString, CtyNumber, CtyValue
from pyvider.cty.encoding import marshal, unmarshal

# Define types
credential_type = CtyObject(
    attribute_types={
        "username": CtyString(),
        "password": CtyString(),
        "expiry_days": CtyNumber()
    }
)

# Create a sensitive mark
class SensitiveMark:
    def __init__(self, reason):
        self.reason = reason
    
    def __str__(self):
        return f"SENSITIVE:{self.reason}"

# Create a regular value
cred_data = {
    "username": "admin",
    "password": "super-secret-password",
    "expiry_days": 30
}

validated = credential_type.validate(cred_data)
cred_val = CtyValue(type_=credential_type, value=validated)

# Mark the password as sensitive
password = cred_val.value["password"]
marked_password = password.mark(SensitiveMark("credential"))

# Replace original password with marked one
cred_val.value["password"] = marked_password

# Check for marks
has_mark = marked_password.has_mark(SensitiveMark("credential"))
print(f"Has sensitive mark: {has_mark}")

# Unmask when needed
unmasked, marks = marked_password.unmark()
print(f"Unmasked value: {unmasked.value}")
print(f"Retrieved marks: {[str(m) for m in marks]}")

# Marshal with marks preserved
marshaled = marshal(cred_val)
print(f"Marshaled size: {len(marshaled)} bytes")

# Unmarshal preserves marks
unmarshaled = unmarshal(marshaled)
password_again = unmarshaled.value["password"]
print(f"Password is marked: {password_again.has_mark(SensitiveMark('credential'))}")
