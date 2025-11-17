#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TODO: Add module docstring."""

import pytest

from pyvider.cty import (
    CtyBool,
    CtyNumber,
    CtyString,
    CtyTuple,
)
from pyvider.cty.exceptions import CtyTupleValidationError


class TestCtyTupleCreation:
    def test_tuple_type_initialization_simple(self) -> None:
        tup = CtyTuple(element_types=(CtyString(), CtyNumber(), CtyBool()))
        assert len(tup.element_types) == 3

    def test_tuple_type_initialization_empty(self) -> None:
        empty_tuple = CtyTuple(element_types=())
        assert len(empty_tuple.element_types) == 0

    def test_tuple_type_init_invalid_element_types(self) -> None:
        with pytest.raises(CtyTupleValidationError, match="element_types must be a tuple"):
            CtyTuple(element_types=[CtyString()])
        with pytest.raises(CtyTupleValidationError, match="Element type at index 1 must be a CtyType"):
            CtyTuple(element_types=(CtyString(), "not-a-type"))

    def test_tuple_type_string_representation(self) -> None:
        simple_tuple = CtyTuple(element_types=(CtyString(), CtyNumber()))
        assert str(simple_tuple) == "tuple([string, number])"

    def test_tuple_type_string_representation_empty(self) -> None:
        empty_tuple = CtyTuple(element_types=())
        assert str(empty_tuple) == "tuple([])"


# 🌊🪢🔚
