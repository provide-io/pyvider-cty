#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""The scalar half of the stdlib sweep table: strings, numbers, logic, dynamic.

Split out of `test_stdlib_sweep.py` at this repository's 500-line ceiling for a
test file. The division is by argument shape rather than by anything the driver
cares about -- it walks `CASES`, which is the two halves concatenated.
"""

from __future__ import annotations

from tests.compatibility._sweep_args import (
    CONJUNCT,
    DYNAMIC_UK,
    FAMILY,
    FLAGS,
    HANGUL_JAMO,
    THUMB_TONED,
    Arg,
    bl,
    ln_uk_len,
    ls,
    mp,
    nm,
    nm_uk,
    st,
    st_uk,
)

# (function name, arguments). The id is derived, so adding a row is one line.
SCALAR_CASES: list[tuple[str, list[Arg]]] = [
    # strings
    ("upper", [st("héllo")]),
    ("lower", [st("HÉLLO")]),
    # Case mappings that are not one code point to one code point. `héllo` and
    # `HÉLLO` map 1:1 in both directions, so the sweep could not tell Go's simple
    # per-rune mapping from Python's full mapping: `str.upper()` expands ß to SS
    # and ﬁ to FI, `str.lower()` picks the final sigma for a trailing Σ, and
    # `İ`.lower() adds a combining dot. go-cty does none of those.
    ("upper", [st("straße")]),
    ("upper", [st("ﬁ")]),
    ("lower", [st("ΣΣ")]),
    ("lower", [st("İ")]),
    ("title", [st("a bc")]),
    ("title", [st("hEllo wOrld")]),
    ("strrev", [st("abc")]),
    ("strrev", [st("héllo")]),
    ("chomp", [st("a\n")]),
    ("chomp", [st("a\r\n")]),
    ("trimspace", [st("  a  ")]),
    ("trimspace", [st("\t a \n")]),
    ("trim", [st("xxaxx"), st("x")]),
    ("trim", [st("abc"), st("z")]),
    ("trimprefix", [st("abc"), st("a")]),
    ("trimprefix", [st("abc"), st("z")]),
    ("trimsuffix", [st("abc"), st("c")]),
    ("trimsuffix", [st("abc"), st("z")]),
    ("replace", [st("aaa"), st("a"), st("b")]),
    ("replace", [st("abc"), st(""), st("-")]),
    ("split", [st(","), st("a,b")]),
    ("split", [st(","), st("")]),
    ("join", [st(","), ls(["a", "b"])]),
    ("join", [st(","), ls([])]),
    ("substr", [st("abcdef"), nm(1), nm(3)]),
    ("substr", [st("abcdef"), nm(1), nm(-1)]),
    ("substr", [st("héllo"), nm(0), nm(2)]),
    # A negative offset counts from the end, and a zero length reached that way
    # means "the rest" rather than "nothing" -- both were refused outright here
    # until the grapheme work went through go-cty's algorithm line by line.
    ("substr", [st("abcdef"), nm(-3), nm(2)]),
    ("substr", [st("abcdef"), nm(-3), nm(0)]),
    ("substr", [st("abcdef"), nm(-100), nm(2)]),
    ("substr", [st("abcdef"), nm(0), nm(0)]),
    ("substr", [st("abcdef"), nm(6), nm(1)]),
    ("substr", [st("abcdef"), nm(2), nm(10)]),
    ("indent", [nm(2), st("a\nb")]),
    ("indent", [nm(0), st("a\nb")]),
    ("assertnotnull", [st("x")]),
    ("assertnotnull", [nm(1)]),
    # Grapheme clusters. `héllo` proves nothing about segmentation -- it
    # NFC-composes to one code point per character, which is why four functions
    # measured in code points for as long as they did. These do not compose.
    ("strlen", [st("abc")]),
    ("strlen", [st(FAMILY)]),
    ("strlen", [st(f"ab{FAMILY}cd")]),
    ("strlen", [st(FLAGS)]),
    ("strlen", [st(THUMB_TONED)]),
    ("strlen", [st(HANGUL_JAMO)]),
    ("strlen", [st(CONJUNCT)]),
    ("strlen", [st("")]),
    ("strlen", [st_uk("abc")]),
    ("strrev", [st(f"ab{FAMILY}cd")]),
    ("strrev", [st(FLAGS)]),
    ("strrev", [st(CONJUNCT)]),
    ("substr", [st(f"{FAMILY}xy"), nm(0), nm(1)]),
    ("substr", [st(f"{FAMILY}xy"), nm(1), nm(1)]),
    ("substr", [st(CONJUNCT), nm(0), nm(1)]),
    ("format", [st("%5s|"), st(FAMILY)]),
    ("format", [st("%-5s|"), st(FAMILY)]),
    ("format", [st("%.1s"), st(FAMILY)]),
    ("format", [st("%.1s"), st(CONJUNCT)]),
    ("format", [st("%q"), st(FAMILY)]),
    ("format", [st("%q"), st("héllo")]),
    # Literal text *before* the first verb. These rows agree trivially when
    # everything is known -- what they exist for is the unknown population,
    # where the deferred result is refined with the template's literal prefix
    # and `SafeKnownPrefix` decides whether the trailing delimiter survives
    # (`ctystrings/prefix.go:140` keeps it; until 2026-08-17 this package
    # dropped it, and no row could see the difference).
    ("format", [st("hi %s"), st("x")]),
    ("format", [st("id-%s"), st("x")]),
    ("format", [st("ab%s"), st("x")]),
    # regexp
    ("regex", [st("a(b)c"), st("abc")]),
    ("regex", [st("a(b)c"), st("zzz")]),
    ("regexall", [st("a(b)"), st("abab")]),
    ("regexall", [st("x"), st("y")]),
    ("regexreplace", [st("-ab-axxb-"), st("a(x*)b"), st("${1}W")]),
    ("regexreplace", [st("-ab-axxb-"), st("a(x*)b"), st("$1W")]),
    # numbers
    ("abs", [nm(-3)]),
    ("abs", [nm("3.5")]),
    ("ceil", [nm("1.2")]),
    ("ceil", [nm("-1.2")]),
    ("floor", [nm("1.8")]),
    ("floor", [nm("-1.8")]),
    ("signum", [nm(-5)]),
    ("signum", [nm(0)]),
    ("int", [nm("3.9")]),
    ("int", [nm("-3.9")]),
    ("add", [nm(1), nm(2)]),
    ("add", [nm("1.5"), nm("2.25")]),
    ("subtract", [nm(5), nm(2)]),
    ("subtract", [nm(2), nm(5)]),
    ("multiply", [nm(3), nm(4)]),
    ("multiply", [nm(-3), nm(4)]),
    ("divide", [nm(7), nm(2)]),
    ("divide", [nm(1), nm(3)]),
    ("modulo", [nm(7), nm(3)]),
    ("modulo", [nm(-7), nm(3)]),
    ("negate", [nm(3)]),
    ("negate", [nm(0)]),
    ("pow", [nm(2), nm(10)]),
    ("pow", [nm(2), nm("0.5")]),
    # go-cty computes `pow` in float64, so its answer carries that type's
    # rounding, its overflow to an infinity and its range refusal.
    ("pow", [nm("1.1"), nm(2)]),
    ("pow", [nm(10), nm(308)]),
    ("pow", [nm(10), nm(400)]),
    ("pow", [nm(10), nm(1000000)]),
    ("pow", [nm(10), nm(-1000000)]),
    ("pow", [nm(0), nm(0)]),
    ("pow", [nm(0), nm(-1)]),
    ("pow", [nm(-8), nm("0.5")]),
    ("pow", [nm("-0.0"), nm(-1)]),
    ("log", [nm(8), nm(2)]),
    ("max", [nm(1), nm(5)]),
    ("max", [nm(-1), nm(-5)]),
    ("max", [nm(1), nm(2), nm(3)]),
    ("min", [nm(1), nm(5)]),
    ("min", [nm(-1), nm(-5)]),
    ("min", [nm(1), nm(2), nm(3)]),
    ("parseint", [st("ff"), nm(16)]),
    ("parseint", [st("-10"), nm(10)]),
    # comparison and logic. Both boolean outcomes for every operator: until
    # 2026-08-17 each had exactly one row, all of them answering true, so a
    # comparison that always answered true would have swept clean.
    ("equal", [st("a"), st("a")]),
    ("equal", [st("a"), st("b")]),
    ("equal", [nm(1), nm("1.0")]),
    ("notequal", [st("a"), st("b")]),
    ("notequal", [st("a"), st("a")]),
    ("greaterthan", [nm(2), nm(1)]),
    ("greaterthan", [nm(1), nm(2)]),
    ("greaterthanorequalto", [nm(1), nm(1)]),
    ("greaterthanorequalto", [nm(1), nm(2)]),
    ("lessthan", [nm(1), nm(2)]),
    ("lessthan", [nm(2), nm(1)]),
    ("lessthanorequalto", [nm(1), nm(1)]),
    ("lessthanorequalto", [nm(2), nm(1)]),
    # Refined unknowns travelling *into* a function. The comparisons consult
    # the ranges and can answer while the value stays unknown; the arithmetic
    # and min/max rows pin the opposite -- however tight the bounds, functions
    # whose parameters do not admit an unknown answer a bare not-null unknown,
    # because go-cty's bound arithmetic lives on Value's operators, not here.
    ("lessthan", [nm_uk(upper=("10", False)), nm(20)]),
    ("lessthan", [nm_uk(lower=("10", True), upper=("20", True)), nm(15)]),
    ("greaterthan", [nm_uk(lower=("100", False)), nm(50)]),
    ("max", [nm_uk(upper=("10", False)), nm(20)]),
    ("min", [nm_uk(lower=("100", False)), nm(50)]),
    ("add", [nm_uk(lower=("0", False)), nm_uk(lower=("0", False))]),
    ("length", [ln_uk_len(3, 3)]),
    ("length", [ln_uk_len(1, 5)]),
    ("length", [ln_uk_len(2, None)]),
    ("coalescelist", [ln_uk_len(1, None), ls(["b"])]),
    # `cty.DynamicVal` at each interesting shape: unary, variadic-first,
    # collection position, index position, a type-callback that must unify it.
    # go-cty stops checking arguments at the first inexactly-typed one and the
    # framework port had this wrong for twenty functions, found by review
    # rather than by a row -- these are the rows that would have found it.
    ("not", [DYNAMIC_UK]),
    ("length", [DYNAMIC_UK]),
    ("coalesce", [DYNAMIC_UK, st("b")]),
    ("concat", [DYNAMIC_UK, ls(["b"])]),
    ("jsonencode", [DYNAMIC_UK]),
    ("format", [st("%s!"), DYNAMIC_UK]),
    ("equal", [DYNAMIC_UK, st("a")]),
    ("merge", [mp({"a": "1"}), DYNAMIC_UK]),
    ("element", [DYNAMIC_UK, nm(0)]),
    ("not", [bl(True)]),
    ("not", [bl(False)]),
    ("and", [bl(True), bl(False)]),
    ("and", [bl(True), bl(True)]),
    ("and", [bl(False), bl(False)]),
    ("or", [bl(True), bl(False)]),
    ("or", [bl(False), bl(False)]),
    ("or", [bl(True), bl(True)]),
]

# 🌊🪢🔚
