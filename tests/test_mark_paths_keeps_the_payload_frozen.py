#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`mark_with_paths` hands back a map or object payload as frozen as it got it.

Both halves rebuilt a mapping with a plain `dict(...)`, so a value went in
holding a `FrozenDict` and came out holding a plain `dict`. Equality still held,
which is why nothing caught it, but the two are not interchangeable here:

  * `FrozenDict` is what makes a mapping payload memoizable. `collect_marks_deep`
    only takes its memo when the walk proves the subtree immutable, and a plain
    dict fails that test -- so a round trip through `mark_with_paths` silently
    cost every later mark question a full re-walk. That gate exists because a
    memo over something that can still change under-reports, and an
    under-reporting mark memo is a silent declassification.
  * A frozen payload refuses `value.value[k] = x`, which is a documented 0.5.0
    breaking change made deliberately: the silent alternative corrupted
    sensitivity tracking.

So the downgrade quietly undid both, on the one code path whose entire job is to
put sensitivity back. `_strip` is the half that matters most: the value it
returns is what goes to the serializer.
"""

from __future__ import annotations

from pyvider.cty import CtyMap, CtyObject, CtyString
from pyvider.cty.mark_paths import mark_with_paths, unmark_deep_with_paths
from pyvider.cty.marks import collect_marks_deep
from pyvider.cty.values.frozen import FrozenDict

SENSITIVE = "sensitive"


def test_a_map_payload_survives_the_round_trip_frozen() -> None:
    value = CtyMap(element_type=CtyString()).validate({"k": CtyString().validate("v").with_marks({SENSITIVE})})
    assert isinstance(value.value, FrozenDict)

    restored = mark_with_paths(*unmark_deep_with_paths(value))

    assert isinstance(restored.value, FrozenDict)


def test_an_object_payload_survives_the_round_trip_frozen() -> None:
    value = CtyObject(attribute_types={"a": CtyString()}).validate(
        {"a": CtyString().validate("v").with_marks({SENSITIVE})}
    )

    restored = mark_with_paths(*unmark_deep_with_paths(value))

    assert isinstance(restored.value, FrozenDict)


def test_the_round_trip_restores_the_marks() -> None:
    """The downgrade is only worth fixing if the thing still works."""
    value = CtyMap(element_type=CtyString()).validate({"k": CtyString().validate("v").with_marks({SENSITIVE})})

    restored = mark_with_paths(*unmark_deep_with_paths(value))

    assert restored == value
    assert collect_marks_deep(restored) == frozenset({SENSITIVE})


def test_the_restored_payload_refuses_mutation() -> None:
    """The 0.5.0 contract: a mapping payload cannot be assigned into."""
    import pytest

    value = CtyMap(element_type=CtyString()).validate({"k": CtyString().validate("v").with_marks({SENSITIVE})})
    restored = mark_with_paths(*unmark_deep_with_paths(value))

    with pytest.raises(TypeError):
        restored.value["k"] = CtyString().validate("other")


# 🐍🏗️🔚
