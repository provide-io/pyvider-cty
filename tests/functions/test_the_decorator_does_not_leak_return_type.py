#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Calling a stdlib function does not require the argument the framework injects.

Thirteen functions declare `return_type` and receive it from the framework --
`flatten`, `sort`, `keys`, `values`, `concat`, `reverse`, `distinct`,
`coalesce`, `formatlist`, `chunklist` and friends. `stdlib_function` was typed
as an identity, so the *implementation's* signature was what a caller saw, and
`flatten(x)` was a type error demanding an argument nobody is allowed to pass.

Runtime was always fine, which is exactly why it went unnoticed here: this
package's own gate runs mypy over `src`, and `src` never calls these. It showed
up in `scripts/perf/benchmark.py`, which is outside the gate.

Checked by running the type checker, because nothing else can check a typing
fix -- asserting on the runtime call would have passed before the fix too.
"""

from __future__ import annotations

import subprocess
import sys
import textwrap

import pytest

# One call per shape: keyword-only `return_type`, positional-only, and variadic.
SNIPPET = textwrap.dedent(
    """
    from pyvider.cty import CtyList, CtyString
    from pyvider.cty.functions import chunklist, concat, flatten, keys, sort
    from pyvider.cty import CtyNumber, CtyMap

    strings = CtyList(element_type=CtyString()).validate(["b", "a"])
    numbers = CtyNumber().validate(2)
    mapping = CtyMap(element_type=CtyString()).validate({"a": "1"})

    sort(strings)
    flatten(strings)
    keys(mapping)
    chunklist(strings, numbers)
    concat(strings, strings)
    """
)


@pytest.mark.slow
def test_calling_them_type_checks(tmp_path) -> None:
    """No `Missing named argument "return_type"`, on any of the five shapes."""
    module = tmp_path / "calls.py"
    module.write_text(SNIPPET)

    completed = subprocess.run(  # nosec B603 - fixed argv, no shell
        [sys.executable, "-m", "mypy", "--strict", "--no-error-summary", str(module)],
        capture_output=True,
        check=False,
        text=True,
    )
    output = completed.stdout + completed.stderr

    assert "return_type" not in output, output
    assert completed.returncode == 0, output


# 🐍🏗️🔚
