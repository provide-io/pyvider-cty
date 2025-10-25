# Marks System

Marks are a powerful feature in `pyvider.cty` that allow you to attach metadata to `cty` values. This metadata can then be used to add extra information to the values, such as sensitivity, or to control how the values are processed in a data pipeline.

## What are Marks?

A mark is a piece of metadata that is attached to a `cty` value. Marks are represented as `CtyMark` objects, and a single value can have multiple marks.

Marks are "sticky". This means that when you perform an operation on a marked value, the marks are automatically transferred to the resulting value.

## Marking a Value

You can mark a value using the `mark` method (for a single mark) or `with_marks` method (for multiple marks) of a `cty` value:

```python
from pyvider.cty import CtyString
from pyvider.cty.marks import CtyMark

# Create a string value
cty_string = CtyString().validate("hello")

# Create a mark
sensitive_mark = CtyMark("sensitive")

# Mark the value as "sensitive" using the mark() method
sensitive_string = cty_string.mark(sensitive_mark)
```

You can also add multiple marks at once using `with_marks`, which accepts a set of marks:

```python
# Create multiple marks
sensitive_mark = CtyMark("sensitive")
private_mark = CtyMark("private")

# Mark the value with both marks
private_sensitive_string = cty_string.with_marks({sensitive_mark, private_mark})
```

Marks can optionally include additional details:

```python
# Create a mark with details
pii_mark = CtyMark("pii", details={"category": "email", "source": "user_input"})
marked_value = cty_string.mark(pii_mark)
```

## Checking for Marks

You can check if a value has a specific mark by checking if it's in the `marks` property:

```python
sensitive_mark = CtyMark("sensitive")
sensitive_string = cty_string.mark(sensitive_mark)

# Check using 'in' operator
assert sensitive_mark in sensitive_string.marks

# Or use the has_mark() method
assert sensitive_string.has_mark(sensitive_mark)
```

You can also get a frozenset of all the marks on a value using the `marks` property:

```python
assert len(sensitive_string.marks) == 1
```

## Removing Marks

To remove all marks from a value, use the `unmark` method, which returns both the unmarked value and the marks that were removed:

```python
unmarked_value, removed_marks = sensitive_string.unmark()
assert len(unmarked_value.marks) == 0
assert sensitive_mark in removed_marks
```

## Use Cases for Marks

Marks are a flexible feature that can be used in a variety of ways. Here are a few examples:

*   **Sensitive Data**: You can use marks to flag sensitive data, such as passwords or API keys. You can then use these marks to ensure that the data is handled appropriately, such as by redacting it from logs or encrypting it before storing it.

*   **Data Lineage**: You can use marks to track the lineage of data as it flows through a data pipeline. This can be useful for debugging and for understanding how a particular value was derived.

*   **Controlling Behavior**: You can use marks to control the behavior of functions and other operations. For example, you could create a function that only operates on values that have a specific mark.

## See Also

- **[Terraform Interoperability](terraform-interop.md)** - Using marks with Terraform sensitive values
- **[Working with Values](../core-concepts/values.md)** - Understanding CtyValue properties
- **[go-cty Comparison](../../reference/go-cty-comparison.md)** - Marks API differences between go-cty and pyvider.cty
