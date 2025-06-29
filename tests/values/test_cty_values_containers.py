import pytest
from pyvider.cty import (
    CtyList, CtyMap, CtyNumber, CtyObject, CtySet, CtyString, CtyTuple, CtyValue
)

class TestCtyValueContainerOperations:
    @pytest.fixture
    def list_val(self):
        return CtyList(element_type=CtyString()).validate(["a", "b", "c"])
    
    @pytest.fixture
    def map_val(self):
        return CtyMap(key_type=CtyString(), value_type=CtyNumber()).validate({"a": 1, "b": 2})

    @pytest.fixture
    def obj_val(self):
        return CtyObject(
            attribute_types={"name": CtyString(), "age": CtyNumber()}
        ).validate({"name": "Alice", "age": 30})

    def test_list_operations(self, list_val):
        assert len(list_val) == 3
        assert list_val[1].value == "b"
        assert "a" in list_val
        assert "z" not in list_val
        assert [v.value for v in list_val] == ["a", "b", "c"]

    def test_map_operations(self, map_val):
        assert len(map_val) == 2
        assert map_val["a"].value == 1
        assert "b" in map_val
        assert "c" not in map_val
        # Note: Iterating a CtyMap value yields its keys
        assert sorted(list(map_val)) == ["a", "b"]

    def test_object_operations(self, obj_val):
        assert len(obj_val) == 2
        assert obj_val["name"].value == "Alice"
        assert "age" in obj_val
        assert "height" not in obj_val
        assert sorted(list(obj_val)) == ["age", "name"]
