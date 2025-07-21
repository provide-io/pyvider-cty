import pytest
from pyvider.cty.conversion.raw_to_cty import _unify_types
from pyvider.cty.types import CtyDynamic, CtyString, CtyNumber


def test_unify_types_empty():
    assert _unify_types(set()) == CtyDynamic()

def test_unify_types_single():
    assert _unify_types({CtyString()}) == CtyString()

def test_unify_types_all_same():
    assert _unify_types({CtyString(), CtyString()}) == CtyString()

def test_unify_types_different():
    assert _unify_types({CtyString(), CtyNumber()}) == CtyDynamic()
