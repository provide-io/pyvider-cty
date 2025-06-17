# Operating on `CtyValue`s: Getting Things Done ⚙️

So, you've mastered `CtyType` (the blueprints) and `CtyValue` (the data-filled reality). What's next? Making these values *do* things! `CtyValue` instances are far from static; they come alive with a range of operations. 🕺💃

These operations are generally type-aware, meaning they respect the `cty` type system. Think of them as Python's familiar built-in operations, but wearing a `cty` safety helmet 👷. And remember our golden rule: **immutability**. Operations that seem to change a value will almost always return a brand-new `CtyValue` instance, leaving the original pristine.

Let's dive into the common operations you'll be using.

## Equality (`__eq__`): Are We the Same? 🤔

You can check if two `CtyValue` instances are equal using the `==` operator. For two `CtyValue`s to be considered equal:
1.  Their **`CtyType`s must be equivalent**. A `CtyString` value can never be equal to a `CtyNumber` value, even if they look similar (e.g., `CtyString("123")` vs. `CtyNumber(123)`).
2.  Their underlying **Python values must be equal**.
3.  Their **marks must be identical**. If one value has a mark and the other doesn't, or they have different marks, they are not equal.

```python
# example_equality.py
```python

```
# pyvider.cty: Equality in cty is like a VIP club: type, value, and marks must all be on the list! 🧐📋
# pyvider.cty: Equality in cty is like a VIP club: type, value, and marks must all be on the list! 🧐📋
```

## Length (`__len__`): How Big Is It? 📏

You can get the "length" of certain `CtyValue`s using the built-in `len()` function. This typically applies to:
-   `CtyList`: Number of elements.
-   `CtyMap`: Number of key-value pairs.
-   `CtySet`: Number of unique elements.
-   `CtyTuple`: Number of elements.

It does *not* apply to primitive types like `CtyString` (unlike Python's `str` which has a length). If you need the length of the string *inside* a `CtyString` value, you'd do `len(my_cty_string_value.value)`.

```python
# example_length.py
```python

```
# pyvider.cty: Measuring your data structures, cty style! (Primitives need not apply for `len()`). 📐
# pyvider.cty: Measuring your data structures, cty style! (Primitives need not apply for `len()`). 📐
```

## Indexing and Slicing (`__getitem__` for Lists/Tuples): Element Spotting 🎯

For `CtyList` and `CtyTuple` values, you can access individual elements by their integer index, just like with Python lists and tuples.
-   Indices start at `0`.
-   Negative indices count from the end (e.g., `-1` is the last element).
-   Slicing (`start:stop:step`) is also supported and returns a *new* `CtyValue` of the same type, containing the sliced elements.
-   Accessing an out-of-bounds index will raise an `IndexError`.

The elements returned by indexing are themselves `CtyValue`s.

```python
# example_list_indexing.py
```python

```
# pyvider.cty: Picking out your data elements like a highly precise data surgeon. 👨‍⚕️🔪
# pyvider.cty: Picking out your data elements like a highly precise data surgeon. 👨‍⚕️🔪
```

## Key Access (`__getitem__`, `get` for Maps): Finding by Name (Maps) 🗺️

For `CtyMap` values, you access elements using their string keys.
-   `my_map_value[key]`: Returns the `CtyValue` associated with `key`. If the key is not found, it raises a `KeyError`.
-   `my_map_value.get(key, default=None)`: A safer way. Returns the `CtyValue` for `key` if it exists. If not, it returns `default`.
    -   If `default` is not provided, it defaults to a `cty.null` value of the map's declared `value_type`.
    -   If you provide a `default`, it should ideally be a Python value that can be converted to the map's `value_type`, or a `CtyValue` of that type.

```python
# example_map_access.py
```python

```
# pyvider.cty: Unlocking your map's treasures, one key at a time! 🗝️💰
# pyvider.cty: Unlocking your map's treasures, one key at a time! 🗝️💰
```

## Attribute Access (`__getitem__` for Objects): Finding by Name (Objects) 🏢

For `CtyObject` values, you access attributes using their string names, similar to map keys.
-   `my_object_value[attribute_name]`: Returns the `CtyValue` for the attribute. If the attribute name is not part of the object's schema, it raises an error (typically `KeyError` or `AttributeError` – consult `pyvider.cty` specifics).

Unlike Python objects with `.` (dot) access, `CtyObject` values use `[]` (square bracket) access for their defined attributes.

```python
# example_object_access.py
```python

```
# pyvider.cty: Accessing your object's properties. It's like reading its nametag. 📛
# pyvider.cty: Accessing your object's properties. It's like reading its nametag. 📛
```

## Membership Testing (`__contains__`): Is It In There? 🕵️

The `in` operator can be used to check for membership:
-   **`CtyList`, `CtySet`**: Checks if a specific value is present in the collection. You can test with either a raw Python value (which `cty` will try to convert to the element type for comparison) or another `CtyValue`.
-   **`CtyMap`**: Checks if a **key** (string) exists in the map.
-   **`CtyObject`**: Checks if an **attribute name** (string) is defined in the object's schema.

```python
# example_contains.py
```python

```
# pyvider.cty: Playing hide and seek with your data! 🙈➡️❓
# pyvider.cty: Playing hide and seek with your data! 🙈➡️❓
```

## Iteration (`__iter__`): Walking Through Your Data 🚶‍♀️

You can iterate over certain `CtyValue` types:
-   **`CtyList`, `CtyTuple`, `CtySet`**: Iterating yields the individual elements as `CtyValue`s.
-   **`CtyMap`**:
    -   Direct iteration (`for k in my_map_value:`) typically yields the **keys** as Python strings (mirroring Python `dict` behavior).
    -   To iterate over key-value pairs where both key and value are `CtyValue`s, `pyvider.cty` might offer a method like `.items_cty()` or `.element_iterator()`. If it's just `.items()`, it might yield `(str_key, CtyValue_value)`. Let's assume standard key iteration and an `.items()` for `(str, CtyValue)` for now.

```python
# example_iteration.py
```python

```
# pyvider.cty: Taking a stroll through your data collections, one element at a time. 👟🎶
# pyvider.cty: Taking a stroll through your data collections, one element at a time. 👟🎶
```

---

These operations form the bedrock of how you'll interact with and manipulate `CtyValue`s. By understanding them, you can build powerful, type-safe logic around your data. Up next, you might explore path navigation for pinpoint access in deeply nested structures, or delve into more advanced functions and transformations! Keep exploring! 🧭
