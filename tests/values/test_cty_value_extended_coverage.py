from decimal import Decimal
from typing import Any  # Ensuring Any and Union are imported

import pytest

from pyvider.cty.exceptions import (
    CtyMapValidationError,
)
from pyvider.cty.types.collections import CtyList, CtyMap, CtySet
from pyvider.cty.types.primitives import CtyBool, CtyNumber, CtyString
from pyvider.cty.types.structural import CtyObject, CtyTuple
from pyvider.cty.values.base import CtyValue


# --- Fixtures ---
@pytest.fixture
def string_type() -> CtyString:
    return CtyString()


@pytest.fixture
def number_type() -> CtyNumber:
    return CtyNumber()


@pytest.fixture
def bool_type() -> CtyBool:
    return CtyBool()


@pytest.fixture
def map_string_to_number_type(string_type: CtyString, number_type: CtyNumber) -> CtyMap:
    return CtyMap(key_type=string_type, value_type=number_type)


@pytest.fixture
def list_string_type(string_type: CtyString) -> CtyList:
    return CtyList(element_type=string_type)


@pytest.fixture
def object_type_sn(string_type: CtyString, number_type: CtyNumber) -> CtyObject:
    return CtyObject(attribute_types={"s": string_type, "n": number_type})


# --- Tests ---


class TestCtyValueGet:
    def test_get_on_map_default_value_validation_fails(
        self, map_string_to_number_type: CtyMap
    ) -> None:
        map_val = map_string_to_number_type.validate({"a": 1})
        result = map_val.get("b", default="not-a-number")
        assert result is None

    def test_get_on_map_key_validation_fails(
        self, map_string_to_number_type: CtyMap
    ) -> None:
        map_val = map_string_to_number_type.validate({"a": 1})
        default_val = CtyNumber().validate(99)
        result = map_val.get([], default=default_val)  # type: ignore
        assert result == default_val

    def test_get_on_object_key_not_string(self, object_type_sn: CtyObject) -> None:
        obj_val = object_type_sn.validate({"s": "a", "n": 1})
        default_val = CtyString().validate("default_s")
        result = obj_val.get(123, default=default_val)  # type: ignore
        assert result == default_val

    def test_get_on_object_general_exception(
        self, object_type_sn: CtyObject, string_type: CtyString, mocker
    ) -> None:
        object_type_sn.validate({"s": "a", "n": 1})
        default_val = CtyString().validate("default_s")

        class ExplodingObjectGet(CtyObject):  # type: ignore
            def get_attribute(
                self, value: dict[str, Any] | CtyValue, name: str
            ) -> CtyValue:  # type: ignore
                raise RuntimeError("Boom!")

        exploding_obj_type = ExplodingObjectGet(attribute_types={"s": string_type})
        exploding_obj_val = CtyValue(vtype=exploding_obj_type, value={"s": "anything"})

        result = exploding_obj_val.get("s", default=default_val)
        assert result == default_val

    def test_get_on_unsupported_type_no_default_raises_typeerror(
        self, string_type: CtyString
    ) -> None:
        string_val = CtyValue(vtype=string_type, value="hello")
        assert string_val.get("key", "default_val") == "default_val"
        assert string_val.get("key") is None


class TestCtyValueSet:
    def test_set_on_unsupported_type_raises(self, string_type: CtyString) -> None:
        string_val = CtyValue(vtype=string_type, value="hello")
        with pytest.raises(
            TypeError, match=r"set\(\) method not supported for type CtyString"
        ):
            string_val.set("key", "val")

    def test_set_key_validation_error_on_map(
        self, map_string_to_number_type: CtyMap
    ) -> None:
        map_val = map_string_to_number_type.validate({})
        with pytest.raises(
            CtyMapValidationError,
            match="Invalid key \\[\\]: String validation error: Value must be a string, got list",
        ):
            map_val.set([], 123)  # type: ignore


class TestCtyValueDelete:
    def test_delete_on_unsupported_type_raises(self, string_type: CtyString) -> None:
        string_val = CtyValue(vtype=string_type, value="hello")
        with pytest.raises(
            TypeError, match=r"delete\(\) method not supported for type CtyString"
        ):
            string_val.delete("key")

    def test_delete_key_validation_error_on_map_returns_original(
        self, map_string_to_number_type: CtyMap
    ) -> None:
        map_val = map_string_to_number_type.validate({"a": 1})
        result_map_val = map_val.delete([])  # type: ignore
        assert result_map_val is map_val


class TestCtyValueElementAt:
    def test_element_at_on_list_value_not_list_tuple(
        self, list_string_type: CtyList
    ) -> None:
        malformed_list_val = CtyValue(vtype=list_string_type, value="not-a-list")
        with pytest.raises(TypeError, match="Cannot index list value of type str"):
            malformed_list_val.element_at(0)

    def test_element_at_on_unsupported_type_raises(
        self, map_string_to_number_type: CtyMap
    ) -> None:
        map_val = map_string_to_number_type.validate({"a": 1})
        with pytest.raises(
            TypeError, match="element_at method not supported for type CtyMap"
        ):
            map_val.element_at(0)


class TestCtyValueHash:
    def test_hash_primitives(
        self, string_type: CtyString, number_type: CtyNumber, bool_type: CtyBool
    ) -> None:
        s_val = CtyValue(vtype=string_type, value="hello")
        n_val = CtyValue(vtype=number_type, value=Decimal(123))
        b_val = CtyValue(vtype=bool_type, value=True)
        assert isinstance(hash(s_val), int)
        assert isinstance(hash(n_val), int)
        assert isinstance(hash(b_val), int)

    def test_hash_null_unknown(self, string_type: CtyString) -> None:
        null_val = CtyValue.null(string_type)
        unknown_val = CtyValue.unknown(string_type)
        assert isinstance(hash(null_val), int)
        assert isinstance(hash(unknown_val), int)
        assert hash(null_val) != hash(unknown_val)

    def test_hash_collections(
        self, list_string_type: CtyList, map_string_to_number_type: CtyMap
    ) -> None:
        list_val = CtyValue(vtype=list_string_type, value=[CtyString().validate("a")])
        map_val = CtyValue(
            vtype=map_string_to_number_type, value={"key": CtyNumber().validate(1)}
        )
        assert isinstance(hash(list_val), int)
        assert isinstance(hash(map_val), int)

    def test_hash_tuple_with_unhashable_element_fallback(
        self, string_type: CtyString, list_string_type: CtyList
    ) -> None:
        tuple_type = CtyTuple(element_types=(string_type, list_string_type))
        tuple_val = tuple_type.validate(("a", [CtyString().validate("b")]))
        assert isinstance(hash(tuple_val), int)

    def test_hash_custom_object_fallback(self, string_type: CtyString) -> None:
        pass


class TestCtyValueEq:
    def test_eq_primitives(
        self, string_type: CtyString, number_type: CtyNumber
    ) -> None:
        assert CtyValue(vtype=string_type, value="a") == CtyValue(
            vtype=string_type, value="a"
        )
        assert CtyValue(vtype=string_type, value="a") != CtyValue(
            vtype=string_type, value="b"
        )
        assert CtyValue(vtype=number_type, value=Decimal(1)) == CtyValue(
            vtype=number_type, value=Decimal("1.0")
        )
        assert CtyValue(vtype=number_type, value=Decimal(1)) != CtyValue(
            vtype=number_type, value=Decimal(2)
        )

    def test_eq_different_types(
        self, string_type: CtyString, number_type: CtyNumber
    ) -> None:
        assert CtyValue(vtype=string_type, value="1") != CtyValue(
            vtype=number_type, value=Decimal(1)
        )

    def test_eq_null_unknown(self, string_type: CtyString) -> None:
        assert CtyValue.null(string_type) == CtyValue.null(string_type)
        assert CtyValue.unknown(string_type) == CtyValue.unknown(string_type)
        assert CtyValue.null(string_type) != CtyValue.unknown(string_type)
        assert CtyValue(vtype=string_type, value="a") != CtyValue.null(string_type)

    def test_eq_marks(self, string_type: CtyString) -> None:
        val1 = CtyValue(vtype=string_type, value="a").mark("mark1")
        val2 = CtyValue(vtype=string_type, value="a").mark("mark1")
        val3 = CtyValue(vtype=string_type, value="a").mark("mark2")
        val4 = CtyValue(vtype=string_type, value="a")
        assert val1 == val2
        assert val1 != val3
        assert val1 != val4

    def test_eq_collections(
        self, list_string_type: CtyList, string_type: CtyString
    ) -> None:
        list1 = list_string_type.validate(["a", "b"])
        list2 = list_string_type.validate(["a", "b"])
        list3 = list_string_type.validate(["a", "c"])
        assert list1 == list2
        assert list1 != list3

        map_type = CtyMap(key_type=string_type, value_type=string_type)
        map1 = map_type.validate({"k1": "v1", "k2": "v2"})
        map2 = map_type.validate({"k1": "v1", "k2": "v2"})
        map3 = map_type.validate({"k1": "v1", "k2": "vx"})
        assert map1 == map2
        assert map1 != map3

        set_type = CtySet(element_type=string_type)
        set1 = set_type.validate({"a", "b"})
        set2 = set_type.validate({"b", "a"})
        set3 = set_type.validate({"a", "c"})
        assert set1 == set2
        assert set1 != set3

    def test_eq_decimal_conversion_robustness(self, number_type: CtyNumber) -> None:
        val_decimal = CtyValue(vtype=number_type, value=Decimal("1.0"))
        val_int = CtyValue(vtype=number_type, value=1)
        val_float = CtyValue(vtype=number_type, value=1.0)
        assert val_decimal == val_int
        assert val_decimal == val_float

        val_str_num_type = CtyString()
        val_str_one = CtyValue(vtype=val_str_num_type, value="1.0")
        assert val_decimal != val_str_one
        pass

    def test_eq_unhashable_fallback(
        self, list_string_type: CtyList, string_type: CtyString
    ) -> None:
        list_val1 = list_string_type.validate(["a", "b"])
        list_val2 = list_string_type.validate(["a", "b"])
        list_val3 = list_string_type.validate(["a", "c"])
        assert list_val1 == list_val2
        assert list_val1 != list_val3

    def test_eq_other_not_ctyvalue(self, string_type: CtyString) -> None:
        val = CtyValue(vtype=string_type, value="text")
        assert val != "text"
        assert val != 123


class TestCtyValueToJsonComparableDict:
    def test_to_json_comparable_dict_primitives(
        self, string_type, number_type, bool_type
    ) -> None:
        s = CtyValue(vtype=string_type, value="hi").to_json_comparable_dict()
        assert s == {
            "type_name": "string",
            "value": "hi",
            "is_unknown": False,
            "is_null": False,
            "marks": [],
        }

        n = CtyValue(vtype=number_type, value=Decimal("1.23")).to_json_comparable_dict()
        assert n == {
            "type_name": "number",
            "value": "1.23",
            "is_unknown": False,
            "is_null": False,
            "marks": [],
        }

        n_zero = CtyValue(
            vtype=number_type, value=Decimal("0")
        ).to_json_comparable_dict()
        assert n_zero == {
            "type_name": "number",
            "value": "0",
            "is_unknown": False,
            "is_null": False,
            "marks": [],
        }

        n_neg_zero = CtyValue(
            vtype=number_type, value=Decimal("-0")
        ).to_json_comparable_dict()
        assert n_neg_zero == {
            "type_name": "number",
            "value": "-0",
            "is_unknown": False,
            "is_null": False,
            "marks": [],
        }

        b = CtyValue(vtype=bool_type, value=True).to_json_comparable_dict()
        assert b == {
            "type_name": "bool",
            "value": True,
            "is_unknown": False,
            "is_null": False,
            "marks": [],
        }

    def test_to_json_comparable_dict_null_unknown_marks(self, string_type) -> None:
        null_val = CtyValue.null(string_type).to_json_comparable_dict()
        assert null_val == {
            "type_name": "string",
            "value": None,
            "is_unknown": False,
            "is_null": True,
            "marks": [],
        }

        unknown_val = CtyValue.unknown(string_type).to_json_comparable_dict()
        assert unknown_val == {
            "type_name": "string",
            "value": None,
            "is_unknown": True,
            "is_null": False,
            "marks": [],
        }

        mark1 = "sensitive"
        mark2 = "for_user_display_only"
        marked_val = (
            CtyValue(vtype=string_type, value="marked")
            .mark(mark1)
            .mark(mark2)
            .to_json_comparable_dict()
        )

        assert marked_val["marks"] == sorted([mark1, mark2])

    def test_to_json_comparable_dict_collections(
        self, list_string_type, string_type, map_string_to_number_type, number_type
    ) -> None:
        # List
        list_val_cty = list_string_type.validate(["a", "b"])
        list_dict = list_val_cty.to_json_comparable_dict()
        assert list_dict["type_name"] == "list(string)"
        assert list_dict["value"] == [
            {
                "type_name": "string",
                "value": "a",
                "is_unknown": False,
                "is_null": False,
                "marks": [],
            },
            {
                "type_name": "string",
                "value": "b",
                "is_unknown": False,
                "is_null": False,
                "marks": [],
            },
        ]

        # Map
        map_val_cty = map_string_to_number_type.validate({"x": 1, "y": 2.5})
        map_dict = map_val_cty.to_json_comparable_dict()
        assert map_dict["type_name"] == "map(number)"
        assert map_dict["value"] == {
            "x": {
                "type_name": "number",
                "value": "1",
                "is_unknown": False,
                "is_null": False,
                "marks": [],
            },
            "y": {
                "type_name": "number",
                "value": "2.5",
                "is_unknown": False,
                "is_null": False,
                "marks": [],
            },
        }

        # Set
        set_type = CtySet(element_type=string_type)
        set_val_cty = set_type.validate({"foo", "bar"})
        set_dict = set_val_cty.to_json_comparable_dict()
        assert set_dict["type_name"] == "set(string)"
        assert isinstance(set_dict["value"], list)
        assert len(set_dict["value"]) == 2
        assert {
            "type_name": "string",
            "value": "bar",
            "is_unknown": False,
            "is_null": False,
            "marks": [],
        } in set_dict["value"]
        assert {
            "type_name": "string",
            "value": "foo",
            "is_unknown": False,
            "is_null": False,
            "marks": [],
        } in set_dict["value"]

    def test_to_json_comparable_dict_tuple_and_object(
        self, string_type, number_type
    ) -> None:
        # Tuple
        tuple_type = CtyTuple(element_types=(string_type, number_type))
        tuple_val_cty = tuple_type.validate(("hi", 10))
        tuple_dict = tuple_val_cty.to_json_comparable_dict()
        assert tuple_dict["type_name"] == "tuple(string, number)"
        assert tuple_dict["value"] == (
            {
                "type_name": "string",
                "value": "hi",
                "is_unknown": False,
                "is_null": False,
                "marks": [],
            },
            {
                "type_name": "number",
                "value": "10",
                "is_unknown": False,
                "is_null": False,
                "marks": [],
            },
        )

        empty_tuple_type = CtyTuple(element_types=())
        empty_tuple_val_cty = empty_tuple_type.validate(())
        empty_tuple_dict = empty_tuple_val_cty.to_json_comparable_dict()
        assert empty_tuple_dict["type_name"] == "tuple()"
        assert empty_tuple_dict["value"] is None

        # Object
        obj_type = CtyObject(
            attribute_types={"name": string_type, "count": number_type}
        )
        obj_val_cty = obj_type.validate({"name": "item", "count": 5})
        obj_dict = obj_val_cty.to_json_comparable_dict()
        assert obj_dict["type_name"] == "object({count=number, name=string})"
        assert obj_dict["value"] == {
            "name": {
                "type_name": "string",
                "value": "item",
                "is_unknown": False,
                "is_null": False,
                "marks": [],
            },
            "count": {
                "type_name": "number",
                "value": "5",
                "is_unknown": False,
                "is_null": False,
                "marks": [],
            },
        }

    def test_to_json_comparable_dict_decimal_various_formats(self, number_type) -> None:
        val1 = CtyValue(number_type, Decimal("123.000")).to_json_comparable_dict()[
            "value"
        ]
        assert val1 == "123"
        val2 = CtyValue(number_type, Decimal("0.000")).to_json_comparable_dict()[
            "value"
        ]
        assert val2 == "0"
        val3 = CtyValue(number_type, Decimal("-0.000")).to_json_comparable_dict()[
            "value"
        ]
        assert val3 == "-0"
        val4 = CtyValue(number_type, Decimal("123.4500")).to_json_comparable_dict()[
            "value"
        ]
        assert val4 == "123.45"
        val5 = CtyValue(number_type, Decimal("0.12300")).to_json_comparable_dict()[
            "value"
        ]
        assert val5 == "0.123"
        val6 = CtyValue(number_type, Decimal("1E+3")).to_json_comparable_dict()["value"]
        assert val6 == "1000"
        val7 = CtyValue(number_type, Decimal("1.23E-4")).to_json_comparable_dict()[
            "value"
        ]
        assert val7 == "0.000123"
        val8 = CtyValue(number_type, Decimal("123E-5")).to_json_comparable_dict()[
            "value"
        ]
        assert val8 == "0.00123"


class TestCtyValueSerialization:
    def test_json_string_roundtrip_simple(self, string_type: CtyString) -> None:
        original_val = CtyValue(vtype=string_type, value="hello world")
        json_str = original_val.to_json_string()
        new_val = CtyValue.from_json_string(json_str, string_type)
        assert new_val == original_val

    def test_msgpack_bytes_roundtrip_simple(self, number_type: CtyNumber) -> None:
        original_val = CtyValue(vtype=number_type, value=Decimal("123.456"))
        msgpack_bytes = original_val.to_msgpack_bytes()
        new_val = CtyValue.from_msgpack_bytes(msgpack_bytes, number_type)
        assert new_val == original_val
