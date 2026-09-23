#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`make diagrams-check` asks whether a diagram was rendered from its source, not how.

The check compared rendered SVG bytes, and those bytes belong to the renderer:
PlantUML 1.2026.8 reorders attributes and rounds coordinates differently from the
1.2026.6 that rendered the committed diagrams, so every diagram read as stale
with no source changed, and a Linux runner's graphviz and fonts differ again.
PlantUML embeds each diagram's source in the SVG it writes, so the check reads
that instead -- which needs no PlantUML at all, and gives the same answer on any
machine. The shared theme is an `!include` the embedded source does not expand,
so rendering records the theme's digest beside it and the check compares that.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import shutil
from types import ModuleType

import pytest

REPO = Path(__file__).resolve().parents[2]


def _load_script() -> ModuleType:
    spec = importlib.util.spec_from_file_location("render_diagrams", REPO / "scripts" / "render_diagrams.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


render_diagrams = _load_script()


@pytest.fixture
def diagrams(tmp_path: Path) -> Path:
    """A copy of the committed diagrams, free to be broken."""
    copy = tmp_path / "architecture"
    shutil.copytree(REPO / "docs" / "architecture", copy)
    return copy


def _check(directory: Path) -> int:
    return int(
        render_diagrams.check(
            sorted(directory.glob("*.puml")),
            directory / "_theme.iuml",
            directory / "_theme.sha256",
        )
    )


def test_the_committed_diagrams_match_their_sources() -> None:
    directory = REPO / "docs" / "architecture"

    assert render_diagrams.stale_diagrams(sorted(directory.glob("*.puml"))) == []
    assert not render_diagrams.theme_is_stale(directory / "_theme.iuml", directory / "_theme.sha256")


def test_the_embedded_source_is_the_diagram_body() -> None:
    puml = REPO / "docs" / "architecture" / "01-type-system.puml"

    embedded = render_diagrams.embedded_source(puml.with_suffix(".svg"))

    assert embedded is not None
    assert embedded.startswith("!include _theme.iuml")
    assert embedded.strip() == render_diagrams.diagram_body(puml)


def test_a_copy_of_the_committed_diagrams_passes(diagrams: Path) -> None:
    assert _check(diagrams) == 0


def test_an_edited_source_is_stale(diagrams: Path) -> None:
    source = diagrams / "02-value-model.puml"
    source.write_text(
        source.read_text(encoding="utf-8").replace("@enduml", "note as N\n  changed\nend note\n@enduml"),
        encoding="utf-8",
    )

    assert render_diagrams.stale_diagrams(sorted(diagrams.glob("*.puml"))) == ["02-value-model.puml"]
    assert _check(diagrams) == 1


def test_a_missing_svg_is_stale(diagrams: Path) -> None:
    (diagrams / "03-validation-conversion.svg").unlink()

    assert render_diagrams.stale_diagrams(sorted(diagrams.glob("*.puml"))) == ["03-validation-conversion.puml"]


def test_an_svg_without_an_embedded_source_is_stale(diagrams: Path) -> None:
    """Nothing to compare is not a match. An SVG drawn by hand, or by a renderer
    told not to embed its source, cannot show which source it came from."""
    svg = diagrams / "05-wire-codecs.svg"
    svg.write_text("<svg xmlns='http://www.w3.org/2000/svg'></svg>\n")

    assert render_diagrams.stale_diagrams(sorted(diagrams.glob("*.puml"))) == ["05-wire-codecs.puml"]


def test_a_theme_changed_since_the_last_render_is_stale(diagrams: Path) -> None:
    theme = diagrams / "_theme.iuml"
    theme.write_text(
        theme.read_text(encoding="utf-8") + "\n' a comment is still a change nobody rendered\n",
        encoding="utf-8",
    )

    assert render_diagrams.theme_is_stale(theme, diagrams / "_theme.sha256")
    assert _check(diagrams) == 1


def test_a_missing_theme_stamp_is_stale(diagrams: Path) -> None:
    (diagrams / "_theme.sha256").unlink()

    assert render_diagrams.theme_is_stale(diagrams / "_theme.iuml", diagrams / "_theme.sha256")


def test_a_theme_checked_out_with_windows_line_endings_is_not_stale(diagrams: Path) -> None:
    """Git on Windows checks text out with CRLF line endings unless told not to.

    The theme is the same text either way, so the stamp recorded from an LF
    checkout must still match it. Hashing the checkout's bytes read every
    Windows checkout as a theme nobody rendered.
    """
    theme = diagrams / "_theme.iuml"
    theme.write_bytes(theme.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))

    assert b"\r\n" in theme.read_bytes()
    assert not render_diagrams.theme_is_stale(theme, diagrams / "_theme.sha256")
    assert _check(diagrams) == 0


def test_rendering_records_the_theme_it_rendered_with(diagrams: Path) -> None:
    """A theme change is resolved by rendering, not by editing the stamp by hand."""
    theme = diagrams / "_theme.iuml"
    stamp = diagrams / "_theme.sha256"
    theme.write_text(theme.read_text(encoding="utf-8") + "\n' changed\n", encoding="utf-8")

    render_diagrams.record_theme(theme, stamp)

    assert not render_diagrams.theme_is_stale(theme, stamp)
    assert stamp.read_text(encoding="utf-8").endswith("\n")
