# tests/test_cty_type_conversion.py



from pyvider.cty import CtyString


def test_type_eq_hash_consistency() -> None:


    t = CtyString()

    assert t == t
    assert hash(t) == hash(t)
    assert t in {t}
