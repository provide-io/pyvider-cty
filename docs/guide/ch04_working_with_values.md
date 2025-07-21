# Chapter 4: Working with Values

In `pyvider.cty`, a "value" is an instance of a `cty` type. Values are the lifeblood of the `cty` system, as they hold the actual data that you work with.

## The `CtyValue` Base Class

All `pyvider.cty` values inherit from the `CtyValue` base class. This class provides the common interface for all values, including methods for accessing the raw data and performing type-safe operations.

### Accessing the Raw Value

You can access the raw Python value of a `cty` value using the `raw_value` property:

```python
raw_value = cty_value.raw_value
```

This will return the original Python value that was used to create the `cty` value.

### Immutability

One of the key features of `cty` values is that they are **immutable**. This means that once a value is created, it cannot be changed. If you need to modify a value, you must create a new one.

This immutability has several advantages:

*   **Predictability**: It makes your code more predictable, as you can be sure that a value will not change unexpectedly.
*   **Safety**: It helps to prevent bugs caused by unintended side effects.
*   **Concurrency**: It makes it easier to write concurrent code, as you don't have to worry about race conditions when accessing values.

## Special Values

In addition to the regular values that you create by validating raw data, `pyvider.cty` also has two special kinds of values:

### 1. Null Values

A null value represents the absence of a value. You can create a null value using the `null` method of a `cty` type.

**Use Case:** Representing an optional attribute that is not present.

```python
from pyvider.cty import CtyObject, CtyString, CtyValue

user_type = CtyObject({"name": CtyString(), "email": CtyString()})

# A user with an email
user_with_email = user_type.validate({"name": "Alice", "email": "alice@example.com"})

# A user without an email
user_without_email = user_type.validate({"name": "Bob", "email": CtyValue.null(CtyString())})

assert user_without_email["email"].is_null
```

### 2. Unknown Values

An unknown value represents a value that is not yet known. This is useful when you are working with data that will be populated at a later time, such as in a multi-stage data processing pipeline.

**Use Case:** Planning infrastructure changes where some values will only be known after a resource is created.

```python
from pyvider.cty import CtyObject, CtyString, CtyValue

server_type = CtyObject({"name": CtyString(), "ip_address": CtyString()})

# A plan for a new server, where the IP address is not yet known
server_plan = server_type.validate({
    "name": "web-server-1",
    "ip_address": CtyValue.unknown(CtyString()),
})

assert server_plan["ip_address"].is_unknown
```

## Operations on Values

`pyvider.cty` provides a set of built-in functions for performing operations on `cty` values. These functions are type-safe, meaning that they will only work with the correct types of values.

For example, you can use the `cty_add` function to add two `cty` numbers:

```python
from pyvider.cty import CtyNumber
from pyvider.cty.functions import cty_add

num1 = CtyNumber().validate(10)
num2 = CtyNumber().validate(20)

result = cty_add(num1, num2)

assert result.raw_value == 30
```

We will explore the available functions in more detail in a later chapter.
