"""
TDD Test Suite for CtyCapsule with custom operations.

These tests define the behavior for a capsule type that can be equipped with
custom logic for equality, hashing, and other operations, mirroring the
`CapsuleWithOps` feature from go-cty.
"""

from typing import Any
from unittest.mock import Mock

import pytest

from pyvider.cty import CtyCapsule, CtyCapsuleWithOps, CtyValue


class OpaqueObject:
    """A simple class to be encapsulated."""

    def __init__(self, id: int, data: str) -> None:
        self.id = id
        self.data = data


class TestCtyCapsuleWithOps:
    @pytest.fixture
    def mock_equal_fn(self) -> Mock:
        return Mock(return_value=False)

    @pytest.fixture
    def mock_hash_fn(self) -> Mock:
        return Mock(return_value=42)

    @pytest.fixture
    def capsule_type_with_ops(
        self, mock_equal_fn: Mock, mock_hash_fn: Mock
    ) -> CtyCapsuleWithOps:
        """A capsule type with mocked operational functions."""
        return CtyCapsuleWithOps(
            "Opaque",
            OpaqueObject,
            equal_fn=mock_equal_fn,
            hash_fn=mock_hash_fn,
        )

    def test_equality_uses_custom_equal_fn(
        self, capsule_type_with_ops: CtyCapsuleWithOps, mock_equal_fn: Mock
    ) -> None:
        val1 = capsule_type_with_ops.validate(OpaqueObject(1, "foo"))
        val2 = capsule_type_with_ops.validate(OpaqueObject(2, "bar"))
        mock_equal_fn.return_value = True
        assert val1 == val2
        mock_equal_fn.assert_called_once_with(val1.value, val2.value)

    def test_hash_uses_custom_hash_fn(
        self, capsule_type_with_ops: CtyCapsuleWithOps, mock_hash_fn: Mock
    ) -> None:
        val = capsule_type_with_ops.validate(OpaqueObject(1, "foo"))
        value_hash = hash(val)
        assert value_hash == 42
        mock_hash_fn.assert_called_once_with(val.value)

    def test_set_of_capsules_uses_custom_fns(
        self, capsule_type_with_ops: CtyCapsuleWithOps, mock_equal_fn: Mock, mock_hash_fn: Mock
    ) -> None:
        from pyvider.cty import CtySet
        set_type = CtySet(element_type=capsule_type_with_ops)
        obj1 = OpaqueObject(1, "foo")
        obj2 = OpaqueObject(2, "bar")

        def side_effect_equal(a: Any, b: Any) -> bool:
            return (a is obj1 and b is obj2) or (a is obj2 and b is obj1)

        mock_equal_fn.side_effect = side_effect_equal
        mock_hash_fn.side_effect = lambda obj: 1

        set_val = set_type.validate([obj1, obj2])
        assert len(set_val.value) == 1
        assert mock_hash_fn.call_count >= 2
        assert mock_equal_fn.call_count >= 1

    def test_type_equality(self) -> None:
        type1 = CtyCapsuleWithOps("t", OpaqueObject, equal_fn=lambda a, b: True)
        type2 = CtyCapsuleWithOps("t", OpaqueObject, equal_fn=lambda a, b: True)
        type3 = CtyCapsuleWithOps("t", OpaqueObject, equal_fn=lambda a, b: False)
        assert not type1.equal(type2)
        assert not type1.equal(type3)

    def test_base_capsule_and_ops_capsule_are_not_equal(self) -> None:
        """Verifies that a CtyCapsule and a CtyCapsuleWithOps are never equal."""
        base_type = CtyCapsule("Opaque", OpaqueObject)
        ops_type = CtyCapsuleWithOps("Opaque", OpaqueObject)
        assert not base_type.equal(ops_type)
        assert not ops_type.equal(base_type)
