import pytest
from pyvider.cty.exceptions.validation import (
    CtyValidationError,
    CtyAttributeValidationError,
    CtyListValidationError,
    CtyMapValidationError,
    CtySetValidationError,
    CtyTupleValidationError,
    CtyTypeValidationError,
    CtyTypeMismatchError,
    _get_type_name_from_original,
)
from pyvider.cty.path import CtyPath
from pyvider.cty.types import CtyString, CtyNumber


class TestCtyValidationError:
    def test_str_with_path(self):
        err = CtyValidationError("test message", path=CtyPath.get_attr("foo"))
        assert str(err) == "At foo: test message"

    def test_str_without_path(self):
        err = CtyValidationError("test message")
        assert str(err) == "test message"

    def test_str_with_root_path(self):
        err = CtyValidationError("test message", path=CtyPath())
        assert str(err) == "test message"


class TestGetTypeNameFromOriginal:
    def test_with_original_exception(self):
        orig = CtyValidationError("orig", type_name="Original")
        assert _get_type_name_from_original(orig, "Default") == "Original"

    def test_without_original_exception(self):
        assert _get_type_name_from_original(None, "Default") == "Default"

    def test_with_original_exception_no_type_name(self):
        orig = CtyValidationError("orig")
        assert _get_type_name_from_original(orig, "Default") == "Default"


class TestExceptionSubclasses:
    def test_attribute_validation_error(self):
        orig = CtyValidationError("orig", type_name="MyObject")
        err = CtyAttributeValidationError("attr error", original_exception=orig)
        assert err.type_name == "MyObject"

    def test_list_validation_error(self):
        orig = CtyValidationError("orig", type_name="MyList")
        err = CtyListValidationError("list error", original_exception=orig)
        assert err.type_name == "MyList"

    def test_map_validation_error(self):
        orig = CtyValidationError("orig", type_name="MyMap")
        err = CtyMapValidationError("map error", original_exception=orig)
        assert err.type_name == "MyMap"

    def test_set_validation_error(self):
        orig = CtyValidationError("orig", type_name="MySet")
        err = CtySetValidationError("set error", original_exception=orig)
        assert err.type_name == "MySet"

    def test_tuple_validation_error(self):
        orig = CtyValidationError("orig", type_name="MyTuple")
        err = CtyTupleValidationError("tuple error", original_exception=orig)
        assert err.type_name == "MyTuple"

    def test_type_validation_error(self):
        err = CtyTypeValidationError("type error", type_name="MyType")
        assert err.type_name == "MyType"

    def test_type_mismatch_error(self):
        err = CtyTypeMismatchError(
            "mismatch", actual_type=CtyString(), expected_type=CtyNumber()
        )
        assert "Expected number, got string" in str(err)


# 🐍🎯🧪🪄
