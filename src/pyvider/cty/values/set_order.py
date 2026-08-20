#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""The order go-cty iterates a set's elements in, which reaches the wire.

go-cty orders a set two different ways, and only one of them compares the
values. `setRules.Less` (`cty/set_internals.go:85`) compares a string, a number
or a bool directly -- and for **every other element type** it compares
`makeSetHashBytes`, the byte string cty builds to bucket an element by. That
order is what msgpack writes, and Terraform compares serialized state, so a
different order is a diff that reappears on every plan.

The two disagree in ordinary cases, because the hash bytes carry delimiters and
quotes that take part in the comparison:

  * a set of tuples of numbers hashes to `<12;>` and `<1;>`, and `2` sorts
    before `;`, so go-cty writes `[12]` before `[1]` -- not the numeric order;
  * a set of tuples of strings hashes to `<"";" ";>` and `<"";"";>`, and a space
    sorts before a quote, so the *longer* string comes first.

Both were found on 2026-08-19 by the stdlib fuzz, through `setproduct`, whose
result is exactly a set of tuples. A structural comparison of the members --
which is what this package did, and what the "a sequence that has run out of
members sorts last" rule in `_canonical_sort_key` approximates -- gets the first
wrong always and the second wrong for any character below `"`. The approximation
was measured, but against generated sets drawn from the alphabet `abc`, where
every character outranks a quote and the two rules agree.

go-cty calls this order "consistent-but-undefined" and says it is not a
compatibility constraint. It is still the order on the wire, so it is matched
here -- **for ordering only**. Identity stays with `_canonical_sort_key`:
`makeSetHashBytes` renders a number with `big.Float.String()`, which is ten
significant digits, so two numbers agreeing to ten digits hash alike, and
de-duplicating on that would merge two elements go-cty keeps apart. Where the
hash is equal the canonical key breaks the tie, which is deterministic here and
is bucket order there -- the one place this cannot follow go-cty, and the one
place go-cty guarantees nothing.
"""

from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal, localcontext
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from pyvider.cty.values.base import CtyValue

# Go's `strconv.Quote` escapes, which `fmt.Sprintf("%q", s)` produces for a
# string. The quote character is what makes the encoding prefix-free, and so is
# what decides the order of two strings where one starts with the other.
_GO_ESCAPES = {
    "\a": "\\a",
    "\b": "\\b",
    "\f": "\\f",
    "\n": "\\n",
    "\r": "\\r",
    "\t": "\\t",
    "\v": "\\v",
    "\\": "\\\\",
    '"': '\\"',
}

# `big.Float.String()` is `Text('g', 10)`.
_GO_FLOAT_DIGITS = 10


def go_quoted(text: str) -> str:
    """A string the way Go's `%q` writes it.

    `unicode.IsPrint` and `str.isprintable()` classify the same characters:
    everything outside the control, format, surrogate, private-use, unassigned
    and separator categories, plus the ASCII space. A character Go would escape
    is escaped here in Go's spelling -- `\\x` below 0x80, `\\u` below 0x10000,
    `\\U` above -- so the bytes compare the same way.
    """
    out = ['"']
    for char in text:
        escape = _GO_ESCAPES.get(char)
        if escape is not None:
            out.append(escape)
        elif char.isprintable():
            out.append(char)
        else:
            code = ord(char)
            if code < 0x80:
                out.append(f"\\x{code:02x}")
            elif code < 0x10000:
                out.append(f"\\u{code:04x}")
            else:
                out.append(f"\\U{code:08x}")
    out.append('"')
    return "".join(out)


def go_number_text(number: Decimal) -> str:
    """A number the way `big.Float.String()` writes it: `Text('g', 10)`.

    Ten significant digits, trailing zeros removed, and the C rule for which
    notation to use -- exponent form when the decimal exponent is below -4 or at
    least the precision. So 1e10 is `1e+10` and 0.0001 is `0.0001`, and
    2**100 + 1 is `1.2676506e+30` however many digits it actually has.
    """
    if number.is_nan():
        # go-cty's `big.Float` cannot hold one, so this is unreachable through a
        # value go-cty would accept; spelled rather than raising, because a sort
        # key must be total.
        return "NaN"
    if number.is_infinite():
        return "+Inf" if number > 0 else "-Inf"
    if number.is_zero():
        # Before the rounding below, which would lose the sign: `+Decimal("-0")`
        # is the arithmetic `0 + -0`, and the decimal specification makes that
        # `+0`. `big.Float` keeps the sign bit, and writes `-0`.
        return "-0" if number.is_signed() else "0"

    with localcontext() as ctx:
        ctx.prec = _GO_FLOAT_DIGITS
        rounded = +number
    sign, digits, exponent = rounded.normalize().as_tuple()
    assert isinstance(exponent, int)
    significant = "".join(str(digit) for digit in digits)
    adjusted = len(significant) - 1 + exponent
    lead = "-" if sign else ""

    if adjusted < -4 or adjusted >= _GO_FLOAT_DIGITS:
        mantissa = significant[0] + ("." + significant[1:] if len(significant) > 1 else "")
        return f"{lead}{mantissa}e{'+' if adjusted >= 0 else '-'}{abs(adjusted):02d}"
    return f"{lead}{format(rounded.normalize().copy_abs(), 'f')}"


def _append_hash(value: CtyValue[Any], out: list[str]) -> None:
    """go-cty's `appendSetHashBytes` (`cty/set_internals.go:144`), transcribed.

    Marks are stripped there before hashing and are absent here for the same
    reason: a mark is not part of a value for equality, and so not for order.
    """
    from pyvider.cty.types import (
        CtyBool,
        CtyCapsule,
        CtyDynamic,
        CtyList,
        CtyMap,
        CtyNumber,
        CtyObject,
        CtySet,
        CtyString,
        CtyTuple,
    )
    from pyvider.cty.values.base import CtyValue as _CtyValue

    value = value.unmark()[0] if value.marks else value
    # A `dynamic` position holds the concrete value, and that is what go-cty
    # would have been handed in the first place.
    while isinstance(value.type, CtyDynamic) and isinstance(value.value, _CtyValue):
        value = value.value

    if value.is_unknown:
        out.append("?")
        return
    if value.is_null:
        out.append("~")
        return

    match value.type:
        case CtyNumber():
            out.append(go_number_text(value.value if isinstance(value.value, Decimal) else Decimal(0)))
        case CtyBool():
            out.append("T" if value.value else "F")
        case CtyString():
            out.append(go_quoted(str(value.value)))
        case CtyCapsule():
            # go-cty writes `?` for a capsule with no `HashKey` op, which is
            # every capsule this package defines, so every capsule value hashes
            # alike and the tie-break in `order_key` decides.
            out.append("«?»")
        case CtyMap() | CtyList() | CtySet() | CtyObject() | CtyTuple():
            _append_container_hash(value, out)
        case _:
            out.append(repr(value.value))


def _append_container_hash(value: CtyValue[Any], out: list[str]) -> None:
    """The three bracketings go-cty uses, and what goes between them."""
    from pyvider.cty.types import CtyList, CtyMap, CtyObject, CtySet

    if isinstance(value.type, CtyMap | CtyObject):
        mapping = cast("dict[Any, Any]", value.value)
        # A map hashes its keys as values and an object hashes only the
        # attribute values, both in name order.
        if isinstance(value.type, CtyMap):
            out.append("{")
            for key in sorted(mapping, key=str):
                _append_hash_member(key, out)
                out.append(":")
                _append_hash_member(mapping[key], out)
                out.append(";")
            out.append("}")
        else:
            out.append("<")
            for name in sorted(mapping, key=str):
                _append_hash_member(mapping[name], out)
                out.append(";")
            out.append(">")
        return

    sequence = cast("Iterable[Any]", value.value)
    if isinstance(value.type, CtyList | CtySet):
        out.append("[")
        # A set's own members are hashed in this same order, so that two equal
        # sets nested inside a set hash alike however they were built.
        members = sorted(sequence, key=order_key) if isinstance(value.type, CtySet) else list(sequence)
        for member in members:
            _append_hash_member(member, out)
            out.append(";")
        out.append("]")
        return

    out.append("<")
    for member in sequence:
        _append_hash_member(member, out)
        out.append(";")
    out.append(">")


def _append_hash_member(member: object, out: list[str]) -> None:
    """A container member, or a map key, which is not a `CtyValue`.

    go-cty hashes a map's key by handing it back to `appendSetHashBytes` as a
    string value (`set_internals.go:210`), so it arrives Go-quoted; a payload
    dict here holds the key as a plain `str`. Anything else a hand-built value
    might be carrying falls back to its repr, which is orderable and stable.
    """
    from pyvider.cty.values.base import CtyValue as _CtyValue

    if isinstance(member, _CtyValue):
        _append_hash(member, out)
    elif isinstance(member, str):
        out.append(go_quoted(member))
    else:
        out.append(repr(member))


def hash_bytes(value: CtyValue[Any]) -> str:
    """The whole of `makeSetHashBytes` for one value, as text.

    Compared as a Python string rather than as bytes, which is the same order:
    UTF-8 preserves code-point order, and every character Go escapes is escaped
    into ASCII by `go_quoted` before it can matter.
    """
    out: list[str] = []
    _append_hash(value, out)
    return "".join(out)


def order_key(value: object) -> tuple[Any, ...]:
    """Where one element sorts in a set. go-cty's `setRules.Less`.

    Known first, then unknown, then null -- the ranks `Less` checks before it
    looks at the type at all. A string, number or bool is then compared
    directly, and everything else by its hash bytes, with the canonical key
    breaking a tie so the order stays total.
    """
    from pyvider.cty.types import CtyBool, CtyDynamic, CtyNumber, CtyString
    from pyvider.cty.values.base import CtyValue as _CtyValue

    if not isinstance(value, _CtyValue):
        # Ranked -1 for the same reason `_member_key` does: a raw member sorts
        # ahead of every real type rank rather than interleaving with them.
        return (0, -1, repr(value))

    while isinstance(value.type, CtyDynamic) and isinstance(value.value, _CtyValue):
        value = value.value

    if value.is_null:
        return (2,)
    if value.is_unknown:
        return (1,)

    type_rank = value.type._type_order
    if isinstance(value.type, CtyBool | CtyNumber | CtyString):
        return (0, type_rank, value.value)
    return (0, type_rank, hash_bytes(value), value._canonical_sort_key())


def identity_key(value: CtyValue[Any]) -> tuple[Any, ...]:
    """What makes two set elements the *same* element, as go-cty decides it.

    cty finds an element by hash bucket first and only compares values inside
    the bucket (`set.Set.Has`), so two values that hash differently are two
    elements however they compare. The one case where that bites is a signed
    zero: `makeSetHashBytes` writes `big.Float.String()`, which is `-0` for a
    negative zero and `0` for a positive one, so `toset([0, -0])` has **two**
    elements in go-cty and had one here -- a `Decimal("-0")` equals a
    `Decimal("0")`, so de-duplication merged them and the count that reaches
    Terraform was wrong.

    Deliberately not `__eq__` or `__hash__`, which stay where they are:
    go-cty's own `equal(0, -0)` is *true*, so the two are equal values that are
    nonetheless distinct set members. The canonical key is carried as well as
    the hash because the hash is not injective -- it renders a number at ten
    significant digits -- and cty compares with `Equivalent` inside the bucket
    for exactly that reason.

    Found 2026-08-19 by the stdlib fuzz, through `sethaselement`.
    """
    return (hash_bytes(value), value._canonical_sort_key())


# 🌊🪢🔚
