# Going from Python: where your instinct is wrong

Every function in this library answers what **go-cty** answers, because that is
what Terraform links. Most of the time that is also what Python would answer,
and you can stop reading. This page is the rest — the places where correct-looking
Python produces a different value from the one Terraform will produce, so that
you meet them here rather than in a plan diff.

Every claim below is an assertion that runs in CI. If one of them stops being
true, this page fails the build.

## Numbers

### The sign of a zero is load-bearing, and Python throws it away

`-0` and `0` are different values in go-cty, they encode to different bytes, and
Python's arithmetic operators do not preserve the distinction: `-Decimal(0)` is
the *arithmetic* `0 - 0`, which the decimal specification defines as `+0`.

```python
from decimal import Decimal

from pyvider.cty import CtyNumber
from pyvider.cty.functions import STDLIB

number = CtyNumber()

# Python's own answer, which is not go-cty's.
assert not (-Decimal(0)).is_signed()

# This library's, which is.
negated = STDLIB["negate"](number.validate(0)).value
assert negated.is_zero() and negated.is_signed()
```

Five functions have five different rules for it, all transcribed from go-cty:

```python
def sign_of(func: str, *args: str) -> str:
    answer = STDLIB[func](*[number.validate(Decimal(a)) for a in args]).value
    return "-0" if answer.is_signed() else "0"

assert sign_of("negate", "0") == "-0"        # a big.Float negation flips the sign bit
assert sign_of("int", "-0.5") == "0"         # truncation goes through a big.Int, which has no -0
assert sign_of("int", "-0.0") == "-0"        # already whole: returned untouched
assert sign_of("ceil", "-0.0") == "0"        # ceil has no untouched path at all
assert sign_of("modulo", "-1", "1") == "0"   # a - b*trunc(a/b), and x - x is +0
assert sign_of("modulo", "-0.0", "1") == "-0"  # a zero dividend takes a sign from the divisor
```

### Arithmetic is not computed in your ambient `Decimal` context

Python's default context carries 28 significant digits and rounds silently past
them. go-cty computes in a 512-bit `big.Float`. This library computes at the
width that model spells, so a wide integer keeps every digit:

```python
big = number.validate(2**100)
one = number.validate(1)

assert format(STDLIB["add"](big, one).value, "f") == "1267650600228229401496703205377"

# Not what a plain Decimal add in the default context gives:
from decimal import getcontext
assert getcontext().prec == 28
```

Past that width the two models genuinely differ and always will — a
non-terminating quotient ends `…335` in go-cty because it is a binary float
printed exactly, and `…333` here at any precision. That is
[a recorded divergence](../../reference/go-cty-comparison.md), not a bug, and it
also bounds what a number can be *written* as: go-cty spells at most 154
significant digits and a `Decimal` spells all of them.

### `Decimal` accepts input Terraform will reject

`Decimal(" 1")` is `1`, because the constructor strips surrounding whitespace.
Go's `big.ParseFloat` grammar has no room for a space, so `tonumber` refuses it:

```python
from pyvider.cty import CtyString

string = CtyString()
assert Decimal(" 1") == 1

from pyvider.cty.functions._function import CtyArgumentError

try:
    STDLIB["tonumber"](string.validate(" 1"))
    raise AssertionError("should have refused")
except CtyArgumentError as exc:
    assert "cannot convert string to number" in str(exc)
```

## Sets

### A set is not ordered the way you would sort it

Element order reaches the wire, and go-cty picks it two different ways.
A set of strings, numbers or bools is ordered by **value**. A set of anything
else is ordered by the **bytes of go-cty's element hash**, which renders numbers
as text and quotes strings — so the comparison is not the one a Python
`sorted()` would make:

```python
from pyvider.cty import CtySet, CtyTuple

pairs = CtySet(element_type=CtyTuple(element_types=(CtyNumber(),)))
order = [row.value[0].value for row in pairs.validate([[1], [12], [2]]).value]

# `<12;>` sorts before `<1;>`, because "2" sorts before ";".
assert order == [Decimal(12), Decimal(1), Decimal(2)]

# Primitives are unaffected: still ordered by value.
assert [n.value for n in CtySet(element_type=CtyNumber()).validate([3, 1, 12]).value] == [
    Decimal(1),
    Decimal(3),
    Decimal(12),
]
```

You do not need to reproduce this rule — the codecs apply it — but do not assume
a set's iteration order matches `sorted()` when its elements are containers.

### `toset([0, -0])` has two elements

Set membership in cty is by hash bucket, and a negative zero hashes differently
from a positive one. Two values that compare *equal* can therefore both be in
the set:

```python
numbers = CtySet(element_type=CtyNumber())
assert len(numbers.validate([Decimal(0), Decimal("-0")]).value) == 2

# ...while `equal` still calls them equal, exactly as go-cty does.
assert STDLIB["equal"](number.validate(0), number.validate(Decimal("-0"))).value is True
```

## Regular expressions

Python's `re` is not RE2, in two ways that change *answers* rather than what
compiles.

### The Perl classes are ASCII

RE2 defines `\d`, `\s`, `\w` and `\b` over ASCII only. Python's are
Unicode-aware, so a pattern that looks portable is not:

```python
import re

assert re.findall(r"\w", "²") == ["²"]  # Python: ² is a word character
assert STDLIB["regexall"](string.validate(r"\w"), string.validate("²")).value == ()
```

### An empty match next to a real one is dropped

Go's `FindAll` skips an empty match sitting exactly where the previous match
ended; `re.finditer` keeps it. That is one extra element in a list you index
into, or one extra replacement:

```python
assert re.findall("a*a*", "a") == ["a", ""]

found = STDLIB["regexall"](string.validate("a*a*"), string.validate("a"))
assert [m.value for m in found.value] == ["a"]

replaced = STDLIB["regexreplace"](
    string.validate(" "), string.validate(" *"), string.validate("Z")
)
assert replaced.value == "Z"  # not "ZZ"
```

**The one that only bites in production**: a backreference or a lookaround
compiles here and is *refused* by go-cty, so a pattern tested only against this
library can ship and then fail the first time the configuration runs through
real Terraform. This is the accepted divergence; there is no way to make Python
refuse it without shipping RE2, which cannot be cross-compiled to Pyodide.

## Text and encoding

### `%q` and `%#v` escape HTML characters

go-cty's `%q` is not Go's `%q` — it is `ctyjson.Marshal`, and Go's
`encoding/json` escapes `<`, `>` and `&` by default. Those bytes end up in state
files that are compared textually:

```python
import json

assert json.dumps("a<b>&c") == '"a<b>&c"'
assert STDLIB["format"](string.validate("%q"), string.validate("a<b>&c")).value == (
    '"a\\u003cb\\u003e\\u0026c"'
)
```

### `csvdecode` is as strict as Go's reader

Python's `csv` module has no strict mode and will happily parse a malformed
document. Go's refuses, which means a provider that accepted one here would be
building state Terraform would have rejected:

```python
import csv
import io

assert list(csv.reader(io.StringIO('"unterminated'))) == [["unterminated"]]

for document in ('"unterminated', 'a,b\n1,2"3', "\n"):
    try:
        STDLIB["csvdecode"](string.validate(document))
        raise AssertionError(f"should have refused {document!r}")
    except Exception as exc:
        assert "csvdecode" in str(exc)
```

## Time

`timeadd` shifts by whole nanoseconds and rounds nothing, even though a
`datetime` resolves only to microseconds. The instant is carried as a
whole-second `datetime` plus an integer nanosecond remainder, so both a
sub-microsecond *duration* and a sub-microsecond *timestamp* land on the side of
the second boundary Terraform puts them on:

```python
shifted = STDLIB["timeadd"](
    string.validate("0002-01-01T00:00:00Z"), string.validate("-1ns")
)
assert shifted.value == "0001-12-31T23:59:59Z"

# The nanosecond in the timestamp cancels the one in the duration exactly.
cancelled = STDLIB["timeadd"](
    string.validate("0002-01-01T00:00:00.000000001Z"), string.validate("-1ns")
)
assert cancelled.value == "0002-01-01T00:00:00Z"
```

One limit of the `datetime` representation is still a recorded divergence: the
calendar stops at year 9999 where Go's `time.Time` runs far past it.

## Nulls are not unknowns

The one that catches the most callers, and it predates everything above. A null
argument is refused by most stdlib parameters rather than propagating:

```python
from pyvider.cty.exceptions import CtyFunctionError

try:
    STDLIB["upper"](CtyString().validate(None))
    raise AssertionError("should have refused")
except Exception as exc:
    assert "null" in str(exc)

# An unknown propagates instead, and keeps the return type.
from pyvider.cty import CtyValue

answer = STDLIB["upper"](CtyValue.unknown(CtyString()))
assert answer.is_unknown
assert str(answer.type) == "string"
```

An unknown is a value nobody knows yet; a null is a value that is definitely
absent. Computing with the second invents a fact.

## How this page stays true

Every assertion above runs under `scripts/check_docs.py`, which executes every
Python block in the documentation on each build. The underlying claims are
verified a second way, against a live go-cty binary, by `make compat` — 3,682
differential tests including a generated argument sweep over all 83 stdlib
functions. If you find a difference this page does not list,
[`docs/reference/go-cty-comparison.md`](../../reference/go-cty-comparison.md)
carries the complete parity status, including the divergences that are
deliberate.
