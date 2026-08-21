#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`convert` never performs a conversion `can_convert_unsafe` denies -- over generated types.

`can_convert_unsafe` is 86 lines that mirror `convert`'s 264 by hand, and
`test_can_convert_unsafe.py` checks the two against each other over 81
hand-picked pairs. This is the same contract over the generated population the
oracle suites use: every value shape that has ever been wrong, against every
type shape `unify` has ever been wrong about, including `dynamic` three levels
down and empty tuples and objects. "Unsafe" allows `convert` to refuse on the
*value*, so the direction checked is the one that is never allowed to fail --
a conversion that happened must have been one the predicate permits.
"""

from __future__ import annotations

from typing import Any

from hypothesis import HealthCheck, given, settings

from pyvider.cty import CtyType, CtyValue
from pyvider.cty.conversion import convert
from pyvider.cty.conversion.explicit import can_convert_unsafe
from pyvider.cty.exceptions import CtyError
from tests.compatibility._strategies import cases, types


@given(case=cases(), target=types(max_leaves=6))
@settings(max_examples=400, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_convert_never_does_what_the_predicate_denies(
    case: tuple[CtyType[Any], CtyValue[Any]], target: CtyType[Any]
) -> None:
    source_type, value = case
    if value.is_null or value.is_unknown:
        return  # `convert` answers these by asking the predicate, which proves nothing
    permitted = can_convert_unsafe(source_type, target)
    try:
        converted = convert(value, target)
    except CtyError:
        return  # a refusal on the value is always allowed under "unsafe"
    assert permitted, (
        f"convert performed {source_type} -> {target} on {value!r}, which can_convert_unsafe denied"
    )
    # The result type is not asserted against `target`: a `dynamic` element in
    # the target is resolved from the source (`_collection_target`), so
    # `list(list(string))` to `set(dynamic)` yields `set(list(string))`.
    assert converted is not None


# The case the property above found first, pinned so it cannot come back
# quietly: an empty collection has no element to fail on, so the elementwise
# conversion succeeded where the types alone say it cannot. go-cty decides a
# conversion on the types before it looks at a single element and refuses.
import pytest

from pyvider.cty import CtyList, CtyMap, CtyString
from pyvider.cty.exceptions import CtyConversionError


@pytest.mark.parametrize(
    ("source", "target"),
    [
        (CtyList(element_type=CtyString()), CtyList(element_type=CtyList(element_type=CtyString()))),
        (CtyMap(element_type=CtyString()), CtyMap(element_type=CtyList(element_type=CtyString()))),
    ],
    ids=["empty list", "empty map"],
)
def test_an_empty_collection_is_refused_when_its_element_type_cannot_convert(
    source: CtyType[Any], target: CtyType[Any]
) -> None:
    assert not can_convert_unsafe(source, target)
    empty = source.validate([] if isinstance(source, CtyList) else {})
    with pytest.raises(CtyConversionError):
        convert(empty, target)
