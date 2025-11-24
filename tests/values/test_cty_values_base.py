#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TODO: Add module docstring."""

import pytest

from pyvider.cty import CtyBool, CtyList, CtyMap, CtyNumber, CtyString, CtyValue
from pyvider.cty.marks import CtyMark


class TestCtyValueBasicOperations:
    def test_value_creation_and_access(self) -> None:
        str_type = CtyString()
        str_val = str_type.validate("hello")
        assert str_val.value == "hello", f"Expected 'hello', but got {str_val.value}"
        assert str_val.type.equal(str_type), "Value type should equal the original string type"

    def test_value_marks(self) -> None:
        num_val = CtyNumber().validate(123)
        marked_val = num_val.mark(CtyMark("sensitive"))
        assert not num_val.has_mark(CtyMark("sensitive")), "Original value should not have sensitive mark"
        assert marked_val.has_mark(CtyMark("sensitive")), "Marked value should have sensitive mark"
        unmarked_val, marks = marked_val.unmark()
        assert not unmarked_val.has_mark(CtyMark("sensitive")), "Unmarked value should not have sensitive mark"
        assert CtyMark("sensitive") in marks, "Sensitive mark should be in extracted marks list"


class TestCtyValueEquality:
    def test_equality_simple_values(self) -> None:
        assert CtyString().validate("a") == CtyString().validate("a"), "Equal string values should be equal"
        assert CtyString().validate("a") != CtyString().validate("b"), (
            "Different string values should not be equal"
        )
        assert CtyString().validate("a") != CtyNumber().validate(1), (
            "String and number values should not be equal"
        )

    def test_equality_with_marks(self) -> None:
        val1 = CtyString().validate("a").mark(CtyMark("foo"))
        val2 = CtyString().validate("a").mark(CtyMark("foo"))
        val3 = CtyString().validate("a").mark(CtyMark("bar"))
        assert val1 == val2, "Values with same content and marks should be equal"
        assert val1 != val3, "Values with same content but different marks should not be equal"

    def test_equality_null_unknown(self) -> None:
        assert CtyValue.null(CtyString()) == CtyValue.null(CtyString()), (
            "Null values of same type should be equal"
        )
        assert CtyValue.unknown(CtyString()) == CtyValue.unknown(CtyString()), (
            "Unknown values of same type should be equal"
        )
        assert CtyValue.null(CtyString()) != CtyValue.unknown(CtyString()), (
            "Null and unknown values should not be equal"
        )


class TestCtyValueDunderMethods:
    def test_contains(self) -> None:
        list_val = CtyList(element_type=CtyString()).validate(["a", "b"])
        assert CtyString().validate("a") in list_val, "List should contain 'a'"
        assert CtyString().validate("c") not in list_val, "List should not contain 'c'"

    def test_bool(self) -> None:
        assert bool(CtyString().validate("a")), "Non-empty string value should be truthy"
        assert not bool(CtyValue.null(CtyString())), "Null value should be falsy"
        assert not bool(CtyValue.unknown(CtyString())), "Unknown value should be falsy"

    def test_len(self) -> None:
        list_val = CtyList(element_type=CtyString()).validate(["a", "b"])
        assert len(list_val) == 2, f"Expected length 2, but got {len(list_val)}"

    def test_len_on_null_unknown(self) -> None:
        assert len(CtyValue.null(CtyList(element_type=CtyString()))) == 0, "Null list should have length 0"
        with pytest.raises(TypeError):
            len(CtyValue.unknown(CtyList(element_type=CtyString())))

    def test_iter(self) -> None:
        list_val = CtyList(element_type=CtyString()).validate(["a", "b"])
        assert [v.value for v in list_val] == ["a", "b"], (
            f"Expected ['a', 'b'], but got {[v.value for v in list_val]}"
        )

    def test_getitem(self) -> None:
        list_val = CtyList(element_type=CtyString()).validate(["a", "b"])
        assert list_val[0].value == "a", f"Expected 'a' at index 0, but got {list_val[0].value}"
        map_val = CtyMap(element_type=CtyString()).validate({"name": "Alice"})
        assert map_val["name"].value == "Alice", (
            f"Expected 'Alice' for key 'name', but got {map_val['name'].value}"
        )


class TestCtyValueOtherMethods:
    def test_hash(self) -> None:
        val = CtyString().validate("a")
        assert isinstance(hash(val), int), f"Expected hash to be int, but got {type(hash(val))}"
        with pytest.raises(TypeError):
            hash(CtyList(element_type=CtyString()).validate(["a"]))

    def test_raw_value(self) -> None:
        val = CtyString().validate("a")
        assert val.raw_value == "a", f"Expected raw value 'a', but got {val.raw_value}"
        with pytest.raises(ValueError):
            _ = CtyValue.unknown(CtyString()).raw_value

    def test_is_true_false(self) -> None:
        assert CtyBool().validate(True).is_true(), "True value should be true"
        assert not CtyBool().validate(True).is_false(), "True value should not be false"
        assert CtyBool().validate(False).is_false(), "False value should be false"
        assert not CtyBool().validate(False).is_true(), "False value should not be true"

    def test_is_empty(self) -> None:
        assert CtyList(element_type=CtyString()).validate([]).is_empty(), "Empty list should be empty"
        assert not CtyList(element_type=CtyString()).validate(["a"]).is_empty(), (
            "Non-empty list should not be empty"
        )
        assert not CtyString().validate("a").is_empty(), "Non-empty string should not be empty"


# 🌊🪢🔚
