#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Conversion and unification: fitting a value to the type a schema declares.

Terraform configuration is written by people, so what arrives is rarely the type
a schema asks for: a number written as a string, a tuple where a list belongs, an
object where a map does. `convert` decides whether that gap can be closed and
closes it; `unify` answers the other question -- given several types, what single
type will hold all of them.
"""

from decimal import Decimal
from pathlib import Path
import sys

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from examples.example_utils import configure_for_example  # noqa: E402
from pyvider.cty import (  # noqa: E402
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
    CtyTuple,
    CtyValue,
)
from pyvider.cty.conversion import convert, unify  # noqa: E402
from pyvider.cty.exceptions import CtyConversionError  # noqa: E402

configure_for_example()

string_type = CtyString()
number_type = CtyNumber()

# --------------------------------------------------------------------------- #
# Safe conversions
# --------------------------------------------------------------------------- #

# A number reads as a string without losing anything, so this direction is
# always allowed.
as_text = convert(number_type.validate(42), string_type)
assert as_text.value == "42"

# The other direction is allowed too, but only for text that really is a number.
as_number = convert(string_type.validate("42"), number_type)
assert as_number.value == Decimal(42)

try:
    convert(string_type.validate("forty-two"), number_type)
    raise AssertionError("that is not a number")
except CtyConversionError as exc:
    assert "number" in str(exc)

# --------------------------------------------------------------------------- #
# Collections
# --------------------------------------------------------------------------- #

# A tuple is what HCL produces for a bracketed literal, and a schema almost
# always declares a list. Converting one to the other is the single most common
# conversion in a provider.
literal = CtyTuple(element_types=(number_type, number_type)).validate([1, 2])
numbers = convert(literal, CtyList(element_type=number_type))
assert [element.value for element in numbers.value] == [Decimal(1), Decimal(2)]

# Element types are converted on the way, so a tuple of numbers fits a list of
# strings.
as_strings = convert(literal, CtyList(element_type=string_type))
assert [element.value for element in as_strings.value] == ["1", "2"]

# A list converts to a set, which is where duplicates disappear.
with_duplicates = CtyList(element_type=string_type).validate(["a", "b", "a"])
unique = convert(with_duplicates, CtySet(element_type=string_type))
assert len(unique.value) == 2

# An object converts to a map when every attribute shares one type -- and the
# other way, which is how a map literal in configuration reaches a typed schema.
record = CtyObject(attribute_types={"host": string_type, "user": string_type}).validate(
    {"host": "example.com", "user": "admin"}
)
as_map = convert(record, CtyMap(element_type=string_type))
assert as_map.value["host"].value == "example.com"

# --------------------------------------------------------------------------- #
# What conversion will not do
# --------------------------------------------------------------------------- #

# Nullness is not part of a cty type, so a null still has to be *convertible*:
# "null of list(string)" is no more a string than a populated list is.
try:
    convert(CtyValue.null(CtyList(element_type=string_type)), string_type)
    raise AssertionError("a list does not become a string, null or not")
except CtyConversionError:
    pass

# Converting into `dynamic` is a no-op: it imposes no constraint, so the value
# passes through with its own type intact.
untouched = convert(number_type.validate(1), CtyDynamic())
assert untouched.type.equal(number_type)

# --------------------------------------------------------------------------- #
# Unification
# --------------------------------------------------------------------------- #

# Given several types, which one holds them all? This is what decides the element
# type of a list built from mixed values.
assert unify([number_type, number_type]).equal(number_type)

# A number and a string unify as a string, because every number reads as one.
assert unify([number_type, string_type]).equal(string_type)

# A list and a set unify as a list, because every set reads as one.
assert unify([CtyList(element_type=string_type), CtySet(element_type=string_type)]).equal(
    CtyList(element_type=string_type)
)

# Where nothing will hold both, the answer is `None` rather than a type that
# would be a lie. A caller that wants "anything" has to ask for `dynamic`
# explicitly; unification will not reach for it on their behalf.
assert unify([CtyList(element_type=string_type), CtyObject(attribute_types={"a": string_type})]) is None

# Unification is what makes a heterogeneous literal into a typed collection: the
# tuple's element types are unified, then each element is converted to the result.
mixed = CtyTuple(element_types=(number_type, string_type)).validate([1, "two"])
homogeneous = convert(mixed, CtyList(element_type=string_type))
assert [element.value for element in homogeneous.value] == ["1", "two"]

print("Conversion examples ran successfully.")

# 🌊🪢🔚
