#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from pyvider.cty.types.capsule import CtyCapsule


class MyCustomClass:
    pass


class AnotherCustomClass:
    pass


def test_capsule_creation() -> None:
    """Test basic creation of CtyCapsule."""
    capsule_type = CtyCapsule("MyCustom", MyCustomClass)
    assert capsule_type.name == "MyCustom"
    assert capsule_type.py_type == MyCustomClass


def test_capsule_representation() -> None:
    """Test the string representation of CtyCapsule."""
    capsule_type = CtyCapsule("MyCustom", MyCustomClass)
    assert repr(capsule_type) == "CtyCapsule(MyCustom, MyCustomClass)"


def test_capsule_equality() -> None:
    """Test equality comparisons for CtyCapsule."""
    capsule_type1 = CtyCapsule("MyCustom", MyCustomClass)
    capsule_type2 = CtyCapsule("MyCustom", MyCustomClass)
    capsule_type3 = CtyCapsule("AnotherCustom", AnotherCustomClass)
    capsule_type4 = CtyCapsule("MyCustom", AnotherCustomClass)  # Same name, different type
    capsule_type5 = CtyCapsule("AnotherCustom", MyCustomClass)  # Different name, same type

    assert capsule_type1 == capsule_type2
    assert capsule_type1 != capsule_type3
    assert capsule_type1 != "NotACapsule"
    assert capsule_type1 != capsule_type4
    assert capsule_type1 != capsule_type5


def test_capsule_hash() -> None:
    """Test hashability of CtyCapsule."""
    capsule_type1 = CtyCapsule("MyCustom", MyCustomClass)
    capsule_type2 = CtyCapsule("MyCustom", MyCustomClass)
    capsule_type3 = CtyCapsule("AnotherCustom", AnotherCustomClass)

    assert hash(capsule_type1) == hash(capsule_type2)
    assert hash(capsule_type1) != hash(capsule_type3)

    # Test that it can be used as a dictionary key
    my_dict = {capsule_type1: "value1"}
    assert my_dict[capsule_type2] == "value1"


# 🌊🪢🔚
