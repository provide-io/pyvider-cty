#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""An immutable mapping that is still a `dict`.

`CtyValue` and `CtyObject` are frozen attrs classes, but freezing it freezes the *reference* to
its payload, not the payload itself. Maps and objects hold a mapping, an
object *type* holds its attribute schema, and a plain dict can be changed after
the value is built -- which quietly breaks
things that read payload contents and remember the answer: `__eq__`,
`__hash__`, `_canonical_sort_key`, and the deep-mark memo.

The deep-mark memo is the one that matters, because getting it wrong is a
security failure rather than a surprise. A value that has become sensitive
answering "not sensitive" is a silent declassification, so the memo was made
conditional on the payload being immutable -- which meant maps and objects
re-walked on every stdlib call, at 12 ms each for a 20k-entry map. Every
Terraform resource is an object, so that is the common path, not a corner.

Subclassing `dict` rather than using `MappingProxyType` is deliberate: every
`isinstance(payload, dict)` check in this package and its consumers keeps
working, and msgpack and JSON encoders serialize it without knowing.

This blocks mutation through the public API. Calling an unbound base method
explicitly -- `dict.__init__(payload, ...)`, `dict.update(payload, ...)` --
still reaches the C implementation, exactly as `object.__setattr__` still
defeats a frozen attrs class. That is deliberate subversion rather than an
accident, and no amount of subclassing prevents it.
"""

from __future__ import annotations

from typing import Any, NoReturn

_IMMUTABLE = (
    "This mapping is immutable: it is a CtyValue's payload or a CtyObject's "
    "schema. Build a new one with `attrs.evolve(...)` rather than changing this "
    "one in place: equality, hashing and the deep-mark memo all read its "
    "contents and cache what they find."
)


class FrozenDict(dict[str, Any]):
    """A `dict` that refuses to change after construction."""

    __slots__ = ()

    def _immutable(self, *args: Any, **kwargs: Any) -> NoReturn:
        raise TypeError(_IMMUTABLE)

    __setitem__ = _immutable
    __delitem__ = _immutable
    # `|=` is idiomatic and dispatches to dict.__ior__ in C, which never reaches
    # the overrides below. Without this the whole immutability claim, and the
    # memo that rests on it, was one operator away from being false.
    __ior__ = _immutable
    pop = _immutable
    popitem = _immutable
    clear = _immutable
    update = _immutable
    setdefault = _immutable

    def copy(self) -> dict[str, Any]:
        """A *mutable* copy, matching `dict.copy`'s contract of a plain dict."""
        return dict(self)

    def __copy__(self) -> FrozenDict:
        return self

    def __deepcopy__(self, memo: dict[int, Any]) -> FrozenDict:
        from copy import deepcopy

        return FrozenDict({k: deepcopy(v, memo) for k, v in self.items()})

    def __reduce__(self) -> tuple[Any, ...]:
        return (FrozenDict, (dict(self),))


# 🌊🪢🔚
