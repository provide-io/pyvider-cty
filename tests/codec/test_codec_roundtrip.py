from pyvider.cty import CtyMap, CtyBool
def test_type_codec_roundtrip_map():
    cty_map_type = CtyMap(element_type=CtyBool())
    assert str(cty_map_type) == "map(bool)"
