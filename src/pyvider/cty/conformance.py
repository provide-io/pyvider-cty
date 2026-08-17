#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""go-cty's `Type.TestConformance` (`cty/type_conform.go`).

`usable_as` already answers whether one type satisfies another. This answers
*why not*, and *where*: it collects every specific non-conformance rather than
returning a single boolean, so a caller can tell a practitioner which attribute
is missing instead of printing two whole type names and leaving them to diff it
by eye. go-cty's own comment says as much -- the compound cases exist "so that
we can report specifically what is non-conforming".

Conformance is not symmetric and is not convertibility. `want` being `dynamic`
admits anything; a `string` where a `number` is wanted is non-conformant even
though `convert` would manage it. This is a question about *types* fitting a
shape, not about values being coercible.

Naming: go-cty spells it `TestConformance`. A module-level Python function
called `test_conformance` gets collected as a test case the moment any test
module imports it by name, so this is `conformance_errors`, which also says what
it returns.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from attrs import define

if TYPE_CHECKING:
    from pyvider.cty.types import CtyObject, CtyTuple, CtyType

__all__ = ["ConformanceError", "conformance_errors"]


@define(frozen=True, slots=True)
class ConformanceError:
    """One specific way a type fails to conform, and where.

    `path` is a display string rather than a `CtyPath`, deliberately. go-cty
    marks a collection element with an index step holding an *unknown* key --
    "some element, we cannot say which" -- and a `CtyPath` has no way to say
    that. Inventing `[0]` would point at an element that need not exist.
    """

    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.message}" if self.path else self.message


def conformance_errors(given: CtyType[Any], want: CtyType[Any], /) -> list[ConformanceError]:
    """Every way `given` fails to conform to `want`. Empty means it conforms."""
    errors: list[ConformanceError] = []
    _test(given, want, "", errors)
    return errors


def _test(given: CtyType[Any], want: CtyType[Any], path: str, errors: list[ConformanceError]) -> None:
    # Imported here rather than at module scope: `conformance` sorts before
    # `conversion` alphabetically, so a module-level import lands ahead of it in
    # the package __init__ and breaks the type/conversion import cycle. Python
    # caches modules, so the cost is a dict lookup.
    from pyvider.cty.types import CtyDynamic, CtyList, CtyMap, CtyObject, CtySet, CtyTuple

    if isinstance(want, CtyDynamic):
        return  # Anything goes.
    if given.equal(want):
        return

    if isinstance(given, CtyObject) and isinstance(want, CtyObject):
        _test_object(given, want, path, errors)
        return
    if isinstance(given, CtyTuple) and isinstance(want, CtyTuple):
        _test_tuple(given, want, path, errors)
        return
    for kind in (CtyList, CtyMap, CtySet):
        if isinstance(given, kind) and isinstance(want, kind):
            _test(given.element_type, want.element_type, _join(path, "[*]"), errors)
            return

    errors.append(ConformanceError(path, f"{_name(want)} required, but received {_name(given)}"))


def _test_object(given: CtyObject, want: CtyObject, path: str, errors: list[ConformanceError]) -> None:
    # Both directions are reported. An unexpected attribute is as much a
    # non-conformance as a missing one, and a caller shown only the missing ones
    # will keep adding attributes without being told the extras are the problem.
    #
    # Double quotes, because go-cty uses Go's %q and these messages are written
    # for practitioners rather than for Python. `!r` produced 'b' where go-cty
    # produces "b", which is a difference a user comparing the two sees.
    for name in given.attribute_types:
        if name not in want.attribute_types:
            errors.append(ConformanceError(path, f'unsupported attribute "{name}"'))
    for name in want.attribute_types:
        if name not in given.attribute_types:
            errors.append(ConformanceError(path, f'missing required attribute "{name}"'))

    for name, wanted in want.attribute_types.items():
        if name in given.attribute_types:
            _test(given.attribute_types[name], wanted, _join(path, name), errors)


def _test_tuple(given: CtyTuple, want: CtyTuple, path: str, errors: list[ConformanceError]) -> None:
    if len(given.element_types) != len(want.element_types):
        errors.append(
            ConformanceError(
                path,
                f"{len(want.element_types)} elements are required, but got {len(given.element_types)}",
            )
        )
        return
    for index, wanted in enumerate(want.element_types):
        _test(given.element_types[index], wanted, _join(path, f"[{index}]"), errors)


def _join(path: str, step: str) -> str:
    if not path:
        return step
    return f"{path}{step}" if step.startswith("[") else f"{path}.{step}"


def _name(cty_type: CtyType[Any]) -> str:
    """go-cty's `Type.FriendlyName`, for the types that reach these messages.

    A collection names its element type -- "set of string", not "set" -- and an
    object or tuple deliberately does not name its members, because go-cty's own
    comment says there is no friendly way to write one and the compound cases
    above exist precisely to report the specific member instead.

    Not exposed as `CtyType.friendly_name`. go-cty's has a second mode for type
    *constraints* ("any type", "any single type") with no consumer here, and
    publishing half of an API is how this library has previously ended up with a
    method that answers a slightly different question from the one it is named
    for.
    """
    from pyvider.cty.types import CtyList, CtyMap, CtySet

    if isinstance(cty_type, CtyList | CtySet | CtyMap):
        return f"{cty_type.ctype} of {_name(cty_type.element_type)}"
    return str(cty_type.ctype or type(cty_type).__name__)


# 🌊🪢🔚
