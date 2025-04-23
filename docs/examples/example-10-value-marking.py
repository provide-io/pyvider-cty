#!/usr/bin/env python3
# docs/examples/example-10-value-marking.py

# Corrected imports and usage for serialization and immutable update
from pyvider.cty import CtyObject, CtyString, CtyNumber, CtyValue
# Use the actual conversion API
from pyvider.cty.conversion import CtyWireFormat, JSON

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

    # Add __eq__ and __hash__ for mark comparison/set usage
    def __eq__(self, other):
        return isinstance(other, SensitiveMark) and self.reason == other.reason

    def __hash__(self):
        return hash(("SensitiveMark", self.reason))

# Create a regular value
cred_data = {
    "username": "admin",
    "password": "super-secret-password",
    "expiry_days": 30
}

# Validate returns CtyValue
cred_val = credential_type.validate(cred_data)

# --- Corrected Immutable Update with Marked Value ---
try:
    if not cred_val.is_null and not cred_val.is_unknown:
        # Get the original password CtyValue
        original_password_val = cred_val.value["password"]

        # Mark the password value
        marked_password_val = original_password_val.mark(SensitiveMark("credential"))

        # Create a *new* internal value dictionary for the updated object
        # Start by copying the existing validated attributes
        new_cred_internal_value = dict(cred_val.value)
        # Update the password entry with the *marked* CtyValue
        new_cred_internal_value["password"] = marked_password_val

        # Create a new CtyValue for the credential object with the updated internal value
        # We need to reuse the same type (credential_type)
        cred_val_updated = CtyValue(vtype=credential_type, value=new_cred_internal_value)

        # Check for marks on the password within the *new* updated object value
        password_from_updated = cred_val_updated.value.get("password")
        if password_from_updated:
             has_mark = password_from_updated.has_mark(SensitiveMark("credential"))
             print(f"Has sensitive mark (updated obj): {has_mark}")

             # Unmask when needed
             unmasked, marks = password_from_updated.unmark()
             print(f"Unmasked value: {unmasked.value}")
             print(f"Retrieved marks: {[str(m) for m in marks]}")

             # Marshal the updated value
             marshaled = CtyWireFormat.marshal(cred_val_updated, options={'format_type': JSON})
             print(f"Marshaled size: {len(marshaled)} bytes")

             # Unmarshal preserves marks
             unmarshaled = CtyWireFormat.unmarshal(
                 marshaled,
                 expected_type=credential_type,
                 options={'format_type': JSON}
             )
             if not unmarshaled.is_null and not unmarshaled.is_unknown:
                  password_again = unmarshaled.value.get("password")
                  if password_again:
                      print(f"Password is marked after unmarshal: {password_again.has_mark(SensitiveMark('credential'))}")
                  else:
                      print("Password attribute not found after unmarshal.")
             else:
                  print("Unmarshaled value is null or unknown.")
        else:
             print("Password attribute not found in updated object.")
    else:
        print("Initial credential value is null or unknown.")

except Exception as e:
    print(f"An error occurred: {e}")
