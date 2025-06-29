import pytest
from pyvider.cty import CtyDynamic, CtyNumber, CtyString, CtyTuple

class TestCtyTupleComparison:
    def test_type_usable_as_compatible_elements(self) -> None:
        t1 = CtyTuple(element_types=(CtyString(), CtyNumber()))
        t2_dynamic = CtyTuple(element_types=(CtyDynamic(), CtyDynamic()))
        assert t1.usable_as(t2_dynamic)
        assert not t2_dynamic.usable_as(t1)
