#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from pyvider.cty.exceptions.validation import (
    CtyAttributeValidationError,
    CtyListValidationError,
    CtyMapValidationError,
    CtySetValidationError,
    CtyTupleValidationError,
    CtyTypeMismatchError,
    CtyTypeValidationError,
    CtyValidationError,
    _get_type_name_from_original,
)
from pyvider.cty.path import CtyPath
from pyvider.cty.types import CtyNumber, CtyString


class TestCtyValidationError:
    def test_str_with_path(self) -> None:
        err = CtyValidationError("test message", path=CtyPath.get_attr("foo"))
        assert str(err) == "At foo: test message", f"Expected 'At foo: test message', but got {err!s}"

    def test_str_without_path(self) -> None:
        err = CtyValidationError("test message")
        assert str(err) == "test message", f"Expected 'test message', but got {err!s}"

    def test_str_with_root_path(self) -> None:
        err = CtyValidationError("test message", path=CtyPath())
        assert str(err) == "test message", f"Expected 'test message', but got {err!s}"


class TestGetTypeNameFromOriginal:
    def test_with_original_exception(self) -> None:
        orig = CtyValidationError("orig", type_name="Original")
        assert _get_type_name_from_original(orig, "Default") == "Original", (
            f"Expected 'Original', but got {_get_type_name_from_original(orig, 'Default')}"
        )

    def test_without_original_exception(self) -> None:
        assert _get_type_name_from_original(None, "Default") == "Default", (
            f"Expected 'Default', but got {_get_type_name_from_original(None, 'Default')}"
        )

    def test_with_original_exception_no_type_name(self) -> None:
        orig = CtyValidationError("orig")
        assert _get_type_name_from_original(orig, "Default") == "Default", (
            f"Expected 'Default', but got {_get_type_name_from_original(orig, 'Default')}"
        )


class TestExceptionSubclasses:
    def test_attribute_validation_error(self) -> None:
        orig = CtyValidationError("orig", type_name="MyObject")
        err = CtyAttributeValidationError("attr error", original_exception=orig)
        assert err.type_name == "MyObject", f"Expected type_name 'MyObject', but got {err.type_name}"

    def test_list_validation_error(self) -> None:
        orig = CtyValidationError("orig", type_name="MyList")
        err = CtyListValidationError("list error", original_exception=orig)
        assert err.type_name == "MyList", f"Expected type_name 'MyList', but got {err.type_name}"

    def test_map_validation_error(self) -> None:
        orig = CtyValidationError("orig", type_name="MyMap")
        err = CtyMapValidationError("map error", original_exception=orig)
        assert err.type_name == "MyMap", f"Expected type_name 'MyMap', but got {err.type_name}"

    def test_set_validation_error(self) -> None:
        orig = CtyValidationError("orig", type_name="MySet")
        err = CtySetValidationError("set error", original_exception=orig)
        assert err.type_name == "MySet", f"Expected type_name 'MySet', but got {err.type_name}"

    def test_tuple_validation_error(self) -> None:
        orig = CtyValidationError("orig", type_name="MyTuple")
        err = CtyTupleValidationError("tuple error", original_exception=orig)
        assert err.type_name == "MyTuple", f"Expected type_name 'MyTuple', but got {err.type_name}"

    def test_type_validation_error(self) -> None:
        err = CtyTypeValidationError("type error", type_name="MyType")
        assert err.type_name == "MyType", f"Expected type_name 'MyType', but got {err.type_name}"

    def test_type_mismatch_error(self) -> None:
        err = CtyTypeMismatchError("mismatch", actual_type=CtyString(), expected_type=CtyNumber())
        assert "Expected number, got string" in str(err), (
            f"Expected error message to contain 'Expected number, got string', but got {err!s}"
        )


# 🌊🪢🔚
