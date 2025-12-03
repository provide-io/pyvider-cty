#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from pyvider.cty import CtyNumber, CtyObject, CtySet, CtyString
from pyvider.cty.conversion.raw_to_cty import infer_cty_type_from_raw


def test_infer_set_of_strings() -> None:
    inferred_type = infer_cty_type_from_raw({"a", "b"})
    assert isinstance(inferred_type, CtySet)
    assert isinstance(inferred_type.element_type, CtyString)


def test_infer_object_with_non_identifier_keys() -> None:
    inferred_type = infer_cty_type_from_raw({"a-b": 1})
    # All string-keyed dicts should be inferred as objects.
    assert isinstance(inferred_type, CtyObject)
    assert isinstance(inferred_type.attribute_types["a-b"], CtyNumber)


def test_infer_empty_dict() -> None:
    from pyvider.cty import CtyObject

    inferred_type = infer_cty_type_from_raw({})
    assert isinstance(inferred_type, CtyObject)
    assert inferred_type.attribute_types == {}


def test_infer_from_cty_value() -> None:
    from pyvider.cty import CtyDynamic, CtyString

    val = CtyString().validate("hello")
    inferred = infer_cty_type_from_raw(val)
    assert isinstance(inferred, CtyDynamic)


def test_infer_from_attrs_object() -> None:
    import attrs

    from pyvider.cty import CtyNumber, CtyObject, CtyString

    @attrs.define
    class MyAttrs:
        a: str
        b: int

    inst = MyAttrs("hi", 1)
    inferred = infer_cty_type_from_raw(inst)
    assert isinstance(inferred, CtyObject)
    assert inferred.attribute_types["a"].equal(CtyString())
    assert inferred.attribute_types["b"].equal(CtyNumber())


def test_infer_dict_with_cty_values() -> None:
    from pyvider.cty import CtyNumber, CtyObject, CtyString

    val = {
        "a": CtyString().validate("hello"),
        "b": CtyNumber().validate(123),
    }
    inferred = infer_cty_type_from_raw(val)
    assert isinstance(inferred, CtyObject)
    assert inferred.attribute_types["a"].equal(CtyString())
    assert inferred.attribute_types["b"].equal(CtyNumber())


# 🌊🪢🔚
