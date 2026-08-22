#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""A `CtyValue` built directly, bypassing `validate`, is as immutable as one that was not.

`validate` has handed back a `FrozenDict` or a tuple since 0.5.0, but
`CtyValue(vtype, {"a": ...})` kept the caller's dict -- aliased, mutable through
`value.value`, and its hash changed under the caller's later edits. The same
for a list payload and for a `set` passed as `marks`, which also made
`hash(value)` raise. The constructor now freezes a raw payload shallowly and
the marks always, so the documented "always use validate" is a guard rather
than a caveat.
"""

import pytest

from pyvider.cty import CtyList, CtyMap, CtyObject, CtySet, CtyString, CtyValue
from pyvider.cty.types import CtyCapsule
from pyvider.cty.values.frozen import FrozenDict

S = CtyString()


def test_dict_payload_is_copied_into_a_frozendict() -> None:
    raw = {"a": S.validate("x")}
    value = CtyValue(CtyObject({"a": S}), raw)
    assert isinstance(value.value, FrozenDict)
    with pytest.raises(TypeError):
        value.value["a"] = S.validate("y")  # type: ignore[index]
    before = hash(value)
    raw["a"] = S.validate("z")
    assert value.value["a"].value == "x"
    assert hash(value) == before


def test_list_payload_becomes_a_tuple() -> None:
    raw = [S.validate("x")]
    value = CtyValue(CtyList(element_type=S), raw)
    assert isinstance(value.value, tuple)
    raw.append(S.validate("y"))
    assert len(value.value) == 1


def test_set_payload_becomes_a_frozenset() -> None:
    raw = {S.validate("x")}
    value = CtyValue(CtySet(element_type=S), raw)
    assert isinstance(value.value, frozenset)
    raw.add(S.validate("y"))
    assert len(value.value) == 1


def test_marks_are_always_a_frozenset() -> None:
    raw_marks = {"sensitive"}
    value = CtyValue(S, "x", marks=raw_marks)  # type: ignore[arg-type]
    assert isinstance(value.marks, frozenset)
    hash(value)
    raw_marks.add("other")
    assert value.marks == frozenset({"sensitive"})


def test_an_already_frozen_payload_is_not_copied() -> None:
    validated = CtyMap(element_type=S).validate({"a": "x"})
    assert isinstance(validated.value, FrozenDict)
    rebuilt = CtyValue(validated.type, validated.value)
    assert rebuilt.value is validated.value
    listed = CtyList(element_type=S).validate(["x"])
    assert CtyValue(listed.type, listed.value).value is listed.value


def test_a_capsule_payload_is_left_alone() -> None:
    """A capsule carries an arbitrary Python object; freezing it would break the contract."""
    payload = [1, 2, 3]
    value = CtyValue(CtyCapsule("Thing", list), payload)
    assert value.value is payload


def test_a_dynamic_wrapper_is_left_alone() -> None:
    from pyvider.cty import CtyDynamic

    inner = S.validate("x")
    wrapped = CtyValue(CtyDynamic(), inner)
    assert wrapped.value is inner
