# Changelog

All notable changes to this project are documented here. The format loosely
follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased] - 0.5.0

This release brings pyvider.cty to feature parity with go-cty v1.19.0. Every
behavioral change below was verified against a live go-cty oracle (the
`soup-go` differential harness), not against go-cty's documentation, so a
handful of long-standing pyvider.cty behaviors that never matched go-cty are
corrected here alongside genuinely new go-cty v1.19.0 behavior. See
[docs/how-to/migrate-from-go-cty.md](docs/how-to/migrate-from-go-cty.md) for
the full API mapping.

### Security & Performance

This release includes the results of a comprehensive adversarial parity review targeting algorithmic DoS and memory exhaustion vectors, bringing the validation pipeline to enterprise scale:
- **Algorithmic DoS in `setproduct`**: Enforced a hard cap of 1,000,000 elements on the cartesian product size, preventing a single small payload from causing instant memory exhaustion. (Pyvider is now strictly safer than `go-cty` here.) This is a deliberate divergence and is listed as breaking change 45; it applies only where the product would be materialized, so an unknown-length argument still answers an unknown.
- **JSON Parser Memory Exhaustion**: Eliminated 40% of the memory footprint and 66% of the parsing time during `cty_from_json` deserialization by replacing double-validation loops with direct, lazy-evaluated CtyValue constructors.
- **Set Union Hotspot**: Fixed an $O(N^2)$ execution stall when accumulating marks in large collections (such as `CtySet` deduplication loops) by swapping immutable frozenset unions for mutable `set.update()` accumulations.
- **`RecursionError` from anything asked of a deeply nested type or value.**
  `CtyTuple.equal` and `CtyObject.equal` recursed at two Python frames per level
  of nesting, and `equal` is on the *construction* path -- `validate` compares
  an element's type against the one its container declares -- so a 400-deep
  tuple could not be built at all. It raised on Python 3.11 and passed on 3.13,
  on nothing but where each interpreter puts its frames: 800 frames against a
  limit of 1000. `requires-python` is 3.11, and CI runs it.

  Measuring rather than reading found five more surfaces with the same shape,
  none of them on the construction path and so none of them failing anything
  visibly: a type's `__eq__` (attrs-generated per subclass, so it never routed
  through `equal`), `__hash__`, `usable_as`, `__str__`, and both `__eq__` and
  `__hash__` on `CtyValue`. All of them walk now, off a single decomposition --
  `_structure`, which each container answers once and which equality, hashing
  and rendering all read.

  Two workarounds for this defect are gone with it. The collection types
  flattened the linear chain of same-kind containers and recorded that branching
  shapes were "bounded by the schema's own breadth" -- a single-element tuple
  nested 400 deep is not. And `CtyObject.__hash__` hashed a nested object by its
  attribute *names* only, "to avoid recursion", so two objects differing solely
  in a nested attribute's type shared a bucket; the hash now descends as far as
  equality does.

  One real bug surfaced on the way: `CtyValue.__hash__` did not treat a tuple as
  a container, so a tuple's payload was hashed by Python's own tuple hash rather
  than by its elements' hashes. Besides recursing, that skipped the
  element-hashing that routes a capsule payload through its `hash_fn` -- so two
  tuples holding equal capsule payloads hashed apart, exactly as two lists used
  to before that was fixed for lists.

  `__repr__` is deliberately left recursive: it is a debugger surface and
  reaches no error path, since a refusal spells its type with `str()`.

- **Mark laundering through a capsule conversion**: `convert()` into a `CtyCapsuleWithOps` declaring `convert_to_fn` dropped the source value's marks, because `convert_to_fn` hands back a raw Python object and `@preserves_marks` has nothing to copy from. A sensitive value coerced into a provider's own capsule type came out unmarked, so the codec's refusal to serialize a marked value never fired and the payload reached the msgpack wire in the clear. `convert_to_fn` is new in this release, so no published version is affected. Every return in `convert()` now re-applies the source's marks, and a parametrized sweep over the whole branch space holds the invariant.
- **ReDoS (Regex Denial of Service)**: Explicitly documented the architectural constraint that `google-re2` cannot be cross-compiled to WebAssembly for Pyodide, meaning Pyvider's `regex` family falls back to Python's backtracking NFA. Do not evaluate untrusted patterns from remote APIs.

### Breaking Changes

This release contains **61 breaking changes**. Read this list before
upgrading.

#### Marks and value mutability

1. Set elements no longer carry marks individually; a marked element's marks
   hoist onto the set itself (go-cty's `SetVal` behavior). Read sensitivity
   off the set, not off `set.value[i]`.
2. Serializing a marked value now raises `CtyMarksSerializationError` instead
   of silently dropping the marks. Unmark a value explicitly before encoding
   it if you don't need the marks preserved.
3. Map and object payloads are immutable. `value.value[k] = x` now raises
   `TypeError`; rebuild the value instead of mutating it in place.
4. Refinements now survive `validate()` and a msgpack round-trip, where they
   previously flattened to a bare unknown. The wire bytes for a refined
   unknown change accordingly (ext 12, not the bare-unknown `d4 00 00`).

#### Standard library: signatures and return types

5. `regex` and `regexall` take `(pattern, string)`, not `(string, pattern)`.
   Both arguments are strings, so an un-updated call keeps type-checking.
   Most of them raise once they run — the subject string is rarely a valid
   regex that also matches the pattern text — but some return a wrong answer
   instead (measured: 5 of 7 realistic call shapes raise, 2 return silently).
   Audit every call site rather than relying on an exception to find them all.
6. `regex` returns capture groups (a tuple, or an object for named groups)
   rather than the whole match, and raises on a non-match rather than
   returning `""`. `regexall`'s elements have the same shape.
7. `indent` takes a number of spaces, not a prefix string, and no longer
   indents the first line.
8. `flatten` returns a tuple, recurses through nested sequences, keeps null
   elements, and passes non-sequence elements through instead of raising.
   `chunklist` preserves the element type and accepts a size of 0.
9. `length()` refuses a plain string outright, matching go-cty (which leaves
   strings to `strlen`) rather than counting code points. Use
   `len(value.value)` for a string's length; `strlen` proper is not yet
   available. `length()` now accepts a `dynamic`-wrapped collection, which it
   previously refused.
10. `regexreplace` expands the replacement by Go's rules, not Python's — Go
   reads `$1`/`${name}` and passes `\1` through as literal text, which is the
   exact reverse of Python's `re.sub`. Rewrite every replacement template
   referring to a capture group.
11. `values()` returns a map's values in key order, not insertion order, and
   both `keys()` and `values()` return a tuple (not a list) for an object.
   If you were pairing `keys(m)` with `values(m)` to rebuild a map, both
   halves changed shape.
12. `formatdate` uses go-cty's own format dialect (`YYYY`, `MM`, `DD`, `EEEE`,
   `hh`, `AA`, `ZZZZZ`, with `'...'` literal quoting), not Go's
   `2006-01-02` reference layout or Python `strftime`. Every call site's
   format string needs rewriting.

   **This one is caught for you.** Under go-cty's rules a Go layout is
   literal text, so `formatdate("2006-01-02", ts)` returns the string
   `"2006-01-02"` — not an error, not a date, and shaped exactly like the
   answer you wanted. It was the only change in this release whose wrong
   answer looks right, so a Go layout is now **refused** with a message
   naming the rewrite. This is the one place this library deliberately
   declines something go-cty answers. A bare year still renders as the
   literal it is, and `'2006-01-02'` renders as literal text on both sides
   if that is what you meant.
13. `formatdate` and `timeadd` parse RFC3339 strictly, where they previously
   used `datetime.fromisoformat` and accepted looser input (a bare date, a
   space instead of `T`, a lowercase `t`/`z`, a colonless offset). `timeadd`
   also renders a zero offset as `Z`, not `+00:00`.
14. `jsondecode`, `csvdecode`, and `merge` return concrete types.
   `jsondecode` returns a **tuple** for a JSON array, not a `dynamic`
   wrapper. `csvdecode` returns `list(object(...))` with string-typed
   columns, and now refuses a missing header line, a duplicate column name,
   or a ragged row. `merge` keeps the shared argument type (merging maps
   yields a map, not an object) and returns an empty object for no
   arguments.
15. Strings are measured in grapheme clusters, not code points, in `strrev`,
   `substr`, and `format`'s width/precision. `strrev` no longer produces a
   different emoji by reversing inside a ZWJ sequence, and `substr` no
   longer returns a fragment of a cluster.
16. `substr` accepts what go-cty accepts: a negative offset counts back from
   the end, and any negative length means "the rest" (both were previously
   refused). `format`'s `%q` stops escaping non-ASCII characters.
17. `cty_from_json` reads what go-cty reads — stricter in one direction and
   looser in the other. An attribute the type doesn't declare is now an
   **error** (previously silently dropped); an attribute the document omits
   is now **null** (previously refused). A JSON number for a string-typed
   position is accepted and yields its literal digits (`1.50` →
   `"1.50"`), as are a bool for a string and a string for a number or bool.
18. `cty_to_json` escapes `<`, `>`, and `&`, as Go's encoder does, and
   converts a non-conformant value before serializing. This changes the
   *bytes* of any document containing one of those characters.
19. `zipmap` refuses mismatched key/value lengths instead of silently
   truncating, and returns an **object** (not `map(dynamic)`) for tuple
   values. Keys are declared `list(string)`, so container keys are now
   refused at type-check.
20. `slice` of a tuple returns a tuple, and indexes are range-checked instead
   of silently clamped by Python slicing.
21. `lookup` converts its default argument to the map's element type and
   refuses one that won't convert — `lookup(map(string), k, 5)` now answers
   `"5"`, not `5`.
22. `hasindex`/`index` accept list, map, and tuple only (sets and objects
   were previously accepted); `index` predicts its element type, and a
   tuple index is range-checked at type-check time.

#### The function framework

23. Argument errors now come from the shared function framework, in go-cty's
   wording: a wrong type is `"number required, but received string"`
   (previously per-function prose), and a null argument is
   `"<func>: argument N must not be null"`. Both are `CtyArgumentError`, a
   `CtyFunctionError` subclass carrying a zero-based `index` — existing
   `except CtyFunctionError` handlers keep working unmodified. Roughly 35
   functions that used to return *unknown* for a null argument now raise,
   matching what go-cty's declared parameters required all along.
24. Unknown answers from stdlib functions are now typed and refined —
   `upper(unknown)` is an unknown *string* refined not-null, not a bare
   unknown `dynamic`. The wire bytes change accordingly (ext 12, not
   `d4 00 00`). `length(unknown collection)` now answers a bounded range
   (`[0, 2^63-1]`, or tighter from the input's own bounds) instead of a bare
   unknown.
25. `max`/`min` are numbers-only (`max("z", "a")` now raises) and no longer
   narrow their answer from a refined argument's bounds — a deliberate
   precision loss taken for byte parity with go-cty, whose parameters never
   admit the unknown value to the implementation.
26. The four ordering comparisons (`lessthan`, `lessthanorequalto`,
   `greaterthan`, `greaterthanorequalto`) refuse strings and nulls; they
   previously type-checked and answered. Their bound-aware answers on
   refined unknowns are unchanged.
27. `coalesce` stops at the first unknown (previously skipped past it,
   risking an answer a later `apply` could contradict), unifies its return
   type instead of returning the winning argument unconverted
   (`coalesce(1, "b")` is now the string `"1"`), and refuses an all-null
   argument list instead of returning null.
28. Numeric edge semantics now match go-cty: `divide(x, 0)` is signed
   infinity (`0/0` and `Inf/Inf` still error); `modulo(x, 0)` is `x`;
   `modulo(Inf, y)` is `Inf`; `modulo` computes exactly rather than via
   `float64` `fmod`; `multiply(0, unknown)` is unknown, not known `0`;
   `log`'s edge values return infinities rather than erroring; `pow(0, 0)`
   is `1`; `signum` refuses a fraction; `parseint` takes bases 2-62, uses
   Go's `big.Int.SetString` grammar (no whitespace, `_`, or `0x`), and
   *errors* on an unparseable string rather than returning null; `int`,
   `ceil`, and `floor` handle infinities instead of raising
   `OverflowError`.
29. String functions use Go/Unicode semantics, not Python's: `upper`/`lower`
   use simple per-rune case mapping (`upper("straße")` is `"STRAßE"`, not
   `"STRASSE"`; `lower("ΣΣ")` is `"σσ"`, not `"σς"` — no final-sigma rule);
   `title` capitalizes one letter per word without lowercasing the rest;
   `chomp` removes *all* trailing line breaks; `trimsuffix` with an empty
   suffix returns the string unchanged (it used to delete the whole
   string); `trimspace` trims Unicode `White_Space` only; `substr` refuses
   a fractional index it used to truncate; `split("", s)` splits per
   character instead of raising a bare `ValueError`; `join` is variadic,
   refuses a tuple, and errors on a null element instead of rendering it as
   the literal text `"None"`.
30. `setsubtract` takes exactly two arguments (it was variadic and subtracted
   twice); `sethaselement` answers a definite `false` for a mismatched
   element type instead of erroring; `bytesslice` refuses fractional
   indexes.
31. `distinct` de-duplicates container elements it used to refuse as "not
   hashable" — go-cty compares with three-valued `Equal` and has no such
   refusal.
32. `keys()` of an unknown object answers the attribute names (they're part
   of the type); `reverselist` accepts a set; `compact` drops null elements
   explicitly rather than by truthiness; `formatlist` defers per-row rather
   than per-list (and defers wholly for a set argument holding an unknown
   element, since the set's *length* is what's unknown); `jsonencode` no
   longer promises a `"` prefix for a possibly-null unknown string, and
   `format` promises the template's literal prefix instead; `jsondecode`
   predicts its type from a refined input's known prefix and refuses an
   impossible opening character; `csvdecode` reports header errors at
   type-check. `min()`/`max()` with no arguments, and `formatdate`'s and
   `timeadd`'s argument-error wording, changed with the framework.

#### Container and type semantics

33. A null is now accepted inside a `CtyList` and for any object attribute.
   Both restrictions were invented rules with no go-cty counterpart, and
   both refused on *read* — state that go-cty had already written could not
   be decoded. **`CtyObject.validate` no longer checks required-ness at
   all**, because it never had the information to: a `CtyObject` records
   optionality, which is a wire-format concern, not caller intent. If your
   code relied on cty to enforce "this attribute must be supplied", enforce
   that yourself now (e.g. at the schema layer).
34. `value_range().includes()` no longer answers `True`. It answers `False`
   or "cannot say", matching go-cty: a known value's range is synthetic and
   never concludes membership from bounds alone. The previously-undecided
   answer is now refined not-null, and `value_range()` itself raises on a
   marked value where it used to answer.
35. A list or a set no longer converts to a tuple — go-cty has no such
   conversion, and `can_convert_unsafe` already denied it, so `convert` was
   contradicting its own predicate. Convert to a list, or build the tuple
   explicitly.
36. A conversion result no longer carries a type constraint beyond what the
   source provides: converting to an object type with optional attributes
   produces a value whose type has none, and converting to `list(any)`
   produces a list of the *source's* element type rather than
   `list(dynamic)`. (Widening in the same change, and not breaking: a map
   now converts to an object, which was previously refused.)
37. A traversal now visits a map's keys and an object's attributes in sorted
   order. `walk`, `deep_values`, and `transform` previously used insertion
   order for a map and declaration order for an object — both properties of
   how the value was built, not of the value itself.
38. The wire bytes for a bare unknown change: it now encodes as the fixext1
   `d4 00 00` rather than an empty ext payload, and a refined number bound
   encodes as a number rather than as the UTF-8 bytes of its digits. Both
   spellings decode to the same value either way, so nothing breaks
   functionally — but byte-identical-comparison code needs to expect the
   new bytes.
39. A comparison against null can now be decided by a refinement: an unknown
   refined as not-null, compared against a null, was previously undecided
   and now answers `false`. The undecided answer of `equals()` is likewise
   refined not-null, so asking "could this be null?" now gets "no" where it
   used to get "possibly".
40. **A container holding an unknown element is a *known* container.**
   `is_unknown()` on a partially-unknown list, map, set, or tuple flips from
   `True` to `False`; the question "is anything in here undecided" is now
   `is_wholly_known()`. This is a fix, not a narrowing: the container
   previously encoded to the wire as a bare unknown, destroying its known
   elements and known length. Everything downstream is more precise as a
   result — `length()` answers, `walk` descends, `unknown_as_null` nulls
   the element rather than the container, and `equals()` can decide from an
   element that already differs.
41. A set's payload is an ordered tuple in go-cty's canonical order, not a
   frozenset. Two unknown elements are no longer de-duplicated into one
   (they aren't equivalent), so a set's length can now be larger than
   before; `length()` on a set holding an unknown returns a refined
   unknown range rather than a count. Code doing set algebra directly on
   `value.value` must treat it as a sequence.
42. `sort` defers instead of raising: a list holding an unknown element now
   returns a same-length list of unknowns, where it previously raised
   `CtyFunctionError`. A *null* element still raises.
43. Container-typed values (list, map, set, object) now hash, closing a bare
   `TypeError` that used to escape ten public entry points —
   `equal()`, `setunion()`, `contains()`, `Value.equals`, `in`,
   `without_key`, `lookup`, `zipmap`, and `set[CtyPath]` — on the shape
   Terraform calls a nested block set, including across a msgpack
   round-trip. Containers hash by their canonical sort key, so **a set can
   now hold a list**; a capsule with no `hash_fn` hashes per-type, as
   go-cty's sets do. Set equality now matches go-cty: only *top-level*
   unknown elements defer, so two sets each holding a nested unknown but
   differing in a known part now answer `false`, not unknown.
44. Converting a **set whose length is unknown** into a list now yields an
   *unknown* list, refined `collection_length ∈ [1, store size]`, instead of
   a known list of exactly the store's elements. A set holding an unknown may
   coalesce — `{1, unknown}` can turn out to be one element — so a definite
   length was a claim the data did not support, and `length()` on the source
   and on the result openly contradicted each other. This is deliberately not
   go-cty's answer either: go-cty returns a wholly-unknown list typed from the
   *source's* element type, discarding the target, which yields a value that
   does not conform to the schema the caller asked for. If you relied on the
   converted list being known, guard on `is_unknown` or convert the elements
   yourself.
45. `setproduct` **refuses a product over 1,000,000 elements**, where go-cty
   allocates it. Two 1024-element arguments are 1,048,576 tuples, so a payload
   that fits in an ordinary plan request is a remote memory-exhaustion vector.
   This is the second of the two places this package deliberately declines
   something go-cty answers, and unlike the `formatdate` refusal it raises
   rather than returning anything, so no call site can mistake it for a result.
   The cap applies only to a product that would actually be materialized: an
   argument of unknown length still answers an unknown, which is the shape
   Terraform sends at plan time. See `.provide/GO-CTY-PARITY.md`.

#### Found by generated arguments (2026-08-19)

The 83 stdlib functions had only ever been compared against 444 hand-written
argument rows -- an average of five each, with 31 functions holding two or
fewer. `tests/compatibility/test_stdlib_fuzz.py` generates arguments from each
function's declared signature and compares the answers against the live oracle;
these fifteen are what it found. Every one is a behavior change.

46. **Arithmetic computes at go-cty's width.** `add`, `subtract`, `multiply`,
   `divide`, `modulo`, `abs` and `negate` used the ambient `Decimal` context of
   28 significant digits, so `add(2**100, 1)` answered
   `1267650600228229401496703205000` -- four digits invented and one dropped.
   They compute at 155 digits now, which is what a 512-bit `big.Float` spells.
47. **`modulo` answers where it raised.** A quotient too wide for the context
   raised `DivisionImpossible` out of the implementation, which the framework
   reports as `CtyFunctionPanicError`; go-cty answers.
48. **Set element order follows go-cty's hash bytes.** A set whose elements are
   not primitives is ordered by `makeSetHashBytes`, not by comparing the values:
   `setproduct` writes the tuple `[12]` before `[1]`, and a longer string before
   a shorter one it starts with when the next character is below `"`. Element
   order reaches the wire, so this changes bytes for any `set(list)`,
   `set(tuple)`, `set(map)`, `set(object)` or `set(set)`.
49. **`toset([0, -0])` has two elements.** Set membership is by hash bucket in
   cty, and a negative zero hashes differently from a positive one. The same
   rule makes `sethaselement(toset([0]), -0)` false, as it is in go-cty.
50. **`length` and `flatten` see unknowns at any depth.** A set's length is
   undecided while it holds an unknown *anywhere*, not only as a direct element;
   `flatten` now answers an unknown of dynamic type when a set it would flatten
   has no known length, rather than a tuple whose length go-cty does not claim.
51. **`regexall` and `regexreplace` drop an empty match** that sits where the
   previous match ended, as Go's `FindAll` does. `regexall("a*a*", "a")` was
   `["a", ""]` and is `["a"]`; `regexreplace(" ", " *", "Z")` was `"ZZ"`.
52. **`\d`, `\s`, `\w` and `\b` are ASCII**, as they are in RE2. Patterns
   compile with `re.ASCII` unless the pattern asks for case-insensitivity,
   where RE2 folds over all of Unicode and the flag would narrow that too.
53. **`csvdecode` refuses what Go's reader refuses**: an unterminated quoted
   field, a quoted field followed by other text, a bare quote in a plain field,
   and a document with no header row at all (`"\n"` was an empty table).
54. **`timeadd` shifts by a negative nanosecond correctly.** The duration's
   magnitude was truncated before its sign was applied, so
   `timeadd("0002-01-01T00:00:00Z", "-1ns")` came back unchanged where go-cty
   answers `0001-12-31T23:59:59Z`.
55. **`jsonencode` encodes a `Bytes` capsule** as base64, which is what
   go-cty's JSON codec does with the encapsulated `[]byte`; it used to raise.
56. **`range(0, 0, 0)` is an empty list.** go-cty's zero-step guard never fires
   -- it compares two structs holding different `*big.Float` pointers -- so the
   loop decides: an empty range returns `[]` and a non-empty one reaches the
   1024-value cap. This package refused both.
57. **`%v` and `%g` keep every digit.** Both rounded a number at 28 significant
   digits, so `format("%v", 10**28 + 1)` was `1e+28` against go-cty's
   `1.0000000000000000000000000001e+28`.
58. **`%q` escapes `<`, `>` and `&`.** go-cty's `%q` is `ctyjson.Marshal`, and
   Go's `encoding/json` escapes those by default.
59. **The sign of a zero follows go-cty in five functions.** `negate(0)` is
   `-0`; `int(-0.5)`, `ceil(-0.0)` and `floor(0.5)` are `+0`; `modulo`'s zero
   remainder is `+0`, and a zero *dividend* takes a sign from the divisor.
60. **`tonumber` refuses surrounding whitespace.** `Decimal(" 1")` is 1 and
   Go's `big.ParseFloat` grammar has no room for a space, so `tonumber(" 1")`
   is an error, as it is in go-cty.
61. **An object attribute may be named `""`.** `CtyObject.validate` builds a
   path step per attribute and the step refused an empty name, so no value of
   such a type could be validated -- `merge({"" = "x"}, {})` raised where
   go-cty answers.

### Added

- Ported go-cty's `cty/function` framework: all 83 stdlib functions now
  declare parameter specs, driving argument validation, null handling, and
  unknown/refinement propagation from one shared implementation instead of
  per-function ad hoc code.
- Refinement API: `refine()`, `RefinementBuilder`, `safe_known_prefix()`,
  and `value_range()`, mirroring go-cty's `Refine`/`RefinementBuilder`.
- `walk()`, `deep_values()`, and `transform()` for structural traversal of
  cty values, mirroring go-cty's `cty.Walk`/`cty.Transform`.
- Grapheme-cluster string measurement: `grapheme_cluster_count()` and
  `grapheme_clusters()`.
- Deep-mark helpers, all four exported from top-level `pyvider.cty`:
  `unmark_deep()`, `collect_marks_deep()`, `unmark_deep_with_paths()`, and
  `mark_with_paths()`. `unmark_deep()` is the supported way to serialize a
  value that carries marks, since encoding one directly now raises.
- `unknown_as_null()` (go-cty's `UnknownAsNull`) and three-valued `equals()`
  semantics throughout the comparison surface.
- `Type.conformance_errors()` (go-cty's `TestConformance`) and a `cty/json`
  value codec.
- A completed `CapsuleOps` implementation.
- A live differential compatibility suite (`tests/compatibility/`, run via
  `make compat` or `pytest --run-compat`) that compares wire bytes,
  refinements, and every stdlib function's answers against a real go-cty
  binary (the `soup-go` harness, built from a sibling `tofusoup` checkout),
  replacing a checked-in-fixture suite that had been silently broken.
- Performance-report tooling (`make perf-report`,
  `scripts/perf/perf_report.py`) for comparing hot-path performance against
  a baseline ref.
- The differential suite runs in CI per-commit, on a deliberately pinned Go
  toolchain: go-cty selects `go-textseg` v15 below Go 1.27 and v17 at or
  above it, and four Unicode GB9c cases are strict xfails against the v15
  answer, so the pin decides whether the suite passes.
- Architecture documentation (`docs/architecture/`): eight PlantUML diagrams
  covering the type system, value model, validation and conversion, the
  function-call sequence, the wire codecs, the module dependency map, the
  Terraform integration boundary, and the differential test harness.
  `make diagrams` re-renders them; `make diagrams-check` fails if a
  committed SVG has drifted from its source.

### Fixed

- `timeadd` is exact to the nanosecond in both arguments. A `datetime` resolves
  to microseconds and Go's `time.Time` to nanoseconds, and the two met twice on
  the way through -- once parsing the timestamp's fraction, once turning the
  duration into a `timedelta` -- so the last three digits of a nine-digit
  fraction were dropped before the arithmetic began. The instant is now carried
  as a whole-second `datetime` plus an integer nanosecond remainder and the
  shift as an integer nanosecond count, so `timeadd("...00.000000001Z", "-1ns")`
  answers the same second go-cty does. Only the calendar range is still a
  `datetime` limitation, and it remains a recorded divergence.
- Marks are no longer silently dropped: they now propagate through stdlib
  function arguments, are collected from nested sets and raw containers, and
  survive validation.
- Bare unknown markers are handled consistently across list, set, map,
  object, and tuple validation instead of raising.
- Object types send their optional-attribute names on the wire.
- `equal()`/`not_equal()` now decide comparisons that a value's own
  refinements already answered, instead of returning unknown.
- The recursion depth limit is derived rather than advertising a value it
  couldn't actually deliver.
- `contains()` treats a partially-unknown collection as undecided instead of
  giving a definite answer.
- A refinement that rules nothing out is no longer written to the wire. An
  empty string prefix and a collection length lower bound of 0 are true of
  every value of their type; go-cty records neither and writes a bare unknown,
  where this package wrote a refinement map carrying the vacuous entry. Only
  reachable through the refinement API -- no stdlib function emits one.
- An empty number range is refused instead of being written. `3 < x <= 3` is
  unsatisfiable and was accepted; `5 <= x <= 3` was already refused, so the
  check simply did not cover equal bounds where one of them excludes the value.
  `3 <= x <= 3` is still accepted and still collapses to a known `3`.
- A NaN is no longer serialized. go-cty's number is a `big.Float`, which has no
  NaN at all, so the msgpack string `"NaN"` this package wrote came back from
  go-cty as `number is required` — a value it could put on the wire that
  Terraform's own library could not read. Both codecs refuse it now, and the
  JSON codec's message says `NaN` rather than `infinity`. Infinity is
  unaffected: go-cty holds `+Inf`/`-Inf` and both round-trip. Constructing a NaN
  is still allowed, since `format` spells one the way Go's `fmt` does and no
  stdlib function produces one.
- A value in a `dynamic` position carries its concrete type across the wire,
  whether it is known, unknown, or null. go-cty writes `[type, value]` for every
  value at `cty.DynamicPseudoType`. Two separate faults dropped it here: the
  codec checked knownness before the dynamic branch, so an unknown-of-string
  went out as a bare `d40000`; and `CtyValue` cleared the payload of any null,
  which at `dynamic` *is* the type, so a null-of-string went out as a bare `c0`.
  go-cty read both back as `dynamic` rather than `string`, and deferring as
  `string` and deferring as `dynamic` are different answers to a Terraform
  plan.
- Sets of composite elements serialize in go-cty's byte order. Where one
  element is a *prefix* of another -- `{["a"], ["a","c"]}`, or any set holding
  an empty element -- go-cty ranks running out of elements last and this
  package ranked it first, so the set re-encoded in a different order on every
  round trip. Both spellings decode to the same value, so only a byte
  comparison saw it, and Terraform compares serialized state. `set(object(...))`
  is Terraform's nested-block type, so any block set whose members carry
  different numbers of optional attributes was affected.
- Rendering a number to text no longer rounds it to `decimal`'s default
  28-digit context. `2**100` reached `terraform show -json` as
  `1267650600228229401496703205000` rather than
  `1267650600228229401496703205376`, through every text route --
  `convert(number, string)`, `tostring`, `format("%s", n)`, `jsonencode` and
  the `cty/json` codec. The msgpack codec always carried every digit, so the
  two codecs in this package disagreed about the same value. Numbers now match
  go-cty up to **154 significant digits**, which is what its 512-bit
  `big.Float` can spell; past that the two still differ, and that boundary is
  now a recorded divergence rather than an unexamined one. Distinct from the
  `divide` divergence, which is about a result *computed* at 28 digits rather
  than digits discarded on the way out.

### Performance

- `regexreplace` parses its replacement template once, not once per match.
- The deep-mark walk is memoized over immutable subtrees.
- Set equality now hash-buckets by canonical key: two equal 1000-element
  sets compare in ~13ms, down from ~1295ms.

## [0.4.0] - 2026-04-24

Reconstructed from the commit history on 2026-08-17; no changelog was kept at
the time. The GitHub release note for this tag lists a single CI-plumbing pull
request, which is not what the eighty-two commits behind it contain.

### Fixed

- Windows: `sys.__stdout__` and `sys.__stderr__` are reconfigured to UTF-8, so
  the structured logger's emoji and box-drawing characters no longer raise
  `UnicodeEncodeError` through colorama's cp1252 write path.
- The recursion context is reset after each top-level validation instead of
  leaking depth state into the next one.

### Performance

- Micro-optimizations in the conversion and type-inference hot paths.

### Internal

- Memray memory-stress infrastructure added, excluded from the default test
  run; Hypothesis deadlines tuned for resource-constrained containers.

## Earlier releases

No changelog was kept before 0.4.0, so what follows is not one: it is the
commit subjects between the release tags, grouped by their conventional-commit
prefix. It reports what the commits *say*. It does not describe behaviour, and
a subject that was inaccurate when it was written is reproduced here unchanged.

Produced once, mechanically, on 2026-08-17. Re-derive any section with
`git log <older-tag>..<newer-tag> --no-merges --format=%s`; the only entries
dropped are tooling commits (`[skip ci]` auto-commits, pre-commit auto-fix
passes, and pure formatting commits). History before 0.4.0 does not change, so
this section is frozen rather than regenerated.

Two things it cannot tell you, said plainly so its silence is not mistaken for
coverage. **The `0.0.x` series is absent**: eight versions were published to
PyPI between `0.0.111` and `0.0.1111` with no git tags at all, so there are no
version boundaries to derive spans from. **Fewer than a third of these
subjects are conventional commits**; the rest sit under *Uncategorised* in the
order they were committed, rather than being force-fitted into a category.

For what a release actually changed, the diff remains the record. 0.4.0's own
raw subjects are in `git log v0.3.31.post2..v0.4.0`; its curated notes are
above.

### v0.3.31.post2 - 2026-03-31

Re-tag of the preceding release; no commits of its own.

### v0.3.31.post1 - 2026-03-31

Re-tag of the preceding release; no commits of its own.

### v0.3.31 - 2026-03-31

9 commits, tooling noise excluded.

#### Fixes

- **recursion**: use path emptiness for top-level detection, preserve post-run metrics
- reset recursion context after each top-level validation
- tune Hypothesis deadlines for resource-constrained containers
- apply canonical spdx script fixes (E741, C901, SIM103)

#### Performance

- micro-optimizations in conversion and inference hot paths

#### Chores

- **release**: adopt standard release pipeline
- add pre-commit config (ruff, mypy, standard hooks)
- pin provide-foundation dependency and upgrade lockfile
- add memray infrastructure, .actrc to gitignore, version 0.3.21

### v0.3.21 - 2026-01-12

174 commits, tooling noise excluded.

#### Features

- **codebase**: standardize Python files with header/footer protocol
- Standardize file headers and footers
- Standardize file headers and footers
- **workflow**: Standardize CI/CD workflows to two-file pattern
- **release**: Standardize release workflow with flexible publishing options
- **version**: Add smart TestPyPI version generation logic
- **release**: Adopt uv for TestPyPI publishing workflow
- **cicd**: Complete CI/CD pipeline with PyPI release support
- Add parse-org-helpers action to CI workflow

#### Fixes

- **dependencies**: add quality extras to provide-testkit dev dependency
- **ci**: Remove relative path dependency on provide-foundation in workflow trigger
- **dependency**: resolve dev dependency group relative path issues
- **ci**: correct non-blocking quality checks in CI workflow
- **ci**: correct repository URLs and dependency configuration for CI compatibility
- **ci**: resolve UV build failures by correcting dependency sources

#### Refactoring

- Use centralized GitHub auth action from ci-tooling
- **cty**: migrate type definitions to Python 3.11+ generic syntax

#### Documentation

- update project documentation index
- update installation and index documentation
- update project documentation index
- update project documentation index
- update installation and migration guides with current instructions
- archive architectural and supplementary analysis documents
- Fix documentation errors and security issues
- Add comprehensive supplementary architectural analysis
- Add comprehensive architectural analysis and review
- update documentation for type system, validation, and migration guides
- restructure and consolidate documentation hierarchy
- update API documentation structure and content
- update API documentation structure and content

#### Tests

- **property_based**: skip resource-intensive tests in CI environments
- **codec**: expand roundtrip and robustness test coverage
- add tests for unknown fields handling in object module
- add test for unknown bug scenario
- add dynamic wire protocol codec tests
- add diagnostic tests for exception messages in boolean type handling
- **codec**: add robustness and coverage tests for dynamic deserialization and refined unknowns

#### Chores

- **cty**: remove unused type: ignore comment on msgpack import
- **ci**: update CI workflow to skip CI on auto-commit
- **mutation-testing**: update mutation testing workflow configuration
- update SPDX header scripts and validate coverage
- update SPDX header scripts for consistency and reliability
- **release**: update release workflow with auto-commit trigger
- **ci**: migrate to ci-tooling reusable workflow
- **ci**: update CI workflow configuration
- **release**: update release workflow with auto-commit trigger
- **ci**: update CI workflow configuration
- update wrknv.toml configuration file with auto-generated changes
- auto-commit README.md updates
- update coverage data from automated test run
- update entrypoint script and performance characterization utilities
- synchronize entrypoint and performance scripts across archive and main directories
- auto-commit README.md updates
- auto-commit README.md updates
- update README with automated maintenance changes
- update README with auto-generated content
- update README with project status and setup instructions
- update README with project status and setup instructions
- update CI automation scripts for pipeline validation and artifact collection
- update configuration file with auto-generated changes
- update project configuration via auto-commit
- update project configuration for automated commits
- update project configuration for automated commits
- **pyproject**: update project configuration for dependency management
- update pre-commit configuration and project dependencies
- update project configuration for automated commits
- standardize release workflow to download-from-CI pattern
- **release**: standardize release workflow configuration
- update project configuration for automated commits
- update pyproject.toml and uv.lock for CI sync
- update project configuration files with auto-generated changes
- **ci**: simplify and re-trigger CI workflow
- **ci**: update CI workflow configuration
- **ci**: update CI workflow configuration
- bump version to 0.3.0 for coordinated ecosystem release
- update project configuration for automated commits
- **mkdocs**: auto-commit configuration update
- update mutation testing configuration and example utilities
- auto-commit project maintenance and configuration updates
- **cty**: auto-commit structural object type updates
- update documentation tooling scripts and configuration
- update Makefile with auto-generated maintenance rules
- update project configuration files for CI skip marker consistency
- update documentation assets and configuration for site build
- update secrets configuration and dependencies
- **deps**: Replace individual dev dependencies with provide-testkit[all]
- update project configuration for automated commits
- update project configuration files for automated maintenance
- update gitignore and secrets configuration for auto-commit workflow
- update CI automation scripts and ignore rules for local development environment
- update project documentation structure and ignore rules
- update gitignore with auto-generated patterns for CI artifacts and temporary files
- **cty**: initialize version and module structure
- Conform Python files to header/footer protocol
- update project configuration and ignore rules for automated commits
- standardize Python file headers and footers across codebase
- update version file for auto-commit cycle
- update documentation and examples for marks and type reference
- auto-commit documentation and configuration updates
- automated maintenance and configuration updates across project files
- update project configuration and ignore rules for documentation site
- **mkdocs**: auto-commit configuration update
- update project configuration via automated commit pipeline
- update project configuration for automated commits
- update project documentation files with auto-generated content
- update test configuration and fixtures for consistency
- update project configuration and add memory pressure test scaffold
- update test configuration and fixtures for consistency
- update coverage script and property-based tests for exception and schema validation
- **mutation**: configure mutation testing infrastructure
- **cty**: auto-commit maintenance updates
- **pyproject**: update dependencies and configuration
- update project documentation and test infrastructure
- update version file for auto-commit cycle
- **cty**: update auto-committed source files
- **cty**: update codec module with auto-generated changes
- update project configuration for automated commits
- **cty**: update version file for auto-commit
- **cty**: update project structure and module organization
- **cty**: update conversion module structure and caching logic
- **release**: update release workflow and project metadata for automation
- **ci**: migrate workflows to ci-tooling and consolidate redundant files
- auto-commit configuration and dependency updates
- **cty**: auto-commit cache implementation updates
- update project configuration for automated commits
- **mkdocs**: auto-commit configuration update
- **ci**: update ci-new.yml to use ci-tooling@v0.0.0
- **ci**: update CI workflow configuration
- update example scripts and verification utilities
- update mkdocs configuration with backup file handling
- auto-commit maintenance updates
- **cty**: auto-commit maintenance updates
- **pyproject**: update project configuration metadata
- update auto-generated files and examples for compatibility and performance checks
- update project configuration and dependencies
- **cty**: update conversion and object modules with auto-committed changes
- update environment configuration files for consistency
- **go**: update Go module dependencies and build configuration
- **compatibility**: auto-commit maintenance updates
- auto-commit maintenance updates across cty module
- **version**: update version to 0.1.0
- update CI/CD infrastructure and project templates
- update CI and release workflows and related configuration files
- update environment and dependency configuration
- update environment and workspace configuration files
- update project configuration for automated commits
- update project configuration with auto-generated changes
- update project configuration for automated commits
- update environment and project configuration files
- update environment configuration files for consistency and clarity
- update environment configuration files with auto-generated content

#### Scaffolding

- **agents**: establish project documentation structure
- **examples**: initialize example modules and structure
- **cty**: initialize exception hierarchy for cty module
- **chunker**: establish initial module structure and entry points
- **cty**: establish core module structure and foundational components
- **cty**: establish core module structure and foundational components
- **docs**: introduce new documentation structure with chapter-based organization

#### Baselines

- **project**: establish latest pristine pyvider-cty baseline

#### Uncategorised (no conventional-commit prefix)

- qualify(extreme_scale): make tests deterministic to prevent flaky failures
- interface(release): add permissions for reusable release workflow
- qualify(codec): expand roundtrip and coverage test suites for codec module
- qualify(codec): expand codec test coverage and robustness suite
- qualify(property_based): add property-based tests for collections and exception coverage
- qualify(codec): add comprehensive codec test coverage and hardening
- qualify(adversarial): add property-based fuzzing tests for adversarial inputs
- qualify(codec): expand codec test coverage and robustness suite
- qualify(inference_cache): add safety tests for inference cache behavior under concurrent access
- qualify(diagnostics): add exception message tests for improved diagnostics coverage
- qualify(inference): add concurrency safety tests for inference conversion logic
- qualify(ci): Add complete CI migration test using shared tooling
- qualify(codec): expand roundtrip and robustness test coverage for serialization logic
- qualify(codec): expand roundtrip and robustness test coverage for serialization/deserialization
- qualify(codec): expand roundtrip and robustness test coverage for serialization logic

### v0.3.0 - 2025-08-02

Everything from the first commit up to this tag.

291 commits, tooling noise excluded.

#### Features

- **cty**: introduce dynamic type inference with caching and concurrency safety
- **cty**: introduce unified cty type system and value encoding
- Increase test coverage for collection functions
- Increase test coverage
- **cty**: introduce comprehensive codec and conversion subsystem
- **cty**: implement capsule type support with operations and validation
- **feature**: add more comparable features to improve feature alignment
- **cty**: implement convert and unify logic for type conversion
- Add release readiness evaluation and CI/CD pipeline
- Generate .pyi files
- Improve test coverage for pyvider.cty.types
- Improve test coverage for pyvider.cty.types
- **cty**: Improve test coverage and fix linting issues
- Improve test coverage and fix linting issues
- **cty**: Implement arithmetic functions for CtyNumber values
- **cty**: Add comprehensive documentation and examples for pyvider.cty
- Add comprehensive documentation and examples for pyvider.cty
- Add comprehensive documentation and examples for pyvider.cty
- Add comprehensive documentation and examples for pyvider.cty
- **cty**: Add comprehensive documentation and examples for pyvider.cty library
- **cty**: implement dynamic type system with runtime type inference
- **cty**: implement dynamic type codec support
- Improve test coverage for pyvider.cty
- **cty**: introduce core type system with value, path, and conversion support
- Add comprehensive Msgpack compatibility tests
- **cty**: introduce pytest and Hypothesis-based compatibility testing framework
- **telemetry**: introduce common telemetry infrastructure
- **cty**: introduce capsule type and serialization support
- **cty**: introduce create_object factory for CtyObject construction
- **cty**: implement CtyList with improved validation messages and nested type support

#### Fixes

- **cty**: correct CtyValue to CtyString conversion for numeric values
- **cty**: resolve mypy errors and failing tests
- **docs**: correct erroneous code examples in primitive, collection, dynamic, capsule, and path navigation guides
- **docs**: correct code examples in getting started guide
- **cty**: align Go and Python cty value comparisons
- **test**: resolve failing test and improve code readability
- **cty**: resolve type errors in core type and value implementations
- **cty**: resolve circular import and mypy/ruff issues
- **cty**: correct JSON serialization and path navigation errors
- **serialization**: resolve unmarshal fallback behavior in example-09
- **example**: correct data accessors in example-09-serialization.py
- **cty**: serialize full type string in JsonEncoder for accurate deserialization
- **cty**: correct CtyList.__getitem__ type hint to typing.Union[int, slice]
- **cty**: replace union syntax with typing.Union for compatibility
- **core**: resolve syntax and import errors blocking static analysis
- **cty**: resolve type annotation errors and forward reference issues
- **schema**: correct type encoding logic for schema type encoder
- **cty**: correct SyntaxWarnings in test match strings
- **cty**: correct CtyMap.get() to return typed null and enforce key type checks
- **cty**: resolve AttributeError and incorrect return values in CtyMap
- **cty**: correct MsgPack serialization and validation for CtyDynamic values
- **msgpack**: correct serialization and deserialization of wrapped CtyValues in CtyDynamic
- **cty**: resolve test suite failures and improve serialization compatibility
- **cty**: resolve 25 failing tests in msgpack conversion and test suite
- **cty**: resolve TypeError in operation_context usage
- **cty**: correct CtyMap key validation for CtyValue inputs
- **regex**: correct map coverage regex pattern
- **cty**: enforce strict string validation for malformed CtyValue instances
- **msgpack**: resolve test failures in MsgPack encoder
- **cty**: correct KeyError handling in CtyValue.__getitem__ and adjust test expectations
- **cty**: correct positional argument misuse in collection constructors within tests
- **cty**: resolve test failures by renaming CtyValue.set factory and improving get() error handling
- **path**: correct regex for number_key_path error assertion in tests
- **cty**: Allow CtyNumber to be used as CtyString in path keys
- **cty**: correct CtyDynamic validation logic and object test assertions
- **cty**: resolve cty.marks import, serialization, and type resolution issues
- **cty**: resolve ModuleNotFoundError and type attribute errors in cty module
- **cty**: enhance unmarshal_type for deeply nested map and list type strings
- **cty**: resolve nested type unmarshalling for complex type strings
- **cty**: resolve ModuleNotFoundError for CtyDynamic import and improve JSON encoding logic
- **cty**: resolve CtyDynamic JSON encoding and test failures
- **bool**: resolve NameError and add missing Decimal import
- **cty**: correct list validation to return CtyValue instead of self
- **cty**: enable nested parentheses in type format regex
- **cty**: correct null/unknown value handling in primitives and collections
- **cty**: correct type and value handling in collections and primitives
- **cty**: correct type assertions in object coverage tests
- **cty**: correct type assertions in object validation tests
- **msgpack**: remove async/await from synchronous serialization methods
- **cty**: handle non-value elements in container membership checks
- **cty**: correct syntax error in msgpack serializer pattern match

#### Refactoring

- **cty**: restructure type and value modules for consistency
- **cty**: restructure codebase to resolve failing tests and improve quality
- **cty**: standardize typing and prepare for preview release
- **cty**: restructure conversion module for clarity and maintainability
- **cty**: restructure type system and conversion modules
- **cty**: stabilize test suite and align serialization with go-cty
- **cty**: restructure encoding and type handling for consistency
- **cty**: restructure string type handling for consistency
- **cty**: resolve circular imports and correct type validation logic
- **cty**: modernize type hints and fix test instantiations
- **cty**: modernize type annotations using PEP 604 syntax
- **cty**: restructure conversion module hierarchy for clarity and maintainability
- **cty**: restructure conversion module internals for clarity and maintainability
- **cty**: replace manual class definition with @define decorator
- **cty**: restructure equality logic across primitive and collection types
- **cty**: reorganize exception module structure
- **marshal**: restructure marshaling logic for clarity and maintainability
- **marshal**: restructure marshaling logic for clarity and maintainability
- **cty**: rename internal attributes to underscore-prefixed variants
- **cty**: restructure base value types and map implementation
- **cty**: restructure object type implementation for clarity and maintainability
- **cty**: standardize attrs decorators and field naming conventions
- **cty**: remove frozen semantics from value classes
- **cty**: restructure list type implementation for clarity and consistency
- **cty**: restructure exception hierarchy and rename validation errors
- **cty**: restructure object type implementation for clarity and maintainability
- **cty**: restructure collections and path modules for clarity and correctness
- **path**: restructure path module into unified implementation
- **cty**: restructure operations and conversion modules into dedicated subsystems
- **cty**: restructure object type implementation for clarity and maintainability
- **cty**: restructure encoding and conversion subsystems
- **cty**: simplify protobuf encoding module structure
- **cty**: restructure dynamic value encoding logic
- **cty**: restructure dynamic value encoding logic
- **cty**: restructure base value handling for clarity and maintainability
- **cty**: rename Value class to CtyValue and reorganize imports
- **cty**: restructure module imports and internal organization

#### Documentation

- restructure documentation into chapter-based layout
- Add release readiness evaluation and feature comparison
- update guide chapters and index with revised content
- consolidate and restructure user documentation into chapter-based guide
- add dry-testing documentation and migration guide
- update operations guide with incomplete task status and feedback request
- correct API usage and examples across core documentation files
- correct code examples and fix documentation errors in README and QUICK_START
- add and organize documentation for cty library
- **cty**: add incomplete documentation for conversion, operations, paths, serialization, types, values, and README
- add feature matrix for cty module
- **cty**: expand documentation for serialization and type handling
- update path navigation example to use modern API
- add initial documentation file for Claude integration
- replace outdated cty documentation with updated version
- add initial Pyvider CTY documentation files
- add Claude summary document for 2025-03-10
- introduce Pyvider RPC plugin usage guide and architecture overview
- add initial user guides and chat logs for system design documentation
- add and organize chat transcripts and research notes from 2025-03-08
- **schema**: introduce schema documentation and research materials

#### Tests

- add Go-cty compatibility tests for encoding functions
- **cty**: add comprehensive test coverage for core functions and modules
- add comprehensive test coverage for cty types and collections
- **map**: fix failing tests by updating error message regex patterns
- **path**: update regex assertions to match current error output
- **compatibility**: add initial compatibility test framework for cty conversion
- **tuple**: add comprehensive test coverage for cty tuple operations
- add validation tests for cty map type
- **path**: remove async from synchronous path operations in tests
- **map**: add and refine test coverage for map creation logic
- **list**: rename and reorganize test methods for clarity and coverage
- **cty**: reorganize and expand map test suite with dedicated modules
- **list**: expand and reorganize list type tests
- **cty**: add initial test suite for cty types and collections

#### Chores

- merge mono-cty branch into main history
- **cty**: regenerate stub files from source
- **cty**: apply ruff formatting across modules
- **examples**: update example scripts for consistency and correctness
- update example script permissions
- **examples**: add and update example scripts for schema and performance testing
- merge work-in-progress branch into release preparation analysis
- **cty**: clean up debugging artifacts and unused code ahead of preview release
- **cty**: remove JULES_DEBUG log messages and update tests
- **cty**: modernize typing and formatting standards
- **github**: update CI and release workflows with automated fixes
- update project configuration to resolve build failure
- **pytest**: remove invalid log_levels option from configuration
- remove coverage reports and update TODO list
- **msgpack**: clean up unused imports and formatting
- **pyproject**: update project metadata and dependencies
- **dependency**: move pytest-mock to core dependencies to resolve fixture availability issues
- update project metadata and configuration
- remove cty compatibility kit project
- **env**: fix environment script
- **env**: initialize environment configuration file
- **build**: initialize project structure and environment
- update project metadata and dependencies
- **cty**: update emoji in conversion format comment
- **cty**: standardize module header comments
- **bool**: add whitespace for readability
- **env**: update environment configuration
- update project documentation and test harness configuration
- **cty**: update msgpack serializer module
- **docs**: restructure and expand example documentation
- **cty**: remove shebang line from dynamic_value.py

#### Scaffolding

- **project**: establish project structure, documentation, and examples
- **compatibility**: add Go compatibility test infrastructure
- **cty**: establish core type system and conversion infrastructure
- **cty**: add initial string and dynamic type modules
- **cty**: add initial list and tuple type implementations
- **cty**: add initial codec and base value structures
- **schema**: introduce schema type encoder infrastructure
- **optimizer**: introduce optimizer module skeleton and identity optimizer
- **cty**: add JSON encoder infrastructure for dynamic types
- **docs**: initialize TODO tracking document
- **cty**: introduce conversion module structure and marshaling utilities
- **encoding**: introduce core encoding subsystem structure
- **cty**: establish Go and Python compatibility test infrastructure
- **cty**: introduce operations module for value manipulation
- **pyvider**: initialize project structure and namespace module

#### Baselines

- **cty**: establish initial codebase structure and typing standards
- **cty**: add executable shebang to conversion module init
- **packaging**: configure license-files metadata for distribution

#### Uncategorised (no conventional-commit prefix)

- remediate(cty): resolve mypy type errors and failing tests in collection functions
- harden(dynamic): add defensive handling for malformed deserialization inputs
- qualify(cty): add type annotations to resolve mypy errors
- interface(parallel): introduce parallel validation API
- qualify(cty): add comprehensive test coverage for raw-to-cty conversion and function implementations
- remediate(cty): restore codec and conversion functionality
- qualify(conversion): add test coverage for caching behavior in CTY conversion pipeline
- qualify(string): add tests for all string functions to reach 94% coverage
- qualify(cty): add comprehensive test coverage for all function modules
- remediate(cty): fix dynamic type validation and conversion edge cases
- qualify(cty): achieve full test coverage for dynamic wire protocol and codec
- qualify(cty): complete explicit conversion test coverage
- qualify(cty): add TDD tests for explicit conversion enhancements
- qualify(cty): add comprehensive test coverage for capsule operations and validation
- qualify(conversion): add coverage for attrs-to-dict-safe conversion edge cases
- qualify(collection): expand test coverage for collection functions
- qualify(cty): add coverage for primitive string type
- remediate(cty): correct validation and type inference issues
- qualify(cty): add missing test coverage for validation and conversion logic
- qualify(cty): add unit tests for primitive type initializers and comparisons
- qualify(functions): expand test coverage for string, numeric, and collection functions
- qualify(functions): expand test coverage for string, numeric, and collection functions
- qualify(cty): add type annotations and fix mypy errors across core modules
- qualify(cty): add coverage tests for core and function modules
- remediate(path): address pytest hangs in path navigation logic
- specify(cty): update typing standards and documentation across modules
- qualify(cty): update type annotations and resolve mypy errors
- specify(cty): add type documentation for empty value handling
- instantiate(capsule): introduce CtyCapsule type for opaque Python objects
- qualify(map): add test coverage for Map type operations
- qualify(cty): expand msgpack coverage for dynamic values
- qualify(encoding): refine exception messages and add comprehensive tests
- remediate(cty): resolve dynamic msgpack encoding issues for set types
- qualify(msgpack): add encoder tests for edge cases and error handling
- remediate(cty): fix failing test assertion by removing invalid log capture expectation
- qualify(cty): add tests and improve coverage for map and msgpack modules
- qualify(cty): expand test coverage for core typing logic
- qualify(cty): add test coverage for base value handling
- qualify(cty): add test coverage for base value types and factory functions
- qualify(cty): expand test coverage for CtyValue methods in base.py
- qualify(path): add new tests for error handling and edge cases in cty.path modules
- qualify(json): add encoder test coverage for JSON conversion logic
- qualify(cty): restore test coverage for JSON conversion formats
- decouple(cty): restructure tuple type to import CtyValue locally
- qualify(cty): extend test coverage for set types and primitive booleans
- qualify(list): restore and validate list collection tests
- qualify(cty): correct list slicing assertion to check wrapped type instead of direct instance
- interface(cty): expose parse_collection_type and standardize_type_string at package root
- specify(cty): update project initialization emoji in module docstrings
- decouple(cty): relocate import paths to align with new module structure
- interface(cty): re-export classify_type and ensure_quoted_bytes from conversion module
- decouple(cty): consolidate marshal and unmarshal imports into single line
- decouple(cty): restructure conversion module paths to remove legacy core dependency
- instantiate(cty): add conversion module for CTY type handling
- deprecate(logger): remove dedicated logger in favor of telemetry integration
- instantiate(dynamic): introduce DynamicStructuralType class for runtime type evaluation
- instantiate(bool): introduce boolean primitive type implementation
- qualify(list): add comprehensive test coverage for list operations and validation
- qualify(cty): expand test coverage for map operations and validation
- qualify(cty): add comprehensive test coverage for map operations and validation
- remediate(cty): correct type mapping and base value handling
- qualify(cty): add compatibility test structures for go-cty and pyvider-cty type systems
- qualify(map): expand test harness coverage for map operations
- qualify(cty): refine type assertions in map tests to match new return type contract
- interface(cty): update Object.validate to return CtyValue instead of raw dict
- qualify(object): expand test coverage for object operations
- qualify(object): expand coverage for number type edge cases
- qualify(object): add coverage tests for structural object type handling
- qualify(object): expand test coverage for object type validation and behavior
- deprecate(cty): remove CtyDynamicValue export and related code deprecate(logger): remove legacy logger message modules deprecate(encoding): remove dynamic value implementation deprecate(test): remove obsolete dynamic value tests
- qualify(list): expand test coverage to 64 passing tests
- specify(license): standardize license metadata format in pyproject.toml
- decouple(cty): relocate dynamic value implementation to dedicated module
- decouple(cty): rename DynamicValue to CtyDynamicValue for clarity
- decouple(cty): restructure encoding modules to remove duplication and consolidate interfaces
- decouple(cty): replace ctypes module with types module hierarchy
- instantiate(cty): introduce encoding module infrastructure
- decouple(cty): restructure type system by removing legacy type modules
- instantiate(cty): add DynamicValue class for runtime type resolution
- instantiate(cty): introduce Terraform value encoding utilities
- instantiate(cty): introduce CtyDynamicValue class and related encoding infrastructure
- decouple(cty): migrate logger import from rpcplugin to cty module
- specify(cty): update Bool repr to include value for clarity
- decouple(cty): restructure logger import path for better modularity
- instantiate(logger): introduce structured logging infrastructure
- instantiate(cty): introduce protobuf encoding module for cty values
- decouple(cty): restructure module imports to use explicit package paths
- instantiate(cty): introduce new attribute and validation infrastructure
- qualify(cty): add structural object tests for go-cty compatibility
