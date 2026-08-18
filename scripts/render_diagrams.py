#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Re-render every architecture diagram from its PlantUML source.

`docs/architecture/index.md` embeds the SVGs, not the `.puml` files, so a
diagram is only as true as its last render. A committed SVG whose source has
moved on is exactly the kind of document this branch has spent its time
deleting: plausible, detailed, and describing code that no longer exists.

So the rendering is a target rather than a habit. `make diagrams` re-renders
every source; `make diagrams-check` re-renders into a scratch directory and
fails if anything differs from what is committed, which is the form CI would
need if it ever grows a Java toolchain.

PNGs are rendered too, on request, because reviewing a diagram means looking
at it -- and an SVG in a terminal is a wall of XML.

Skips with exit status 0 when PlantUML is not installed. A machine without it
should not fail the build, but it must say that it rendered nothing.
"""

from __future__ import annotations

import argparse
import filecmp
from pathlib import Path
import shutil
import subprocess  # nosec
import sys
import tempfile

REPO = Path(__file__).resolve().parents[1]
DIAGRAMS = REPO / "docs" / "architecture"


def sources() -> list[Path]:
    """Every diagram source, in the order they appear on the page.

    `_theme.iuml` is deliberately not a `.puml`: it is an include, it has no
    diagram of its own, and giving it the same extension made PlantUML render
    an empty image beside the eight real ones.
    """
    return sorted(DIAGRAMS.glob("*.puml"))


def plantuml() -> str | None:
    return shutil.which("plantuml")


def render(binary: str, files: list[Path], out_dir: Path, formats: list[str]) -> int:
    for fmt in formats:
        result = subprocess.run(  # nosec
            [binary, f"-t{fmt}", "-output", str(out_dir), *[str(f) for f in files]],
            cwd=DIAGRAMS,
            check=False,
        )
        if result.returncode != 0:
            print(f"plantuml failed rendering {fmt}.")
            return result.returncode
    # plantuml writes no trailing newline; the repository's end-of-file hook
    # adds one. Without this the two would fight forever -- the hook would
    # rewrite every SVG on commit, and `--check` would then call all eight
    # stale on the next run. Normalising here means the rendered bytes and the
    # committed bytes are the same bytes.
    for svg in out_dir.glob("*.svg"):
        content = svg.read_bytes()
        if not content.endswith(b"\n"):
            svg.write_bytes(content + b"\n")
    return 0


def check(binary: str, files: list[Path]) -> int:
    """Re-render into a scratch directory and diff against what is committed."""
    with tempfile.TemporaryDirectory() as scratch:
        out_dir = Path(scratch)
        if code := render(binary, files, out_dir, ["svg"]):
            return code
        stale = [
            source.name
            for source in files
            if not (committed := source.with_suffix(".svg")).exists()
            or not filecmp.cmp(committed, out_dir / committed.name, shallow=False)
        ]
    if stale:
        print("These diagrams are out of date -- run `make diagrams`:")
        for name in stale:
            print(f"  {name}")
        return 1
    print(f"{len(files)} diagrams are up to date.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--png", action="store_true", help="also render PNGs, for eyeballing")
    parser.add_argument("--check", action="store_true", help="fail if a committed SVG is stale")
    args = parser.parse_args()

    binary = plantuml()
    if binary is None:
        print("plantuml not installed; skipping diagram rendering. (brew install plantuml)")
        return 0

    files = sources()
    if not files:
        print(f"No .puml sources under {DIAGRAMS}.")
        return 0

    if args.check:
        return check(binary, files)

    formats = ["svg", "png"] if args.png else ["svg"]
    if code := render(binary, files, DIAGRAMS, formats):
        return code
    print(f"Rendered {len(files)} diagrams to {', '.join(formats)} in {DIAGRAMS}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# 🌊🪢🔚
