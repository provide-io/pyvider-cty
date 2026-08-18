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

## Marks and Validation

Marks survive `validate()`. Revalidating an already-marked value against its type — which happens routinely, for instance whenever a marked value is nested inside a collection that gets validated — does not strip the marks:

```python
revalidated = CtyString().validate(sensitive_string)
assert sensitive_mark in revalidated.marks
```

## Marks and Sets

Sets are the one place the "sticky" rule works differently. A `CtySet` de-duplicates its elements by hashing their value, and hashing is mark-blind, so an element that kept its own mark could silently collide with an equal unmarked element and lose the mark in the collision. go-cty's `SetVal` avoids this by keeping marks off elements entirely: validating a set hoists every element's marks onto the **set itself**, and each element comes out of validation unmarked.

```python
from pyvider.cty import CtySet

marked_element = CtyString().validate("a").mark(sensitive_mark)
sensitive_set = CtySet(element_type=CtyString()).validate(
    [marked_element, CtyString().validate("b")]
)

assert sensitive_mark in sensitive_set.marks
assert all(not element.marks for element in sensitive_set.value)
```

Read a set's marks off the set, never off its elements — an element will never carry one.

## Marks and Functions

Every function in `pyvider.cty.functions` propagates marks automatically. It computes over unmarked arguments internally, then applies the deep union of every argument's marks — collected at any depth, not just the top level — to the result:

```python
from pyvider.cty.functions import upper

marked = CtyString().validate("hello").mark(sensitive_mark)
result = upper(marked)
assert result.value == "HELLO"
assert sensitive_mark in result.marks
```

Because propagation is automatic and deep, no call into the standard library can silently launder a mark away. To ask the same "any marks in here, at any depth?" question directly, without calling a function, use `collect_marks_deep`; `unmark_deep` does the same walk and also returns the value with every mark stripped:

```python
from pyvider.cty.marks import collect_marks_deep, unmark_deep

marks_found = collect_marks_deep(marked)
assert marks_found == {sensitive_mark}

unmarked_value, removed = unmark_deep(marked)
assert unmarked_value.marks == frozenset()
assert removed == {sensitive_mark}
```

## Marks and Serialization

A marked value cannot be serialized. `cty_to_msgpack` raises `CtyMarksSerializationError` rather than silently dropping the marks, because there is nowhere on the wire for a mark to go — Terraform tracks an attribute's sensitivity in the schema, not in the value, so a mark that made it past serialization would just vanish:

```python
from pyvider.cty.codec import cty_to_msgpack
from pyvider.cty.exceptions import CtyMarksSerializationError

marked = CtyString().validate("hello").mark(sensitive_mark)

try:
    cty_to_msgpack(marked, CtyString())
except CtyMarksSerializationError:
    print("cannot serialize a marked value directly")

# Strip the marks first if you need the bytes and track sensitivity elsewhere.
unmarked_value, _ = marked.unmark()
data = cty_to_msgpack(unmarked_value, CtyString())
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
