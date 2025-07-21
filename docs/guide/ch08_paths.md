# Chapter 8: Navigating Nested Data with CtyPath

Complex data structures are common in real-world applications. `pyvider.cty` provides a powerful mechanism called `CtyPath` to navigate and access data within nested `CtyValue` structures.

## What is a CtyPath?

A `CtyPath` is a sequence of steps that defines a path from the root of a `CtyValue` to a specific element within it. This is particularly useful for:

*   **Extracting specific data:** Pinpoint and retrieve a single value from a large, nested structure.
*   **Targeted validation:** Validate a specific field within a larger configuration.
*   **Error reporting:** Provide precise locations for validation errors.

## Constructing a CtyPath

A `CtyPath` is constructed from a sequence of "path step" objects. The most common step types are:

*   `GetAttrStep(attr_name)`: Accesses an attribute of a `CtyObject`.
*   `IndexStep(index)`: Accesses an element of a `CtyList` or `CtyTuple` by its index.
*   `KeyStep(key)`: Accesses an element of a `CtyMap` by its key.

Here's how you can create a `CtyPath`:

```python
from pyvider.cty.path import CtyPath, GetAttrStep, IndexStep, KeyStep

# Path to user.addresses[0]["zip_code"]
path = CtyPath([
    GetAttrStep("addresses"),
    IndexStep(0),
    KeyStep("zip_code"),
])
```

## Applying a CtyPath

Once you have a `CtyPath`, you can apply it to a `CtyValue` to retrieve the value at the specified path.

### A Complex Example

Let's consider a more complex data model for a user profile:

```python
from pyvider.cty import CtyObject, CtyList, CtyMap, CtyString, CtyNumber, CtyValue
from pyvider.cty.path import CtyPath, GetAttrStep, IndexStep, KeyStep

# Define the data model
user_profile_type = CtyObject({
    "username": CtyString(),
    "email": CtyString(),
    "settings": CtyMap(CtyString()),
    "projects": CtyList(
        CtyObject({
            "name": CtyString(),
            "commits": CtyNumber(),
        })
    ),
})

# Create a CtyValue for the user profile
user_profile_value = user_profile_type.validate({
    "username": "jdoe",
    "email": "jdoe@example.com",
    "settings": {
        "theme": "dark",
        "notifications": "enabled",
    },
    "projects": [
        {"name": "pyvider.cty", "commits": 100},
        {"name": "another-project", "commits": 50},
    ],
})
```

Now, let's use `CtyPath` to access specific data within this structure:

```python
# Path to the user's theme setting
theme_path = CtyPath([
    GetAttrStep("settings"),
    KeyStep("theme"),
])
theme_value = theme_path.apply(user_profile_value)
assert theme_value.value == "dark"

# Path to the number of commits for the first project
commits_path = CtyPath([
    GetAttrStep("projects"),
    IndexStep(0),
    GetAttrStep("commits"),
])
commits_value = commits_path.apply(user_profile_value)
assert commits_value.value == 100
```

### Debugging with CtyPath

`CtyPath` is also invaluable for debugging. When a validation error occurs, `pyvider.cty` uses a `CtyPath` to show you exactly where the error is located.

For example, if we try to validate a user profile with an invalid email address:

```python
try:
    user_profile_type.validate({
        "username": "jdoe",
        "email": 123,  # Invalid email
        "settings": {},
        "projects": [],
    })
except Exception as e:
    print(e)
```

The error message will include the path to the invalid value, something like:

```
at path.to.object.email: expected a string, got a number
```

This makes it much easier to identify and fix errors in your data.
