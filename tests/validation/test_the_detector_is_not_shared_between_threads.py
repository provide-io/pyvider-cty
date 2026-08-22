#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""One detector serves every thread, so it must hold no thread's context.

`with_recursion_detection` allocates a single `RecursionDetector` per decorated
function, at decoration time. Every thread that validates through that function
uses that one instance. The decorator used to assign the calling thread's
context onto it -- `_detector.context = context` -- and the detector then read
`self.context` a dozen-odd lines later. Between the write and the reads, any
other thread could assign its own, so a thread could count its depth into
somebody else's context, mark cycles in somebody else's graph, and read a
`validation_stopped` flag that belonged to another validation entirely.

The existing concurrency test did not catch it: it checks that results are
correct, and a corrupted counter mostly still produces a correct *result* for
small values. What follows watches the context identity itself.
"""

from __future__ import annotations

import sys
import threading
from typing import Any

import pytest

from pyvider.cty import CtyList, CtyObject, CtyString
from pyvider.cty.validation import recursion

INNER = CtyObject({"a": CtyString(), "b": CtyString()})
LIST = CtyList(element_type=INNER)
PAYLOAD: list[dict[str, str]] = [{"a": "x", "b": "y"} for _ in range(12)]

THREADS = 4
ROUNDS = 400


@pytest.fixture
def eager_switching() -> Any:
    """Force the interpreter to switch threads often enough to expose the window."""
    previous = sys.getswitchinterval()
    sys.setswitchinterval(1e-6)
    yield
    sys.setswitchinterval(previous)


def _run_watching_context_identity() -> list[str]:
    """Validate on several threads, recording any read of a foreign context."""
    foreign: list[str] = []
    original = recursion.RecursionDetector.should_continue_validation

    def spy(self: Any, value: Any, current_path: str = "", /) -> Any:
        # What this detector is about to read, against what this thread owns.
        if self.context is not recursion.get_recursion_context():
            foreign.append(threading.current_thread().name)
        return original(self, value, current_path)

    recursion.RecursionDetector.should_continue_validation = spy  # type: ignore[method-assign]
    barrier = threading.Barrier(THREADS)

    def work() -> None:
        # Started together, so the threads are inside the window at the same time.
        barrier.wait()
        for _ in range(ROUNDS):
            LIST.validate(PAYLOAD)

    try:
        threads = [threading.Thread(target=work, name=f"validator-{i}") for i in range(THREADS)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
    finally:
        recursion.RecursionDetector.should_continue_validation = original  # type: ignore[method-assign]

    return foreign


@pytest.mark.usefixtures("eager_switching")
def test_no_thread_ever_reads_another_threads_context() -> None:
    """The reproduction, as a regression test.

    Before the fix this recorded on the order of a thousand foreign reads over
    these four threads; the count is asserted at zero rather than at a threshold
    because one is already a corrupted validation.
    """
    assert _run_watching_context_identity() == []


def test_the_detector_holds_no_context_of_its_own() -> None:
    """The property that makes the above true, stated directly."""
    detector = recursion.RecursionDetector()

    assert detector._pinned is None
    assert detector.context is recursion.get_recursion_context()


def test_a_detector_reports_the_context_of_whichever_thread_asks() -> None:
    shared = recursion.RecursionDetector()
    seen: dict[str, Any] = {}
    ready = threading.Barrier(2)

    def look(tag: str) -> None:
        ready.wait()
        seen[tag] = (shared.context, recursion.get_recursion_context())

    threads = [threading.Thread(target=look, args=(tag,)) for tag in ("one", "two")]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    for from_detector, from_thread in seen.values():
        assert from_detector is from_thread
    assert seen["one"][0] is not seen["two"][0]


def test_an_explicitly_pinned_context_is_still_honoured() -> None:
    """Reading metrics off a finished run passes the context in deliberately."""
    pinned = recursion.RecursionContext()
    detector = recursion.RecursionDetector(pinned)

    assert detector.context is pinned
    assert detector.context is not recursion.get_recursion_context()


def test_the_shared_detector_can_no_longer_be_given_a_context() -> None:
    """The old pattern is now impossible rather than merely discouraged."""
    with pytest.raises(AttributeError):
        recursion.RecursionDetector().context = recursion.RecursionContext()  # type: ignore[misc]


# 🌊🪢🔚
