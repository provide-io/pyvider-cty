"""
TDD Test Suite for CtyCapsule with custom operations.

These tests define the behavior for a capsule type that can be equipped with
custom logic for equality, hashing, and other operations, mirroring the
`CapsuleWithOps` feature from go-cty.
"""

from typing import Any
from unittest.mock import Mock

import pytest

from pyvider.cty import CtyCapsuleWithOps, CtyValue


class OpaqueObject:
    """A simple class to be encapsulated."""

    def __init__(self, id: int, data: str) -> None:
        self.id = id
        self.data = data


class TestCtyCapsuleWithOps:
    @pytest.fixture
    def mock_equal_fn(self) -> Mock:
        # By default, two different instances are not equal.
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
        """TDD: CtyValue equality for capsules should delegate to the provided equal_fn."""
        val1 = capsule_type_with_ops.validate(OpaqueObject(1, "foo"))
        val2 = capsule_type_with_ops.validate(OpaqueObject(2, "bar"))

        # Configure the mock to consider them equal for this test case
        mock_equal_fn.return_value = True

        # This comparison should trigger the mock function
        assert val1 == val2
        mock_equal_fn.assert_called_once_with(val1.value, val2.value)

    def test_hash_uses_custom_hash_fn(
        self, capsule_type_with_ops: CtyCapsuleWithOps, mock_hash_fn: Mock
    ) -> None:
        """TDD: Hashing a capsule CtyValue should delegate to the provided hash_fn."""
        val = capsule_type_with_ops.validate(OpaqueObject(1, "foo"))

        # Hashing the value should trigger the mock
        value_hash = hash(val)

        assert value_hash == 42
        mock_hash_fn.assert_called_once_with(val.value)

    def test_set_of_capsules_uses_custom_fns(
        self, capsule_type_with_ops: CtyCapsuleWithOps, mock_equal_fn: Mock, mock_hash_fn: Mock
    ) -> None:
        """TDD: Using capsules in a set should correctly use both custom functions."""
        from pyvider.cty import CtySet

        set_type = CtySet(element_type=capsule_type_with_ops)
        obj1 = OpaqueObject(1, "foo")
        obj2 = OpaqueObject(2, "bar")

        # Make the mock treat these two distinct objects as equal
        def side_effect_equal(a: Any, b: Any) -> bool:
            return (a is obj1 and b is obj2) or (a is obj2 and b is obj1)

        mock_equal_fn.side_effect = side_effect_equal
        # Make the mock return the same hash for both
        mock_hash_fn.side_effect = lambda obj: 1 # Same hash for both

        # Because obj1 and obj2 are considered equal by the custom functions,
        # the set should only contain one of them.
        set_val = set_type.validate([obj1, obj2])

        assert len(set_val.value) == 1
        assert mock_hash_fn.call_count >= 2
        assert mock_equal_fn.call_count >= 1

    def test_type_equality(self) -> None:
        """Ensures type equality considers the operational functions."""
        type1 = CtyCapsuleWithOps("t", OpaqueObject, equal_fn=lambda a, b: True)
        type2 = CtyCapsuleWithOps("t", OpaqueObject, equal_fn=lambda a, b: True)
        type3 = CtyCapsuleWithOps("t", OpaqueObject, equal_fn=lambda a, b: False)
        
        assert not type1.equal(type2) # Lambdas are not equal
        assert not type1.equal(type3)
