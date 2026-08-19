#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Check the documentation by running it.

Reading is what let the errors in. The 2026-08-17 documentation pass found about
sixty inaccuracies by executing every code block rather than reading it, and did
so by hand; this is that pass, repeatable.

Two things are checked, and the second is the one that rots:

  * A block must run. Blocks share a namespace per document, because docs are
    written as a narrative and later blocks continue from earlier ones -- running
    each in isolation reports a NameError for nearly all of them and says
    nothing about whether the documentation is right.
  * A block marked with the failure marker must actually fail. A document
    promising an error that no longer happens is the inaccuracy no reader can
    detect and no test covers.

**Two earlier versions of this script were wrong in instructive ways**, and the
narrowness below is the result. Matching any `raise` in the source flagged 40
correct documents, because a `raise` inside an uncalled function or a handled
`try/except` says nothing about what the block does. Treating a comment naming
an exception as a promise flagged more. Only the explicit marker, with no
handler in the block, is a claim the reader acts on.

Blocks referencing placeholders that were never defined (`schema`, `my_type`,
`raw_config`) are illustrative rather than runnable, and are skipped rather than
reported -- as are blocks that need the network.

A `NameError` is only skipped when the missing name is a *placeholder*. Skipping
every one of them swallowed the commonest form of documentation rot there is: a
block naming an API symbol that was renamed, removed, or never imported, which
is the shape a reader copies and cannot run. Anything spelled like a symbol of
this package -- a `Cty` prefix, or a name `pyvider.cty` exports -- is reported.

Blocks run in a scratch directory rather than the checkout. `NEEDS_WORLD` only
ever matched `open(`, so the `Path(...).write_bytes` in
`docs/how-to/serialize-values.md` ran against the repository root and left
`person.msgpack` there -- which was then committed. A documentation checker must
not be able to write into the tree it is checking.
"""

from __future__ import annotations

from collections import Counter
import contextlib
import io
import os
import pathlib
import re
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
FENCE = re.compile(r"```(?:python|py)\n(.*?)```", re.DOTALL)
HANDLES = re.compile(r"^\s*try:", re.M)
NEEDS_WORLD = re.compile(r"open\(|requests\.|load_from_go|send_to_go|\.json[\"']\)")
# A failure claim only counts when it is attached to a line that RUNS. Both
# markers appear constantly on commented-out "don't do this" lines, where they
# describe code the block deliberately does not execute.
CLAIM = re.compile(r"❌|[Rr]aises\b")
RAISES_AT_TOP_LEVEL = re.compile(r"^\s{0,4}raise\s", re.M)
# Everything `pyvider.cty` exports, for telling a stale API reference from a
# narrative placeholder. Imported here rather than inside the loop so that an
# import failure is this script's own crash rather than 281 documentation FAILs.
API_NAMES = frozenset(dir(__import__("pyvider.cty", fromlist=["*"])))


def _claims_failure(block: str) -> bool:
    """Whether the block says, in a comment on a line that runs, that it fails.

    Narrow for reasons each found by a false positive:

      * A pure comment line describes code the block does not execute -- the
        `# convert(...)  # ❌ raises` shape, showing what *not* to write.
      * `Raises:` inside a docstring is a section heading, not a claim.
      * `pytest.raises(...)` inside a test function that is defined and never
        called is a handler, not a claim -- and it lives in prose about testing.

    So the marker has to sit in a trailing comment, after real code, on a line
    at module level. A bare top-level `raise` counts too: that is the block
    raising on purpose.
    """
    for line in block.split("\n"):
        code, _, comment = line.partition("#")
        if not code.strip() or not comment:
            continue
        if code.startswith((" ", "\t")):
            continue  # indented: inside a function or class body
        if CLAIM.search(comment):
            return True
    return bool(RAISES_AT_TOP_LEVEL.search(block))


def _is_api_name(missing: str | None) -> bool:
    """Whether an undefined name is this package's rather than the narrative's.

    A `Cty` prefix covers the symbols that were renamed or removed and so are no
    longer exported at all -- which is exactly the rot a membership test against
    the live package would miss.
    """
    if missing is None:
        return False
    return missing.startswith("Cty") or missing in API_NAMES


def check() -> int:
    """Run every block, from a scratch directory a block may safely write into."""
    with tempfile.TemporaryDirectory(prefix="check-docs-") as scratch:
        previous = pathlib.Path.cwd()
        os.chdir(scratch)
        try:
            return _run()
        finally:
            os.chdir(previous)


def _run() -> int:
    rows: list[tuple[str, int, str, str]] = []
    documents = sorted(ROOT.glob("docs/**/*.md")) + sorted(ROOT.glob("*.md"))

    for document in documents:
        name = str(document.relative_to(ROOT))
        namespace: dict[str, object] = {"__name__": "__docs__"}
        for index, block in enumerate(FENCE.findall(document.read_text())):
            body = block.strip()
            if not body or body.startswith((">>>", "$", "#!")) or NEEDS_WORLD.search(block):
                rows.append((name, index, "skip", ""))
                continue
            try:
                code = compile(block, f"{name}:block{index}", "exec")
            except SyntaxError:
                rows.append((name, index, "skip", "not valid Python on its own"))
                continue

            must_fail = _claims_failure(block) and not HANDLES.search(block)
            try:
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    exec(code, namespace)  # noqa: S102 - running the docs is the point
            except NameError as exc:
                if _is_api_name(exc.name):
                    rows.append((name, index, "ok" if must_fail else "FAIL", f"NameError: {exc}"))
                else:
                    rows.append((name, index, "skip", f"illustrative: {exc}"))
                continue
            except Exception as exc:
                rows.append((name, index, "ok" if must_fail else "FAIL", f"{type(exc).__name__}: {exc}"))
                continue
            rows.append((name, index, "STALE" if must_fail else "ok", "marked to fail, but ran clean"))

    counts = Counter(kind for _, _, kind, _ in rows)
    print(f"{len(documents)} documents, {len(rows)} python blocks: {dict(counts)}")
    bad = [row for row in rows if row[2] in ("FAIL", "STALE")]
    for name, index, kind, message in bad:
        print(f"  {kind:5} {name} block {index}: {message[:160]}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(check())
