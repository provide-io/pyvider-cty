#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Run one stress script under memray and compare its allocation count.

This used to come from `wrknv.memray`, which is declared nowhere -- not in
`pyproject.toml`, not in the Makefile, not in CI -- so the whole suite was
uncollectable and `norecursedirs` excluded the directory to hide it. A baseline
nothing can check is not a baseline. Implemented here against `memray` itself,
which *is* a declared dependency.

The number compared is memray's own "Total allocations", the one figure that
tracks the thing these tests exist to catch: a change that starts allocating per
element where it used to allocate once.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess  # nosec B404 - fixed argv, no shell
import sys

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
# Through *this* interpreter, never a bare `memray` off PATH. Outside `uv run` --
# a plain `pytest -m memray`, a tox env, CI with a global install -- the resolved
# executable belongs to whichever environment owns it, and both `run` and `stats`
# then profile a build of pyvider-cty that is not the working tree, silently,
# because the subprocess still exits 0.
MEMRAY = [sys.executable, "-m", "memray"]
TOTAL_ALLOCATIONS = re.compile(r"Total allocations:\s*\n\s*([\d,]+)")

# Allocation counts move with the interpreter's own behaviour -- a patch release
# that changes how a builtin allocates shifts every number here. The band is
# wide enough to survive that and narrow enough to catch a per-element
# regression, which is what these tests are for and is never a few percent.
TOLERANCE = 0.30

UPDATE = os.environ.get("PYVIDER_MEMRAY_UPDATE_BASELINES") == "1"


def total_allocations(binfile: Path) -> int:
    """memray's own count, read from `memray stats`."""
    completed = subprocess.run(  # nosec B603 - fixed argv, no shell
        [*MEMRAY, "stats", str(binfile)],
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )
    if completed.returncode != 0:
        raise AssertionError(f"memray stats failed: {completed.stderr[-400:]}")
    found = TOTAL_ALLOCATIONS.search(completed.stdout)
    if not found:
        raise AssertionError(f"no allocation total in memray stats output: {completed.stdout[:400]}")
    return int(found.group(1).replace(",", ""))


def run_memray_stress(
    script: str,
    baseline_key: str,
    output_dir: Path,
    baselines: dict[str, int],
    baselines_path: Path,
) -> None:
    """Profile `script`, and fail if it allocates materially more than recorded."""
    binfile = Path(output_dir) / f"{Path(script).stem}.bin"
    completed = subprocess.run(  # nosec B603 - fixed argv, no shell
        [*MEMRAY, "run", "--force", "-o", str(binfile), script],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
        timeout=900,
    )
    if completed.returncode != 0:
        raise AssertionError(f"{script} failed under memray: {completed.stderr[-600:]}")

    measured = total_allocations(binfile)

    if UPDATE:
        baselines[baseline_key] = measured
        baselines_path.write_text(json.dumps(dict(sorted(baselines.items())), indent=2) + "\n")
        pytest.skip(f"baseline updated: {baseline_key} = {measured}")

    recorded = baselines.get(baseline_key)
    assert recorded is not None, (
        f"{baseline_key} has no baseline. Record one with "
        f"PYVIDER_MEMRAY_UPDATE_BASELINES=1 rather than inventing a number."
    )
    assert recorded > 0, (
        f"{baseline_key} has a baseline of {recorded}, which no profiled run produces. "
        f"Re-record it with PYVIDER_MEMRAY_UPDATE_BASELINES=1."
    )
    ceiling = recorded * (1 + TOLERANCE)
    # `recorded` is known positive by the assertion above, so the percentage in
    # this message cannot divide by zero -- a ZeroDivisionError raised while
    # *building* an assertion message replaces the regression report with a
    # traceback that says nothing about the regression.
    assert measured <= ceiling, (
        f"{baseline_key}: {measured} allocations against a baseline of {recorded} "
        f"(+{measured / recorded - 1:.0%}, ceiling +{TOLERANCE:.0%}). "
        f"Profile it with `{sys.executable} -m memray flamegraph {binfile}` before moving the baseline."
    )


# 🐍🏗️🔚
