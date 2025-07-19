# Values

A `CtyValue` is an instance of a `CtyType`. It holds the actual data and is immutable. You can create a `CtyValue` by validating a raw Python value against a `CtyType`.

## Creating a `CtyValue`

```python
from pyvider.cty import CtyString

string_type = CtyString()
cty_value = string_type.validate("hello")
```

## Accessing the Raw Value

You can get the raw Python value from a `CtyValue` using the `raw_value` property:

```python
raw_value = cty_value.raw_value
assert raw_value == "hello"
```

## Special Values

There are two special types of `CtyValue` that you should be aware of:

*   **Null:** A null value represents the absence of a value. You can create a null value using the `null` class method on a `CtyType`:

    ```python
    from pyvider.cty import CtyString

    string_type = CtyString()
    null_value = CtyValue.null(string_type)

    assert null_value.is_null
    ```

*   **Unknown:** An unknown value represents a value that is not yet known. This is useful when you are working with values that will be computed at a later time. You can create an unknown value using the `unknown` class method on a `CtyType`:

    ```python
    from pyvider.cty import CtyString

    string_type = CtyString()
    unknown_value = CtyValue.unknown(string_type)

    assert unknown_value.is_unknown
    ```

## Marks

Marks are a way to attach metadata to a `CtyValue`. This can be useful for tracking the origin of a value, or for adding other contextual information.

You can add a mark to a `CtyValue` using the `mark` method:

```python
from pyvider.cty import CtyString, CtyMark

string_type = CtyString()
cty_value = string_type.validate("hello")

marked_value = cty_value.mark(CtyMark("sensitive"))

assert marked_value.has_mark(CtyMark("sensitive"))
```
