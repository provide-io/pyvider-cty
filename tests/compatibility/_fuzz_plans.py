#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""One generated argument list per stdlib function.

`SIGNATURES` says what each function's parameters *are* -- their types, the
variadic one, and the null/unknown/dynamic flags -- so for a function whose
parameters are concrete the argument list can be derived rather than written.
That is `_derived` below, and it covers a little over half the surface.

The rest declare a `dynamic` parameter, which in go-cty means "this function
decides for itself", so a signature cannot say what to generate: `flatten` wants
a sequence of sequences, `keys` wants something with keys, `zipmap` wants two
lists whose lengths matter. Those get a plan of their own here. A plan is still
a *strategy* -- what it fixes is the shape, never the values -- and the shapes
are chosen so the function is actually reached: a pool of arbitrary values would
spend most of its examples watching both implementations refuse the same
argument, which is agreement that proves nothing about the function.

Two plans are deliberately narrow, and both narrow away from a divergence that
is already recorded rather than away from difficulty:

  * **`log` and `pow`** are transcribed through `float64` on both sides, so a
    non-integral answer is a float64 that go-cty writes as eight bytes and this
    package writes as its shortest decimal text. That is the `pow(2,0.5)` entry
    in the sweep's `KNOWN_DIVERGENCES` -- same number, different wire -- so the
    exponents here are the ones whose answers are whole.
  * **`formatdate`** is generated from cty's own token vocabulary and never from
    a Go reference layout. This package refuses `"2006-01-02"` on purpose, where
    go-cty returns it as literal text; that is the deliberate divergence pinned
    in the sweep, and it is about a format nobody should be writing.
"""

from __future__ import annotations

from decimal import Decimal
import json
from typing import Any

from hypothesis import strategies as st

from pyvider.cty import (
    CtyList,
    CtyNumber,
    CtySet,
    CtyString,
    CtyType,
    CtyValue,
)
from pyvider.cty.functions import SIGNATURES
from pyvider.cty.functions._function import CtyParameter
from pyvider.cty.types import BytesCapsule
from tests.compatibility import _fuzz_values as v

Args = st.SearchStrategy[list[CtyValue[Any]]]

S, N = CtyString(), CtyNumber()
STRINGS = CtyList(element_type=S)


def _args(*parts: st.SearchStrategy[Any]) -> Args:
    return st.tuples(*parts).map(list)


def _variadic(part: st.SearchStrategy[Any], *, min_size: int = 1, max_size: int = 3) -> Args:
    return st.lists(part, min_size=min_size, max_size=max_size)


def _fixed_plus_variadic(
    fixed: st.SearchStrategy[Any], part: st.SearchStrategy[Any], *, max_size: int = 3
) -> Args:
    return st.tuples(fixed, st.lists(part, max_size=max_size)).map(lambda pair: [pair[0], *pair[1]])


# --------------------------------------------------------------------------- #
# strings
# --------------------------------------------------------------------------- #


@st.composite
def _string_and_a_piece_of_it(draw: Any, *, count: int = 2) -> list[CtyValue[Any]]:
    """A string plus one or two others, biased toward being *found* in it.

    `trimprefix`, `trimsuffix`, `replace` and `split` all answer trivially when
    the needle is not there, and an unbiased pool of strings almost never puts
    it there. Half the draws take a real slice of the subject.
    """
    text = draw(v.strings)
    pieces: list[CtyValue[Any]] = [S.validate(text)]
    for _ in range(count):
        if text and draw(st.booleans()):
            start = draw(st.integers(min_value=0, max_value=len(text) - 1))
            end = draw(st.integers(min_value=start + 1, max_value=len(text)))
            pieces.append(S.validate(text[start:end]))
        else:
            pieces.append(S.validate(draw(v.strings)))
    return pieces


SEPARATORS = st.sampled_from(["", ",", ", ", "-", "\n", "ab", "👍"])

# A pattern grammar both engines read the same way. RE2 has no backreference and
# no lookaround, so generating either would compare a refusal against an answer
# and report the RE2 divergence this package has already accepted; everything
# below is in both languages.
_ATOMS = st.sampled_from(["a", "b", "c", "1", " ", ".", "[a-c]", "[^a]", r"\d", r"\w", r"\s", "x"])
_QUANTIFIERS = st.sampled_from(["", "", "*", "+", "?", "{1,2}"])


@st.composite
def _patterns(draw: Any) -> str:
    body = "".join(draw(_ATOMS) + draw(_QUANTIFIERS) for _ in range(draw(st.integers(1, 4))))
    if draw(st.booleans()):
        name = draw(st.sampled_from(["one", "two"]))
        body = f"(?P<{name}>{body})" if draw(st.booleans()) else f"({body})"
    prefix = "^" if draw(st.booleans()) else ""
    suffix = "$" if draw(st.booleans()) else ""
    return f"{prefix}{body}{suffix}"


SUBJECTS = st.one_of(
    st.text(alphabet="abc123 xyz", max_size=12),
    v.strings,
)

# Go's expansion syntax, which this package has to translate into Python's.
REPLACEMENTS = st.sampled_from(["", "Z", "$1", "${one}", "$0", "<$1>", "$$", "a$1b"])


@st.composite
def _format_call(draw: Any) -> list[CtyValue[Any]]:
    """A verb, its argument, and sometimes the wrong number of them.

    The mismatches are the point as much as the matches: a format string with a
    verb and no argument, or an argument and no verb, is a refusal both
    implementations owe the caller in the same place.
    """
    verb, argument = draw(
        st.sampled_from(
            [
                ("%s", v.strings.map(S.validate)),
                ("%q", v.strings.map(S.validate)),
                ("%d", st.integers(-(10**6), 10**6).map(N.validate)),
                ("%5d", st.integers(-(10**6), 10**6).map(N.validate)),
                ("%-8s|", v.strings.map(S.validate)),
                ("%.2f", v.fractions.map(N.validate)),
                ("%e", v.fractions.map(N.validate)),
                ("%g", v.fractions.map(N.validate)),
                ("%x", st.integers(0, 10**6).map(N.validate)),
                ("%t", st.booleans().map(v.B.validate)),
                ("%v", v.scalars()),
                ("%#v", v.scalars()),
                ("%%", None),
                ("plain", None),
            ]
        )
    )
    literal = draw(st.sampled_from(["", " ", "x=", "\n"]))
    count = (
        draw(st.integers(min_value=0, max_value=2))
        if argument is None
        else draw(st.sampled_from([1, 1, 1, 0, 2]))
    )
    values = [draw(argument if argument is not None else v.scalars()) for _ in range(count)]
    return [S.validate(literal + verb), *values]


@st.composite
def _formatlist_call(draw: Any) -> list[CtyValue[Any]]:
    """The same, with the arguments lifted into lists of differing lengths."""
    verb = draw(st.sampled_from(["%s", "%d-%s", "%v", "%q"]))
    lists = draw(
        st.lists(
            st.one_of(
                v.lists(S, max_size=3),
                v.lists(N, max_size=3),
                v.scalars(),
            ),
            min_size=1,
            max_size=2,
        )
    )
    return [S.validate(verb), *lists]


# cty's own format vocabulary. Deliberately no digits: a digit run is how Go's
# reference layout is spelled, and this package refuses those on purpose.
_DATE_TOKENS = st.sampled_from(
    [
        "YYYY",
        "YY",
        "MMMM",
        "MMM",
        "MM",
        "M",
        "DD",
        "D",
        "EEEE",
        "EEE",
        "hh",
        "h",
        "HH",
        "mm",
        "m",
        "ss",
        "s",
        "AA",
        "aa",
        "ZZZZZ",
        "ZZZZ",
        "ZZZ",
        "Z",
    ]
)
_DATE_LITERALS = st.sampled_from(["-", "/", ":", " ", "T", ", ", "'at' ", ""])


@st.composite
def _date_format(draw: Any) -> str:
    return "".join(draw(_DATE_TOKENS) + draw(_DATE_LITERALS) for _ in range(draw(st.integers(1, 4))))


# Inside the calendar both implementations share: Go's `time.Time` runs past
# year 9999 and Python's `datetime` does not, which the sweep records.
TIMESTAMPS = st.builds(
    lambda y, mo, d, h, mi, s, z: f"{y:04d}-{mo:02d}-{d:02d}T{h:02d}:{mi:02d}:{s:02d}{z}",
    st.integers(min_value=2, max_value=9998),
    st.integers(min_value=1, max_value=12),
    st.integers(min_value=1, max_value=28),
    st.integers(min_value=0, max_value=23),
    st.integers(min_value=0, max_value=59),
    st.integers(min_value=0, max_value=59),
    st.sampled_from(["Z", "+00:00", "-05:00", "+05:30"]),
)

DURATIONS = st.one_of(
    st.sampled_from(["0", "1h", "-1h", "10m", "1h30m", "1.5h", "90s", "1ms", "-2h45m", "", "1d", "abc"]),
    st.builds(
        lambda n, unit: f"{n}{unit}",
        st.integers(-999, 999),
        st.sampled_from(["ns", "us", "ms", "s", "m", "h"]),
    ),
)


@st.composite
def _json_text(draw: Any) -> str:
    """A JSON document, and sometimes something that is not one."""
    if draw(st.integers(0, 5)) == 0:
        return draw(st.sampled_from(["", "{", "nul", "[1,]", "'x'", '{"a":}', "1 2"]))
    leaves = st.one_of(
        st.none(),
        st.booleans(),
        st.integers(-(10**6), 10**6),
        st.floats(allow_nan=False, allow_infinity=False, width=32),
        st.text(max_size=8),
    )
    document = draw(
        st.recursive(
            leaves,
            lambda children: st.one_of(
                st.lists(children, max_size=3),
                st.dictionaries(st.text(min_size=1, max_size=4), children, max_size=3),
            ),
            max_leaves=6,
        )
    )
    return json.dumps(document)


@st.composite
def _csv_text(draw: Any) -> str:
    """A CSV document with a header row, and sometimes a ragged one."""
    if draw(st.integers(0, 6)) == 0:
        return draw(st.sampled_from(["", "a,b\n1", "a,a\n1,2", '"unterminated', "\n"]))
    columns = draw(st.lists(st.sampled_from(["a", "b", "c", "name"]), min_size=1, max_size=3, unique=True))
    rows = draw(
        st.lists(
            st.lists(
                st.sampled_from(["1", "x", "", "a,b", 'say "hi"', "é"]),
                min_size=len(columns),
                max_size=len(columns),
            ),
            max_size=3,
        )
    )
    lines = [",".join(columns)]
    lines.extend(
        ",".join(f'"{cell}"' if ("," in cell or '"' in cell) else cell for cell in row) for row in rows
    )
    return "\n".join(lines)


DIGIT_STRINGS = st.one_of(
    st.text(alphabet="0123456789abcdefzZ+-", max_size=8),
    st.sampled_from(["0", "-1", "ff", "0x10", "777", "101", "  12", "12 ", "9223372036854775808"]),
)
BASES = st.one_of(st.integers(min_value=0, max_value=64), st.sampled_from([2, 8, 10, 16, 36, 62]))


# --------------------------------------------------------------------------- #
# numbers
# --------------------------------------------------------------------------- #

# A divisor whose reciprocal is exact in both models, plus zero -- which is an
# infinity rather than an error on both sides -- so the quotient stays inside
# the region the two number models share.
EXACT_DIVISORS = st.sampled_from(
    [Decimal(d) for d in (1, -1, 2, -2, 4, 8, 16, 64, 1024, 5, 10, 100, 0, "0.5", "0.25", "Infinity")]
)

# Whole answers only: `pow` and `log` both run through float64, and a
# non-integral result diverges in its *wire spelling* rather than its value.
POW_BASES = st.sampled_from([Decimal(b) for b in (0, 1, -1, 2, -2, 3, 10, "0.5", "Infinity", "-Infinity")])
POW_EXPONENTS = st.sampled_from([Decimal(e) for e in (0, 1, 2, 3, -1, -2, 8, 16)])
LOG_BASES = st.sampled_from([Decimal(b) for b in (2, 10, 0, 1, -1)])
LOG_NUMBERS = st.sampled_from([Decimal(n) for n in (1, 2, 4, 8, 1024, 10, 100, 0, -1, "Infinity")])

# Small enough that `range` cannot ask for a collection worth waiting for.
RANGE_NUMBERS = st.integers(min_value=-12, max_value=12).map(Decimal)


# --------------------------------------------------------------------------- #
# collections
# --------------------------------------------------------------------------- #


@st.composite
def _sequence_and_an_element(draw: Any) -> list[CtyValue[Any]]:
    """A sequence and a value, biased toward one the sequence actually holds.

    `contains` and `index` are only interesting when the answer is sometimes
    yes, and an independently drawn element is almost never in the collection.
    """
    element_type = draw(v.scalar_types)
    sequence = draw(st.one_of(v.lists(element_type), v.sets(element_type)))
    members = [element for element in sequence.value if not element.is_unknown and not element.is_null]
    if members and draw(st.booleans()):
        return [sequence, draw(st.sampled_from(members))]
    return [sequence, draw(v.members(element_type))]


@st.composite
def _mapping_key_and_default(draw: Any) -> list[CtyValue[Any]]:
    """A map or object, a key that is sometimes in it, and a default."""
    mapping = draw(v.mappings())
    names = list(mapping.value) if isinstance(mapping.value, dict) else []
    key = draw(st.sampled_from(names)) if names and draw(st.booleans()) else draw(v.strings)
    return [mapping, S.validate(key), draw(v.scalars())]


@st.composite
def _collection_and_a_key(draw: Any) -> list[CtyValue[Any]]:
    """For `hasindex`, whose key is an index for a sequence and a name for a map."""
    collection = draw(v.collections())
    if isinstance(collection.value, dict):
        names = list(collection.value)
        key = S.validate(draw(st.sampled_from(names)) if names and draw(st.booleans()) else draw(v.strings))
    else:
        key = N.validate(draw(v.indices))
    return [collection, key]


@st.composite
def _nested_sequences(draw: Any) -> CtyValue[Any]:
    """A list or tuple whose elements are themselves sequences, for `flatten`."""
    element_type = draw(v.scalar_types)
    inner = st.one_of(v.lists(element_type, max_size=3), v.sets(element_type, max_size=3))
    rows = draw(st.lists(inner, max_size=3))
    if draw(st.booleans()) and rows:
        # A tuple, so the element types differ from row to row -- which is the
        # shape whose element unification diverged in `unify`.
        from pyvider.cty import CtyTuple

        return CtyTuple(element_types=tuple(row.type for row in rows)).validate(rows)
    return CtyList(element_type=CtyList(element_type=element_type)).validate(
        [CtyList(element_type=element_type).validate(list(row.value)) for row in rows]
    )


@st.composite
def _zipmap_call(draw: Any) -> list[CtyValue[Any]]:
    """Keys and values, whose lengths agree only sometimes."""
    keys = draw(st.lists(v.map_keys, max_size=3))
    element_type = draw(v.scalar_types)
    count = len(keys) if draw(st.booleans()) else draw(st.integers(0, 3))
    values = [draw(v.members(element_type)) for _ in range(count)]
    return [
        STRINGS.validate([S.validate(key) for key in keys]),
        CtyList(element_type=element_type).validate(values),
    ]


@st.composite
def _sets_of_one_or_many_types(draw: Any, *, min_size: int = 1, max_size: int = 3) -> list[CtyValue[Any]]:
    """Sets whose element types agree, or do not.

    Set operations unify their arguments' element types, and unification is the
    surface where seventeen divergences were found on 2026-08-19 -- so half the
    draws hand them element types that have to be reconciled.
    """
    count = draw(st.integers(min_value=min_size, max_value=max_size))
    if draw(st.booleans()):
        element_type = draw(v.scalar_types)
        return [draw(v.sets(element_type)) for _ in range(count)]
    return [draw(v.sets()) for _ in range(count)]


@st.composite
def _coalesce_call(draw: Any) -> list[CtyValue[Any]]:
    """Values of one type, some of them null, which is what `coalesce` is for."""
    element_type = draw(v.scalar_types)
    return draw(
        st.lists(
            st.one_of(v.scalars(element_type), st.just(CtyValue.null(element_type))),
            min_size=1,
            max_size=3,
        )
    )


def _comparable_value() -> st.SearchStrategy[CtyValue[Any]]:
    """Anything `equal` can be asked about that go-cty answers *deterministically*.

    Two exclusions, and the second is not this package's fault.

    **No capsules.** go-cty compares one with no `Equals` op by pointer, so
    `equal(bytes("hi"), bytes("hi"))` is false there for two buffers built
    separately. This package honours the payload's own `__eq__` when it has one,
    which `bytes` does -- a deliberate carve-out recorded in
    `docs/reference/go-cty-comparison.md`, because Python identity for an
    immutable `bytes` is decided by interning.

    **No unknown members.** `cty.Value.Equals` walks a map's keys in Go's *map
    iteration order*, which is randomised, and returns early on either a missing
    key (false) or an undecided element (unknown) -- whichever it reaches first.
    So comparing `{"": null, " ": 0}` with `{"a": 0, " ": unknown}` answers
    `true` or `unknown` depending on the run: eight calls to the harness gave
    five and three. Nothing can match a coin flip. A whole-value unknown is
    still generated, because that path is decided before the walk.
    """
    return st.one_of(
        v.scalars(),
        v.collections(unknowns=False),
        v.scalar_types.map(CtyValue.null),
        v.scalar_types.map(CtyValue.unknown),
    )


@st.composite
def _regex_call(draw: Any) -> list[CtyValue[Any]]:
    """A pattern and a subject, half of them matching by construction.

    `regex` is an error when nothing matches, and a pattern drawn independently
    of its subject matches too rarely to be coverage -- the guard below caught
    exactly that. Half the draws build a literal pattern and then build a
    subject around it, so the match is guaranteed; the other half are the
    generated patterns, which are where a divergence would come from.
    """
    if draw(st.booleans()):
        literal = draw(st.text(alphabet="abcxyz123", min_size=1, max_size=3))
        subject = draw(st.text(alphabet="abc ", max_size=4)) + literal
        return [S.validate(literal), S.validate(subject)]
    return [S.validate(draw(_patterns())), S.validate(draw(SUBJECTS))]


@st.composite
def _slice_call(draw: Any) -> list[CtyValue[Any]]:
    """A sequence with indices drawn from its own length, in and out of range."""
    sequence = draw(st.one_of(v.lists(), v.tuples()))
    size = len(sequence.value)
    start = draw(st.integers(min_value=-1, max_value=size + 1))
    # Half the draws keep the pair in order and in range, so that the function
    # is reached at all; the other half are free to be backwards or past the
    # end, which is where the two implementations could refuse differently.
    if draw(st.booleans()):
        end = draw(st.integers(min_value=min(start, size), max_value=size))
    else:
        end = draw(st.integers(min_value=-1, max_value=size + 1))
    return [sequence, N.validate(Decimal(start)), N.validate(Decimal(end))]


@st.composite
def _bytes_slice_call(draw: Any) -> list[CtyValue[Any]]:
    """A buffer and two offsets, drawn from the buffer's own length.

    Derived from the signature the offsets were ordinary numbers, so every draw
    was out of range and `bytesslice` was never once reached -- which is what
    the coverage guard is for.
    """
    buffer = draw(v.byte_buffers)
    bound = len(buffer) + 1
    return [
        BytesCapsule.validate(buffer),
        N.validate(draw(st.integers(min_value=-1, max_value=bound))),
        N.validate(draw(st.integers(min_value=-1, max_value=bound))),
    ]


@st.composite
def _index_call(draw: Any) -> list[CtyValue[Any]]:
    """A collection and a key into it.

    go-cty's `index` is the *indexing operation* -- `collection[key]` -- and not
    Terraform's `index()`, which searches. So the key is a number for a sequence
    and a name for a mapping, and drawing an element instead only ever produced
    `key for list must be number`.
    """
    # No objects: go-cty's `index` takes "a list, a map or a tuple" and refuses
    # an object outright, so an object draw is never an answer.
    collection = draw(st.one_of(v.lists(), v.maps(), v.tuples()))
    if isinstance(collection.value, dict):
        names = list(collection.value)
        chosen = draw(st.sampled_from(names)) if names and draw(st.booleans()) else draw(v.strings)
        return [collection, S.validate(chosen)]
    size = len(collection.value)
    position = draw(st.integers(min_value=-1, max_value=max(size, 1)))
    return [collection, N.validate(Decimal(position))]


# `inf` is in and `Infinity` is not: Go's `big.ParseFloat` takes the first and
# refuses the second, while `Decimal` takes both. That is the accepted
# divergence pinned by `test_non_finite_numbers.py` -- what this package accepts
# is wider, and every spelling it accepts produces the same `+Inf` go-cty writes,
# so there is no wire consequence and nothing to find by generating it.
NUMERIC_TEXT = st.one_of(
    st.sampled_from(["0", "1", "-1", "1.5", "1e3", "0x10", "", " 1", "abc", "inf", "+Inf", "-Inf"]),
    st.integers(-(10**6), 10**6).map(str),
)


PLANS: dict[str, Args] = {
    # strings
    "trim": _string_and_a_piece_of_it(count=1),
    "trimprefix": _string_and_a_piece_of_it(count=1),
    "trimsuffix": _string_and_a_piece_of_it(count=1),
    "replace": _string_and_a_piece_of_it(count=2),
    "split": _args(SEPARATORS.map(S.validate), v.strings.map(S.validate)),
    "join": _fixed_plus_variadic(SEPARATORS.map(S.validate), v.lists(S)),
    "indent": _args(st.integers(0, 8).map(lambda n: N.validate(Decimal(n))), v.strings.map(S.validate)),
    "substr": _args(v.strings.map(S.validate), v.indices.map(N.validate), v.indices.map(N.validate)),
    "format": _format_call(),
    "formatlist": _formatlist_call(),
    "regex": _regex_call(),
    "regexall": _args(_patterns().map(S.validate), SUBJECTS.map(S.validate)),
    "regexreplace": _args(SUBJECTS.map(S.validate), _patterns().map(S.validate), REPLACEMENTS.map(S.validate)),
    "csvdecode": _args(_csv_text().map(S.validate)),
    "jsondecode": _args(_json_text().map(S.validate)),
    "jsonencode": _args(v.any_value()),
    "formatdate": _args(_date_format().map(S.validate), TIMESTAMPS.map(S.validate)),
    "timeadd": _args(TIMESTAMPS.map(S.validate), DURATIONS.map(S.validate)),
    "parseint": _args(DIGIT_STRINGS.map(S.validate), BASES.map(lambda b: N.validate(Decimal(b)))),
    # bytes
    "bytesslice": _bytes_slice_call(),
    # numbers
    # A whole number inside the int64 range, which is all `signum` accepts; the
    # general pool is mostly wider than that and never reached the function.
    "signum": _args(
        st.integers(min_value=-(2**63), max_value=2**63 - 1).map(lambda i: N.validate(Decimal(i)))
    ),
    "divide": _args(v.numbers.map(N.validate), EXACT_DIVISORS.map(N.validate)),
    "pow": _args(POW_BASES.map(N.validate), POW_EXPONENTS.map(N.validate)),
    "log": _args(LOG_NUMBERS.map(N.validate), LOG_BASES.map(N.validate)),
    "range": _variadic(RANGE_NUMBERS.map(N.validate), max_size=3),
    # collections
    "length": _args(st.one_of(v.collections(), v.scalars(S))),
    # Lists and tuples: go-cty refuses to read an element from a set outright,
    # "because its elements do not have indices".
    "element": _args(st.one_of(v.lists(), v.tuples()), v.indices.map(N.validate)),
    "index": _index_call(),
    "contains": _sequence_and_an_element(),
    "sethaselement": _sequence_and_an_element().map(
        lambda pair: [
            CtySet(element_type=pair[0].type.element_type).validate(list(pair[0].value))
            if isinstance(pair[0].type, CtyList)
            else pair[0],
            pair[1],
        ]
    ),
    "hasindex": _collection_and_a_key(),
    "distinct": _args(v.lists()),
    "chunklist": _args(v.lists(), v.sizes.map(N.validate)),
    "flatten": _args(_nested_sequences()),
    "keys": _args(v.mappings()),
    "values": _args(v.mappings()),
    "lookup": _mapping_key_and_default(),
    "merge": _variadic(v.mappings(), max_size=3),
    # Same shape as `slice`: `coalescelist arguments must be lists or tuples`.
    "coalescelist": _variadic(st.one_of(v.lists(), v.tuples()), max_size=3),
    "coalesce": _coalesce_call(),
    "compact": _args(v.lists(S)),
    "concat": _variadic(v.sequences(), max_size=3),
    "reverselist": _args(st.one_of(v.lists(), v.tuples())),
    "setproduct": _variadic(v.sets(max_size=3), max_size=3),
    # Lists and tuples only: go-cty refuses to slice a set outright, "because
    # its elements do not have indices", so a set draw is never an answer.
    "slice": _slice_call(),
    # Lists of strings only, which is go-cty's whole parameter: `cty.List(cty.String)`.
    # This package widens it to accept a set, a tuple and a non-string element
    # type, because nothing in its call path performs the conversion HCL does
    # before go-cty ever sees the argument. That widening is adjudicated and
    # recorded in `docs/reference/go-cty-comparison.md`; generating into it
    # would re-report a decision as a divergence.
    "sort": _args(v.lists(S)),
    "zipmap": _zipmap_call(),
    # sets
    "setunion": _sets_of_one_or_many_types(min_size=1, max_size=3),
    "setintersection": _sets_of_one_or_many_types(min_size=1, max_size=3),
    "setsymmetricdifference": _sets_of_one_or_many_types(min_size=1, max_size=3),
    "setsubtract": _sets_of_one_or_many_types(min_size=2, max_size=2),
    # conversion and equality
    # Weighted toward what `tostring` converts. go-cty converts a number and a
    # bool and nothing else, so a pool of arbitrary values watches both sides
    # refuse -- which the coverage guard reports as a plan that reaches nothing.
    "tostring": _args(st.one_of(v.scalars(), v.scalars(), v.any_value())),
    # A pool of arbitrary values converts to a number about never, so the
    # numeric spellings -- and the near-misses Go's `big.ParseFloat` refuses --
    # are drawn on purpose. Same for the boolean spellings.
    "tonumber": _args(
        st.one_of(v.scalars(N), NUMERIC_TEXT.map(S.validate), v.any_value()),
    ),
    "tobool": _args(
        st.one_of(
            st.booleans().map(v.B.validate),
            st.sampled_from(["true", "false", "1", "0", "yes", ""]).map(S.validate),
            v.any_value(),
        ),
    ),
    "assertnotnull": _args(v.any_value()),
    # No capsules. go-cty compares a capsule with no `Equals` op by *pointer*,
    # so `equal(bytes("hi"), bytes("hi"))` is false there for two buffers built
    # separately. This package honours the payload's own `__eq__` when it has
    # one, which `bytes` does -- a deliberate carve-out recorded in
    # `docs/reference/go-cty-comparison.md`, because Python identity for an
    # immutable `bytes` is decided by interning and would answer differently
    # depending on how the buffer was built.
    "equal": _args(_comparable_value(), _comparable_value()),
    "notequal": _args(_comparable_value(), _comparable_value()),
}
"""The functions a signature cannot generate for, plus the ones it generates badly."""


def _parameter(param: CtyParameter) -> st.SearchStrategy[Any]:
    """A conforming argument for one declared parameter."""
    declared = param.type
    if isinstance(declared, CtyString):
        return v.strings.map(S.validate)
    if isinstance(declared, CtyNumber):
        return v.numbers.map(N.validate)
    if declared.equal(BytesCapsule):
        return v.bytes_values()
    if isinstance(declared, CtySet):
        return v.sets()
    if isinstance(declared, CtyList):
        element = declared.element_type
        return v.lists(element if not _is_dynamic(element) else None)
    if _is_dynamic(declared):
        return v.any_value()
    return st.booleans().map(declared.validate)


def _is_dynamic(cty_type: CtyType[Any]) -> bool:
    from pyvider.cty import CtyDynamic

    return isinstance(cty_type, CtyDynamic)


def _derived(name: str) -> Args:
    """The argument list a declared signature is enough to generate."""
    spec = SIGNATURES[name].spec
    fixed = [_parameter(param) for param in spec.params]
    if spec.var_param is None:
        return _args(*fixed) if fixed else st.just([])
    variadic = st.lists(_parameter(spec.var_param), min_size=1 if not fixed else 0, max_size=3)
    if not fixed:
        return variadic
    return st.tuples(st.tuples(*fixed), variadic).map(lambda pair: [*pair[0], *pair[1]])


def arguments_for(name: str) -> Args:
    """The generated argument list for `name`, planned or derived.

    An explicit `is None`, not `or`: truth-testing a hypothesis strategy warns,
    and one warning per plan per example is six thousand of them in a wide run.
    """
    planned = PLANS.get(name)
    return _derived(name) if planned is None else planned


# The functions whose arguments come from the signature alone. Derived rather
# than listed, so adding a plan above cannot leave a stale name behind.
DERIVED = sorted(name for name in SIGNATURES if name not in PLANS)


# 🌊🪢🔚
