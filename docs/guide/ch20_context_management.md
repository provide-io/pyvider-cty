# Chapter 20: Context Management

`pyvider.cty` provides a context management system that allows you to control the behavior of CTY operations in different situations. This is useful for tasks such as enabling stricter validation in a testing environment or changing serialization strategies for different output formats.

## The `OperationContext` Enum

The `OperationContext` enum defines the different operational contexts that can be used:

*   `DEFAULT`: The default context.
*   `CONFIG`: For configuration-related operations.
*   `STATE`: For state-related operations.
*   `PLAN`: For plan-related operations.
*   `APPLY`: For apply-related operations.
*   `READ`: For read-related operations.
*   `FUNCTION`: For function-related operations.
*   `SCHEMA`: For schema-related operations.

## The `operation_context` Context Manager

The `operation_context` context manager is used to temporarily set the CTY operational context:

```python
from pyvider.cty.context import OperationContext, operation_context

with operation_context(OperationContext.CONFIG):
    # Operations within this block will use the CONFIG context
    ...
```

## The `ValidationContext`

The `ValidationContext` is used to control the validation depth. This is useful for preventing infinite recursion when validating deeply nested structures.

The `deeper_validation` context manager is used to safely increment and decrement the validation depth:

```python
from pyvider.cty.context.validation_context import deeper_validation

with deeper_validation():
    # The validation depth is now one level deeper
    ...
```

The `get_validation_depth` function can be used to get the current validation depth.
