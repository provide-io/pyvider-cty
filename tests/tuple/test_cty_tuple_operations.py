#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


import pytest

from pyvider.cty import (
    CtyBool,
    CtyNumber,
    CtyString,
    CtyTuple,
    CtyValue,
)


class TestCtyTupleOperations:
    @pytest.fixture
    def tuple_type(self):
        return CtyTuple(element_types=(CtyString(), CtyNumber(), CtyBool()))

    @pytest.fixture
    def tuple_value(self, tuple_type):
        return tuple_type.validate(("data", 123, False))

    def test_element_at_valid_indices(self, tuple_type, tuple_value) -> None:
        el0 = tuple_type.element_at(tuple_value, 0)
        assert isinstance(el0, CtyValue) and el0.value == "data"
        el_neg1 = tuple_type.element_at(tuple_value, -1)
        assert isinstance(el_neg1, CtyValue) and el_neg1.type.equal(CtyBool()) and el_neg1.value is False

    def test_slice_valid(self, tuple_type, tuple_value) -> None:
        slice02_val = tuple_type.slice(tuple_value, 0, 2)
        assert isinstance(slice02_val, CtyValue) and isinstance(slice02_val.type, CtyTuple)
        assert len(slice02_val.type.element_types) == 2
        assert slice02_val.value[0].value == "data"

    def test_value_length(self, tuple_value) -> None:
        assert len(tuple_value) == 3


# 🌊🪢🔚
