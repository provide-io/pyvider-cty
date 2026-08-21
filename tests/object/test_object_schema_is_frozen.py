#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""A `CtyObject`'s schema cannot change after construction.

`CtyObject` is hashable and its hash reads `attribute_types`. go-cty's
`cty.Object()` copies the caller's map at construction for the same reason; a
type that is used as a dict key or cached anywhere must not be able to change
its own hash.
"""

import pytest

from pyvider.cty import CtyNumber, CtyObject, CtyString
from pyvider.cty.exceptions import CtyAttributeValidationError


def test_callers_dict_is_copied_so_hash_is_stable() -> None:
    attrs = {"a": CtyString()}
    obj = CtyObject(attribute_types=attrs)
    before = hash(obj)
    attrs["b"] = CtyNumber()
    assert hash(obj) == before
    assert set(obj.attribute_types) == {"a"}


def test_attribute_types_refuses_mutation() -> None:
    obj = CtyObject(attribute_types={"a": CtyString()})
    with pytest.raises(TypeError):
        obj.attribute_types["b"] = CtyNumber()  # type: ignore[index]
    with pytest.raises(TypeError):
        obj.attribute_types.pop("a")
    assert set(obj.attribute_types) == {"a"}


def test_attribute_types_is_still_a_dict() -> None:
    """Every `isinstance(..., dict)` check in this package and its consumers keeps working."""
    obj = CtyObject(attribute_types={"a": CtyString()})
    assert isinstance(obj.attribute_types, dict)


def test_optional_name_not_in_schema_is_refused_at_construction() -> None:
    with pytest.raises(CtyAttributeValidationError, match="Unknown optional attributes: ghost"):
        CtyObject(attribute_types={"a": CtyString()}, optional_attributes={"ghost"})


def test_empty_object_builds() -> None:
    obj = CtyObject()
    assert obj.attribute_types == {}
    assert isinstance(obj.attribute_types, dict)
