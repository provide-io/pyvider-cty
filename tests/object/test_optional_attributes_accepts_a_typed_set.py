#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`optional_attributes` accepts the sets a caller actually has.

`CtyObject` declared the field as `field(factory=frozenset, converter=frozenset)`.
attrs derives the `__init__` parameter type from the converter, and passing the
`frozenset` *class* resolves to its own overloads -- `Iterable[_T_co]`, carrying
an unbound TypeVar. Nothing concrete satisfies that, so under a strict type
checker every call was an error, `frozenset[str]` included:

    Argument "optional_attributes" to "CtyObject" has incompatible type
    "frozenset[str]"; expected "Iterable[_T_co]"

Runtime was always fine, which is why it survived: the field works, and this
package's own gate only caught it once, in `raw_to_cty.py`, where it was papered
over with a `# type: ignore[arg-type]` rather than fixed. Downstream callers had
to carry the same cast.

Checked by running the type checker, because nothing else can check a typing
fix -- the runtime call passed before the fix too.
"""

from __future__ import annotations

import subprocess
import sys
import textwrap

import pytest

# One call per shape a caller plausibly has on hand.
SNIPPET = textwrap.dedent(
    """
    from pyvider.cty import CtyObject, CtyString

    attrs = {"a": CtyString(), "b": CtyString()}

    frozen: frozenset[str] = frozenset({"b"})
    CtyObject(attrs, optional_attributes=frozen)

    mutable: set[str] = {"b"}
    CtyObject(attrs, optional_attributes=mutable)

    CtyObject(attrs, optional_attributes={"b"})
    CtyObject(attrs, optional_attributes=["b"])
    CtyObject(attrs, optional_attributes=(name for name in ("b",)))
    CtyObject(attrs)
    """
)


@pytest.mark.slow
def test_passing_optional_attributes_type_checks(tmp_path) -> None:
    """No `expected "Iterable[_T_co]"`, on any of the shapes."""
    module = tmp_path / "optionals.py"
    module.write_text(SNIPPET)

    completed = subprocess.run(  # nosec B603 - fixed argv, no shell
        [sys.executable, "-m", "mypy", "--strict", "--no-error-summary", str(module)],
        capture_output=True,
        check=False,
        text=True,
    )
    output = completed.stdout + completed.stderr

    assert "_T_co" not in output, output
    assert completed.returncode == 0, output


def test_the_field_still_holds_a_frozenset() -> None:
    """The converter still copies whatever it is given into a frozenset."""
    from pyvider.cty import CtyObject, CtyString

    obj = CtyObject({"a": CtyString(), "b": CtyString()}, optional_attributes=["b"])
    assert obj.optional_attributes == frozenset({"b"})
    assert isinstance(obj.optional_attributes, frozenset)


# 🐍🏗️🔚
