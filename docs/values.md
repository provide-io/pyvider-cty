# `CtyValue`: The Heart of Your Data ❤️

Welcome, data adventurer! You've learned about `CtyType` and how it defines the blueprints for your data. Now, let's meet `CtyValue` – the actual, living, breathing data itself, all dressed up in its type-safe `cty` attire. If `CtyType` is the recipe, `CtyValue` is the delicious cake 🎂 (or the perfectly structured dataset, if you prefer).

Every single piece of data you'll work with in the `pyvider.cty` system is wrapped in a `CtyValue` instance. It's the universal container that not only holds your Python value but also *knows* its `CtyType`, ensuring everything plays by the rules.

## Creating `CtyValue` Instances: Bringing Data to Life ✨

The primary way to create a `CtyValue` is by using its constructor:

`CtyValue(type: CtyType, py_value: Any)`

-   `type`: This is an instance of a `CtyType` (e.g., `CtyString()`, `CtyNumber()`, `CtyList(CtyString())`). It tells the `CtyValue` what kind of data it's supposed to hold.
-   `py_value`: This is your raw Python data (e.g., a string, a number, a list, a dictionary).

When you create a `CtyValue`, a crucial validation step happens: `pyvider.cty` checks if the provided `py_value` actually conforms to the specified `CtyType`.
-   If it's a match (e.g., you give a Python string for `CtyString()`), all is well!
-   If it's a mismatch (e.g., you try to pass a Python list to `CtyNumber()`), `pyvider.cty` will raise an eyebrow and then an error (usually a `CtyTypeError` or similar, depending on the exact mismatch). This is `cty` saving you from future headaches!

Let's see it in action:

```python
# example_create_value.py
from pyvider.cty import (
    CtyString, CtyNumber, CtyList, CtyObject, CtyBool, # Assuming these are your type classes
    CtyValue, CtyTypeError
)
from decimal import Decimal

# Define some basic types
string_type = CtyString()
number_type = CtyNumber()
bool_type = CtyBool()

try:
    # --- Simple Valid Values ---
    str_val = CtyValue(string_type, "Hello, `cty` value!")
    print(f"String value created: {str_val} (Type: {str_val.type})")

    num_val = CtyValue(number_type, Decimal("123.45")) # Using Decimal for precision
    print(f"Number value created: {num_val} (Type: {num_val.type})")

    bool_val = CtyValue(bool_type, True)
    print(f"Boolean value created: {bool_val} (Type: {bool_val.type})")

    # --- Example with a Collection (List of Strings) ---
    list_of_strings_type = CtyList(string_type)
    py_list = ["apple", "banana", "cherry"]
    cty_list_val = CtyValue(list_of_strings_type, py_list)
    print(f"List of strings value: {cty_list_val} (Type: {cty_list_val.type})")

    # --- Example with an Object ---
    user_profile_type = CtyObject({
        "name": string_type,
        "id": number_type,
        "is_active": bool_type
    })
    user_py_data = {"name": "Depy McTypeFace", "id": Decimal(777), "is_active": True}
    user_cty_val = CtyValue(user_profile_type, user_py_data)
    print(f"User object value: {user_cty_val} (Type: {user_cty_val.type})")

    # --- Invalid Value Example ---
    print("\nAttempting to create a CtyValue with a type mismatch (expect an error):")
    # Trying to put a string into a number_type. Oh, the humanity!
    invalid_val = CtyValue(number_type, "this is definitely not a number")
    # The line above should raise a CtyTypeError, so the print below won't execute.
    # print(f"This won't print: {invalid_val}")

except CtyTypeError as e:
    print(f"💥 As expected, a CtyTypeError: {e}")
except Exception as e:
    print(f"An unexpected error occurred during CtyValue creation: {e}")

# Depy: Values are born, types are checked, order is maintained. 秩序!
```

## Accessing the Underlying Python Value: The `.value` Property 🎁

Once you have a `CtyValue`, you'll often want to get the raw Python data back out to work with it in non-`cty` parts of your code or to send it to external systems. This is done using the `.value` property:

`python_data = my_cty_value.value`

The type of `python_data` will be the corresponding Python type:
-   `str` for `CtyString`
-   `decimal.Decimal` for `CtyNumber` (usually!)
-   `bool` for `CtyBool`
-   `list` for `CtyList`
-   `dict` for `CtyMap` and `CtyObject`
-   `set` for `CtySet` (or sometimes a list, check your implementation)
-   `tuple` for `CtyTuple`

**Important Caveats for `.value`**:
-   **Null Values**: If `my_cty_value` is a *null* value (see next section), `my_cty_value.value` will return `None`. This is perfectly fine and expected.
-   **Unknown Values**: If `my_cty_value` is an *unknown* value (see next section), trying to access `my_cty_value.value` will result in an error (often an `InvalidOperationError` or similar, as the value isn't actually known yet!). You must check if a value is known before trying to get its Python representation.

```python
# example_access_value.py
from pyvider.cty import (
    CtyString, CtyNumber, CtyBool, CtyList, CtyObject,
    CtyValue, CtyTypeError # Assuming InvalidOperationError for unknowns might come from here or a sub-module
)
# from pyvider.cty.errors import InvalidOperationError # Or wherever it's defined
from decimal import Decimal

# Create some known values
str_val = CtyValue(CtyString(), "Hi there, I'm a Python string inside a CtyValue!")
print(f"The Python string: '{str_val.value}' (type: {type(str_val.value).__name__})")

num_val = CtyValue(CtyNumber(), Decimal("101.1"))
print(f"The Python number: {num_val.value} (type: {type(num_val.value).__name__})")

complex_obj_type = CtyObject({"item": CtyString(), "qty": CtyNumber()})
complex_val = CtyValue(complex_obj_type, {"item": "widget", "qty": 10})
print(f"The Python dict from object: {complex_val.value} (type: {type(complex_val.value).__name__})")

# Null value example
null_str_val = CtyValue.null(CtyString()) # Creates a null value of type CtyString
print(f"Python value of a null string: {null_str_val.value} (Is it None? {null_str_val.value is None})")

# Unknown value example (illustrating the error)
unknown_num_val = CtyValue.unknown(CtyNumber()) # Creates an unknown value of type CtyNumber
print(f"Unknown number CtyValue: {unknown_num_val}")
try:
    print(f"Trying to access .value of an unknown CtyValue: {unknown_num_val.value}")
except Exception as e: # Replace Exception with the specific expected error like InvalidOperationError
    print(f"🎉 Error accessing .value of an unknown value (this is expected!): {e}")

# Depy: Peeking inside the CtyValue box! What treasures will we find? 🎁
```

## Null and Unknown Values: The Zen of Emptiness and Mystery 🧘❓

`pyvider.cty` has special ways to represent values that are intentionally absent (null) or not yet determined (unknown). These are critical for building robust systems that handle incomplete or evolving data.

### Null Values (`.is_null`)

A **null value** means "there's definitely no value here, and that's on purpose." It's not zero, it's not an empty string; it's the explicit absence of a value. However, a null value *still knows its type*. For example, you can have a null string, a null number, or a null object.

-   **Creation**: `CtyValue.null(target_type: CtyType)`
    *   Example: `null_user = CtyValue.null(CtyObject({"name": CtyString()}))`
-   **Checking**: Use the `.is_null` boolean property.
-   **`.value` Property**: Accessing `.value` on a null `CtyValue` returns `None`.

### Unknown Values (`.is_unknown`)

An **unknown value** is a powerful concept, especially in systems like Terraform that plan changes before applying them. It means "there *will be* a value here eventually, and we know what *type* it will be, but we just don't know *what* that value is right now."

-   **Creation**: `CtyValue.unknown(target_type: CtyType)`
    *   Example: `future_ip_address = CtyValue.unknown(CtyString())`
-   **Checking**: Use the `.is_unknown` boolean property.
-   **`.is_known` Property**: This is the convenient inverse of `.is_unknown`. If `.is_known` is `True`, the value is not unknown (it could be null or a concrete value).
-   **`.value` Property**: **CRITICAL!** You **cannot** access the `.value` of an unknown `CtyValue`. Doing so will raise an error (e.g., `InvalidOperationError`) because, well, the value isn't known!

```python
# example_null_unknown.py
from pyvider.cty import (
    CtyString, CtyNumber, CtyObject, CtyList,
    CtyValue, CtyTypeError # Assuming InvalidOperationError might be here
)
# from pyvider.cty.errors import InvalidOperationError # Or from specific errors module

string_type = CtyString()
number_type = CtyNumber()
object_type = CtyObject({"status": string_type})

# --- Null Values ---
null_string = CtyValue.null(string_type)
print(f"Null String: {null_string}")
print(f"  Type: {null_string.type}, Is Null: {null_string.is_null}, Is Unknown: {null_string.is_unknown}, Is Known: {null_string.is_known}")
print(f"  Python Value: {null_string.value} (Is it None? {null_string.value is None})")

null_object = CtyValue.null(object_type)
print(f"\nNull Object: {null_object}")
print(f"  Type: {null_object.type}, Is Null: {null_object.is_null}, Python Value: {null_object.value}")


# --- Unknown Values ---
unknown_number = CtyValue.unknown(number_type)
print(f"\nUnknown Number: {unknown_number}")
print(f"  Type: {unknown_number.type}, Is Null: {unknown_number.is_null}, Is Unknown: {unknown_number.is_unknown}, Is Known: {unknown_number.is_known}")
try:
    print(f"  Attempting to get Python value of unknown: {unknown_number.value}")
except Exception as e: # Replace with specific error like InvalidOperationError
    print(f"  🎉 As expected, error getting value of unknown: {e}")

unknown_list_type = CtyList(string_type)
unknown_list = CtyValue.unknown(unknown_list_type)
print(f"\nUnknown List: {unknown_list}")
print(f"  Type: {unknown_list.type}, Is Unknown: {unknown_list.is_unknown}")


# --- A Known, Non-Null, Non-Unknown Value ---
real_string = CtyValue(string_type, "I'm definitely here and not mysterious at all.")
print(f"\nReal String: {real_string}")
print(f"  Is Null: {real_string.is_null}, Is Unknown: {real_string.is_unknown}, Is Known: {real_string.is_known}, Value: '{real_string.value}'")

# Depy: To be null, or to be unknown, that is the question. Or maybe just be known. 🤔
```

## Marks: Like Sticky Notes for Your Data 🏷️

Marks are a neat feature of `pyvider.cty` that let you attach arbitrary string metadata to `CtyValue`s. These marks don't change the value itself, its type, or how it behaves in equality checks. Think of them as non-stick, yet informative, sticky notes. They tell you something *about* the data without changing the data itself. You can peel them off, read them, or even ignore them if you're feeling rebellious. 😉

Common uses for marks include:
-   Tagging data as "sensitive" so it can be redacted in logs.
-   Tracking data provenance (e.g., "derived_from_user_input", "computed_value").
-   Indicating that a value might be "tainted" and needs sanitization.

**Key characteristics and operations:**
-   **Immutability**: `CtyValue`s are immutable. When you add or remove marks, you get a *new* `CtyValue` instance with the changes; the original remains untouched.
-   **Accessing Marks**: `my_value.marks` usually returns a `frozenset` of strings (or custom `CtyMark` objects) representing the marks on the value.
-   **Adding Marks**: `my_value.mark("new_mark_1", "new_mark_2")` returns a new `CtyValue` with "new_mark_1" and "new_mark_2" added to its existing marks.
-   **Removing Marks**: `my_value.unmark("mark_to_remove")` returns a new `CtyValue` with "mark_to_remove" gone from its marks (if it was there).
-   **Setting Marks Explicitly**: `my_value.with_marks({"exact_mark_1", "exact_mark_2"})` returns a new `CtyValue` that has *only* "exact_mark_1" and "exact_mark_2", regardless of what marks it had before.

```python
# example_marks.py
from pyvider.cty import CtyString, CtyValue # Assuming CtyMark might be an internal detail or just strings

# Start with a plain value
secret_agent_name = CtyValue(CtyString(), "James Bond")
print(f"Initial value: '{secret_agent_name.value}', Marks: {secret_agent_name.marks}")

# Add some marks - returns a NEW CtyValue
confidential_name = secret_agent_name.mark("confidential", "source:MI6")
print(f"Marked value: '{confidential_name.value}', Marks: {confidential_name.marks}")
# Original value is unchanged due to immutability!
print(f"Original value still has marks: {secret_agent_name.marks}")

# Add another mark to the already marked value
top_secret_name = confidential_name.mark("eyes-only")
print(f"More marks: '{top_secret_name.value}', Marks: {top_secret_name.marks}")

# Remove a mark - also returns a NEW CtyValue
still_secret_name = top_secret_name.unmark("source:MI6")
print(f"Unmarked 'source:MI6': '{still_secret_name.value}', Marks: {still_secret_name.marks}")

# Remove a non-existent mark (no error, no change)
unchanged_name = still_secret_name.unmark("non_existent_mark")
print(f"Unmark non-existent: '{unchanged_name.value}', Marks: {unchanged_name.marks} (Same as before? {unchanged_name.marks == still_secret_name.marks})")

# Replace all marks with a new set
public_alias = still_secret_name.with_marks({"alias", "public-figure"})
print(f"Replaced all marks: '{public_alias.value}', Marks: {public_alias.marks}")

# Clear all marks by setting them to an empty collection
unmarked_again = public_alias.with_marks(set()) # Pass an empty set or list
print(f"All marks removed: '{unmarked_again.value}', Marks: {unmarked_again.marks}")

# Depy: Tagging your data like a pro graffiti artist, but, you know, organized. 🎨🔖
```

---

Phew! That's the grand tour of `CtyValue`. From creation to accessing its core, handling the nuances of null and unknown states, and even jazzing it up with marks, you're now well-equipped to manage runtime data within the `pyvider.cty` framework.

Next up, you might want to explore how to navigate through complex `CtyValue` structures (like objects and lists) or perform operations and transformations on them. Happy typing! 🎉
