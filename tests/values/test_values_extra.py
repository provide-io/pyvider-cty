#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


import pytest

from pyvider.cty import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyObject,
    CtySet,
    CtyString,
    CtyTuple,
    CtyValue,
)


def test_value_eq() -> None:
    assert CtyString().validate("a") != "a"


def test_value_contains() -> None:
    assert "a" in CtyString().validate("a")
    assert "b" not in CtyString().validate("a")
    assert not CtyValue.unknown(CtyString()).__contains__("a")


def test_value_bool() -> None:
    assert bool(CtyString().validate("a"))
    assert not bool(CtyValue.null(CtyString()))
    assert not bool(CtyValue.unknown(CtyString()))
    assert bool(CtyValue(CtyDynamic(), CtyString().validate("a")))


def test_value_len() -> None:
    with pytest.raises(TypeError):
        len(CtyValue.unknown(CtyString()))
    assert len(CtyValue.null(CtyList(element_type=CtyString()))) == 0
    with pytest.raises(TypeError):
        len(CtyString().validate("a"))
    assert len(CtyValue(CtyDynamic(), CtyList(element_type=CtyString()).validate(["a"]))) == 1


def test_value_iter() -> None:
    with pytest.raises(TypeError):
        iter(CtyValue.unknown(CtyString()))
    assert list(iter(CtyValue.null(CtyList(element_type=CtyString())))) == []
    map_val = CtyMap(element_type=CtyString()).validate({"a": "b"})
    assert [v.value for v in iter(map_val)] == ["b"]
    with pytest.raises(TypeError):
        iter(CtyString().validate("a"))


def test_value_getitem() -> None:
    with pytest.raises(TypeError):
        CtyValue.unknown(CtyString())["a"]
    with pytest.raises(TypeError):
        CtyString().validate("a")["a"]
    with pytest.raises(TypeError):
        CtyObject({}).validate({})[1]
    list_val = CtyList(element_type=CtyString()).validate(["a", "b"])
    assert list_val[0].value == "a"
    slice_val = list_val[1:]
    assert isinstance(slice_val, CtyValue) and isinstance(slice_val.value, tuple)
    assert len(slice_val.value) == 1 and slice_val.value[0].value == "b"


def test_value_hash() -> None:
    # Test that unhashable collection types correctly raise TypeError
    with pytest.raises(TypeError):
        hash(CtyList(element_type=CtyString()).validate([]))
    with pytest.raises(TypeError):
        hash(CtySet(element_type=CtyString()).validate(set()))
    with pytest.raises(TypeError):
        hash(CtyMap(element_type=CtyString()).validate({}))
    with pytest.raises(TypeError):
        hash(CtyObject({}).validate({}))

    # NOTE: This is a known deviation from go-cty, where tuples are not hashable.
    # This is a pragmatic choice to allow `setproduct` and sets of tuples to function.
    tuple_val = CtyTuple(element_types=()).validate(())
    assert isinstance(hash(tuple_val), int)

    # Unknown values are hashable
    assert isinstance(hash(CtyValue.unknown(CtyString())), int)


def test_is_true_false_empty() -> None:
    assert CtyBool().validate(True).is_true() and not CtyBool().validate(False).is_true()
    assert not CtyBool().validate(True).is_false() and CtyBool().validate(False).is_false()
    assert CtyValue(CtyDynamic(), CtyBool().validate(True)).is_true()
    assert not CtyValue(CtyDynamic(), CtyBool().validate(False)).is_true()
    assert not CtyValue(CtyDynamic(), CtyBool().validate(True)).is_false()
    assert CtyValue(CtyDynamic(), CtyBool().validate(False)).is_false()
    assert CtyList(element_type=CtyString()).validate([]).is_empty()
    assert CtyString().validate("").is_empty()
    assert CtyMap(element_type=CtyString()).validate({}).is_empty()


def test_post_init() -> None:
    val = CtyValue(vtype=CtyString(), is_unknown=True, is_null=True)
    assert val.is_unknown and not val.is_null
    val2 = CtyValue(vtype=CtyString(), is_null=True, value="some value")
    assert val2.is_null and val2.value is None


def test_raw_value_unknown() -> None:
    with pytest.raises(ValueError):
        _ = CtyValue.unknown(CtyString()).raw_value


# 🌊🪢🔚
