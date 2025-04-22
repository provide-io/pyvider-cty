# tests/test_cty_type_conversion.py

import pytest

import re

from pyvider.cty import (
    CtyType, CtyString, CtyNumber, CtyBool, CtyDynamic,
    CtyList, CtyMap, CtySet, CtyTuple
)

def test_type_eq_hash_consistency():

    from pyvider.cty import (
        CtyType, CtyString, CtyNumber, CtyBool, CtyDynamic,
        CtyList, CtyMap, CtySet, CtyTuple
    )

    t = CtyString()

    assert t == t
    assert hash(t) == hash(t)
    assert t in {t}
