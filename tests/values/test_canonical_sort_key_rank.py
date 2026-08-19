#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""A validated container takes the *known* rank, never the null or unknown one.

This file exists to falsify one specific hypothesis, and it is worth writing
down which, because the hypothesis is otherwise unfalsifiable from the record.

On 2026-08-16 a parallel run of the suite under `-n auto` produced five
`assert 0 == 2` failures spread across four xdist workers, all of them in
`TestCanonicalSortKey`. Two accounts explain that signature and the captured
data cannot separate them (see the entry in `.provide/GO-CTY-PARITY.md`):

1.  **A mixed tree.** Commit `a98a920` inverted the three ranks -- they were
    null 0, unknown 1, known 2, and go-cty's `setRules.Less`
    (`cty/set_internals.go:99-110`) ranks known 0, unknown 1, null 2 -- and it
    changed the ranks and the tests in the same commit. A `git checkout`
    landing while a run was in flight leaves early workers holding the old
    test file and late workers holding the new source, and that mixture
    reproduces all five failures deterministically. This is reproduced and
    understood.

2.  **A real fault**, in which a *validated* container reports itself null (or
    otherwise takes a non-known rank) in its canonical sort key. Under the
    ranks in force at the time a null keyed as `(0,)` and the old test asserted
    `key[0] == 2`, so this account predicts the identical `assert 0 == 2`
    string, on the identical four tests, with the identical two tests passing.

The datum that would have discriminated -- which xdist worker ran
`test_canonical_sort_key_null` -- was never captured, so the archaeology is
closed as undecidable. What is *not* undecidable is whether account 2 is true
of the library now, and whether it would be noticed if it ever became true.
That is what the tests below assert: exhaustively, for every container type
this library has, for the empty case as well as the populated one, for a
`CtyDynamic` wrapping each, and for containers whose *elements* are null or
unknown -- which is the only plausible route by which nullness could leak
upward onto a container in the first place.

**If a test in this file fails, the flake was real and it is account 2.** Under
the current ranks that surfaces as `assert 2 == 0` (a container keying as null)
or `assert 1 == 0` (a container keying as unknown) -- the inverse of the string
in the 2026-08-16 sighting, because the ranks were inverted in between. It is
not a test-ordering problem and it is not a stale checkout: these assertions
read only the value in front of them.

The rank scheme itself is pinned here too. `_canonical_sort_key` is this
library's only notion of value identity -- `CtySet.validate` de-duplicates with
it, `__hash__` hashes it, and the codec sorts a set's wire bytes by it -- so a
silent flip of the three ranks is a change to serialized state that only a byte
comparison against go-cty would otherwise catch.
"""

from __future__ import annotations

from collections.abc import Callable
import threading
from typing import Any

import pytest

from pyvider.cty import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
    CtyTuple,
    CtyValue,
)

# The three ranks, spelled out as names so a failure reads as a claim about
# go-cty's ordering rather than as a comparison of two integers.
KNOWN_RANK = 0
UNKNOWN_RANK = 1
NULL_RANK = 2


def _list_populated() -> CtyValue[Any]:
    return CtyList(element_type=CtyString()).validate(["a", "b"])


def _list_empty() -> CtyValue[Any]:
    return CtyList(element_type=CtyString()).validate([])


def _list_nested() -> CtyValue[Any]:
    return CtyList(element_type=CtyList(element_type=CtyString())).validate([["a"], []])


def _set_populated() -> CtyValue[Any]:
    return CtySet(element_type=CtyString()).validate({"a", "b"})


def _set_empty() -> CtyValue[Any]:
    return CtySet(element_type=CtyString()).validate(set())


def _set_nested() -> CtyValue[Any]:
    return CtySet(element_type=CtyList(element_type=CtyString())).validate([["a"], []])


def _map_populated() -> CtyValue[Any]:
    return CtyMap(element_type=CtyString()).validate({"b": "2", "a": "1"})


def _map_empty() -> CtyValue[Any]:
    return CtyMap(element_type=CtyString()).validate({})


def _map_nested() -> CtyValue[Any]:
    inner = CtyObject(attribute_types={"n": CtyNumber(), "s": CtySet(element_type=CtyString())})
    return CtyMap(element_type=inner).validate({"k": {"n": 1, "s": ["x"]}})


def _object_populated() -> CtyValue[Any]:
    return CtyObject(attribute_types={"name": CtyString(), "age": CtyNumber()}).validate(
        {"name": "Alice", "age": 30}
    )


def _object_empty() -> CtyValue[Any]:
    return CtyObject(attribute_types={}).validate({})


def _object_nested() -> CtyValue[Any]:
    return CtyObject(
        attribute_types={
            "l": CtyList(element_type=CtyMap(element_type=CtyString())),
            "s": CtySet(element_type=CtyNumber()),
            "o": CtyObject(attribute_types={"b": CtyBool()}),
        }
    ).validate({"l": [{"m": "v"}], "s": [1, 2], "o": {"b": True}})


def _tuple_populated() -> CtyValue[Any]:
    return CtyTuple(element_types=(CtyString(), CtyNumber())).validate(["a", 1])


def _tuple_empty() -> CtyValue[Any]:
    return CtyTuple(element_types=()).validate([])


def _tuple_nested() -> CtyValue[Any]:
    return CtyTuple(
        element_types=(
            CtyList(element_type=CtyString()),
            CtyMap(element_type=CtyString()),
            CtyTuple(element_types=()),
        )
    ).validate([["a"], {"k": "v"}, []])


#: Every container shape this library has, in three populations each: a
#: populated value, an EMPTY value (the obvious suspect for a null-ish rank,
#: since an empty payload is the one that most resembles "no payload"), and a
#: nested combination.
CONTAINER_BUILDERS: list[tuple[str, Callable[[], CtyValue[Any]]]] = [
    ("list-populated", _list_populated),
    ("list-empty", _list_empty),
    ("list-nested", _list_nested),
    ("set-populated", _set_populated),
    ("set-empty", _set_empty),
    ("set-nested", _set_nested),
    ("map-populated", _map_populated),
    ("map-empty", _map_empty),
    ("map-nested", _map_nested),
    ("object-populated", _object_populated),
    ("object-empty", _object_empty),
    ("object-nested", _object_nested),
    ("tuple-populated", _tuple_populated),
    ("tuple-empty", _tuple_empty),
    ("tuple-nested", _tuple_nested),
]


def _dynamic_wrapping(build: Callable[[], CtyValue[Any]]) -> Callable[[], CtyValue[Any]]:
    """A `CtyDynamic` wrapping whatever `build` produces.

    Included because a dynamic mirrors its payload's nullness onto itself in
    `CtyValue.__attrs_post_init__`, which is the one place in this package
    where a container's `is_null` is written after construction. If nullness
    were ever going to leak onto a validated container, that is the code that
    would do it.
    """

    def _build() -> CtyValue[Any]:
        return CtyDynamic().validate(build())

    return _build


DYNAMIC_BUILDERS: list[tuple[str, Callable[[], CtyValue[Any]]]] = [
    (f"dynamic({name})", _dynamic_wrapping(build)) for name, build in CONTAINER_BUILDERS
]

ALL_BUILDERS = CONTAINER_BUILDERS + DYNAMIC_BUILDERS


class TestValidatedContainersTakeTheKnownRank:
    """The regression guard for the real-fault account of the 2026-08-16 flake.

    A failure here means a `validate` call returned a container that reports
    itself null or unknown -- which is exactly the hypothesis the tracker
    records as "untouched by any evidence gathered so far", and the one that
    could not be ruled out from the captured transcript. It is asserted
    directly rather than inferred from a sort order, so a failure names the
    fault instead of pointing at a downstream symptom.
    """

    def test_the_three_ranks_are_go_ctys(self) -> None:
        """known 0, unknown 1, null 2 -- go-cty's `setRules.Less` order.

        These ranks reach the wire through the set codec, so an inversion is a
        change to serialized state that Terraform compares textually. They were
        inverted before `a98a920`; this is the assertion that a re-inversion
        has to walk past.
        """
        assert CtyString().validate("a")._canonical_sort_key()[0] == KNOWN_RANK
        assert CtyValue.unknown(CtyString())._canonical_sort_key() == (UNKNOWN_RANK,)
        assert CtyValue.null(CtyString())._canonical_sort_key() == (NULL_RANK,)

    @pytest.mark.parametrize(
        "build",
        [pytest.param(build, id=name) for name, build in ALL_BUILDERS],
    )
    def test_validated_container_is_neither_null_nor_unknown(self, build: Callable[[], CtyValue[Any]]) -> None:
        """A container that came out of `validate` is a known value."""
        value = build()
        assert value.is_null is False
        assert value.is_unknown is False

    @pytest.mark.parametrize(
        "build",
        [pytest.param(build, id=name) for name, build in ALL_BUILDERS],
    )
    def test_validated_container_takes_the_known_rank(self, build: Callable[[], CtyValue[Any]]) -> None:
        """...and so its canonical sort key opens with the known rank.

        The three assertions are deliberately redundant. The first is the
        positive claim; the other two name the two wrong answers, so a failure
        message says which of them was returned rather than leaving the reader
        to decode a rank integer.
        """
        key = build()._canonical_sort_key()
        assert key[0] == KNOWN_RANK
        assert key != (NULL_RANK,), "a validated container reported itself null"
        assert key != (UNKNOWN_RANK,), "a validated container reported itself unknown"

    @pytest.mark.parametrize(
        "build",
        [pytest.param(build, id=name) for name, build in ALL_BUILDERS],
    )
    def test_validated_container_key_carries_its_type_rank(self, build: Callable[[], CtyValue[Any]]) -> None:
        """A known key is `(0, type_rank, *members)`, not the bare `(0,)`.

        Without this, a container degenerating to a one-element key would still
        satisfy the rank assertion above while having lost every member --
        which is a different bug with the same first element.
        """
        value = build()
        key = value._canonical_sort_key()
        assert len(key) >= 2
        assert key[1] == value.type._type_order


class TestNullnessDoesNotLeakFromElementsOntoContainers:
    """A container holding a null or an unknown is still a *known* container.

    This is the mechanism by which account 2 could have been true: an element's
    nullness being hoisted onto the container that holds it. go-cty draws the
    line at `IsKnown` vs `IsWhollyKnown` and this library follows it -- a list
    of `["a", null]` is a known list of length two, not a null list -- so the
    container keeps the known rank and only the element takes the null one.
    """

    @pytest.mark.parametrize(
        ("build", "expected_member_rank"),
        [
            pytest.param(
                lambda: CtyList(element_type=CtyString()).validate(["a", None]),
                NULL_RANK,
                id="list-with-null",
            ),
            pytest.param(
                lambda: CtyList(element_type=CtyString()).validate(["a", CtyValue.unknown(CtyString())]),
                UNKNOWN_RANK,
                id="list-with-unknown",
            ),
            pytest.param(
                lambda: CtySet(element_type=CtyString()).validate(["a", None]),
                NULL_RANK,
                id="set-with-null",
            ),
            pytest.param(
                lambda: CtySet(element_type=CtyString()).validate(["a", CtyValue.unknown(CtyString())]),
                UNKNOWN_RANK,
                id="set-with-unknown",
            ),
            pytest.param(
                lambda: CtyMap(element_type=CtyString()).validate({"a": "x", "b": None}),
                NULL_RANK,
                id="map-with-null",
            ),
            pytest.param(
                lambda: CtyMap(element_type=CtyString()).validate(
                    {"a": "x", "b": CtyValue.unknown(CtyString())}
                ),
                UNKNOWN_RANK,
                id="map-with-unknown",
            ),
            pytest.param(
                lambda: CtyObject(attribute_types={"a": CtyString(), "b": CtyString()}).validate(
                    {"a": "x", "b": None}
                ),
                NULL_RANK,
                id="object-with-null",
            ),
            pytest.param(
                lambda: CtyObject(attribute_types={"a": CtyString(), "b": CtyString()}).validate(
                    {"a": "x", "b": CtyValue.unknown(CtyString())}
                ),
                UNKNOWN_RANK,
                id="object-with-unknown",
            ),
            pytest.param(
                lambda: CtyTuple(element_types=(CtyString(), CtyString())).validate(["a", None]),
                NULL_RANK,
                id="tuple-with-null",
            ),
            pytest.param(
                lambda: CtyTuple(element_types=(CtyString(), CtyString())).validate(
                    ["a", CtyValue.unknown(CtyString())]
                ),
                UNKNOWN_RANK,
                id="tuple-with-unknown",
            ),
        ],
    )
    def test_container_keeps_the_known_rank(
        self, build: Callable[[], CtyValue[Any]], expected_member_rank: int
    ) -> None:
        """The container ranks known; the offending member ranks null/unknown."""
        value = build()
        key = value._canonical_sort_key()

        assert value.is_null is False
        assert value.is_unknown is False
        assert key[0] == KNOWN_RANK, "an element's nullness leaked onto its container"

        # And the member itself did take the rank, so this is not passing
        # because the null or unknown was quietly dropped on the way in. A
        # mapping's members are `(_PRESENT, name, member_key)` triples; a
        # sequence's are the member keys themselves. Both end with the
        # exhaustion terminator, which is not a member and is sliced off.
        is_mapping = isinstance(value.type, CtyMap | CtyObject)
        member_keys = [member[2] if is_mapping else member for member in key[2:-1]]
        assert (expected_member_rank,) in member_keys


class TestRankInvariantUnderConcurrentValidation:
    """The same invariant, asserted while several threads validate at once.

    Bounded and cheap on purpose. The 2026-08-16 sighting was a parallel run,
    and the only shared state that could plausibly cross tests here is the
    inference cache (`pyvider.cty.conversion.inference_cache`, whose
    `ContextVar` tokens the root `conftest.py` resets per test) and the
    memoized mark walks written back onto frozen values with
    `object.__setattr__` (`marks.py:110`, `marks.py:256`). xdist workers are
    *processes* and cannot share any of it, so this can never reproduce the
    sighting -- what it can do is catch a shared-state fault of the same shape
    inside one interpreter, which is the only version of the hypothesis a test
    is able to reach.
    """

    def test_rank_holds_across_threads(self) -> None:
        """Eight threads, every container shape, asserting the known rank."""
        failures: list[str] = []
        barrier = threading.Barrier(8)

        def worker() -> None:
            barrier.wait()
            for _ in range(25):
                for name, build in ALL_BUILDERS:
                    value = build()
                    key = value._canonical_sort_key()
                    if key[0] != KNOWN_RANK or value.is_null or value.is_unknown:
                        failures.append(f"{name}: is_null={value.is_null} key={key!r}")

        threads = [threading.Thread(target=worker) for _ in range(8)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        assert failures == []

    def test_rank_holds_when_threads_share_the_inference_cache_path(self) -> None:
        """The same, driven through type inference rather than explicit types.

        `CtyDynamic().validate(raw)` goes through `infer_cty_type_from_raw`,
        which is the one path in this package with a process-wide cache behind
        it. Threads get their own `ContextVar` values, so the cache should be
        per-thread -- this asserts that the answer does not depend on that
        being true.
        """
        raws: list[Any] = [
            {"a": ["x", "y"], "b": {"c": 1}},
            [],
            {},
            [[], {}, ""],
            {"nested": {"deep": [{"k": True}]}},
        ]
        failures: list[str] = []
        barrier = threading.Barrier(8)

        def worker() -> None:
            barrier.wait()
            for _ in range(25):
                for raw in raws:
                    value = CtyDynamic().validate(raw)
                    key = value._canonical_sort_key()
                    if key[0] != KNOWN_RANK or value.is_null or value.is_unknown:
                        failures.append(f"{raw!r}: is_null={value.is_null} key={key!r}")

        threads = [threading.Thread(target=worker) for _ in range(8)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        assert failures == []


# 🌊🪢🔚
