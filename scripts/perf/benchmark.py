#!/usr/bin/env python3
"""
Benchmark scenarios for the hot paths in pyvider-cty.

Emits one JSON object on stdout so the same file can be run against two
different checkouts and the results diffed. Run it through
`scripts/perf/perf_report.py` (or `make perf-report`) rather than directly.

Each scenario is here because something once made it slower. Mark propagation
touches every `validate` and every stdlib call, so the cost of asking "does this
value carry a mark" lands on paths that used to be O(1) -- `length()` on a
20k-entry map once went from 0.003 ms to 2.7 ms a call that way, and nothing
caught it, because the only performance tests in the suite are gated behind
`--run-benchmarks` and never run.
"""

# Deliberately no sys.path manipulation anywhere in this file. It is run against
# two different checkouts and the tree under measurement is chosen entirely by
# PYTHONPATH -- inserting this script's own `src` would silently pin both runs to
# the working tree, and the comparison would then report every scenario as
# unchanged. Which is precisely what a broken harness looks like: a clean result.
import json
import sys
import time
from typing import Any

from pyvider.cty import (
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
)
from pyvider.cty.codec import cty_from_msgpack, cty_to_msgpack
import pyvider.cty.functions as F

REPEATS = 5


def best_of(fn: Any, repeats: int = REPEATS) -> float:
    """Milliseconds for the fastest run, which is the least noisy estimator."""
    fn()  # warm up: first call pays import and memo costs
    best = None
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        elapsed = time.perf_counter() - start
        best = elapsed if best is None else min(best, elapsed)
    return (best or 0.0) * 1000


def build_fixtures() -> dict[str, Any]:
    strings = CtyList(element_type=CtyString())
    string_set = CtySet(element_type=CtyString())
    string_map = CtyMap(element_type=CtyString())
    obj = CtyObject(attribute_types={"a": CtyString(), "b": CtyNumber()})
    objs = CtyList(element_type=obj)
    nested = CtyList(element_type=CtyList(element_type=CtyString()))

    raw_list = [str(i) for i in range(50_000)]
    raw_set = [str(i) for i in range(20_000)]
    raw_map = {str(i): str(i) for i in range(20_000)}
    raw_objs = [{"a": str(i), "b": i} for i in range(10_000)]
    raw_nested = [[str(i)] for i in range(10_000)]

    big_list = strings.validate(raw_list)
    big_map = string_map.validate(raw_map)
    big_objs = objs.validate(raw_objs)
    big_nested = nested.validate(raw_nested)

    # Marked variants. Their absence is why a 16,000x slowdown on the marked
    # path survived the benchmark that motivated the optimisation: everything
    # measured was unmarked, and the marked path is the one providers use for
    # every sensitive attribute.
    from pyvider.cty.marks import CtyMark

    sensitive = CtyMark("sensitive")
    marked_list = big_list.mark(sensitive)
    marked_map = big_map.mark(sensitive)

    return {
        "strings": strings,
        "string_set": string_set,
        "string_map": string_map,
        "objs": objs,
        "nested": nested,
        "raw_list": raw_list,
        "raw_set": raw_set,
        "raw_map": raw_map,
        "raw_objs": raw_objs,
        "raw_nested": raw_nested,
        "big_list": big_list,
        "big_map": big_map,
        "big_objs": big_objs,
        "big_nested": big_nested,
        "marked_list": marked_list,
        "marked_map": marked_map,
        "objs_packed": cty_to_msgpack(big_objs, objs),
    }


def scenarios(f: dict[str, Any]) -> dict[str, Any]:
    s = CtyString()
    return {
        # validation: every element passes through the mark machinery
        "validate list[50k]": lambda: f["strings"].validate(f["raw_list"]),
        "validate set[20k]": lambda: f["string_set"].validate(f["raw_set"]),
        "validate map[20k]": lambda: f["string_map"].validate(f["raw_map"]),
        "validate list[obj][10k]": lambda: f["objs"].validate(f["raw_objs"]),
        "validate nested list[10k]": lambda: f["nested"].validate(f["raw_nested"]),
        "revalidate list[50k]": lambda: f["strings"].validate(f["big_list"]),
        "dynamic validate obj list": lambda: CtyDynamic().validate(f["raw_objs"][:2000]),
        # stdlib: the wrapper collects marks from every argument on every call
        "fn length(list[50k]) x50": lambda: [F.length(f["big_list"]) for _ in range(50)],
        "fn length(map[20k]) x50": lambda: [F.length(f["big_map"]) for _ in range(50)],
        "fn upper(scalar) x20000": lambda: [F.upper(s.validate("ab")) for _ in range(20_000)],
        "fn equal(scalar) x20000": lambda: [F.equal(s.validate("a"), s.validate("a")) for _ in range(20_000)],
        "fn join(list[50k])": lambda: F.join(s.validate(","), f["big_list"]),
        "fn contains(list[50k], hit)": lambda: F.contains(f["big_list"], s.validate("0")),
        "fn contains(list[50k], miss)": lambda: F.contains(f["big_list"], s.validate("nope")),
        "fn keys(map[20k])": lambda: F.keys(f["big_map"]),
        # marked: every sensitive attribute a provider handles takes this path
        "fn length(MARKED list[50k]) x50": lambda: [F.length(f["marked_list"]) for _ in range(50)],
        "fn length(MARKED map[20k]) x50": lambda: [F.length(f["marked_map"]) for _ in range(50)],
        "fn contains(MARKED list[50k], hit)": lambda: F.contains(f["marked_list"], CtyString().validate("0")),
        "fn sort(list[50k])": lambda: F.sort(f["big_list"]),
        # go-cty-shaped results: `flatten` builds a tuple type with one entry
        # per output element, and `chunklist` one list per chunk. Both allocate
        # per element where the old implementations allocated one shared type,
        # so both are here to make that cost visible rather than assumed.
        # `regexall` is deliberately absent: its arguments changed order, so a
        # run against an older base would be measuring a different call.
        "fn flatten(list[list][10k])": lambda: F.flatten(f["big_nested"]),
        "fn chunklist(list[50k], 100)": lambda: F.chunklist(f["big_list"], CtyNumber().validate(100)),
        # wire
        "msgpack encode obj list[10k]": lambda: cty_to_msgpack(f["big_objs"], f["objs"]),
        "msgpack decode obj list[10k]": lambda: cty_from_msgpack(f["objs_packed"], f["objs"]),
    }


def main() -> int:
    import pyvider.cty

    fixtures = build_fixtures()
    results = {name: best_of(fn) for name, fn in scenarios(fixtures).items()}
    # Report which module was actually measured. The caller verifies it, so a
    # path mix-up surfaces as an error rather than as a comparison of a tree
    # against itself.
    print(
        json.dumps(
            {
                "python": sys.version.split()[0],
                "module": pyvider.cty.__file__,
                "results": results,
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
