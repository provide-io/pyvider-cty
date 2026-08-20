# Handoff — 2026-08-19 (stdlib fuzz)

Branch `main`. Working tree clean at the point this was written.

## What was asked

**"do stdlib fuzzing"** — the last surface no generated input had ever reached.
Named at the end of the previous session and picked up verbatim: the 83 stdlib
functions were compared only against 444 hand-written argument rows, an average
of five each, with 31 functions holding two or fewer and `log` holding one.

## What was built

Three modules, `tests/compatibility/`:

| file | what it is |
|---|---|
| `_fuzz_values.py` | the value pool, and the region it stays inside |
| `_fuzz_plans.py` | one generated argument list per function |
| `test_stdlib_fuzz.py` | the driver, plus two guards |

`SIGNATURES` is what makes it cheap. Every function declares its parameters,
its variadic one and its null/unknown/dynamic policy, so for a little over half
the surface the argument list is **derived from the signature**. The rest
declare a `dynamic` parameter — which in go-cty means "this function decides for
itself" — and get a shaped plan: `flatten` wants a sequence of sequences,
`zipmap` wants two lists whose lengths matter, `index` wants a *key* and not an
element (go-cty's `index` is the indexing operation, not Terraform's search).
A plan fixes the shape and never the values.

Running at 120 examples per function is ~10,000 generated calls in two minutes.
The committed default is 20; `PYVIDER_COMPAT_EXAMPLES=120 make compat` widens
every function at once.

## What it found: sixteen divergences, all fixed

CHANGELOG breaking changes 46–61. Grouped by what was actually wrong:

* **Arithmetic ran at the `Decimal` default of 28 significant digits.**
  `add(2**100, 1)` answered `1267650600228229401496703205000` — four digits
  invented and one dropped, in a value that goes to Terraform state. Seven
  functions; they compute at go-cty's own 155 now (`floor(512·log₁₀2)+1`, the
  widest a 512-bit `big.Float` spells), which agrees where go-cty is exact and
  rounds where it rounds. `modulo` additionally raised `DivisionImpossible` out
  of the implementation — a *panic*-class error — where go-cty answers.
* **Set ordering was structural where go-cty's is byte-wise.** `setRules.Less`
  compares a string, number or bool by value and **every other element type** by
  the bytes of `makeSetHashBytes`. So `setproduct` writes the tuple `[12]`
  before `[1]`, and a longer string can precede one it starts with. New module
  `pyvider.cty.values.set_order` implements the byte comparison — Go's `%q` and
  `big.Float.String()` included — and all six ordering sites use it.
  **Membership follows from the same place**: cty finds an element by hash
  bucket, so `toset([0, -0])` is two elements there and was one here.
* **Six rules for the sign of a zero**, none of which a `Decimal` gives by
  default: `negate(0)` is `-0`; `int(-0.5)`, `ceil(-0.0)`, `floor(0.5)` and a
  zero remainder are `+0`; a zero *dividend* in `modulo` takes its sign from the
  divisor.
* **Two regex classes.** RE2's `\d`, `\s`, `\w`, `\b` are ASCII and Python's are
  Unicode; and Go's `FindAll` drops an empty match sitting where the previous
  match ended, which `finditer` keeps. Both contradicted the parity document's
  claim that "every pattern valid in both engines behaves identically".
* **Four output surfaces**: `%v`/`%g` rounded at 28 digits, `%q` and `%#v` did
  not apply Go's HTML escaping, `csvdecode` had no strict mode, `jsonencode`
  refused a `Bytes` capsule go-cty base64s.
* **Three smaller**: `timeadd` truncated a duration's magnitude before its sign,
  `range(0,0,0)` was refused where go-cty answers `[]`, `tonumber(" 1")` was
  accepted because `Decimal` strips whitespace, and an object attribute named
  `""` could not be validated at all.

## Two upstream quirks, found and handled differently

* **`range`'s zero-step guard never fires.** It compares two structs holding
  different `*big.Float` pointers. **Matched**, because the loop's own answer is
  the observable one.
* **`cty.Value.Equals` on maps is nondeterministic.** It walks Go's randomised
  map iteration order and returns early on either a missing key (false) or an
  undecided element (unknown), whichever it reaches first — eight calls to the
  harness gave five and three. **Not matched**; nothing can match a coin flip.
  The generator stays out of that shape and says so.

## Three comparison-channel faults, in the test suite itself

The fuzz found these before it found any library bug, and all three were
*inventing* divergences:

* go's answer was read from JSON and ours from msgpack, so `abs(2**63)` reported
  as an integer against text while the two write byte-identical msgpack. The
  fuzz compares values now, and says why in its docstring; the byte question is
  `test_differential_properties`'s, which asks it of both sides.
* `json.loads` without `parse_int=Decimal` turned JSON `-0` into the int `0`,
  hiding every signed-zero divergence. Fixing that is what made four of them
  visible.
* `splitlines()` splits on U+0085, which Go does not escape, so a result string
  containing one arrived as unterminated JSON and read as a broken harness.

## The state it is in

| gate | result |
|---|---|
| `ruff check` / `ruff format --check` | clean, 351 files |
| `mypy src/` | clean, 82 files |
| `bandit -ll -r src/` | exit 0 |
| `pytest tests/` | **3018 passed** |
| `make compat` | **3682 passed, 26 xfailed, 0 XPASS** |
| `check_docs.py` | 51 documents, 281 blocks, 249 ok / 32 skip |
| `render_diagrams.py --check` | 8 up to date |
| `examples/run_all_examples.py` | 11/11 |

The 26 xfails are the 13 accepted divergences across two populations, unchanged
— none of the fixes here disturbed the ledger, and none was added to hide
anything.

## Documents updated

`CHANGELOG.md` (45 → 61 breaking changes), `docs/reference/release-notes.md`,
`docs/reference/go-cty-comparison.md` (three claims the fuzz falsified: the set
hashing rule, "every pattern valid in both engines behaves identically", and the
28-digit computation limit), `.provide/GO-CTY-PARITY.md` (a section of its own),
and both architecture diagrams that describe set ordering
(`05-wire-codecs.puml`) and the differential suite (`08-differential-testing.puml`,
which had `373 rows` and no generated population).

## For the next session

**The examples are thin, and always were.** Eleven files, 517 lines, covering
types, marks, paths, serialization and Terraform interop. `advanced/functions.py`
demonstrated exactly one stdlib function out of 83 and carried a stale note
saying arithmetic was unsupported; it now shows the registry and predicts a
return type, but the gap is real: examples are a getting-started surface here,
not a coverage surface. Expanding them is worth doing on its own terms and was
not in this session's ask.

**Where the fuzz could go next**, in order of what it would likely find:

1. **The `cty` package surfaces**, the way the stdlib just was. `convert`,
   `unify` and `conformance` have generated coverage; `walk`, `transform`,
   `mark_paths` and `unknown_as_null` are still table-only.
2. **Two arguments at once.** Every plan draws its arguments independently
   except where coherence was needed. Drawing a *pair* of related values —
   the same collection at two types, a value and its own refinement — reaches
   shapes neither side of a single draw can.
3. **The residual in `timeadd`**: a timestamp with sub-microsecond digits is
   still truncated, because the instant is a `datetime`. Closing it means an
   integer nanosecond count, which is the same change the recorded calendar-range
   divergence would need.

The release is still cross-repo and still Tim's: `pyvider` releases at or before
`pyvider-cty`, and CI checks out `tofusoup`'s default branch.
