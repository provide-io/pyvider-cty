# Operating on `CtyValue`s: Getting Things Done ⚙️

So, you've mastered `CtyType` (the blueprints) and `CtyValue` (the data-filled reality). What's next? Making these values *do* things! `CtyValue` instances are far from static; they come alive with a range of operations. 🕺💃

These operations are generally type-aware, meaning they respect the `cty` type system. Think of them as Python's familiar built-in operations, but wearing a `cty` safety helmet 👷. And remember our golden rule: **immutability**. Operations that seem to change a value will almost always return a brand-new `CtyValue` instance, leaving the original pristine.

Let's dive into the common operations you'll be using.

## Equality (`__eq__`): Are We the Same? 🤔

You can check if two `CtyValue` instances are equal using the `==` operator. For two `CtyValue`s to be considered equal:
1.  Their **`CtyType`s must be equivalent**. A `CtyString` value can never be equal to a `CtyNumber` value, even if they look similar (e.g., `CtyValue.string("123")` vs. `CtyValue.number(123)`).
2.  Their underlying **Python values must be equal**.
3.  Their **marks must be identical**. If one value has a mark and the other doesn't, or they have different marks, they are not equal.

```python
# example_equality.py
from pyvider.cty import CtyString, CtyNumber, CtyValue
from decimal import Decimal

# Basic comparisons
val1_s = CtyValue.string("hello")
val2_s = CtyValue.string("hello")
val3_s = CtyValue.string("world")
val4_n = CtyValue.number(Decimal("123"))
val5_n_str = CtyValue.string("123") # String type, but value looks like val4_n's

print(f"val1_s == val2_s: {val1_s == val2_s}") # True
print(f"val1_s == val3_s: {val1_s == val3_s}") # False
print(f"val1_s == val4_n: {val1_s == val4_n}") # False
print(f"val4_n == val5_n_str: {val4_n == val5_n_str}") # False

# Comparisons with marks
val_marked_s = val1_s.mark("sensitive")
val_marked_s_again = CtyValue.string("hello").mark("sensitive")
val_differently_marked_s = val1_s.mark("public")

print(f"\nval1_s == val_marked_s: {val1_s == val_marked_s}") # False
print(f"val_marked_s == val_marked_s_again: {val_marked_s == val_marked_s_again}") # True
print(f"val_marked_s == val_differently_marked_s: {val_marked_s == val_differently_marked_s}") # False
```
<!-- pyvider.cty: Equality in cty is like a VIP club: type, value, and marks must all be on the list! 🧐📋 -->

## Length (`__len__`): How Big Is It? 📏

You can get the "length" of certain `CtyValue`s using the built-in `len()` function. This typically applies to:
-   `CtyList`, `CtyMap`, `CtySet`, `CtyTuple`: Returns the number of elements.
-   `CtyString`: Returns the length of the underlying Python string (e.g., `len(CtyValue.string("hello"))` is `5`).

```python
# example_length.py
from pyvider.cty import CtyList, CtyString, CtyMap, CtyNumber, CtySet, CtyTuple, CtyValue
from decimal import Decimal

# List
list_val = CtyValue.list(CtyString(), ["a", "b", "c", "d"])
print(f"Length of list_val (CtyList): {len(list_val)}")

# Map
map_val = CtyValue.map(CtyString(), CtyNumber(), {"x": Decimal(10), "y": Decimal(20)})
print(f"Length of map_val (CtyMap): {len(map_val)}")

# Set
set_val = CtyValue.make_set(CtyString(), {"apple", "banana"})
print(f"Length of set_val (CtySet): {len(set_val)}")

# Tuple
tuple_val = CtyValue.tuple(
    (CtyString(), CtyNumber()),
    (CtyValue.string("hello"), CtyValue.number(100))
)
print(f"Length of tuple_val (CtyTuple): {len(tuple_val)}")

# String
string_val = CtyValue.string("hello world")
print(f"Length of string_val (CtyString): {len(string_val)}")
print(f"Length of the Python string inside string_val (.value): {len(string_val.value)}")
```
<!-- pyvider.cty: Measuring your data structures, cty style! 📐 -->

## Indexing and Slicing (`__getitem__` for Lists/Tuples): Element Spotting 🎯

For `CtyList` and `CtyTuple` values, you can access individual elements by their integer index.
-   Slicing (`start:stop:step`) is also supported for `CtyList` and returns a *new* `CtyList` value.
-   Accessing an out-of-bounds index raises an `IndexError`.
-   Elements returned by indexing are `CtyValue`s. Access `.value` for the native Python value.

```python
# example_list_indexing.py
from pyvider.cty import CtyList, CtyString, CtyNumber, CtyValue, CtyTuple
from decimal import Decimal

elements = ["zeroth", "first", "second", "third", "fourth"]
list_val = CtyValue.list(CtyString(), elements)

print("--- List Indexing ---")
first_el_cty_val = list_val[0]
print(f"Element at index 0: '{first_el_cty_val.value}' (Type: {first_el_cty_val.type})")

slice_cty_val = list_val[1:4]
print(f"Slice [1:4]: {[v.value for v in slice_cty_val.value]}")

try:
    _ = list_val[10]
except IndexError as e:
    print(f"Error accessing index 10: {e} (Expected!)")

tuple_elements_cty = (CtyValue.string("Widget"), CtyValue.number(Decimal("99.99")))
tuple_val = CtyValue.tuple((CtyString(), CtyNumber()), tuple_elements_cty)
print("
--- Tuple Indexing ---")
print(f"Tuple element 0: '{tuple_val[0].value}'")
```
<!-- pyvider.cty: Picking out your data elements like a highly precise data surgeon. 👨‍⚕️🔪 -->

## Key Access (`__getitem__`, `get` for Maps): Finding by Name (Maps) 🗺️

For `CtyMap` values, access elements using their string keys.
-   `my_map_value[key]`: Returns the `CtyValue`. Raises `KeyError` if key not found.
-   `my_map_value.get(key, default=None)`: Safer. Returns `default` (or null `CtyValue` of map's value type if `default` is omitted) if key not found. `default` should be a `CtyValue`.

```python
# example_map_access.py
from pyvider.cty import CtyMap, CtyNumber, CtyString, CtyValue
from decimal import Decimal

map_data = {"alpha": Decimal("1.0"), "beta": Decimal("2.5")}
map_val = CtyValue.map(CtyString(), CtyNumber(), map_data)

print(f"Value of 'alpha': {map_val['alpha'].value}")
try:
    _ = map_val['delta']
except KeyError as e:
    print(f"Error accessing key 'delta': {e} (Expected!)")

delta_val_get = map_val.get('delta') # Returns null CtyNumber
print(f"Value of 'delta' via .get(): {delta_val_get} (Is null: {delta_val_get.is_null})")
```
<!-- pyvider.cty: Unlocking your map's treasures, one key at a time! 🗝️💰 -->

## Attribute Access (`__getitem__` for Objects): Finding by Name (Objects) 🏢

For `CtyObject` values, access attributes using their string names via `[]`.
- Raises `CtyAttributeValidationError` if attribute is not in schema.
- Accessing an optional attribute not present in data yields a null `CtyValue`.

```python
# example_object_access.py
from pyvider.cty import CtyObject, CtyString, CtyNumber, CtyValue
from pyvider.cty.exceptions import CtyAttributeValidationError # Correct exception
from decimal import Decimal

obj_schema_dict = {"name": CtyString(), "version": CtyNumber(), "author": CtyString()}
obj_type = CtyObject(attribute_types=obj_schema_dict, optional_attributes={"author"})

obj_val_full = obj_type.validate({"name": "Lib", "version": Decimal("1.0"), "author": "Dev"})
print(f"Name: {obj_val_full['name'].value}")
print(f"Author (present): {obj_val_full['author'].value}")

obj_val_no_author = obj_type.validate({"name": "LibCore", "version": Decimal("0.5")})
print(f"Author (missing optional): {obj_val_no_author['author']} (Is null: {obj_val_no_author['author'].is_null})")

try:
    _ = obj_val_full['license']
except CtyAttributeValidationError as e:
    print(f"Error accessing 'license': {e} (Expected!)")
```
<!-- pyvider.cty: Accessing your object's properties. It's like reading its nametag. 📛 -->

## Membership Testing (`__contains__`): Is It In There? 🕵️

Use `in` to check for membership:
-   **`CtyList`, `CtySet`**: Checks if a value is present. Test with raw Python values or `CtyValue`s.
-   **`CtyMap`**: Checks if a **key** (string) exists.
-   **`CtyObject`**: Checks if an **attribute name** (string) is defined in the schema.

```python
# example_contains.py
from pyvider.cty import CtyList, CtyString, CtyMap, CtyNumber, CtyObject, CtyValue, CtySet
from decimal import Decimal

list_val = CtyValue.list(CtyString(), ["hello", "world"])
print(f"'world' in list_val: {'world' in list_val}")

map_val = CtyValue.map(CtyString(), CtyNumber(), {"a": Decimal(1)})
print(f"'a' in map_val: {'a' in map_val}")

obj_schema = {"attr1": CtyString(), "opt": CtyNumber()}
obj_type = CtyObject(attribute_types=obj_schema, optional_attributes={"opt"})
obj_val = CtyValue.object(obj_schema, {"attr1": "val1"}) # Use schema_dict for creation
print(f"'attr1' in obj_val: {'attr1' in obj_val}")
print(f"'opt' in obj_val (defined in type): {'opt' in obj_val}")
print(f"'opt' in obj_val.value: {'opt' in obj_val.value}") # Check if key exists in actual value data
```
<!-- pyvider.cty: Playing hide and seek with your data! 🙈➡️❓ -->

## Iteration (`__iter__`): Walking Through Your Data 🚶‍♀️

-   **`CtyList`, `CtyTuple`, `CtySet`**: Iterating `cty_value.value` yields `CtyValue` elements.
-   **`CtyMap`**: Direct iteration (`for k in my_map_value:`) yields keys. Use `my_map_value.value.items()` for `(str_key, CtyValue_value)` pairs.

```python
# example_iteration.py
from pyvider.cty import CtyList, CtyString, CtyMap, CtyNumber, CtyTuple, CtyValue, CtySet
from decimal import Decimal

list_val = CtyValue.list(CtyString(), ["echo", "foxtrot"])
print("Iterating List (via .value):")
for item_val in list_val.value: print(f"  '{item_val.value}'")

map_val = CtyValue.map(CtyString(), CtyNumber(), {"x": Decimal(100), "y": Decimal(200)})
print("Iterating Map (Keys):")
for key_str in map_val: print(f"  Key: '{key_str}', Value: {map_val[key_str].value}")
```
<!-- pyvider.cty: Taking a stroll through your data collections, one element at a time. 👟🎶 -->
