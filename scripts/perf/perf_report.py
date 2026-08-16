#!/usr/bin/env python3
"""
Performance report: this working tree against a baseline git ref.

Exports the baseline with `git archive`, runs the same benchmark file against
both trees, and prints the comparison.

**Reports, never fails.** Exit status is 0 whatever the numbers say. A
threshold that fails the build would have to pick a number, and the honest
number varies by machine, by scenario and by what the change is for -- some
regressions are the price of a fix and should be visible and accepted rather
than argued past with a tuned constant. The point is that nobody merges a
96,401% regression without seeing it, which is what happened when the only
performance tests in the suite were gated behind `--run-benchmarks`.

Usage:
    make perf-report
    make perf-report BASE=origin/main
    uv run python scripts/perf/perf_report.py --base gh-origin/main
"""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess  # nosec
import sys
import tempfile

REPO_ROOT = Path(__file__).resolve().parents[2]
BENCHMARK = Path(__file__).resolve().parent / "benchmark.py"

# Reported, but not treated as failure. Loud enough to notice in a diff.
NOTABLE_REGRESSION_PCT = 15.0
NOTABLE_IMPROVEMENT_PCT = -15.0


def run_benchmark(src_root: Path) -> dict[str, float]:
    """Run the benchmark with `src_root` ahead of everything on the path.

    The tree under measurement is selected only by PYTHONPATH, and the
    benchmark deliberately does no path manipulation of its own -- otherwise
    both runs silently measure the working tree and every scenario reports as
    unchanged.
    """
    env = dict(os.environ)
    env["PYTHONPATH"] = str(src_root)
    completed = subprocess.run(  # nosec
        [sys.executable, str(BENCHMARK)],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"benchmark failed under {src_root}:\n{completed.stderr[-2000:]}")
    measured = json.loads(completed.stdout)
    if Path(measured["module"]).resolve() != (src_root / "pyvider" / "cty" / "__init__.py").resolve():
        raise RuntimeError(
            f"benchmark measured {measured['module']}, expected a module under {src_root}. "
            "The comparison would be meaningless."
        )
    return measured["results"]


def export_baseline(ref: str, destination: Path) -> Path:
    """Materialise `ref` into a directory, without touching the working tree."""
    destination.mkdir(parents=True, exist_ok=True)
    archive = subprocess.run(  # nosec
        ["git", "archive", ref],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
    )
    if archive.returncode != 0:
        raise SystemExit(f"cannot export baseline {ref!r}: {archive.stderr.decode()[-500:]}")
    subprocess.run(  # nosec
        ["tar", "-x", "-C", str(destination)],
        input=archive.stdout,
        check=True,
    )
    return destination / "src"


def render(base: dict[str, float], head: dict[str, float]) -> None:
    shared = [name for name in head if name in base]
    rows = []
    for name in shared:
        before, after = base[name], head[name]
        delta = ((after - before) / before * 100) if before else 0.0
        rows.append((delta, name, before, after))
    rows.sort(reverse=True)

    print(f"{'scenario':<34}{'base ms':>10}{'head ms':>10}{'delta':>9}")
    print("-" * 63)
    for delta, name, before, after in rows:
        if delta >= NOTABLE_REGRESSION_PCT:
            note = "  slower"
        elif delta <= NOTABLE_IMPROVEMENT_PCT:
            note = "  faster"
        else:
            note = ""
        print(f"{name:<34}{before:>10.2f}{after:>10.2f}{delta:>8.0f}%{note}")

    missing = sorted(set(base) - set(head))
    added = sorted(set(head) - set(base))
    if missing:
        print(f"\nnot present in this tree: {', '.join(missing)}")
    if added:
        print(f"new scenarios (no baseline): {', '.join(added)}")

    slower = [r for r in rows if r[0] >= NOTABLE_REGRESSION_PCT]
    print(f"\n{len(shared)} scenarios compared, {len(slower)} at least {NOTABLE_REGRESSION_PCT:.0f}% slower.")
    print("Report only -- this never fails a build. Read the numbers and decide.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base",
        default="gh-origin/main",
        help="git ref to compare against (default: gh-origin/main)",
    )
    args = parser.parse_args()

    workdir = Path(tempfile.mkdtemp(prefix="pyvider-cty-perf-"))
    try:
        print(f"baseline: {args.base}\nhead:     working tree\n")
        base_src = export_baseline(args.base, workdir / "base")
        base = run_benchmark(base_src)
        head = run_benchmark(REPO_ROOT / "src")
        render(base, head)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
