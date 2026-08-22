#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""The third element of a wire type is an object's optional-attribute list.

go-cty writes `["object", {...}, ["a", "b"]]` and nothing else ever has a third
element. The check that those names are strings used to run before the kind
dispatch, so `["list", "string", "junk"]` was refused with a message about
*object* optional names, and `["list", "string", ["a"]]` was accepted with the
extra element silently dropped. Both are malformed; neither is an object.
"""

import pytest

from pyvider.cty import CtyList, CtyObject, CtyString
from pyvider.cty.exceptions import CtyValidationError
from pyvider.cty.parser import parse_tf_type_to_ctytype


def test_object_with_optional_names_parses() -> None:
    parsed = parse_tf_type_to_ctytype(["object", {"a": "string", "b": "string"}, ["b"]])
    assert parsed == CtyObject({"a": CtyString(), "b": CtyString()}, optional_attributes={"b"})


def test_object_with_non_list_optional_names_is_refused() -> None:
    with pytest.raises(CtyValidationError, match="optional attribute names must be a list of strings"):
        parse_tf_type_to_ctytype(["object", {"a": "string"}, "a"])


def test_object_with_non_string_optional_name_is_refused() -> None:
    with pytest.raises(CtyValidationError, match="optional attribute names must be a list of strings"):
        parse_tf_type_to_ctytype(["object", {"a": "string"}, [1]])


@pytest.mark.parametrize("kind", ["list", "set", "map"])
def test_collection_with_a_third_element_is_refused(kind: str) -> None:
    with pytest.raises(CtyValidationError, match="only an object type carries a third element"):
        parse_tf_type_to_ctytype([kind, "string", ["a"]])


def test_tuple_with_a_third_element_is_refused() -> None:
    with pytest.raises(CtyValidationError, match="only an object type carries a third element"):
        parse_tf_type_to_ctytype(["tuple", ["string"], ["a"]])


def test_two_element_collection_still_parses() -> None:
    assert parse_tf_type_to_ctytype(["list", "string"]) == CtyList(element_type=CtyString())
