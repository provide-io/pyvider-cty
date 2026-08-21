#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""A list is ordered, so only an ordered input can become one.

`CtyList.validate` accepted a `set` or `frozenset`, and the element order it
produced changed with `PYTHONHASHSEED`: the same configuration produced a
different list, and therefore different state bytes, in different processes.
`CtySet` keeps accepting a list, because canonical set ordering makes that
deterministic.
"""

import pytest

from pyvider.cty import CtyList, CtySet, CtyString
from pyvider.cty.exceptions import CtyListValidationError


@pytest.mark.parametrize("unordered", [{"a", "b"}, frozenset({"a", "b"})])
def test_list_refuses_a_set(unordered: object) -> None:
    with pytest.raises(CtyListValidationError, match="Expected list, tuple"):
        CtyList(element_type=CtyString()).validate(unordered)


def test_list_still_accepts_a_tuple() -> None:
    assert [e.value for e in CtyList(element_type=CtyString()).validate(("a", "b")).value] == ["a", "b"]


def test_set_still_accepts_a_list() -> None:
    assert {e.value for e in CtySet(element_type=CtyString()).validate(["a", "b"]).value} == {"a", "b"}
