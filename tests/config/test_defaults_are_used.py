#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Every `ERR_*` constant must be referenced by the code that raises it.

`config/defaults.py` claims to be the single place error text lives. It was not:
130 of its 240 constants were never referenced, while the functions that should
have used them built the same text inline. The duplication had not drifted yet --
sampling showed the inline copies matching their constants exactly -- but two
copies of a user-facing string is a wording change waiting to be applied to one
of them.

The 130 were deleted rather than wired up. A constant nobody uses is not a
single source of truth, it is a second one; removing them makes the file's claim
true without touching a single raise site, so no message text could change in
the process. Wiring them up instead would have meant 108 mechanical edits to
error paths for no behavioural gain.

This test is what stops it recurring. It was noticed three separate times as a
side effect of other work, which is the signature of a problem that needs a
mechanism rather than another fix. **Deliberately no allowlist**: an allowlist of
130 entries would be a guard that cannot fire, which is the failure mode this
repository has catalogued repeatedly. Adding a constant now means using it.
"""

from __future__ import annotations

import ast
from pathlib import Path
import re

SOURCE_ROOT = Path(__file__).resolve().parents[2] / "src"
DEFAULTS = SOURCE_ROOT / "pyvider" / "cty" / "config" / "defaults.py"


def _declared_constants() -> set[str]:
    tree = ast.parse(DEFAULTS.read_text())
    return {
        target.id
        for node in tree.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name) and target.id.startswith("ERR_")
    }


def _referenced_constants() -> set[str]:
    body = "\n".join(path.read_text() for path in SOURCE_ROOT.rglob("*.py") if path.name != "defaults.py")
    return set(re.findall(r"\bERR_[A-Z0-9_]+\b", body))


def test_every_error_constant_is_referenced() -> None:
    unused = sorted(_declared_constants() - _referenced_constants())

    assert unused == [], (
        f"{len(unused)} ERR_* constants are declared and never referenced: {unused[:8]}. "
        "Either use the constant at the raise site, or do not declare it -- an unreferenced "
        "constant means the same message text exists twice and only one copy will be edited."
    )


def test_every_referenced_constant_is_declared() -> None:
    """The other direction: a reference to a constant that does not exist.

    Would fail at import rather than here, but only on the code path that
    raises -- which for an error message may be the path nobody exercises until
    a practitioner does.
    """
    missing = sorted(_referenced_constants() - _declared_constants())

    assert missing == [], f"referenced but not declared in defaults.py: {missing}"


# 🌊🪢🔚
