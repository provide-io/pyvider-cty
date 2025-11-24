#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TDD Test Suite for Pre-Release Hardening Recommendations.

This suite defines the required strict behavior for:
1. Deserialization of CtyDynamic values, which must fail on malformed payloads.
2. The CtyCapsuleWithOps constructor, which must validate function arity.
3. Hashing rules for CtyValue, aligning with Python idioms."""

from typing import Any

import msgpack  # type: ignore
import pytest

from pyvider.cty import (
    CtyCapsuleWithOps,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyObject,
    CtySet,
    CtyString,
    CtyTuple,
    CtyValue,
)
from pyvider.cty.codec import cty_from_msgpack
from pyvider.cty.exceptions import DeserializationError


class TestStrictDynamicDeserialization:
    """
    TDD tests for Recommendation #5: Enforce Strict CtyDynamic Deserialization.

    This suite defines that the deserializer MUST fail on malformed dynamic
    payloads, mirroring go-cty's strict behavior.
    """

    def test_dynamic_deserialization_with_malformed_type_json_raises_error(
        self,
    ) -> None:
        """
        TDD: A malformed type spec in a dynamic value payload must always
        raise a DeserializationError. There is no fallback.
        """
        # This payload mimics the dynamic value structure but has invalid JSON.
        payload = [b"{not-json", "some_value"]
        packed_bytes = msgpack.packb(payload, use_bin_type=True)

        with pytest.raises(
            DeserializationError,
            match="Failed to decode dynamic value type spec from JSON",
        ):
            cty_from_msgpack(packed_bytes, CtyDynamic())


class TestCapsuleWithOpsContract:
    """
    TDD tests for Recommendation #7: Strengthen the CtyCapsuleWithOps Contract.

    This suite defines constructor validation for the callables passed to CtyCapsuleWithOps.
    """

    class Opaque:
        """A dummy class for encapsulation."""

    @pytest.mark.parametrize(
        "bad_func",
        [
            lambda: True,  # 0 args
            lambda a: True,  # 1 arg
            lambda a, b, c: True,  # 3 args
        ],
    )
    def test_constructor_rejects_equal_fn_with_wrong_arity(self, bad_func: Any) -> None:
        """TDD: `equal_fn` must accept exactly 2 arguments."""
        with pytest.raises(TypeError, match="`equal_fn` must be a callable that accepts 2 arguments"):
            CtyCapsuleWithOps("Opaque", self.Opaque, equal_fn=bad_func)

    @pytest.mark.parametrize(
        "bad_func",
        [
            lambda: 1,  # 0 args
            lambda a, b: 1,  # 2 args
        ],
    )
    def test_constructor_rejects_hash_fn_with_wrong_arity(self, bad_func: Any) -> None:
        """TDD: `hash_fn` must accept exactly 1 argument."""
        with pytest.raises(TypeError, match="`hash_fn` must be a callable that accepts 1 argument"):
            CtyCapsuleWithOps("Opaque", self.Opaque, hash_fn=bad_func)

    @pytest.mark.parametrize(
        "bad_func",
        [
            lambda: None,  # 0 args
            lambda a: None,  # 1 arg
            lambda a, b, c: None,  # 3 args
        ],
    )
    def test_constructor_rejects_convert_fn_with_wrong_arity(self, bad_func: Any) -> None:
        """TDD: `convert_fn` must accept exactly 2 arguments."""
        with pytest.raises(TypeError, match="`convert_fn` must be a callable that accepts 2 arguments"):
            CtyCapsuleWithOps("Opaque", self.Opaque, convert_fn=bad_func)

    def test_constructor_accepts_correctly_defined_fns(self) -> None:
        """TDD: Correctly defined functions should not raise an error."""
        try:
            CtyCapsuleWithOps(
                "Opaque",
                self.Opaque,
                equal_fn=lambda a, b: True,
                hash_fn=lambda a: 1,
                convert_fn=lambda val, target_type: CtyValue.null(target_type),
            )
        except TypeError as e:
            pytest.fail(f"Correctly defined functions raised an unexpected error: {e}")


class TestValueHashingContract:
    """
    TDD tests for Recommendation #2: Formalize Python-Idiomatic Hashing.
    This suite asserts that Tuples are hashable, while all other collections are not.
    """

    def test_tuple_value_is_hashable(self) -> None:
        """TDD: A CtyValue wrapping a tuple of hashable primitives MUST be hashable."""
        tuple_type = CtyTuple(element_types=(CtyString(),))
        tuple_val = tuple_type.validate(("hello",))
        try:
            # The ability to be a key in a set proves hashability.
            _ = {tuple_val}
        except TypeError:
            pytest.fail("CtyValue(CtyTuple, ...) was not hashable, but should be.")

    @pytest.mark.parametrize(
        "unhashable_val",
        [
            CtyList(element_type=CtyString()).validate(["a"]),
            CtySet(element_type=CtyString()).validate({"a"}),
            CtyMap(element_type=CtyString()).validate({"a": "b"}),
            CtyObject({"a": CtyString()}).validate({"a": "b"}),
        ],
    )
    def test_collection_values_are_unhashable(self, unhashable_val: CtyValue) -> None:
        """TDD: CtyValues wrapping lists, sets, maps, and objects MUST be unhashable."""
        with pytest.raises(TypeError, match="unhashable type"):
            hash(unhashable_val)


# 🌊🪢🔚
