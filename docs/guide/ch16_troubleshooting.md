# Chapter 16: Troubleshooting

This chapter provides guidance on common issues you might encounter while using `pyvider.cty`.

## `ValidationError`

The most common issue you will encounter is the `ValidationError`. This exception is raised when you try to validate a raw Python value that does not conform to the given `cty` type.

When a `ValidationError` is raised, it will include a detailed message that explains what went wrong. The message will typically include the path to the invalid value, the expected type, and the actual value that was received.

For example, if you try to validate an object with a missing attribute, you might see an error message like this:

```
ValidationError: at path.to.object: missing required attribute "attribute_name"
```

To troubleshoot a `ValidationError`, carefully read the error message and inspect the raw Python value that you are trying to validate. Make sure that the value has the correct structure and that all the values have the correct types.

## `TypeError`

You may also encounter a `TypeError` if you try to perform an operation on a `cty` value with an incompatible type. For example, if you try to add a `CtyString` to a `CtyNumber`, you will get a `TypeError`.

To troubleshoot a `TypeError`, make sure that you are using the correct types of values for the operation that you are trying to perform. You can use the `type` property of a `cty` value to check its type.

## Debugging Tips

*   **Inspect the raw value**: When you are troubleshooting a validation issue, it can be helpful to inspect the raw Python value that you are trying to validate. You can use the `repr` function to get a string representation of the value.

*   **Use a debugger**: If you are having trouble understanding why a validation is failing, you can use a debugger to step through the validation code and inspect the values at each step.

*   **Simplify the problem**: If you are working with a complex data structure, it can be helpful to simplify the problem by creating a smaller, more manageable test case. This can help you to isolate the source of the problem.
