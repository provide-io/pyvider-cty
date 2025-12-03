#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from pyvider.cty import CtyBool, CtyDynamic, CtyNumber, CtyString, CtyTuple


class TestCtyTupleComparison:
    def test_type_usable_as_compatible_elements(self) -> None:
        t1 = CtyTuple(element_types=(CtyString(), CtyNumber()))
        t2_dynamic = CtyTuple(element_types=(CtyDynamic(), CtyDynamic()))
        assert t1.usable_as(t2_dynamic)
        assert not t2_dynamic.usable_as(t1)

    def test_equal(self) -> None:
        t1 = CtyTuple(element_types=(CtyString(), CtyNumber()))
        t2 = CtyTuple(element_types=(CtyString(), CtyNumber()))
        t3 = CtyTuple(element_types=(CtyString(), CtyBool()))
        t4 = CtyTuple(element_types=(CtyString(),))
        assert t1.equal(t2)
        assert not t1.equal(t3)
        assert not t1.equal(t4)
        assert not t1.equal(CtyString())


# 🌊🪢🔚
