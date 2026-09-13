#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Re-render every architecture diagram from its PlantUML source, or check that it was.

`docs/architecture/index.md` embeds the SVGs, not the `.puml` files, so a
diagram is only as true as its last render. A committed SVG whose source has
moved on is exactly the kind of document this branch has spent its time
deleting: plausible, detailed, and describing code that no longer exists.

So the rendering is a target rather than a habit. `make diagrams` re-renders
every source; `make diagrams-check` fails if any committed SVG was not rendered
from its current source.

**The check reads what the SVG says it was rendered from, not what it looks
like.** It used to re-render into a scratch directory and compare bytes, and
those bytes belong to the renderer rather than the diagram: PlantUML 1.2026.8
orders attributes and rounds coordinates differently from the 1.2026.6 that
rendered the committed set, so all eight read as stale with no source changed --
and a CI runner's graphviz and fonts would differ again. PlantUML embeds each
diagram's source in the SVG it writes (`<?plantuml-src ...?>`), so the check
decodes that and compares it with the `.puml`. It needs no PlantUML and gives
the same answer on every machine.

The embedded source does not expand `!include`, so it cannot see the shared
theme. Rendering therefore records the digest of the theme it rendered with in
`_theme.sha256`, and the check compares that too. A digest rather than git
history, because a comment-only theme edit renders byte-identical SVGs: git
would record no newer SVG, and a history-based check would stay red with
nothing a re-render could fix.

PNGs are rendered too, on request, because reviewing a diagram means looking
at it -- and an SVG in a terminal is a wall of XML.

Rendering skips with exit status 0 when PlantUML is not installed. A machine
without it should not fail the build, but it must say that it rendered nothing.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
from pathlib import Path
import re
import shutil
import subprocess  # nosec
import sys
import zlib

REPO = Path(__file__).resolve().parents[1]
DIAGRAMS = REPO / "docs" / "architecture"
THEME = DIAGRAMS / "_theme.iuml"
THEME_STAMP = DIAGRAMS / "_theme.sha256"

# PlantUML's text encoding: raw deflate, then base64 over its own alphabet.
PLANTUML_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
BASE64_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
RAW_DEFLATE_WBITS = -15
EMBEDDED_SOURCE = re.compile(r"<\?plantuml-src (\S+)\?>")


def sources() -> list[Path]:
    """Every diagram source, in the order they appear on the page.

    `_theme.iuml` is deliberately not a `.puml`: it is an include, it has no
    diagram of its own, and giving it the same extension made PlantUML render
    an empty image beside the eight real ones.
    """
    return sorted(DIAGRAMS.glob("*.puml"))


def plantuml() -> str | None:
    return shutil.which("plantuml")


def embedded_source(svg: Path) -> str | None:
    """The diagram source PlantUML embedded in an SVG, or None if there is none to read."""
    if not svg.exists():
        return None
    match = EMBEDDED_SOURCE.search(svg.read_text(encoding="utf-8"))
    if match is None:
        return None
    encoded = match.group(1).translate(str.maketrans(PLANTUML_ALPHABET, BASE64_ALPHABET))
    encoded += "=" * (-len(encoded) % 4)
    try:
        return zlib.decompress(base64.b64decode(encoded), RAW_DEFLATE_WBITS).decode("utf-8")
    except (ValueError, zlib.error):
        return None


def diagram_body(puml: Path) -> str:
    """A `.puml` file as PlantUML embeds it: the lines between `@startuml` and `@enduml`."""
    lines = puml.read_text(encoding="utf-8").strip().splitlines()
    if lines and lines[0].startswith("@start"):
        lines = lines[1:]
    if lines and lines[-1].startswith("@end"):
        lines = lines[:-1]
    return "\n".join(lines).strip()


def stale_diagrams(files: list[Path]) -> list[str]:
    """Sources whose committed SVG is missing, unreadable, or rendered from other text."""
    stale = []
    for source in files:
        embedded = embedded_source(source.with_suffix(".svg"))
        if embedded is None or embedded.strip() != diagram_body(source):
            stale.append(source.name)
    return stale


def theme_digest(theme: Path) -> str:
    return hashlib.sha256(theme.read_bytes()).hexdigest()


def record_theme(theme: Path, stamp: Path) -> None:
    """Note the theme a render used. Trailing newline, for the end-of-file hook."""
    stamp.write_text(theme_digest(theme) + "\n", encoding="utf-8")


def theme_is_stale(theme: Path, stamp: Path) -> bool:
    """Whether the theme differs from the one the committed diagrams were rendered with."""
    if not stamp.exists():
        return True
    return stamp.read_text(encoding="utf-8").strip() != theme_digest(theme)


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
    # rewrite every SVG on commit, and a render would then show all eight as
    # modified. Normalising here means the rendered bytes and the committed
    # bytes are the same bytes.
    for svg in out_dir.glob("*.svg"):
        content = svg.read_bytes()
        if not content.endswith(b"\n"):
            svg.write_bytes(content + b"\n")
    return 0


def check(files: list[Path], theme: Path, stamp: Path) -> int:
    """Fail if a committed SVG was not rendered from its current source and theme."""
    stale = stale_diagrams(files)
    theme_changed = theme_is_stale(theme, stamp)
    if stale:
        print("These diagrams were not rendered from their current source -- run `make diagrams`:")
        for name in stale:
            print(f"  {name}")
    if theme_changed:
        print(f"{theme.name} has changed since the diagrams were last rendered -- run `make diagrams`.")
    if stale or theme_changed:
        return 1
    print(f"{len(files)} diagrams match their sources and {theme.name}.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--png", action="store_true", help="also render PNGs, for eyeballing")
    parser.add_argument("--check", action="store_true", help="fail if a committed SVG is stale")
    args = parser.parse_args()

    files = sources()
    if not files:
        print(f"No .puml sources under {DIAGRAMS}.")
        return 0

    if args.check:
        return check(files, THEME, THEME_STAMP)

    binary = plantuml()
    if binary is None:
        print("plantuml not installed; skipping diagram rendering. (brew install plantuml)")
        return 0

    formats = ["svg", "png"] if args.png else ["svg"]
    if code := render(binary, files, DIAGRAMS, formats):
        return code
    record_theme(THEME, THEME_STAMP)
    print(f"Rendered {len(files)} diagrams to {', '.join(formats)} in {DIAGRAMS}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# 🌊🪢🔚
