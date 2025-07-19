# Validation

Validation is the process of checking if a raw Python value conforms to a given `CtyType`. The `validate` method on a `CtyType` is used for this purpose.

If the value is valid, `validate` will return a new `CtyValue` instance. If the value is invalid, it will raise a `CtyValidationError`.

```python
from pyvider.cty import CtyString, CtyValidationError

string_type = CtyString()

# This is a valid value
cty_value = string_type.validate("hello")

# This is an invalid value
try:
    string_type.validate(123)
except CtyValidationError as e:
    print(e)
```

## Validation Errors

When validation fails, a `CtyValidationError` is raised. This exception contains information about the error, including a human-readable message, the value that failed validation, and the path to the value within a larger data structure.

There are several subclasses of `CtyValidationError` that are raised for specific types of validation errors:

*   `CtyBoolValidationError`
*   `CtyNumberValidationError`
*   `CtyStringValidationError`
*   `CtyListValidationError`
*   `CtyMapValidationError`
*   `CtySetValidationError`
*   `CtyTupleValidationError`
*   `CtyAttributeValidationError`
*   `CtyTypeValidationError`
*   `CtyTypeMismatchError`

You can use these specific exception types to handle different validation errors in different ways.
