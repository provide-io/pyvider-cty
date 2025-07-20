# Navigating Your Data with `CtyPath`: X Marks the Spot! 🗺️

Alright, data navigators! You've got your `CtyType` blueprints, your `CtyValue` treasure chests filled with data, and you know how to perform basic operations. But what if your treasure chest is actually a series of nested chests, like a Russian doll of data? How do you pinpoint that one specific gem 💎 deep inside? Enter `CtyPath`!

`CtyPath` is your GPS for `CtyValue` structures. It's a mechanism that allows you to define a precise "path" from the root of a complex `CtyValue` (like an object with nested lists of maps) to a specific element within it. This is incredibly important for:
-   **Extracting specific pieces of data.**
-   **Targeted updates or transformations** (though `cty` values are immutable, so this would mean creating a new value with a change at a specific path).
-   **Validating specific fields** within a larger configuration.

Think of it as shouting, "Hey `cty`, go to `config`, then find the `users` list, look at the first user, and tell me their `email`!" – but in a more structured, programmatic way.

## Constructing `CtyPath`s: Charting Your Course 🧭

A `CtyPath` is essentially a sequence of steps that tells `cty` how to traverse a `CtyValue`. The primary building blocks for these paths are:

-   **`GetAttrStep(attr_name: str)`**: Used to access an attribute of a `CtyObject` value. (e.g., `user_object.name`)
-   **`IndexStep(index: int)`**: Used to access an element at a specific index within a `CtyList` or `CtyTuple` value. (e.g., `items_list[2]`)
-   **`KeyStep(key: Any)`**: Used to access an element by its key within a `CtyMap` value. (e.g., `settings_map["timeout"]`)
    *(Note: While `KeyStep` might accept `Any` for flexibility, map keys in `cty` are typically expected to be strings for interoperability, so you'll usually use strings here.)*

You typically create a `CtyPath` by providing a list of these step objects to its constructor.

```python
# example_construct_path.py
from pyvider.cty import CtyPath
# Assuming path steps are importable from pyvider.cty.path or similar
# If they are directly under pyvider.cty, adjust the import.
from pyvider.cty.path import GetAttrStep, IndexStep, KeyStep

# Path to an attribute "username" in an object
# Equivalent to: some_object.username
path_to_username = CtyPath([GetAttrStep("username")])
print(f"Path to username: {path_to_username}")

# Path to index 2 of a list/tuple
# Equivalent to: some_list[2]
path_to_index_2 = CtyPath([IndexStep(2)])
print(f"Path to index 2: {path_to_index_2}")

# Path to key "api_key" in a map
# Equivalent to: some_map["api_key"]
path_to_api_key = CtyPath([KeyStep("api_key")])
print(f"Path to key 'api_key': {path_to_api_key}")

# A more complex, combined path: user.addresses[0].details["zip_code"]
# This would navigate:
# 1. Attribute "addresses" of an object.
# 2. Index 0 of the resulting list/tuple.
# 3. Attribute "details" of that element (if it's an object).
# 4. Key "zip_code" of the resulting map.
complex_path = CtyPath([
    GetAttrStep("addresses"), # e.g., user.addresses
    IndexStep(0),           # e.g., user.addresses[0]
    GetAttrStep("details"),   # e.g., user.addresses[0].details
    KeyStep("zip_code")       # e.g., user.addresses[0].details["zip_code"]
])
print(f"Complex path (user.addresses[0].details[\"zip_code\"]): {complex_path}")

# Depy: Plotting paths like a cartographer of code! ✍️🗺️
```
**A Note on Path Creation**: While programmatic construction using steps is fundamental, some systems provide helper functions or even string parsing (e.g., `CtyPath.fromString("user.addresses[0].details['zip_code']")`) for more convenient path creation. Check the `pyvider.cty` specifics if such helpers are available, as they can be more user-friendly for common cases. For now, we're focusing on the explicit step-by-step construction.

## Applying Paths to `CtyValue`s: Reaching Your Destination 🎯

Once you have a `CtyPath`, you can use it to retrieve a value from within a `CtyValue` structure using the `apply_path` method:

`destination_value: CtyValue = my_path.apply_path(root_value: CtyValue)`

This method traverses the `root_value` according to the steps defined in `my_path`. If successful, it returns the `CtyValue` found at the destination.

**Error Handling and Special Cases**:
-   **Path Not Found**: If any step in the path cannot be completed (e.g., an attribute doesn't exist, an index is out of bounds, a key is missing), `apply_path` will typically raise an error (e.g., `CtyPathError`, `KeyError`, `IndexError`, or similar).
-   **Encountering an Unknown Value**: If `apply_path` encounters a `CtyValue` that `.is_unknown` at any point *along* the path (not necessarily the final target), the operation short-circuits, and the result is a `CtyValue.unknown()` of the type that *would have been* at the destination. The unknown-ness propagates.
-   **Encountering a Null Value**: If `apply_path` attempts to traverse *through* a `CtyValue` that `.is_null` (e.g., trying to get an attribute from a null object, or an index from a null list), it will usually raise an error. You can't get something from nothing! However, if the null value *is* the destination of the path, then that null value is returned successfully.

```python
# example_apply_path_value.py
from pyvider.cty import (
    CtyObject, CtyList, CtyMap, CtyString, CtyNumber, CtyBool,
    CtyValue, CtyPath, CtyTypeError
)
# Assuming path steps and potential CtyPathError are importable
from pyvider.cty.path import GetAttrStep, IndexStep, KeyStep
# from pyvider.cty.errors import CtyPathError # Or similar specific error

from decimal import Decimal

# --- Setup a nested structure ---
server_spec_type = CtyObject({
    "name": CtyString(),
    "ip_list": CtyList(element_type=CtyString()), # List of IP addresses
    "config": CtyMap(element_type=CtyString())  # Map for various config settings
})

server_value = CtyValue(server_spec_type, {
    "name": "PrimaryServer-01",
    "ip_list": ["192.168.1.10", "10.0.0.5"],
    "config": {"region": "us-east-1", "status_check_url": "/healthz"}
})

# --- Successful Path Applications ---
# Path to server_value.ip_list[1]
path_to_second_ip = CtyPath([GetAttrStep("ip_list"), IndexStep(1)])
second_ip_value = path_to_second_ip.apply_path(server_value)
print(f"Value at '.ip_list[1]': '{second_ip_value.value}' (Type: {second_ip_value.type})")

# Path to server_value.config["status_check_url"]
path_to_health_url = CtyPath([GetAttrStep("config"), KeyStep("status_check_url")])
health_url_value = path_to_health_url.apply_path(server_value)
print(f"Value at '.config[\"status_check_url\"]': '{health_url_value.value}' (Type: {health_url_value.type})")

# --- Path leading to a non-existent element ---
path_to_missing_key = CtyPath([GetAttrStep("config"), KeyStep("non_existent_key")])
try:
    missing_value = path_to_missing_key.apply_path(server_value)
    print(f"This shouldn't print: {missing_value}")
except Exception as e: # Replace with specific CtyPathError, KeyError etc.
    print(f"Error applying path to missing key: {e} (Expected!)")

# --- Path encountering an Unknown value ---
list_of_strings_type = CtyList(element_type=CtyString())
unknown_ip_list_server_value = CtyValue(server_spec_type, {
    "name": "ServerWithUnknownIPs",
    "ip_list": CtyValue.unknown(list_of_strings_type), # The ip_list itself is unknown
    "config": {"region": "eu-west-1"}
})
# path_to_second_ip still targets .ip_list[1]
result_from_unknown_path = path_to_second_ip.apply_path(unknown_ip_list_server_value)
print(f"\nPath through unknown list: {result_from_unknown_path}")
print(f"  IsUnknown: {result_from_unknown_path.is_unknown}, Type (of the unknown): {result_from_unknown_path.type}")
# The type should be CtyString, as that's the element type of ip_list.

# --- Path encountering a Null value to traverse through ---
null_ip_list_server_value = CtyValue(server_spec_type, {
    "name": "ServerWithNullIPs",
    "ip_list": CtyValue.null(list_of_strings_type), # ip_list is null
    "config": {"region": "ap-south-1"}
})
try:
    print("\nAttempting to apply path through a null list:")
    path_to_second_ip.apply_path(null_ip_list_server_value)
except Exception as e: # Replace with specific error like "cannot traverse null value"
    print(f"Error applying path through null list: {e} (Expected!)")

# --- Path where the destination IS null (but path itself is valid) ---
server_with_null_config_val = CtyValue(server_spec_type, {
    "name": "ServerWithNullConfig",
    "ip_list": [],
    "config": CtyValue.null(CtyMap(element_type=CtyString())) # The config map itself is null
})
path_to_config = CtyPath([GetAttrStep("config")])
null_config_result = path_to_config.apply_path(server_with_null_config_val)
print(f"\nPath to a null config map: {null_config_result}")
print(f"  Is it null? {null_config_result.is_null()}, Type: {null_config_result.type}")


# Depy: "Are we there yet?" - CtyPath, probably, as it navigates your data. 📍➡️📦
```

## Applying Paths to `CtyType`s: What *Kind* of Treasure? 📜

Beyond just getting values, `CtyPath` can also tell you the `CtyType` of the data that *would be* at the end of a path, without needing an actual `CtyValue`. This is done using the `apply_path_type` method:

`destination_type: CtyType = my_path.apply_path_type(root_type: CtyType)`

This is super useful for:
-   **Schema Introspection**: Understanding the structure of your data types.
-   **Static Validation**: Checking if a path is valid for a given type structure *before* you even have data.
-   **Tooling**: Building tools that need to reason about data structures.

**Error Handling**: If the path is invalid for the given `root_type` (e.g., trying `GetAttrStep` on a `CtyList` type, or an `IndexStep` on a `CtyObject` type where the attribute isn't a list), this method will raise an error.

```python
# example_apply_path_type.py
from pyvider.cty import (
    CtyObject, CtyList, CtyMap, CtyString, CtyNumber, CtyBool,
    CtyValue, CtyPath, CtyTypeError
)
from pyvider.cty.path import GetAttrStep, IndexStep, KeyStep
# from pyvider.cty.errors import CtyPathError # Or similar specific error

# Define a type structure
complex_data_type = CtyObject({
    "id": CtyString(),
    "user_settings": CtyMap(element_type=CtyBool()),
    "history": CtyList(
        CtyObject({
            "timestamp": CtyNumber(),
            "action": CtyString()
        })
    )
})

# Path to .user_settings["enable_notifications"]
path_to_setting = CtyPath([GetAttrStep("user_settings"), KeyStep("enable_notifications")])
setting_type = path_to_setting.apply_path_type(complex_data_type)
print(f"Type at '.user_settings[\"enable_notifications\"]': {setting_type}") # Should be CtyBool

# Path to .history[0].action
path_to_first_action = CtyPath([
    GetAttrStep("history"),
    IndexStep(0),         # Gets the type of an element in the list (the CtyObject)
    GetAttrStep("action") # Gets the type of the "action" attribute from that CtyObject
])
action_type = path_to_first_action.apply_path_type(complex_data_type)
print(f"Type at '.history[0].action': {action_type}") # Should be CtyString

# --- Path invalid for the type structure ---
# Trying to apply an IndexStep to "id" which is a CtyString
path_invalid_on_string = CtyPath([GetAttrStep("id"), IndexStep(0)])
try:
    print("\nAttempting to apply an invalid path (IndexStep on CtyString type):")
    path_invalid_on_string.apply_path_type(complex_data_type)
except Exception as e: # Replace with specific error for invalid path on type
    print(f"Error applying invalid path to type: {e} (Expected!)")

# Trying to get a non-existent attribute from the root type
path_to_non_existent_attr = CtyPath([GetAttrStep("non_existent_attribute")])
try:
    print("\nAttempting to apply path with non-existent attribute on type:")
    path_to_non_existent_attr.apply_path_type(complex_data_type)
except Exception as e: # Replace with specific error
    print(f"Error applying non-existent attribute path to type: {e} (Expected!)")

# Depy: Predicting the type of data you'll find, even before the data exists! Psychic powers, activate! 🔮✨
```

---

Mastering `CtyPath` is key to effectively working with complex, nested data structures in `pyvider.cty`. Whether you're digging for specific values or just trying to understand the shape of your types, paths are your indispensable guide. Happy navigating!
