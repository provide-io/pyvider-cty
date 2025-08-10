import pytest

from pyvider.cty import CtyBool, CtyList, CtyMap, CtyNumber, CtyString, CtyValue
from pyvider.cty.marks import CtyMark


class TestCtyValueBasicOperations:
    def test_value_creation_and_access(self) -> None:
        str_type = CtyString()
        str_val = str_type.validate("hello")
        assert str_val.value == "hello"
        assert str_val.type.equal(str_type)

    def test_value_marks(self) -> None:
        num_val = CtyNumber().validate(123)
        marked_val = num_val.mark(CtyMark("sensitive"))
        assert not num_val.has_mark(CtyMark("sensitive"))
        assert marked_val.has_mark(CtyMark("sensitive"))
        unmarked_val, marks = marked_val.unmark()
        assert not unmarked_val.has_mark(CtyMark("sensitive"))
        assert CtyMark("sensitive") in marks

class TestCtyValueEquality:
    def test_equality_simple_values(self) -> None:
        assert CtyString().validate("a") == CtyString().validate("a")
        assert CtyString().validate("a") != CtyString().validate("b")
        assert CtyString().validate("a") != CtyNumber().validate(1)

    def test_equality_with_marks(self) -> None:
        val1 = CtyString().validate("a").mark(CtyMark("foo"))
        val2 = CtyString().validate("a").mark(CtyMark("foo"))
        val3 = CtyString().validate("a").mark(CtyMark("bar"))
        assert val1 == val2
        assert val1 != val3

    def test_equality_null_unknown(self) -> None:
        assert CtyValue.null(CtyString()) == CtyValue.null(CtyString())
        assert CtyValue.unknown(CtyString()) == CtyValue.unknown(CtyString())
        assert CtyValue.null(CtyString()) != CtyValue.unknown(CtyString())

class TestCtyValueDunderMethods:
    def test_contains(self) -> None:
        list_val = CtyList(element_type=CtyString()).validate(["a", "b"])
        assert CtyString().validate("a") in list_val
        assert CtyString().validate("c") not in list_val

    def test_bool(self) -> None:
        assert bool(CtyString().validate("a"))
        assert not bool(CtyValue.null(CtyString()))
        assert not bool(CtyValue.unknown(CtyString()))

    def test_len(self) -> None:
        list_val = CtyList(element_type=CtyString()).validate(["a", "b"])
        assert len(list_val) == 2

    def test_len_on_null_unknown(self) -> None:
        assert len(CtyValue.null(CtyList(element_type=CtyString()))) == 0
        with pytest.raises(TypeError):
            len(CtyValue.unknown(CtyList(element_type=CtyString())))

    def test_iter(self) -> None:
        list_val = CtyList(element_type=CtyString()).validate(["a", "b"])
        assert [v.value for v in list_val] == ["a", "b"]

    def test_getitem(self) -> None:
        list_val = CtyList(element_type=CtyString()).validate(["a", "b"])
        assert list_val[0].value == "a"
        map_val = CtyMap(element_type=CtyString()).validate({"name": "Alice"})
        assert map_val["name"].value == "Alice"

class TestCtyValueOtherMethods:
    def test_hash(self) -> None:
        val = CtyString().validate("a")
        assert isinstance(hash(val), int)
        with pytest.raises(TypeError):
            hash(CtyList(element_type=CtyString()).validate(["a"]))

    def test_raw_value(self) -> None:
        val = CtyString().validate("a")
        assert val.raw_value == "a"
        with pytest.raises(ValueError):
            _ = CtyValue.unknown(CtyString()).raw_value

    def test_is_true_false(self) -> None:
        assert CtyBool().validate(True).is_true()
        assert not CtyBool().validate(True).is_false()
        assert CtyBool().validate(False).is_false()
        assert not CtyBool().validate(False).is_true()

    def test_is_empty(self) -> None:
        assert CtyList(element_type=CtyString()).validate([]).is_empty()
        assert not CtyList(element_type=CtyString()).validate(["a"]).is_empty()
        assert not CtyString().validate("a").is_empty()


# 🐍🎯🧪🪄
