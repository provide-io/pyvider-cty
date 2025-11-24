#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Test suite for CtyCapsule and CtyCapsuleWithOps edge cases.

This test suite focuses on achieving 100% coverage of capsule.py, particularly:
- Lines 47, 49, 56 (null/unknown handling in validate)
- Lines 70-72 (usable_as with CtyDynamic)
- Lines 134 (hash for CtyCapsuleWithOps)
- Edge cases with custom equality/hash/convert functions"""

import pytest

from pyvider.cty import CtyNumber, CtyValue
from pyvider.cty.exceptions import CtyValidationError
from pyvider.cty.types.capsule import CtyCapsule, CtyCapsuleWithOps
from pyvider.cty.types.structural import CtyDynamic


# Sample custom type for testing
class CustomObject:
    """A custom Python class for capsule testing."""

    def __init__(self, value: int):
        self.value = value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CustomObject):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)


class AnotherCustomObject:
    """Another custom type for type mismatch tests."""

    def __init__(self, data: str):
        self.data = data


class TestCtyCapsuleValidation:
    """Test basic CtyCapsule validation edge cases."""

    def test_validate_ctyvalue_null(self) -> None:
        """Test: validate CtyValue.null() returns null (line 47)."""
        capsule = CtyCapsule("custom", CustomObject)
        null_value = CtyValue.null(capsule)
        result = capsule.validate(null_value)

        assert result.is_null
        assert result.type == capsule

    def test_validate_ctyvalue_unknown(self) -> None:
        """Test: validate CtyValue.unknown() returns unknown (line 49)."""
        capsule = CtyCapsule("custom", CustomObject)
        unknown_value = CtyValue.unknown(capsule)
        result = capsule.validate(unknown_value)

        assert result.is_unknown
        assert result.type == capsule

    def test_validate_none_returns_null(self) -> None:
        """Test: validate None returns null (line 56)."""
        capsule = CtyCapsule("custom", CustomObject)
        result = capsule.validate(None)

        assert result.is_null
        assert result.type == capsule

    def test_validate_wrong_type_raises_error(self) -> None:
        """Test: validate with wrong Python type raises CtyValidationError."""
        capsule = CtyCapsule("custom", CustomObject)
        wrong_obj = AnotherCustomObject("data")

        with pytest.raises(
            CtyValidationError,
            match=r"Value is not an instance of CustomObject\. Got AnotherCustomObject\.",
        ):
            capsule.validate(wrong_obj)

    def test_validate_correct_type_succeeds(self) -> None:
        """Test: validate with correct Python type succeeds."""
        capsule = CtyCapsule("custom", CustomObject)
        obj = CustomObject(42)
        result = capsule.validate(obj)

        assert not result.is_null
        assert not result.is_unknown
        assert result.value == obj
        assert result.type == capsule


class TestCtyCapsuleEquality:
    """Test CtyCapsule.equal() method edge cases."""

    def test_equal_same_name_and_type(self) -> None:
        """Test: two capsules with same name and py_type are equal."""
        cap1 = CtyCapsule("custom", CustomObject)
        cap2 = CtyCapsule("custom", CustomObject)

        assert cap1.equal(cap2)
        assert cap2.equal(cap1)

    def test_not_equal_different_name(self) -> None:
        """Test: capsules with different names are not equal."""
        cap1 = CtyCapsule("custom1", CustomObject)
        cap2 = CtyCapsule("custom2", CustomObject)

        assert not cap1.equal(cap2)

    def test_not_equal_different_py_type(self) -> None:
        """Test: capsules with different py_types are not equal."""
        cap1 = CtyCapsule("custom", CustomObject)
        cap2 = CtyCapsule("custom", AnotherCustomObject)

        assert not cap1.equal(cap2)

    def test_not_equal_to_capsule_with_ops(self) -> None:
        """Test: CtyCapsule not equal to CtyCapsuleWithOps (line 65)."""
        cap1 = CtyCapsule("custom", CustomObject)
        cap2 = CtyCapsuleWithOps("custom", CustomObject)

        assert not cap1.equal(cap2)

    def test_not_equal_to_other_cty_type(self) -> None:
        """Test: CtyCapsule not equal to other CtyType."""
        capsule = CtyCapsule("custom", CustomObject)
        number_type = CtyNumber()

        assert not capsule.equal(number_type)


class TestCtyCapsuleUsableAs:
    """Test CtyCapsule.usable_as() method (lines 69-72)."""

    def test_usable_as_dynamic(self) -> None:
        """Test: capsule is usable as CtyDynamic (line 70-71)."""
        capsule = CtyCapsule("custom", CustomObject)
        dynamic = CtyDynamic()

        assert capsule.usable_as(dynamic)

    def test_usable_as_equal_type(self) -> None:
        """Test: capsule is usable as itself."""
        capsule = CtyCapsule("custom", CustomObject)

        assert capsule.usable_as(capsule)

    def test_not_usable_as_different_type(self) -> None:
        """Test: capsule not usable as different type."""
        cap1 = CtyCapsule("custom1", CustomObject)
        cap2 = CtyCapsule("custom2", CustomObject)

        assert not cap1.usable_as(cap2)


class TestCtyCapsuleWithOpsValidation:
    """Test CtyCapsuleWithOps initialization and validation."""

    def test_create_with_valid_equal_fn(self) -> None:
        """Test: create CtyCapsuleWithOps with valid equal_fn."""

        def custom_equal(a: CustomObject, b: CustomObject) -> bool:
            return a.value == b.value

        capsule = CtyCapsuleWithOps("custom", CustomObject, equal_fn=custom_equal)

        assert capsule.equal_fn == custom_equal

    def test_create_with_valid_hash_fn(self) -> None:
        """Test: create CtyCapsuleWithOps with valid hash_fn."""

        def custom_hash(obj: CustomObject) -> int:
            return hash(obj.value)

        capsule = CtyCapsuleWithOps("custom", CustomObject, hash_fn=custom_hash)

        assert capsule.hash_fn == custom_hash

    def test_create_with_valid_convert_fn(self) -> None:
        """Test: create CtyCapsuleWithOps with valid convert_fn."""

        def custom_convert(obj: CustomObject, target_type: CtyNumber) -> CtyValue[int] | None:
            return CtyNumber().validate(obj.value)

        capsule = CtyCapsuleWithOps("custom", CustomObject, convert_fn=custom_convert)

        assert capsule.convert_fn == custom_convert

    def test_equal_fn_wrong_arity_raises_error(self) -> None:
        """Test: equal_fn with wrong arity raises TypeError."""

        def bad_equal(a: CustomObject) -> bool:  # Only 1 arg, needs 2
            return True

        with pytest.raises(TypeError, match="`equal_fn` must be a callable that accepts 2 arguments"):
            CtyCapsuleWithOps("custom", CustomObject, equal_fn=bad_equal)

    def test_hash_fn_wrong_arity_raises_error(self) -> None:
        """Test: hash_fn with wrong arity raises TypeError."""

        def bad_hash(a: CustomObject, b: CustomObject) -> int:  # 2 args, needs 1
            return hash(a)

        with pytest.raises(TypeError, match="`hash_fn` must be a callable that accepts 1 argument"):
            CtyCapsuleWithOps("custom", CustomObject, hash_fn=bad_hash)

    def test_convert_fn_wrong_arity_raises_error(self) -> None:
        """Test: convert_fn with wrong arity raises TypeError."""

        def bad_convert(obj: CustomObject) -> CtyValue[int]:  # 1 arg, needs 2
            return CtyNumber().validate(obj.value)

        with pytest.raises(TypeError, match="`convert_fn` must be a callable that accepts 2 arguments"):
            CtyCapsuleWithOps("custom", CustomObject, convert_fn=bad_convert)


class TestCtyCapsuleWithOpsEquality:
    """Test CtyCapsuleWithOps equality method."""

    def test_equal_same_ops(self) -> None:
        """Test: two CtyCapsuleWithOps with same ops are equal."""

        def eq_fn(a: CustomObject, b: CustomObject) -> bool:
            return a.value == b.value

        def hash_fn(obj: CustomObject) -> int:
            return hash(obj.value)

        cap1 = CtyCapsuleWithOps("custom", CustomObject, equal_fn=eq_fn, hash_fn=hash_fn)
        cap2 = CtyCapsuleWithOps("custom", CustomObject, equal_fn=eq_fn, hash_fn=hash_fn)

        assert cap1.equal(cap2)

    def test_not_equal_different_equal_fn(self) -> None:
        """Test: different equal_fn makes capsules not equal."""

        def eq_fn1(a: CustomObject, b: CustomObject) -> bool:
            return a.value == b.value

        def eq_fn2(a: CustomObject, b: CustomObject) -> bool:
            return True

        cap1 = CtyCapsuleWithOps("custom", CustomObject, equal_fn=eq_fn1)
        cap2 = CtyCapsuleWithOps("custom", CustomObject, equal_fn=eq_fn2)

        assert not cap1.equal(cap2)

    def test_not_equal_to_regular_capsule(self) -> None:
        """Test: CtyCapsuleWithOps not equal to regular CtyCapsule."""
        cap1 = CtyCapsuleWithOps("custom", CustomObject)
        cap2 = CtyCapsule("custom", CustomObject)

        assert not cap1.equal(cap2)


class TestCtyCapsuleHashing:
    """Test hash functions for CtyCapsule and CtyCapsuleWithOps (line 134)."""

    def test_capsule_hash_consistent(self) -> None:
        """Test: CtyCapsule hash is consistent."""
        cap = CtyCapsule("custom", CustomObject)
        hash1 = hash(cap)
        hash2 = hash(cap)

        assert hash1 == hash2

    def test_capsule_with_ops_hash_consistent(self) -> None:
        """Test: CtyCapsuleWithOps hash is consistent (line 134)."""

        def eq_fn(a: CustomObject, b: CustomObject) -> bool:
            return a.value == b.value

        cap = CtyCapsuleWithOps("custom", CustomObject, equal_fn=eq_fn)
        hash1 = hash(cap)
        hash2 = hash(cap)

        assert hash1 == hash2

    def test_capsule_with_ops_hash_includes_ops(self) -> None:
        """Test: CtyCapsuleWithOps hash changes with different ops."""

        def eq_fn1(a: CustomObject, b: CustomObject) -> bool:
            return a.value == b.value

        def eq_fn2(a: CustomObject, b: CustomObject) -> bool:
            return True

        cap1 = CtyCapsuleWithOps("custom", CustomObject, equal_fn=eq_fn1)
        cap2 = CtyCapsuleWithOps("custom", CustomObject, equal_fn=eq_fn2)

        # Different equal_fn should produce different hash
        assert hash(cap1) != hash(cap2)


# 🌊🪢🔚
