#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""The third element of an `["object", {...}, [...]]` type spec is a list of names.

It was fed straight to `frozenset(...)`, so the string `"ab"` became the two
optional attributes `a` and `b`. go-cty decodes it as `[]string` and refuses
anything else; so does this parser now, and a name that is not in the schema
is refused at the same boundary.
"""

import pytest

from pyvider.cty.exceptions import CtyValidationError
from pyvider.cty.parser import parse_tf_type_to_ctytype


def test_a_list_of_names_is_accepted() -> None:
    t = parse_tf_type_to_ctytype(["object", {"a": "string", "b": "string"}, ["a"]])
    assert t.optional_attributes == frozenset({"a"})


@pytest.mark.parametrize("bad", ["a", 1, {"a": True}, [1], ["a", 2]])
def test_anything_but_a_list_of_strings_is_refused(bad: object) -> None:
    with pytest.raises(CtyValidationError, match="optional attribute names"):
        parse_tf_type_to_ctytype(["object", {"a": "string"}, bad])


def test_a_name_outside_the_schema_is_refused() -> None:
    with pytest.raises(CtyValidationError, match="Unknown optional attributes: ghost"):
        parse_tf_type_to_ctytype(["object", {"a": "string"}, ["ghost"]])
