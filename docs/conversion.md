# Type Conversion Utilities: Advanced Type Wrangling 🛠️

Welcome, `cty` connoisseurs, to the engine room! The `pyvider.cty.conversion` module offers tools for working with `CtyType` definitions and their string representations. These utilities can be helpful for:

-   **Schema Introspection**: Understanding the structure of your types from their string forms.
-   **Custom Tooling**: Creating your own libraries or tools that interoperate with or extend `pyvider.cty`.
-   **Working with Type Strings**: Parsing or standardizing type information provided as text.

## Classifying Type Strings: `classify_type` _from `pyvider.cty.conversion`_ 🏷️📊

When you have a string representation of a `cty` type (e.g., `"string"`, `"list(number)"`), `classify_type` can tell you its general category.

-   **`classify_type(type_str: str) -> TypeCategory`**: Takes a type string and returns a `TypeCategory` enum member. The `TypeCategory` enum (also from `pyvider.cty.conversion`) includes members like:
    -   `TypeCategory.PRIMITIVE` (for `"string"`, `"number"`, `"bool"`, `"dynamic"`)
    -   `TypeCategory.COLLECTION` (for `"list(...)"`, `"map(...)"`, `"set(...)"`)
    -   `TypeCategory.STRUCTURED` (Note: `classify_type` based on `format.py` may not yet distinguish this from `UNKNOWN` for complex object/tuple strings directly, it primarily identifies primitive and basic collection string patterns.)
    -   `TypeCategory.UNKNOWN` (for unrecognized type string patterns)

**Code Example:**

```python
# example_classify_type.py
from pyvider.cty import CtyString, CtyNumber, CtyBool, CtyList, CtyMap, CtySet, CtyObject, CtyTuple, CtyDynamic
from pyvider.cty.conversion import classify_type, TypeCategory # Correct import
import typing # For cast

# Type strings for classification
type_strings_to_classify: list[str] = [
    "string", "number", "bool", "dynamic",
    "list(string)", "map(number)", "set(bool)",
    "object({name=string})",
    "tuple([string,number])",
    "invalidtype"
]

print("--- Type String Classification Examples ---")
for i, type_s in enumerate(type_strings_to_classify):
    from pyvider.cty.conversion import standardize_type_string # Import inside loop for example clarity
    standardized_type_s = standardize_type_string(type_s)

    category = classify_type(standardized_type_s)
    category_name = category.value

    print(f"  Type String {i+1}: '{type_s}' (Standardized: '{standardized_type_s}')")
    print(f"    Classified as: {category_name}\n")

def describe_type_str(type_str: str) -> None:
    from pyvider.cty.conversion import standardize_type_string, parse_collection_type # Local import for example

    standardized_type_s = standardize_type_string(type_str)
    classification = classify_type(standardized_type_s)
    print(f"Describing type string: '{type_str}' (Standardized: '{standardized_type_s}')")

    if classification == TypeCategory.PRIMITIVE:
        print("  It's a primitive type string!")
    elif classification == TypeCategory.COLLECTION:
        try:
            coll_kind, el_type_str = parse_collection_type(standardized_type_s)
            print(f"  It's a {coll_kind} collection string, with element type string: '{el_type_str}'")
        except ValueError as e:
            print(f"  It's a collection string, but element type parsing failed: {e}")
    else:
        print(f"  It's a {classification.value} type string.")

print("--- Using classification in a function (with type strings) ---")
describe_type_str("list(number)")
describe_type_str("object({name=string,active=bool})")
describe_type_str("string")
describe_type_str("invalid(type)")
```

## Working with Type Strings 📝⚙️

The `pyvider.cty.conversion` module also provides utilities for normalizing and parsing type strings. This can be useful if you are receiving type information as text from external sources.

### `standardize_type_string(type_str: str | None) -> str`
This function takes a type string and converts it into a canonical form. For example, it might convert `"  List < Number > "` to `"list(number)"`. It handles various quoting and spacing inconsistencies. If `None` is passed, it typically returns `"dynamic"`.

### `parse_collection_type(type_str: str) -> tuple[str, str]`
This function parses a collection type string (like `"list(string)"` or `"map(number)"`) into its base collection kind and its element type string. For example, `"list(string)"` would be parsed to `("list", "string")`.

**Code Example:**

```python
# example_string_utils.py
from pyvider.cty.conversion import standardize_type_string, parse_collection_type, classify_type, TypeCategory

print("--- standardize_type_string Examples ---")
strings_to_standardize = [
    "  String  ",
    "\'list(NUMBER)\'",
    '" map ( string ) "',
    "set( bool )",
    "dynamic",
    None # Example with None
]
for s in strings_to_standardize:
    standardized = standardize_type_string(s)
    print(f"Original: '{s}' -> Standardized: '{standardized}'")

print("\n--- parse_collection_type Examples ---")
collection_strings = [
    "list(string)",
    "map(number)",
    "set(bool)",
    "list(map(string))"
]
for cs in collection_strings:
    try:
        kind, element_type_str = parse_collection_type(cs)
        print(f"Original: '{cs}' -> Kind: '{kind}', Element Type Str: '{element_type_str}'")
    except ValueError as e:
        print(f"Error parsing '{cs}': {e}")

standardized_nested = standardize_type_string("list( map(string) )")
kind, element_type_str = parse_collection_type(standardized_nested)
print(f"Standardized Nested: '{standardized_nested}' -> Kind: '{kind}', Element Type Str: '{element_type_str}'")

if classify_type(element_type_str) == TypeCategory.COLLECTION:
    sub_kind, sub_element_type_str = parse_collection_type(element_type_str)
    print(f"  Sub-parsed: Kind: '{sub_kind}', Element Type Str: '{sub_element_type_str}'")
```

## Regarding `marshal_type` and `unmarshal_type` (from `pyvider.cty.conversion.marshal`)

The `pyvider.cty.conversion.marshal` module contains `marshal_type` and `unmarshal_type`. These are specialized for encoding `CtyType` instances into a compact **byte string** format (often quoted, e.g., `b'"string"'`, `b'"list(number)"'`) suitable for the Terraform plugin protocol, and decoding them back.

- `marshal_type(type_obj: CtyType | str) -> bytes`
- `unmarshal_type(type_bytes: bytes) -> CtyType`

These functions **do not** convert `CtyType` instances to or from general-purpose Python dictionaries or JSON structures representing the type's full schema details. If you need such a representation, you would typically build it by introspecting the `CtyType` instance's attributes (e.g., `.element_type` for lists, `.attribute_types` for objects, etc.) or look for other specific utilities if available.

---

The utilities in `pyvider.cty.conversion` (from `format.py`) are primarily for handling textual representations of types. For direct type-to-bytes encoding for wire protocols, see `pyvider.cty.conversion.marshal`.
