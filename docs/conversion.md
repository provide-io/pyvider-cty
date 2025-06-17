# Type Conversion Utilities: Advanced Type Wrangling 🛠️

Welcome, `cty` connoisseurs, to the engine room! The `pyvider.cty.conversion` module (and some of its key functions directly available from `pyvider.cty`) offers lower-level tools for working directly with `CtyType` definitions. While day-to-day operations often revolve around `CtyValue`s and their direct methods, these conversion utilities are your best friends for more advanced scenarios like:

-   **Dynamic Type Construction**: Building types on the fly based on external schemas or configurations.
-   **Schema Introspection**: Deeply understanding the structure of your types.
-   **Custom Tooling**: Creating your own libraries or tools that interoperate with or extend `pyvider.cty`.
-   **Storing Type Definitions**: Saving and loading the blueprints of your data, not just the data itself.

Let's unscrew the panel and see what shiny knobs and levers we have!

## Serializing Types: `marshal_type` and `unmarshal_type` 📜🔁

Ever wanted to save a `CtyType` definition itself to a file, perhaps as JSON, or send it over a network? That's precisely what `marshal_type` and `unmarshal_type` are for! They allow you to convert a `CtyType` instance into a serializable Python dictionary and then reconstruct the `CtyType` from that dictionary.

-   **`marshal_type(type_instance: CtyType) -> dict`**: Takes a `CtyType` instance (e.g., `CtyString()`, `CtyList(CtyNumber())`) and returns a Python dictionary that represents it. This dictionary is designed to be easily convertible to JSON or other common serialization formats.
-   **`unmarshal_type(type_dict: dict) -> CtyType`**: Takes a dictionary (previously produced by `marshal_type`) and reconstructs the original `CtyType` instance from it.

This is incredibly powerful for systems where type definitions need to be dynamic or stored externally.

**Code Example:**

```python
# example_type_serialization.py
from pyvider.cty import (
    CtyString, CtyNumber, CtyBool, CtyList, CtyMap, CtyObject, CtyTuple, CtyDynamic,
    CtyType, # Base type for type hinting
    # marshal_type and unmarshal_type are often exposed directly via pyvider.cty
    marshal_type, unmarshal_type
)
# If not, adjust import: from pyvider.cty.conversion import marshal_type, unmarshal_type

# A collection of diverse types to test
types_to_roundtrip: list[CtyType] = [
    CtyString(),
    CtyNumber(),
    CtyBool(),
    CtyList(CtyString()),
    CtyMap(CtyNumber()),
    CtyObject({
        "name": CtyString(),
        "tags": CtyList(CtyString()),
        "config": CtyMap(CtyBool())
    }),
    CtyTuple((CtyString(), CtyNumber(), CtyBool())),
    CtyDynamic(),
    CtyObject({"optional_attr": CtyString()}, optional_attributes={"optional_attr"})
]

print("--- Type Serialization and Deserialization Roundtrip ---")
for i, original_type_instance in enumerate(types_to_roundtrip):
    print(f"\nTest Case {i+1}:")
    print(f"  Original Type : {original_type_instance}")

    # 1. Marshal the CtyType instance to a dictionary
    marshaled_dict = marshal_type(original_type_instance)
    print(f"  Marshaled Dict: {marshaled_dict}") # This dict is JSON-friendly

    # 2. Unmarshal the dictionary back to a CtyType instance
    unmarshaled_type_instance = unmarshal_type(marshaled_dict)
    print(f"  Unmarshaled Type: {unmarshaled_type_instance}")

    # 3. Verify that the original and unmarshaled types are equivalent
    # CtyType instances should have an .equals() method or support == for equality.
    are_equal = original_type_instance.equals(unmarshaled_type_instance) if hasattr(original_type_instance, 'equals') else original_type_instance == unmarshaled_type_instance
    print(f"  Types are equivalent after roundtrip? {are_equal}")
    assert are_equal, f"Type roundtrip failed for {original_type_instance}"

print("\nAll type serialization roundtrips successful! 🎉")

# Depy: Packing and unpacking your type blueprints like a pro architect! 📐📦
```

## Classifying Types: `classify_type` 🏷️📊

Sometimes, you don't need all the nitty-gritty details of a type, but just its general category. Is it a primitive? A list? An object? `classify_type` helps you with exactly this.

-   **`classify_type(type_instance: CtyType) -> TypeCategory`**: Takes a `CtyType` instance and returns an enumeration member (or a string) representing its broad category. Common categories might include:
    -   `PRIMITIVE` (for `CtyString`, `CtyNumber`, `CtyBool`)
    -   `LIST`
    -   `MAP`
    -   `SET`
    -   `OBJECT`
    -   `TUPLE`
    -   `DYNAMIC` (for `CtyDynamic`)

*(The exact `TypeCategory` enum members/string values depend on the `pyvider.cty` implementation. We'll assume an enum `TypeCategory` for this example.)*

**Code Example:**

```python
# example_classify_type.py
from pyvider.cty import (
    CtyString, CtyNumber, CtyBool, CtyList, CtyMap, CtySet,
    CtyObject, CtyTuple, CtyDynamic, CtyType,
    # classify_type and TypeCategory are often exposed directly via pyvider.cty
    classify_type, TypeCategory # Assuming TypeCategory enum exists
)
# If not, adjust import: from pyvider.cty.conversion import classify_type, TypeCategory

types_to_classify: list[CtyType] = [
    CtyString(), CtyNumber(), CtyBool(),
    CtyList(CtyString()),
    CtyMap(CtyNumber()),
    CtySet(CtyBool()),
    CtyObject({"id": CtyString()}),
    CtyTuple((CtyString(), CtyNumber())),
    CtyDynamic()
]

print("--- Type Classification Examples ---")
for i, type_instance in enumerate(types_to_classify):
    category = classify_type(type_instance)
    # Assuming TypeCategory is an enum, .name gives the string representation of the enum member
    category_name = category.name if hasattr(category, 'name') else str(category)
    print(f"  Type Instance {i+1}: {type_instance}")
    print(f"    Classified as: {category_name}\n")

# Example usage in a function
def describe_type(some_type: CtyType) -> None:
    classification = classify_type(some_type)
    print(f"Describing type: {some_type}")
    if classification == TypeCategory.PRIMITIVE:
        print("  It's a fundamental building block!")
    elif classification == TypeCategory.LIST:
        list_type = typing.cast(CtyList, some_type) # For type hinting
        print(f"  It's a list holding elements of type: {list_type.element_type}")
    elif classification == TypeCategory.OBJECT:
        obj_type = typing.cast(CtyObject, some_type) # For type hinting
        print(f"  It's an object with attributes: {list(obj_type.attribute_types.keys())}")
    else:
        print(f"  It's a {classification.name if hasattr(classification, 'name') else classification} type.")

import typing # For cast
print("--- Using classification in a function ---")
describe_type(CtyList(CtyNumber()))
describe_type(CtyObject({"name": CtyString(), "active": CtyBool()}))
describe_type(CtyString())


# Depy: Sorting your types into neat little boxes. So organized! 🗂️🧐
```

## Parsing and Standardizing Type Strings (Briefly Noted) 📝⚙️

Libraries like `pyvider.cty` sometimes include utilities for working with string representations of types, especially if they support defining types from configuration files or simplified string notations. Two such utilities often found are:

-   **`parse_collection_type(type_str: str) -> tuple[str, str | None]`** (or similar signature):
    This function would typically take a string like `"list(string)"` or `"map(number)"` and parse it into its constituent parts, for example, `("list", "string")` or `("map", "number")`. This can be a first step in converting a string-defined type into a `CtyType` instance.

-   **`standardize_type_string(type_str: str) -> str`**:
    This function would take a potentially loosely formatted type string (e.g., `"  List < Number > "`) and convert it into a canonical or standardized form (e.g., `"list(number)"`). This is useful for ensuring consistency when dealing with type strings from various sources.

**Conceptual Usage (Illustrative - check `pyvider.cty` for exact behavior and availability):**

```python
# example_string_utils.py
from pyvider.cty import (
    parse_collection_type, standardize_type_string # Assuming direct import
)

# Illustrative example for parse_collection_type
# Actual behavior/signature might vary in pyvider.cty
print("--- Conceptual: parse_collection_type ---")
try:
    parsed_list = parse_collection_type("list(string)")
    print(f"Parsed 'list(string)': {parsed_list}") # e.g., ('list', 'string')
    parsed_map = parse_collection_type("map(number)")
    print(f"Parsed 'map(number)': {parsed_map}")   # e.g., ('map', 'number')
except NotImplementedError:
    print("parse_collection_type example skipped (may not be fully implemented/exposed as assumed).")
except Exception as e:
    print(f"Error in parse_collection_type example: {e}")


# Illustrative example for standardize_type_string
print("\n--- Conceptual: standardize_type_string ---")
try:
    standardized = standardize_type_string("  Map< Number > ")
    print(f"Standardized '  Map< Number > ': '{standardized}'") # e.g., 'map(number)'
    standardized_primitive = standardize_type_string(" String ")
    print(f"Standardized ' String ': '{standardized_primitive}'") # e.g., 'string'
except NotImplementedError:
    print("standardize_type_string example skipped (may not be fully implemented/exposed as assumed).")
except Exception as e:
    print(f"Error in standardize_type_string example: {e}")

# Depy: Tidying up those type strings! Even type definitions like a bit of sparkle. ✨🧹
```
These string utilities can be very helpful if you're building systems that need to interpret type information provided as text. Refer to the specific `pyvider.cty` documentation for their exact signatures, capabilities, and recommended usage patterns.

---

The `pyvider.cty.conversion` utilities provide a powerful toolkit for developers needing to perform advanced manipulations or get deeper insights into `CtyType` structures. While not always needed for basic value handling, they are invaluable for building sophisticated, type-aware applications and tools on top of `pyvider.cty`.
