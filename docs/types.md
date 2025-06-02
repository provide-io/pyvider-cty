# Core Types in `pyvider.cty` 🧐

Welcome, intrepid data explorer, to the very heart of `pyvider.cty`: its type system! Understanding these types is like getting the keys to a very organized, very predictable kingdom of data. 🔑

## `CtyType`: The Master Blueprint 🏛️

At the foundation of it all lies `CtyType`. Think of it as the abstract concept of "type" within the `pyvider.cty` universe. Every specific type you'll encounter (strings, numbers, lists of gizmos, etc.) is a specialized version of `CtyType`.

Its main job? To define the "shape" and "rules" for your data.
-   What kind of data is it (text, a whole number, a true/false value)?
-   What can it contain (if it's a collection)?
-   What are its attributes (if it's an object)?

You won't typically create a `CtyType` instance directly, but rather one of its more concrete children. It's the wise ancestor all other types look up to.

## Primitive Types: The Building Blocks 🧱

These are your absolute basics, the fundamental elements from which more complex structures are forged. They're straightforward, dependable, and probably very familiar.

### `CtyString`

Represents a sequence of characters – good old text. If you're dealing with names, descriptions, messages, or anything wordy, `CtyString` is your go-to. It's basically Python's `str` type, but with the `cty` seal of approval. 📜

**Python Counterpart:** `str`

**Instantiation & Usage:**

To define that something *should* be a string, you first create an instance of `CtyString`. Then, you can create values that adhere to this type.

```python
# string_example.py
from pyvider.cty import CtyString, CtyValue, CtyTypeError

# 1. Define the "string" type
string_spec = CtyString()
print(f"Type defined: {string_spec}")

# 2. Create a CtyValue that IS a string
try:
    greeting_value = CtyValue.string(string_spec, "Hello, `cty` world! 👋")
    print(f"My string value: '{greeting_value.value}' (Python type: {type(greeting_value.value)})")

    # Accessing via .as_string() is also handy
    print(f"As string: '{greeting_value.as_string()}'")

    # What if we try to give it a number? Prepare for a polite refusal!
    print("\nAttempting to create a string value with a number (expect an error):")
    non_string_value = CtyValue.string(string_spec, 12345)
    # The line above will raise CtyTypeError, so the print below won't be reached
    # print(f"This won't print: {non_string_value}")

except CtyTypeError as e:
    print(f"💥 Kaboom! As expected, an error: {e}")
except Exception as e:
    print(f"An unexpected oops: {e}")

# Depy: String theory, but for actual strings! 🧵
```

If you try to create a `CtyValue` for a `CtyString` type using a non-string Python value (like an integer or a list), `pyvider.cty` will raise a `CtyTypeError`. It's just looking out for you!

### `CtyNumber`

This type handles numerical values. Whether it's the number of coconuts 🥥 you've collected or the precise measurement of a widget, `CtyNumber` is on the case.

A super important detail: `CtyNumber` uses Python's `decimal.Decimal` type internally. Why? PRECISION! This helps avoid those pesky floating-point arithmetic quirks that can turn exact calculations into "close enough" approximations. So, if you're dealing with money or anything that needs to be spot-on, `CtyNumber` is your financial advisor. 🧐💰

**Python Counterparts:** `decimal.Decimal`, `int`. It can also accept `float` but will convert it to `Decimal` (with a potential precision shift if you're not careful with float representations).

**Instantiation & Usage:**

```python
# number_example.py
import decimal
from pyvider.cty import CtyNumber, CtyValue, CtyTypeError

# 1. Define the "number" type
number_spec = CtyNumber()
print(f"Type defined: {number_spec}")

# 2. Create CtyValues that ARE numbers
try:
    # Using an integer
    count_value = CtyValue.number(number_spec, 123)
    print(f"\nInteger as number: {count_value.value} (Python type: {type(count_value.value)})")
    print(f"As number: {count_value.as_number()}") # Returns Decimal

    # Using a string that looks like a number (cty often converts)
    price_value_from_string = CtyValue.number(number_spec, "99.99")
    print(f"\nString '99.99' as number: {price_value_from_string.value} (Python type: {type(price_value_from_string.value)})")

    # Using a float (converted to Decimal)
    pi_approx_value = CtyValue.number(number_spec, 3.14159)
    print(f"\nFloat 3.14159 as number: {pi_approx_value.value} (Python type: {type(pi_approx_value.value)})")
    print(f"Note: Floats are converted to Decimals. Be mindful of precision expectations.")

    # Using a Decimal directly for ultimate precision
    precise_tax_rate = decimal.Decimal("0.075")
    tax_value = CtyValue.number(number_spec, precise_tax_rate)
    print(f"\nDecimal('0.075') as number: {tax_value.value} (Python type: {type(tax_value.value)})")


    # What if we try to give it something that's clearly not a number?
    print("\nAttempting to create a number value with 'not-a-number' (expect an error):")
    nan_value = CtyValue.number(number_spec, "banana")
    # This line will raise CtyTypeError

except CtyTypeError as e:
    print(f"💥 Bam! Expected error for non-numeric input: {e}")
except Exception as e:
    print(f"An unexpected oops: {e}")

# Depy: Numerical nirvana, thanks to Decimal! ✨
```
Trying to assign a value that cannot be reasonably interpreted as a number (e.g., `"apple"`) to a `CtyNumber`-typed `CtyValue` will result in a `CtyTypeError`.

### `CtyBool`

The simplest of the bunch: `CtyBool` represents a boolean value, which can only be `True` or `False`. Is the light switch on? Is the cat adorable? These are questions for `CtyBool`. ✅❌

**Python Counterpart:** `bool`

**Instantiation & Usage:**

```python
# bool_example.py
from pyvider.cty import CtyBool, CtyValue, CtyTypeError

# 1. Define the "boolean" type
bool_spec = CtyBool()
print(f"Type defined: {bool_spec}")

# 2. Create CtyValues that ARE booleans
try:
    is_enabled_value = CtyValue.boolean(bool_spec, True)
    print(f"\nBoolean 'True': {is_enabled_value.value} (Python type: {type(is_enabled_value.value)})")
    print(f"As boolean: {is_enabled_value.as_bool()}")

    has_stock_value = CtyValue.boolean(bool_spec, False)
    print(f"\nBoolean 'False': {has_stock_value.value} (Python type: {type(has_stock_value.value)})")

    # Cty is pretty smart about interpreting "truthy" or "falsy" strings for convenience in some contexts,
    # but direct boolean values are safest.
    # For example, CtyValue.boolean(bool_spec, "true") might work depending on conversion rules,
    # but it's better practice to pass actual booleans.

    # What if we try to give it something that's not a boolean at all?
    print("\nAttempting to create a boolean value with a number (expect an error):")
    not_a_bool_value = CtyValue.boolean(bool_spec, 123)
    # This line will raise CtyTypeError

except CtyTypeError as e:
    print(f"🔥 Whoops! Expected error for non-boolean input: {e}")
except Exception as e:
    print(f"An unexpected oops: {e}")

# Depy: To bool, or not to bool? That is the CtyBool.  Hamlet, probably. 🤔
```
If you attempt to create a `CtyValue` for a `CtyBool` type with a value that isn't a Python `bool` (like `0`, `1`, or `"true"` without specific conversion logic, or an arbitrary string like `"maybe"`), it will typically raise a `CtyTypeError`. Stick to `True` and `False` for clarity!

---

## Collection Types: Organizing Your Data Horde 🧺

Primitives are great, but what about when you need to group things? That's where Collection Types come in, allowing you to manage lists, sets, and maps of data. These types are all about holding *other* types, but with rules, of course!

### `CtyList(element_type: CtyType)`

Represents an **ordered sequence** of elements, where all elements must be of the **same specified type**. Think of Python's `list`, but with a strict bouncer at the club door checking everyone's type ID. 깐깐한 목록 😉

**Python Counterpart:** `list`

**Instantiation & Usage:**

To create a list type, you must tell it what kind of elements it's allowed to hold. For instance, a list of strings, or a list of numbers.

```python
# list_example.py
from pyvider.cty import CtyList, CtyString, CtyNumber, CtyValue, CtyTypeError
import decimal # For CtyNumber examples

# 1. Define a list type that only accepts strings
string_list_spec = CtyList(CtyString())
print(f"String list type defined: {string_list_spec}")

# 2. Create a CtyValue for this list type
try:
    names_py_list = ["Alice", "Bob", "Charlie"]
    names_cty_value = CtyValue.list_of_strings(string_list_spec, names_py_list) # Using specific helper
    # Or more generally: names_cty_value = CtyValue(string_list_spec, names_py_list)
    print(f"My list of names: {names_cty_value.value} (Python type: {type(names_cty_value.value)})")
    print(f"As list of strings: {names_cty_value.as_list_of_strings()}")


    # What if we try to sneak in a number into our list of strings? 🚨
    print("\nAttempting to create a list of strings with a number (expect an error):")
    mixed_py_list = ["David", 42, "Eve"] # Oh dear, a number!
    # This will fail because 42 is not a string.
    error_prone_value = CtyValue(string_list_spec, mixed_py_list)
    # print(f"This won't print: {error_prone_value}")

except CtyTypeError as e:
    print(f"🚫 Expected error due to type mismatch in list: {e}")
except Exception as e:
    print(f"An unexpected list oops: {e}")

# 3. Example: A list of numbers
number_list_spec = CtyList(CtyNumber())
print(f"\nNumber list type defined: {number_list_spec}")
lucky_numbers_py_list = [7, 42, 101.0, decimal.Decimal("33.3")] # Mix of int, float, Decimal
lucky_numbers_cty_value = CtyValue(number_list_spec, lucky_numbers_py_list)
print(f"My lucky numbers: {lucky_numbers_cty_value.value}")
# Note: all numbers in lucky_numbers_cty_value.value will be Decimals.

# Depy: Keeping your lists orderly and type-consistent, one element at a time! 🧐
```
The key here is **homogeneity**. All elements in a `CtyList` must conform to the `element_type` specified when the list type was defined.

### `CtyMap(value_type: CtyType)`

Represents a collection of **key-value pairs**. The keys are always **strings** (just like JSON objects or Python dictionaries used in similar contexts), and all values must be of the **same specified `value_type`**. It's like a dictionary where you know what kind of item you'll get for every key. 🗺️

**Python Counterpart:** `dict`

**Instantiation & Usage:**

When defining a map type, you specify the type of its values. Keys are implicitly strings.

```python
# map_example.py
from pyvider.cty import CtyMap, CtyString, CtyNumber, CtyBool, CtyValue, CtyTypeError
import decimal # For CtyNumber examples

# 1. Define a map type: string keys to number values
# e.g., {"apples": 5, "bananas": 12}
inventory_spec = CtyMap(CtyNumber())
print(f"Inventory map type defined: {inventory_spec}")

# 2. Create a CtyValue for this map type
try:
    fruit_counts_py_dict = {"apples": 10, "bananas": 5, "oranges": 0}
    inventory_cty_value = CtyValue.map_of_numbers(inventory_spec, fruit_counts_py_dict) # Specific helper
    # Or generally: inventory_cty_value = CtyValue(inventory_spec, fruit_counts_py_dict)
    print(f"My fruit inventory: {inventory_cty_value.value}")
    print(f"Inventory as map of numbers: {inventory_cty_value.as_map_of_numbers()}")


    # What if a value has the wrong type?
    print("\nAttempting to create a map with a non-number value (expect an error):")
    invalid_inventory_py_dict = {"grapes": 100, "berries": "lots"} # "lots" is not a number!
    error_prone_map_value = CtyValue(inventory_spec, invalid_inventory_py_dict)
    # print(f"This won't print: {error_prone_map_value}")

except CtyTypeError as e:
    print(f"🚫 Expected error due to type mismatch in map value: {e}")
except Exception as e:
    print(f"An unexpected map oops: {e}")

# 3. Example: A map of string keys to boolean values
feature_flags_spec = CtyMap(CtyBool())
print(f"\nFeature flags map type defined: {feature_flags_spec}")
flags_py_dict = {"new_dashboard": True, "beta_feature": False, "dark_mode": True}
flags_cty_value = CtyValue(feature_flags_spec, flags_py_dict)
print(f"My feature flags: {flags_cty_value.value}")

# Depy: Mapping out your data, one strongly-typed value at a time! 🧭
```
Remember, keys are always strings in `CtyMap`. All values must adhere to the single `value_type` you define for the map.

### `CtySet(element_type: CtyType)`

Represents an **unordered collection of unique elements**, all of which must be of the **same specified `element_type`**. It's like Python's `set`: no duplicates allowed, and the order doesn't matter (though `pyvider.cty` might store them in a canonical order internally for consistency). 💎

**Python Counterpart:** `set` (though the `CtyValue` will often present it as a sorted list for predictability).

**Instantiation & Usage:**

Similar to `CtyList`, you specify the type of elements the set can contain.

```python
# set_example.py
from pyvider.cty import CtySet, CtyString, CtyNumber, CtyValue, CtyTypeError
import decimal # For CtyNumber examples

# 1. Define a set type that only accepts strings
tags_spec = CtySet(CtyString())
print(f"Tags set type defined: {tags_spec}")

# 2. Create a CtyValue for this set type
try:
    # Note: Input can be a list or a set. Duplicates will be removed.
    py_tags_list_with_duplicates = ["cloud", "python", "awesome", "python"]
    tags_cty_value = CtyValue.set_of_strings(tags_spec, py_tags_list_with_duplicates) # Specific helper
    # Or generally: tags_cty_value = CtyValue(tags_spec, py_tags_list_with_duplicates)

    # The .value might be a list (sorted for consistency) or a set,
    # depending on internal representation.
    # The key is that it *behaves* like a set of unique, typed elements.
    print(f"My tags set: {tags_cty_value.value} (Python type: {type(tags_cty_value.value)})")
    print(f"As set of strings: {tags_cty_value.as_set_of_strings()}") # Often returns a Python set

    # What if we try to add an element of the wrong type?
    print("\nAttempting to create a set of strings with a number (expect an error):")
    mixed_py_collection = ["important", 123] # 123 is not a string!
    error_prone_set_value = CtyValue(tags_spec, mixed_py_collection)
    # print(f"This won't print: {error_prone_set_value}")

except CtyTypeError as e:
    print(f"🚫 Expected error due to type mismatch in set: {e}")
except Exception as e:
    print(f"An unexpected set oops: {e}")

# 3. Example: A set of numbers
scores_spec = CtySet(CtyNumber())
print(f"\nScores set type defined: {scores_spec}")
py_scores = [100, 95.5, 80, 95.5] # Duplicate 95.5
scores_cty_value = CtyValue(scores_spec, py_scores)
print(f"Unique scores: {scores_cty_value.value}") # Duplicates removed, numbers are Decimals

# Depy: Ensuring your collections are unique and type-safe, like a well-curated museum! 🖼️
```
`CtySet` ensures both **homogeneity** (all elements of the same type) and **uniqueness**. If you provide a list with duplicates when creating a `CtySet` value, the duplicates are silently removed.

---

## Structural Types: Building Complex Schemas 🏗️

Now we're getting to the really fancy stuff! Structural types let you define custom, complex data structures with fixed layouts. This is where `pyvider.cty` truly shines in helping you model intricate data with precision.

### `CtyObject(attribute_types: dict[str, CtyType], optional_attributes: set[str] | None = None)`

Objects are like custom blueprints for your data structures. You define a set of named 'attributes' (like fields or properties) and specify the `CtyType` for each one. Think of them as Python dictionaries that went to finishing school and are now very particular about their keys and value types. 깐깐한 객체! 🧐

When you define an object, you provide a dictionary for `attribute_types` where keys are the attribute names (strings) and values are their corresponding `CtyType` instances.

The `optional_attributes` parameter is a set of attribute names that don't need to be present when creating a value. If an optional attribute is missing, its value will effectively be `null` within `pyvider.cty`.

**Python Counterpart:** `dict` (but a very disciplined one)

**Instantiation & Usage:**

```python
# object_example.py
from pyvider.cty import (
    CtyObject, CtyString, CtyNumber, CtyBool, CtyValue, CtyTypeError
)

# 1. Define an object type for a user profile
# Attributes: 'name' (string, required), 'age' (number, required),
#             'email' (string, optional)
user_profile_spec = CtyObject(
    attribute_types={
        "name": CtyString(),
        "age": CtyNumber(),
        "email": CtyString(), # Email is also a string
        "is_active": CtyBool()
    },
    optional_attributes={"email"} # Make 'email' optional
)
print(f"User profile type defined: {user_profile_spec}")

# 2. Create CtyValues for this object type
try:
    # User with all attributes, including optional 'email'
    user1_py_data = {"name": "Alice", "age": 30, "email": "alice@example.com", "is_active": True}
    user1_cty_value = CtyValue.object(user_profile_spec, user1_py_data)
    print(f"\nUser 1 (all attrs): {user1_cty_value.value}")
    # .value is a dict: {'name': 'Alice', 'age': Decimal('30'), 'email': 'alice@example.com', 'is_active': True}

    # User missing the optional 'email' attribute
    user2_py_data = {"name": "Bob", "age": 25, "is_active": False}
    user2_cty_value = CtyValue.object(user_profile_spec, user2_py_data)
    print(f"\nUser 2 (optional 'email' missing): {user2_cty_value.value}")
    # .value is a dict: {'name': 'Bob', 'age': Decimal('25'), 'email': None, 'is_active': False}
    # Note: missing optional attributes are represented as None in the Python dict value,
    # which corresponds to a cty null value of the attribute's type (CtyString.null()).

    # Attempting to create an object with a type mismatch for 'age'
    print("\nAttempting user with type mismatch for 'age' (expect an error):")
    user3_py_data_invalid = {"name": "Charlie", "age": "young", "is_active": True} # 'age' should be a number
    error_prone_obj_value1 = CtyValue.object(user_profile_spec, user3_py_data_invalid)
    # This line will raise CtyTypeError

except CtyTypeError as e:
    print(f"🚫 Expected error (type mismatch or missing required): {e}")
except Exception as e:
    print(f"An unexpected object oops: {e}")

try:
    # Attempting to create an object missing a *required* attribute ('age')
    print("\nAttempting user missing required 'age' (expect an error):")
    user4_py_data_invalid = {"name": "Dave", "email": "dave@example.com", "is_active": False}
    error_prone_obj_value2 = CtyValue.object(user_profile_spec, user4_py_data_invalid)
    # This line will raise CtyTypeError

except CtyTypeError as e:
    print(f"🚫 Expected error (type mismatch or missing required): {e}")
except Exception as e:
    print(f"An unexpected object oops: {e}")


# Depy: Structuring your world, one well-defined object at a time. 📐
```
If you try to create a `CtyObject` value without a required attribute, or if an attribute's value doesn't match its defined `CtyType`, `pyvider.cty` will let you know with a `CtyTypeError`.

### `CtyTuple(element_types: tuple[CtyType, ...])`

A `CtyTuple` represents an **ordered sequence** of elements, much like `CtyList`. However, the key difference is that each element in a `CtyTuple` can (and often does) have a **different, specific `CtyType`**, defined by its position in the sequence. Think of Python's `tuple` when used as a simple, fixed-size record to group related but different kinds of data. 📦

**Python Counterpart:** `tuple`

**Instantiation & Usage:**

You define a tuple type by providing a Python tuple of `CtyType` instances. The order matters!

```python
# tuple_example.py
from pyvider.cty import (
    CtyTuple, CtyString, CtyNumber, CtyBool, CtyValue, CtyTypeError
)

# 1. Define a tuple type for a (string, number, boolean) structure
# e.g., ("item_name", item_count, is_in_stock)
item_record_spec = CtyTuple((
    CtyString(),  # Element 0: Name (string)
    CtyNumber(),  # Element 1: Count (number)
    CtyBool()     # Element 2: In Stock (boolean)
))
print(f"Item record tuple type defined: {item_record_spec}")

# 2. Create a CtyValue for this tuple type
try:
    record1_py_data = ("Laptop X2000", 15, True)
    record1_cty_value = CtyValue(item_record_spec, record1_py_data)
    print(f"\nRecord 1: {record1_cty_value.value} (Python type: {type(record1_cty_value.value)})")
    # .value is a tuple: ('Laptop X2000', Decimal('15'), True)

    # Accessing elements (cty values can be indexed if they are sequences)
    print(f"Name: {record1_cty_value[0].as_string()}, Count: {record1_cty_value[1].as_number()}")


    # Attempting to create a tuple with the wrong number of elements
    print("\nAttempting tuple with wrong number of elements (expect an error):")
    invalid_data_len = ("Too short", 10)
    error_prone_tuple1 = CtyValue(item_record_spec, invalid_data_len)
    # This line will raise CtyTypeError

except CtyTypeError as e:
    print(f"🚫 Expected error (element count or type mismatch): {e}")
except Exception as e:
    print(f"An unexpected tuple oops: {e}")

try:
    # Attempting to create a tuple with a type mismatch for an element
    print("\nAttempting tuple with type mismatch (element 1) (expect an error):")
    invalid_data_type = ("Keyboard", "twenty", False) # "twenty" is not a number
    error_prone_tuple2 = CtyValue(item_record_spec, invalid_data_type)
    # This line will raise CtyTypeError

except CtyTypeError as e:
    print(f"🚫 Expected error (element count or type mismatch): {e}")
except Exception as e:
    print(f"An unexpected tuple oops: {e}")

# Depy: Tuples - when order and type variety matter in a sequence! ✨
```
A `CtyTuple` value must have exactly the number of elements defined in its type, and each element must conform to the `CtyType` specified for its position.

### `CtyDynamic` (aka `DynamicPseudoType`)

And now for something completely different: `CtyDynamic`! This is the wildcard, the "I'm not sure yet" or "anything goes" type in `pyvider.cty`. It acts as a placeholder for a value whose specific `cty` type isn't known when the *type itself* is being specified. 🃏

**Don't be fooled!** While `CtyDynamic` can *represent* any type, a `CtyValue` that is "dynamically typed" in this way will *still* have an actual, concrete underlying `CtyType` (like `CtyString`, `CtyNumber`, `CtyList(CtyString)`, etc.). `CtyDynamic` is a way of saying "the type checker shouldn't be too picky about *this specific slot* right now, because its true type will be revealed by the value it eventually holds."

**Python Counterpart:** There isn't a direct one, as Python is dynamically typed by nature. `CtyDynamic` brings a controlled form of this dynamism into the `cty` type system.

**Instantiation & Usage:**

```python
# dynamic_example.py
from pyvider.cty import (
    CtyDynamic, CtyString, CtyNumber, CtyList, CtyValue, CtyTypeError
)

# 1. Define the dynamic type
dynamic_spec = CtyDynamic() # Or: from pyvider.cty.types import DynamicPseudoType; dynamic_spec = DynamicPseudoType
print(f"Dynamic type defined: {dynamic_spec}")

# 2. Create CtyValues using the dynamic type
# The dynamic type itself doesn't impose constraints, but the value
# passed to CtyValue() will be introspected to find its concrete cty type.
try:
    # A string value, wrapped in CtyDynamic context
    val_string = CtyValue(dynamic_spec, "I'm a string!")
    print(f"\nDynamic holding a string: {val_string.value} (Actual cty type: {val_string.ty})")
    # val_string.ty will be CtyString

    # A number value
    val_number = CtyValue(dynamic_spec, 123.45)
    print(f"Dynamic holding a number: {val_number.value} (Actual cty type: {val_number.ty})")
    # val_number.ty will be CtyNumber

    # A list of strings value
    val_list_str = CtyValue(dynamic_spec, ["one", "two", "three"])
    print(f"Dynamic holding a list of strings: {val_list_str.value} (Actual cty type: {val_list_str.ty})")
    # val_list_str.ty will be CtyList(CtyString)

    # Even a null value has a concrete type when seen through CtyDynamic
    # (it becomes a null of dynamic type, but if it were from a typed source, it would be e.g., CtyString.null())
    # For direct construction with CtyValue(dynamic_spec, None), it might be CtyDynamic.null()
    # More practically, if you had a CtyValue.null(CtyString), it would be accepted by CtyDynamic.
    val_null_from_typed_source = CtyValue.null(CtyString())
    val_dynamic_null = CtyValue(dynamic_spec, val_null_from_typed_source.value) # Passing the actual null value
    print(f"Dynamic holding a null (from typed source): {val_dynamic_null.is_null()}, (Actual cty type: {val_dynamic_null.ty})")


except CtyTypeError as e:
    # This is less likely with CtyDynamic directly unless the input Python value is totally unusable.
    print(f"🚫 Error with dynamic value: {e}")
except Exception as e:
    print(f"An unexpected dynamic oops: {e}")

# Depy: CtyDynamic - for when you need to keep your type options open! 😉
```

**When is it useful?**
`CtyDynamic` is particularly handy in scenarios where:
*   You're working with data whose structure isn't fully known until runtime (e.g., processing arbitrary JSON payloads).
*   You're writing functions or components that need to operate on a wide variety of types in a generic way.
*   You're gradually migrating a system to use `pyvider.cty` and need placeholders for parts not yet strictly typed.

It provides flexibility, but remember: with great power comes great responsibility! Overusing `CtyDynamic` can undermine the benefits of static type checking that `pyvider.cty` otherwise offers.

---

And that's a wrap on the major `CtyType` categories in `pyvider.cty`! From simple Primitives to organized Collections, and finally to custom-defined Structures (with a dash of Dynamic flexibility), you now have the tools to define almost any data shape imaginable.

Understanding these types is the first giant leap. Next, you'll want to explore how `CtyValue` brings these type definitions to life by holding your actual data. Onwards, to `values.md` (conceptually speaking, of course, as you're already a pro reader of Markdown files!). 🚀
