# Chapter 10: Marks

Marks are a powerful feature in `pyvider.cty` that allow you to attach metadata to `cty` values. This metadata can then be used to add extra information to the values, such as sensitivity, or to control how the values are processed in a data pipeline.

## What are Marks?

A mark is a piece of metadata that is attached to a `cty` value. Marks are represented as strings, and a single value can have multiple marks.

Marks are "sticky". This means that when you perform an operation on a marked value, the marks are automatically transferred to the resulting value.

## Marking a Value

You can mark a value using the `with_marks` method of a `cty` value:

```python
from pyvider.cty import CtyString

# Create a string value
cty_string = CtyString().validate("hello")

# Mark the value as "sensitive"
sensitive_string = cty_string.with_marks("sensitive")
```

You can also add multiple marks at once:

```python
# Mark the value as "sensitive" and "private"
private_sensitive_string = cty_string.with_marks("sensitive", "private")
```

## Checking for Marks

You can check if a value has a specific mark using the `has_mark` method:

```python
assert sensitive_string.has_mark("sensitive") is True
assert sensitive_string.has_mark("private") is False
```

You can also get a set of all the marks on a value using the `marks` property:

```python
assert sensitive_string.marks == {"sensitive"}
```

## Use Cases for Marks

Marks are a flexible feature that can be used in a variety of ways. Here are a few examples:

*   **Sensitive Data**: You can use marks to flag sensitive data, such as passwords or API keys. You can then use these marks to ensure that the data is handled appropriately, such as by redacting it from logs or encrypting it before storing it.

*   **Data Lineage**: You can use marks to track the lineage of data as it flows through a data pipeline. This can be useful for debugging and for understanding how a particular value was derived.

*   **Controlling Behavior**: You can use marks to control the behavior of functions and other operations. For example, you could create a function that only operates on values that have a specific mark.
