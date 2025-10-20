> ⚠️ **Note:** This is a preview release of \`pyvider.cty\`. The API may change, and it is not yet recommended for production use without thorough testing.

# `pyvider.cty` - Type System Magic ✨

Well hello there, data wrangler! 👋 Ever found yourself wrestling with Python dictionaries and lists, wishing they had a little more... backbone? A bit more predictability? Enter `pyvider.cty`, your new best friend for taming the wild world of structured data in Python.

Think of `pyvider.cty` as the Pythonic cousin of the very capable `go-cty` library from the land of Go. Its mission, should you choose to accept it, is to provide a robust system for representing and manipulating structured data with the glorious safety net of types. Why is this a big deal, you ask? Imagine trying to build a skyscraper with LEGOs of unknown shapes and sizes – chaotic, right? `pyvider.cty` gives you precisely engineered building blocks.

**Benefits include:**
*   **Type Safety:** Catch errors early! Know that your data structures are what you expect them to be. No more runtime surprises when a "number" turns out to be a "string_that_looks_like_a_number_but_isnt". 😉
*   **Clarity:** Define complex data structures in a clear, unambiguous way. Your future self (and your colleagues) will thank you.
*   **Interoperability:** Designed to play nicely with common serialization formats like JSON and Msgpack.
*   **Power Features:** Handle special cases like unknown or null values with grace, and track metadata with "marks".

## Core Concepts 🕵️‍♀️

Let's peek under the hood, shall we?

*   **`CtyType` (The Blueprint 📜):** This is where you define the *shape* of your data. Is it a number? A string? A list of objects, each with a specific set of attributes? `CtyType` is your blueprint. For example, you might define a type for "a list of strings" or "an object with a 'name' (string) and 'age' (number) attribute".

*   **`CtyValue` (The Actual Building 🧱):** If `CtyType` is the blueprint, `CtyValue` is the actual structure built according to that blueprint. It holds your data, and it *knows* its own type. This means a `CtyValue` created from a "number" type can only hold numbers. Try to sneak in a string, and `pyvider.cty` will politely (or not so politely 🤨) refuse.

*   **Immutability (Set in Stone... Mostly 🗿):** Once a `CtyValue` is created, it generally cannot be changed directly. This might sound restrictive, but it's a powerful feature for predictability and avoiding accidental data corruption. If you need to "change" something, you typically create a *new* value based on the old one.

*   **Unknown & Null Values (The Mysteries ❓🤷):**
    *   **Null:** Represents an intentionally absent value. It's like saying, "There's definitely nothing here, and I mean it."
    *   **Unknown:** Represents a value that *will* be known eventually, but isn't right now. Think of it as a placeholder: "Hold this spot, the real value is coming later!" This is super useful in systems where data is resolved in stages.

*   **Marks (Sticky Notes 📝):** Imagine you have a piece of data, and you want to attach some extra information to it *without* changing the data itself. That's what Marks are for! They're like little sticky notes you can put on your `CtyValue`s to carry along context or metadata.

## Overview of Available Types 🗂️

`pyvider.cty` comes with a handy selection of types to model your data:

*   **Primitive Types:** The basic building blocks.
    *   `String`: For text, naturally.
    *   `Number`: For your integers and floats. It's smart enough to handle both.
    *   `Bool`: For good old `True` or `False`.
*   **Collection Types:** For grouping things together.
    *   `List`: An ordered sequence of elements, all of the same type.
    *   `Set`: An unordered collection of unique elements, all of the same type.
    *   `Map`: A collection of key-value pairs, where keys are strings and values are all of the same type.
*   **Structural Types:** For more complex arrangements.
    *   `Object`: A collection of named attributes, each with its own defined type. Like a custom blueprint for a specific kind of thing.
    *   `Tuple`: An ordered sequence of elements, where each element can have a *different* type.
*   **Special Types:**
    *   `DynamicPseudoType`: A special type that acts as a placeholder when a type isn't known yet, but will be determined later. It's the "anything goes" type, but use it wisely!

## Key Functionalities Overview 🛠️

Beyond just defining types and values, `pyvider.cty` helps you work with them:

*   **Path Navigation:** Access nested data within complex structures using a clear path-based syntax. No more endless `['key']['another_key'][0]['yet_another_key']`!
*   **Serialization/Deserialization:** Easily convert your `CtyValue`s to and from standard formats:
    *   **JSON:** The web's favorite data format.
    *   **Msgpack:** A more compact binary serialization format.

## Quick Start Example 🚀

Enough talk! Let's see some action. Here's a snippet to whet your appetite. Imagine this is in a Python file (but it's right here in your README!):

```python
# No official header/footer needed for a README code block,
# but let's imagine this is how you'd structure a real .py file.
# #!/usr/bin/env python3
# -*- coding: utf-8 -*-
# src/pyvider/cty/examples/simple_usage.py
# Copyright (C) 2024 Your Name Here
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the MIT License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# MIT License for more details.

"""A simple example demonstrating pyvider.cty basics."""

from pyvider.cty import (
    CtyObject,
    CtyString,
    CtyNumber,
    CtyList,
    CtyValue,
)

def main() -> None:
    """Demonstrates basic pyvider.cty type and value creation."""

    # 1. Define a Type (the blueprint)
    # Let's define a type for a user profile: an object with a
    # 'name' (string), 'age' (number), and 'hobbies' (list of strings).
    user_profile_type = CtyObject({
        "name": CtyString,
        "age": CtyNumber,
        "hobbies": CtyList(element_type=CtyString),
    })

    print(f"Defined type: {user_profile_type}")

    # 2. Create a Value (the actual data, matching the blueprint)
    # This data MUST conform to user_profile_type.
    user_data = CtyValue.object(
        user_profile_type, # Specify the type this value conforms to
        {
            "name": CtyValue.string("Alice"),
            "age": CtyValue.number(30),
            "hobbies": CtyValue.list_of_strings(CtyList(element_type=CtyString), ["reading", "hiking"]),
        }
    )

    print(f"Created value: {user_data}")

    # 3. Accessing Content (with type safety!)
    # You can access attributes using dictionary-like notation.
    # The great thing is, cty knows the type of each attribute.

    name_value = user_data["name"]
    age_value = user_data["age"]
    hobbies_value = user_data["hobbies"]

    print(f"User's Name: {name_value.as_string()}, Type: {name_value.ty}")
    print(f"User's Age: {age_value.as_number()}, Type: {age_value.ty}")
    print(f"User's Hobbies: {hobbies_value.as_list_of_strings()}, Type: {hobbies_value.ty}")

    # What if you try to create data that *doesn't* match the type?
    # For example, putting a number where a string is expected for 'name'.
    # This would typically raise an error during value creation (not shown here for brevity,
    # but rest assured, cty is watching! 🧐).

if __name__ == "__main__":
    main()

# For a real .py file, you might have:
# pylint: disable=all
# Depy: ✨ PREPARE TO BE DAZZLED ✨
# Depy: 🚀 THIS IS HOW WE ROLL 🚀
```

And there you have it! A whirlwind tour of `pyvider.cty`. We hope this helps you build more robust, predictable, and delightful Python applications. Dive in, explore, and may your data always be well-typed! 🎉


## Known Limitations ⚠️

As of the current version, please be aware of the following limitations:

*   **MessagePack Cross-Language Compatibility:** There are known issues where \\`go-cty\\` may fail to deserialize certain MessagePack structures generated by \\`pyvider.cty\\` (and vice-versa). For critical cross-language communication, JSON is currently more reliable.
*   **Python Version Requirement:** This library currently requires Python 3.13 or newer.
*   **Performance:** Comprehensive performance benchmarks have not yet been conducted. While functional, performance for very large or deeply nested data structures is not yet optimized.
*   **Incomplete Type Parsing in Codec:** The \\`codec.py\\` module's type string parsing capabilities, while functional for common cases, may not cover all esoteric or highly complex type string definitions.
