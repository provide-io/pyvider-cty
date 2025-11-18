#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TODO: Add module docstring."""

from pyvider.cty import CtyDynamic, CtyList, CtyNumber, CtyObject, CtyString


class TestTypeUsabilityMatrix:
    """
    Tests the `usable_as` method across a matrix of different types to ensure
    consistent and correct behavior for type compatibility.
    """

    def test_concrete_types_are_usable_as_dynamic(self) -> None:
        """TDD Test: Any concrete type can be safely used where a dynamic type is expected."""
        t_dyn = CtyDynamic()

        assert CtyString().usable_as(t_dyn)
        assert CtyNumber().usable_as(t_dyn)
        assert CtyList(element_type=CtyNumber()).usable_as(t_dyn)
        assert CtyObject(attribute_types={"a": CtyString()}).usable_as(t_dyn)

    def test_object_subtyping_rules(self) -> None:
        """TDD Test: An object with more attributes/stricter requirements is usable as one with less."""
        # Superset of attributes
        t_large = CtyObject(attribute_types={"a": CtyString(), "b": CtyNumber()})
        t_small = CtyObject(attribute_types={"a": CtyString()})
        assert t_large.usable_as(t_small)
        assert not t_small.usable_as(t_large)

        # Optional vs. Required attributes
        t_req = CtyObject(attribute_types={"a": CtyString()})  # 'a' is required
        t_opt = CtyObject(attribute_types={"a": CtyString()}, optional_attributes=frozenset(["a"]))
        assert t_req.usable_as(t_opt)
        assert not t_opt.usable_as(t_req)


# 🌊🪢🔚
