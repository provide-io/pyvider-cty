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
from pyvider.cty import CtyString, CtyNumber, CtyValue
from decimal import Decimal

# Basic comparisons
val1_s = CtyValue(CtyString(), "hello")
val2_s = CtyValue(CtyString(), "hello")
val3_s = CtyValue(CtyString(), "world")
val4_n = CtyValue(CtyNumber(), Decimal("123"))
val5_n_str = CtyValue(CtyString(), "123") # String type, but value looks like val4_n's

print(f"val1_s == val2_s: {val1_s == val2_s} # True: Same type, same value, same (no) marks")
print(f"val1_s == val3_s: {val1_s == val3_s} # False: Different values")
print(f"val1_s == val4_n: {val1_s == val4_n} # False: Different types (String vs Number)")
print(f"val4_n == val5_n_str: {val4_n == val5_n_str} # False: Different types, even if '123' looks similar")

# Comparisons with marks
val_marked_s = val1_s.mark("sensitive")
val_marked_s_again = CtyValue(CtyString(), "hello").mark("sensitive")
val_differently_marked_s = val1_s.mark("public")

print(f"\nval1_s == val_marked_s: {val1_s == val_marked_s} # False: val1_s has no marks, val_marked_s does")
print(f"val_marked_s == val_marked_s_again: {val_marked_s == val_marked_s_again} # True: Same type, value, and marks")
print(f"val_marked_s == val_differently_marked_s: {val_marked_s == val_differently_marked_s} # False: Different marks")

# Depy: Equality in cty is like a VIP club: type, value, and marks must all be on the list! 🧐📋
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
from pyvider.cty import CtyList, CtyString, CtyMap, CtyNumber, CtySet, CtyTuple, CtyValue
from decimal import Decimal

# List
list_type = CtyList(CtyString())
list_val = CtyValue(list_type, ["a", "b", "c", "d"])
print(f"Length of list_val (CtyList): {len(list_val)}") # Output: 4

# Map
map_type = CtyMap(CtyNumber())
map_val = CtyValue(map_type, {"x": Decimal(10), "y": Decimal(20), "z": Decimal(30)})
print(f"Length of map_val (CtyMap): {len(map_val)}")   # Output: 3

# Set
set_type = CtySet(CtyString())
set_val = CtyValue(set_type, ["apple", "banana", "apple"]) # "apple" is duplicate
print(f"Length of set_val (CtySet): {len(set_val)}")   # Output: 2 (duplicates are removed)

# Tuple
tuple_type = CtyTuple((CtyString(), CtyNumber()))
tuple_val = CtyValue(tuple_type, ("hello", Decimal(100)))
print(f"Length of tuple_val (CtyTuple): {len(tuple_val)}") # Output: 2

# String (illustrating the difference from Python str)
string_val = CtyValue(CtyString(), "hello world")
# print(f"Length of string_val (CtyString): {len(string_val)}") # This would typically raise a TypeError
try:
    len(string_val)
except TypeError as e:
    print(f"Error getting len(CtyString): {e} (This is expected!)")
print(f"Length of the Python string inside string_val: {len(string_val.value)}") # Output: 11

# Depy: Measuring your data structures, cty style! (Primitives need not apply for `len()`). 📐
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
from pyvider.cty import CtyList, CtyString, CtyNumber, CtyValue, CtyTuple
from decimal import Decimal

# List example
list_type = CtyList(CtyString())
elements = ["zeroth", "first", "second", "third", "fourth"]
list_val = CtyValue(list_type, elements)

print("--- List Indexing ---")
first_el_val = list_val[0]
print(f"Element at index 0: '{first_el_val.value}' (Type: {first_el_val.type})") # 'zeroth'

last_el_val = list_val[-1]
print(f"Element at index -1: '{last_el_val.value}' (Type: {last_el_val.type})")  # 'fourth'

# Slicing
slice_val = list_val[1:4] # Elements at index 1, 2, 3 ("first", "second", "third")
print(f"Slice [1:4]: {slice_val.value}, Original Type: {slice_val.type}")

try:
    print(f"Attempting out-of-bounds access: {list_val[10].value}")
except IndexError as e:
    print(f"Error accessing index 10: {e} (Expected!)")

# Tuple example
tuple_type = CtyTuple((CtyString(), CtyNumber(), CtyString()))
tuple_val = CtyValue(tuple_type, ("Widget", Decimal("99.99"), "SKU123"))
print("\n--- Tuple Indexing ---")
name_val = tuple_val[0]
price_val = tuple_val[1]
print(f"Tuple element 0: '{name_val.value}' (Type: {name_val.type})")
print(f"Tuple element 1: {price_val.value} (Type: {price_val.type})")

# Depy: Picking out your data elements like a highly precise data surgeon. 👨‍⚕️🔪
```

## Key Access (`__getitem__`, `get` for Maps): Finding by Name (Maps) 🗺️

For `CtyMap` values, you access elements using their string keys.
-   `my_map_value[key]`: Returns the `CtyValue` associated with `key`. If the key is not found, it raises a `KeyError`.
-   `my_map_value.get(key, default=None)`: A safer way. Returns the `CtyValue` for `key` if it exists. If not, it returns `default`.
    -   If `default` is not provided, it defaults to a `cty.null` value of the map's declared `value_type`.
    -   If you provide a `default`, it should ideally be a Python value that can be converted to the map's `value_type`, or a `CtyValue` of that type.

```python
# example_map_access.py
from pyvider.cty import CtyMap, CtyNumber, CtyString, CtyValue
from decimal import Decimal

map_value_type = CtyNumber()
map_type = CtyMap(map_value_type)
data = {"alpha": Decimal("1.0"), "beta": Decimal("2.5"), "gamma": Decimal("3.14")}
map_val = CtyValue(map_type, data)

print(f"Value of 'alpha': {map_val['alpha'].value} (Type: {map_val['alpha'].type})")

try:
    print(f"Attempting to access non-existent key 'delta': {map_val['delta']}")
except KeyError as e:
    print(f"Error accessing key 'delta' with []: {e} (Expected!)")

# Using .get()
print(f"\nValue of 'beta' using .get(): {map_val.get('beta').value}")
gamma_val_get = map_val.get('gamma')
print(f"Value of 'gamma' using .get(): {gamma_val_get.value}")

# .get() with non-existent key (returns cty.null of the map's value type)
delta_val_get = map_val.get('delta')
print(f"Value of 'delta' using .get() (key not found): {delta_val_get}")
print(f"  Is it null? {delta_val_get.is_null()}, Type: {delta_val_get.type}")

# .get() with a Python default value
epsilon_val_get = map_val.get('epsilon', Decimal("0.0")) # Python value as default
print(f"Value of 'epsilon' using .get() (Python default): {epsilon_val_get.value}, Type: {epsilon_val_get.type}")

# .get() with a CtyValue default value
default_cty_val = CtyValue(map_value_type, Decimal("-1.0"))
zeta_val_get = map_val.get('zeta', default_cty_val)
print(f"Value of 'zeta' using .get() (CtyValue default): {zeta_val_get.value}, Type: {zeta_val_get.type}")


# Depy: Unlocking your map's treasures, one key at a time! 🗝️💰
```

## Attribute Access (`__getitem__` for Objects): Finding by Name (Objects) 🏢

For `CtyObject` values, you access attributes using their string names, similar to map keys.
-   `my_object_value[attribute_name]`: Returns the `CtyValue` for the attribute. If the attribute name is not part of the object's schema, it raises an error (typically `KeyError` or `AttributeError` – consult `pyvider.cty` specifics).

Unlike Python objects with `.` (dot) access, `CtyObject` values use `[]` (square bracket) access for their defined attributes.

```python
# example_object_access.py
from pyvider.cty import CtyObject, CtyString, CtyNumber, CtyValue
from decimal import Decimal

obj_type_def = {
    "name": CtyString(),
    "version": CtyNumber(),
    "author": CtyString()
}
obj_type = CtyObject(obj_type_def, optional_attributes={"author"})
data = {"name": "PyviderKit", "version": Decimal("2.1"), "author": "Depy"}
obj_val = CtyValue(obj_type, data)

print(f"Attribute 'name': '{obj_val['name'].value}' (Type: {obj_val['name'].type})")
print(f"Attribute 'version': {obj_val['version'].value} (Type: {obj_val['version'].type})")
print(f"Attribute 'author' (optional): '{obj_val['author'].value}' (Type: {obj_val['author'].type})")

# Accessing a missing optional attribute that wasn't in data
data_no_author = {"name": "PyviderCore", "version": Decimal("0.5")}
obj_val_no_author = CtyValue(obj_type, data_no_author)
print(f"Attribute 'author' (missing optional): {obj_val_no_author['author']}") # Will be cty.null of CtyString
print(f"  Is it null? {obj_val_no_author['author'].is_null()}")


try:
    print(f"Attempting to access non-existent attr 'license': {obj_val['license']}")
except Exception as e: # Should be KeyError or AttributeError specific to cty
    print(f"Error accessing attribute 'license': {e} (Expected!)")

# Depy: Accessing your object's properties. It's like reading its nametag. 📛
```

## Membership Testing (`__contains__`): Is It In There? 🕵️

The `in` operator can be used to check for membership:
-   **`CtyList`, `CtySet`**: Checks if a specific value is present in the collection. You can test with either a raw Python value (which `cty` will try to convert to the element type for comparison) or another `CtyValue`.
-   **`CtyMap`**: Checks if a **key** (string) exists in the map.
-   **`CtyObject`**: Checks if an **attribute name** (string) is defined in the object's schema.

```python
# example_contains.py
from pyvider.cty import CtyList, CtyString, CtyMap, CtyNumber, CtyObject, CtyValue
from decimal import Decimal

# --- List ---
list_type = CtyList(CtyString())
list_val = CtyValue(list_type, ["hello", "world", "cty"])
print("--- List Membership ---")
print(f"'world' in list_val: {'world' in list_val} # Test with Python value")
print(f"CtyValue(CtyString(), 'cty') in list_val: {CtyValue(CtyString(), 'cty') in list_val} # Test with CtyValue")
print(f"'python' in list_val: {'python' in list_val}")

# --- Map (checks for keys) ---
map_type = CtyMap(CtyNumber())
map_val = CtyValue(map_type, {"a": Decimal(1), "b": Decimal(2)})
print("\n--- Map Key Membership ---")
print(f"'a' in map_val: {'a' in map_val}")
print(f"'c' in map_val: {'c' in map_val}")
# print(f"Decimal(1) in map_val: {Decimal(1) in map_val}") # This would be False, 'in' checks keys for maps

# --- Object (checks for attribute names) ---
obj_type = CtyObject({"attr1": CtyString(), "optional_attr": CtyNumber()}, optional_attributes={"optional_attr"})
obj_val = CtyValue(obj_type, {"attr1": "value1"}) # optional_attr is not provided, but is in schema
print("\n--- Object Attribute Membership ---")
print(f"'attr1' in obj_val: {'attr1' in obj_val}")
print(f"'optional_attr' in obj_val: {'optional_attr' in obj_val}") # True, it's in the schema
print(f"'non_existent_attr' in obj_val: {'non_existent_attr' in obj_val}")

# Depy: Playing hide and seek with your data! 🙈➡️❓
```

## Iteration (`__iter__`): Walking Through Your Data 🚶‍♀️

You can iterate over certain `CtyValue` types:
-   **`CtyList`, `CtyTuple`, `CtySet`**: Iterating yields the individual elements as `CtyValue`s.
-   **`CtyMap`**:
    -   Direct iteration (`for k in my_map_value:`) typically yields the **keys** as Python strings (mirroring Python `dict` behavior).
    -   To iterate over key-value pairs where both key and value are `CtyValue`s, `pyvider.cty` might offer a method like `.items_cty()` or `.element_iterator()`. If it's just `.items()`, it might yield `(str_key, CtyValue_value)`. Let's assume standard key iteration and an `.items()` for `(str, CtyValue)` for now.

```python
# example_iteration.py
from pyvider.cty import CtyList, CtyString, CtyMap, CtyNumber, CtyTuple, CtyValue, CtySet
from decimal import Decimal

# --- List ---
list_type = CtyList(CtyString())
list_val = CtyValue(list_type, ["echo", "foxtrot", "golf"])
print("--- Iterating List ---")
for item_val in list_val:
    print(f"  List Element: '{item_val.value}' (Type: {item_val.type})")

# --- Tuple ---
tuple_type = CtyTuple((CtyString(), CtyNumber()))
tuple_val = CtyValue(tuple_type, ("hotel", Decimal(800)))
print("\n--- Iterating Tuple ---")
for item_val in tuple_val:
    print(f"  Tuple Element: {item_val} (Value: '{item_val.value}')")

# --- Set ---
set_type = CtySet(CtyNumber())
# Note: Iteration order for sets is not guaranteed, but cty might enforce one.
set_val = CtyValue(set_type, [Decimal(1), Decimal(3), Decimal(2)])
print("\n--- Iterating Set ---")
for item_val in set_val:
    print(f"  Set Element: {item_val.value} (Type: {item_val.type})")


# --- Map ---
map_type = CtyMap(CtyNumber())
map_data = {"x-ray": Decimal(100), "yankee": Decimal(200), "zulu": Decimal(300)}
map_val = CtyValue(map_type, map_data)

# Direct iteration (usually yields keys as Python strings)
print("\n--- Iterating Map (Keys) ---")
for key_str in map_val:
    value_cty = map_val[key_str] # Get the CtyValue for the key
    print(f"  Key: '{key_str}', Value: {value_cty.value} (Type: {value_cty.type})")

# Iterating items (key-value pairs)
# Assuming an .items() method that yields (str_key, CtyValue_value)
# If pyvider.cty has `element_iterator()` yielding (CtyValue_key, CtyValue_value), adapt accordingly.
print("\n--- Iterating Map (Items like dict.items()) ---")
if hasattr(map_val, 'items'): # Check if .items() exists
    for py_key, cty_element_value in map_val.items(): # Example: Python dict-like .items()
        print(f"  Item: Key='{py_key}', Value='{cty_element_value.value}' (Type: {cty_element_value.type})")
else:
    print("  Skipping .items() example as it's not found on this CtyMap mock.")


# Depy: Taking a stroll through your data collections, one element at a time. 👟🎶
```

---

These operations form the bedrock of how you'll interact with and manipulate `CtyValue`s. By understanding them, you can build powerful, type-safe logic around your data. Up next, you might explore path navigation for pinpoint access in deeply nested structures, or delve into more advanced functions and transformations! Keep exploring! 🧭
