# Comparison with go-cty

`pyvider.cty` is a Python implementation of the `cty` type system, which was originally developed in Go as `go-cty` for use in HashiCorp's Terraform. This page is the parity matrix: a complete, checked-against-the-running-code account of where the two libraries agree, where they deliberately differ, and what "parity" does and does not mean here.

> **Looking to migrate from go-cty?** See the **[How-To: Migrate from go-cty](../how-to/migrate-from-go-cty.md)** guide for step-by-step migration instructions and a complete checklist. This document focuses on feature comparison and API differences.

**Baseline**: this matrix was checked against go-cty `v1.19.0` (specifically `v1.19.0-1-g0d1eb26`) and `pyvider.cty` at the tip of the branch that becomes `0.5.0`. It was verified two ways: by executing every runnable example on this page against the installed library, and by consulting `.provide/GO-CTY-PARITY.md`, this project's own parity tracker, for every claim about go-cty's behavior that could not be checked directly (there is no Go toolchain in this environment, so go-cty itself was not re-run while writing this page — the tracker's own account is the record of a differential test suite that *does* run both libraries side by side, most recently at 2310 passed / 12 xfailed).

**What "parity" means on this page.** A row marked "Full parity" means: same result, same result type, same error behavior, checked directly (for library surfaces) or checked via the tracker's oracle-driven test suite (for the 83 stdlib functions, where re-deriving each comparison by hand in this document was not practical). "Parity" with a footnote means the two libraries agree except for one specific, named, deliberate divergence — the footnote says what it is and what it changes for a caller. Nothing on this page is marked "parity" because it merely *looks* similar; every row traces to either a runnable example above the table or a specific entry in the tracker.

**What this page does not cover.** It does not cover performance characteristics in any quantitative way (see [Performance Considerations](#performance-considerations) for the qualitative story). It does not cover the Go-side API beyond what is needed to translate a call — this is not a go-cty reference. And it does not promise that a future go-cty release stays matched: the baseline above is a snapshot, and the tracker's own header records the date it was last fully reviewed.

## Overview

Both libraries implement the same conceptual type system with:
- Primitive, collection, and structural types
- Null and unknown value semantics, including refinements on an unknown value
- A mark system for out-of-band metadata (sensitivity, provenance, and so on)
- Type conversion and unification
- MessagePack serialization for cross-language compatibility, byte-for-byte where it matters (Terraform diffs serialized state, not just decoded values)

## (a) The Type System

| Feature | go-cty | pyvider.cty | Notes |
|---|---|---|---|
| Primitive types (String, Number, Bool) | `cty.String`, `cty.Number`, `cty.Bool` | `CtyString`, `CtyNumber`, `CtyBool` | Full parity. `CtyNumber` uses `Decimal`, not a fixed-width float, matching go-cty's own arbitrary-precision `big.Float` in shape (see the numeric precision divergence below for the one place the *digits* differ). |
| Collection types (List, Map, Set) | `cty.List`, `cty.Map`, `cty.Set` | `CtyList`, `CtyMap`, `CtySet` | Full parity, including that a `CtySet` can hold another collection as an element (containers hash by their canonical sort key, matching go-cty's `HashSetRules`). |
| Structural types (Object, Tuple) | `cty.Object`, `cty.Tuple` | `CtyObject`, `CtyTuple` | Full parity. `CtyObject` optional attributes are wire-format metadata (`OptionalAttributes`), not a "must not be null" rule — see the value-model section below. |
| Dynamic (pseudo-)type | `cty.DynamicVal`, `cty.DynamicPseudoType` | `CtyDynamic` | Full parity: a `CtyDynamic` wrapper is transparent to `walk`/`deep_values`/`transform`/path `apply`, and `conformance_errors` treats a `want` of `CtyDynamic` as a wildcard. |
| Capsule types | `cty.Capsule`, `cty.CapsuleWithOps` | `CtyCapsule`, `CtyCapsuleWithOps` | Full parity, including `ConversionTo`/`ConversionFrom` capsule-to-capsule conversion and no-ops equality by identity (a capsule with no declared `equal_fn` compares by Python identity, matching go-cty's pointer-identity default; a class defining its own `__eq__` is honored, since that is an explicit opt-in with no Go equivalent). |
| Type unification | `convert.Unify` / `convert.UnifyUnsafe` | `unify()` | Ported entire, not patched: `dynamic` has the *lowest* preference (only absorbing among collections), objects with different attribute names unify as a map, and tuples of different lengths unify as a list. |
| `Type.TestConformance` | `Type.TestConformance(want)` → `[]error` | `conformance_errors(given, want)` → `list[ConformanceError]` | Full parity in behavior (path-tagged errors, `dynamic` wildcards on either side), different name: a module-level function named `test_*` gets collected as a pytest test case by accident, so it is exported as `conformance_errors`. Errors carry a display-string path (`[*]` for a collection element, since a `CtyPath` step cannot hold an *unknown* index) rather than a `CtyPath`. |

```python
from pyvider.cty import CtyList, CtyString, CtyNumber, CtyDynamic, conformance_errors

errors = conformance_errors(CtyList(element_type=CtyString()), CtyList(element_type=CtyNumber()))
print(errors)  # [ConformanceError(path='[*]', message='number required, but received string')]

# `want=CtyDynamic()` is a wildcard: anything conforms to it.
print(conformance_errors(CtyList(element_type=CtyString()), CtyDynamic()))  # []
```

## (b) The Value Model — Marks, Unknowns, and Refinements

| Feature | go-cty | pyvider.cty | Notes |
|---|---|---|---|
| Null values | `cty.NullVal(type)` | `CtyValue.null(type)` | Full parity. |
| Unknown values | `cty.UnknownVal(type)` | `CtyValue.unknown(type)` | Full parity. |
| A container holding an unknown element | `IsKnown()` false only if the *container itself* is unknown | `is_unknown` is `False` for a known container with an unknown element; `is_wholly_known()` asks whether anything inside it is still undecided | Full parity: a known container's known elements and known length survive encoding regardless of an unknown element inside it. |
| Three-valued equality | `Value.Equals(other)` → `cty.Value` (a boolean-typed value, possibly unknown) | `value.equals(other)` → `CtyValue` (same shape) | Full parity for list, tuple and primitive types, where go-cty is itself deterministic. For object and map types, go-cty is **not** deterministic (see the accepted divergence below) and this library deliberately answers a fixed `False` rather than reproducing the nondeterminism. |
| Marks | `Value.Mark(v)`, `HasMark`, `Unmark()` | `value.mark(m)`, `m in value.marks`, `value.unmark()` | Full parity for the shallow API. Deep, path-aware mark operations (`UnmarkDeepWithPaths`/`MarkWithPaths`) are `unmark_deep_with_paths()`/`mark_with_paths()` in `pyvider.cty.mark_paths`, plus the simpler flat `unmark_deep()`/`collect_marks_deep()` in `pyvider.cty.marks`. A `CtySet` hoists element marks onto the set during validation (`SetVal`'s own behavior) — `set.value[i].marks` is always empty; read sensitivity off the set. |
| Serializing a marked value | `msgpack.Marshal` returns an error: "value has marks, so it cannot be serialized" | `cty_to_msgpack()` raises `CtyMarksSerializationError` | Full parity: encoding refuses outright rather than silently dropping the marks. |
| Refinements on an unknown value | `cty.UnknownVal(t).Refine()` → `RefinementBuilder` | `refine(value)` → `RefinementBuilder` (`pyvider.cty.refinement`) | Full parity: refinements only narrow (a wider bound is discarded, not stored), and refining can produce a *known* value — an unknown refined to `[5, 5]` *is* 5. |
| `Value.Range()` / range membership | `Value.Range()` → `ValueRange`, `.Includes(candidate)` → three-valued | `value_range(value)` → `ValueRange`, `.includes(candidate)` → three-valued `CtyValue` | Full parity: `includes()` never concludes membership from bounds for a *known* value (go-cty builds a synthetic range and only ever excludes), so `.includes()` answers `False` or "cannot say", never a bare `True`. |
| `SafeKnownPrefix` | `stdlib.StringPrefix` / internal `SafeKnownPrefix` | `safe_known_prefix(prefix)` | Full parity, including go-cty's trailing-delimiter allowlist and dropping the final grapheme cluster (a later character may combine with it). |
| `UnknownAsNull` | `cty.UnknownAsNull(val)` | `unknown_as_null(value)` | Full parity: rewrites unknowns nested anywhere inside a value to null, recursively, without touching already-known or already-null values. |

Three-valued equality — the point of it is that it can decide from a part of the value that is already known, without waiting on the part that is not:

```python
from pyvider.cty import CtyObject, CtyString, CtyValue

obj_type = CtyObject(attribute_types={"a": CtyString(), "b": CtyString()})

# "b" already differs, so the answer is a definite False no matter what "a" turns out to be.
left = obj_type.validate({"a": CtyValue.unknown(CtyString()), "b": "x"})
right = obj_type.validate({"a": "z", "b": "DIFFERENT"})
print(left.equals(right).value)  # False

# Only "a" could still decide it, and "a" is unknown, so the answer is itself unknown.
left2 = obj_type.validate({"a": CtyValue.unknown(CtyString()), "b": "x"})
right2 = obj_type.validate({"a": "z", "b": "x"})
print(left2.equals(right2).is_unknown)  # True
```

A container with an unknown element is a *known* container, and everything downstream gets more precise because of it:

```python
from pyvider.cty import CtyList, CtyString, CtyValue
from pyvider.cty.functions import length

partial = CtyList(element_type=CtyString()).validate(["a", CtyValue.unknown(CtyString()), "c"])
print(partial.is_unknown)          # False -- the list itself is known
print(partial.is_wholly_known())   # False -- but not every element is
print(length(partial).value)       # 3 -- the length doesn't depend on what the unknown resolves to
```

Path-aware marks round-trip through a container, unlike the flat `unmark_deep()`:

```python
from pyvider.cty import CtyObject, CtyString, unmark_deep_with_paths, mark_with_paths

obj_type = CtyObject(attribute_types={"a": CtyString(), "b": CtyString()})
value = obj_type.validate({
    "a": CtyString().validate("x").mark("sensitive"),
    "b": CtyString().validate("y").mark("secret"),
})

unmarked, path_marks = unmark_deep_with_paths(value)
restored = mark_with_paths(unmarked, path_marks)
print(restored["a"].marks, restored["b"].marks)  # frozenset({'sensitive'}) frozenset({'secret'})
```

A refinement narrows what an unknown value could be, and `value_range().includes()` is honest about what the bounds can and cannot decide:

```python
from pyvider.cty import CtyNumber, CtyValue, refine, value_range

refined = refine(CtyValue.unknown(CtyNumber())).number_range_inclusive(0, 100).new_value()

rng = value_range(refined)
print(rng.includes(CtyNumber().validate(200)).value)   # False -- definitely excluded
print(rng.includes(CtyNumber().validate(50)).is_unknown)  # True -- within bounds, but not equality
```

## (c) Standard Library Functions

Every one of go-cty's 83 stdlib functions is implemented, declared through the `cty/function` framework (below), and checked against the tracker's differential oracle. "Full parity" below means the tracker's oracle found zero divergences for that function as of the baseline above. A footnoted "Parity" means one specific, named, deliberate difference — see [Accepted Divergences](#e-accepted-divergences) for what each footnote means and what it changes for a caller.

| go-cty name | pyvider.cty name | Status |
|---|---|---|
| **Numeric** | | |
| `abs` | `abs_fn` | Full parity |
| `add` | `add` | Full parity |
| `ceil` | `ceil_fn` | Full parity |
| `divide` | `divide` | Parity (N) |
| `floor` | `floor_fn` | Full parity |
| `int` | `int_fn` | Full parity |
| `log` | `log_fn` | Parity (N) |
| `max` | `max_fn` | Full parity |
| `min` | `min_fn` | Full parity |
| `modulo` | `modulo` | Full parity |
| `multiply` | `multiply` | Full parity |
| `negate` | `negate` | Full parity |
| `parseint` | `parseint_fn` | Full parity |
| `pow` | `pow_fn` | Parity (N) |
| `signum` | `signum_fn` | Full parity |
| `subtract` | `subtract` | Full parity |
| **Boolean** | | |
| `and` | `and_fn` | Full parity |
| `or` | `or_fn` | Full parity |
| `not` | `not_fn` | Full parity |
| **Comparison** | | |
| `equal` | `equal` | Full parity |
| `notequal` | `not_equal` | Full parity |
| `greaterthan` | `greater_than` | Full parity |
| `greaterthanorequalto` | `greater_than_or_equal_to` | Full parity |
| `lessthan` | `less_than` | Full parity |
| `lessthanorequalto` | `less_than_or_equal_to` | Full parity |
| **String** | | |
| `chomp` | `chomp` | Full parity |
| `format` | `format_fn` | Parity (U) |
| `indent` | `indent` | Full parity |
| `join` | `join` | Full parity |
| `lower` | `lower` | Full parity |
| `regex` | `regex` | Superset (R) |
| `regexall` | `regexall` | Superset (R) |
| `regexreplace` | `regexreplace` | Superset (R) |
| `replace` | `replace` | Full parity |
| `split` | `split` | Full parity |
| `strlen` | `strlen` | Parity (U) |
| `strrev` | `strrev` | Parity (U) |
| `substr` | `substr` | Parity (U) |
| `title` | `title` | Full parity |
| `trim` | `trim` | Full parity |
| `trimprefix` | `trimprefix` | Full parity |
| `trimspace` | `trimspace` | Full parity |
| `trimsuffix` | `trimsuffix` | Full parity |
| `upper` | `upper` | Full parity |
| **Collection** | | |
| `chunklist` | `chunklist` | Parity (W) |
| `coalesce` | `coalesce` | Full parity |
| `coalescelist` | `coalescelist` | Full parity |
| `compact` | `compact` | Parity (W) |
| `concat` | `concat` | Full parity |
| `contains` | `contains` | Full parity |
| `distinct` | `distinct` | Parity (W) |
| `element` | `element` | Full parity |
| `flatten` | `flatten` | Parity (M) |
| `formatlist` | `formatlist` | Full parity |
| `hasindex` | `hasindex` | Full parity |
| `index` | `index` | Full parity |
| `keys` | `keys` | Full parity |
| `length` | `length` | Parity (M) |
| `lookup` | `lookup` | Full parity |
| `merge` | `merge` | Full parity |
| `range` | `range_fn` | Full parity |
| `reverselist` | `reverse` | Full parity |
| `slice` | `slice` | Full parity |
| `sort` | `sort` | Parity (W)(S) |
| `values` | `values` | Full parity |
| `zipmap` | `zipmap` | Full parity |
| **Set** | | |
| `sethaselement` | `sethaselement` | Full parity |
| `setintersection` | `setintersection` | Full parity |
| `setproduct` | `setproduct` | Parity (L) |
| `setsubtract` | `setsubtract` | Full parity |
| `setsymmetricdifference` | `setsymmetricdifference` | Full parity |
| `setunion` | `setunion` | Full parity |
| **Bytes** | | |
| `byteslen` | `byteslen` | Full parity |
| `bytesslice` | `bytesslice` | Full parity |
| **Conversion** | | |
| `tobool` | `to_bool` | Full parity |
| `tonumber` | `to_number` | Full parity |
| `tostring` | `to_string` | Parity (N) |
| **Encoding** | | |
| `csvdecode` | `csvdecode` | Full parity |
| `jsondecode` | `jsondecode` | Full parity |
| `jsonencode` | `jsonencode` | Full parity |
| **Date/Time** | | |
| `formatdate` | `formatdate` | Parity (D) |
| `timeadd` | `timeadd` | Parity (C) |
| **Misc (assertion)** | | |
| `assertnotnull` | `assertnotnull` | Full parity |

`pyvider.cty` name is the importable symbol from `pyvider.cty.functions`; several are renamed from go-cty's spelling only where Python forces it — `and`/`or`/`not` are keywords, `abs`/`ceil`/`floor`/`int`/`log`/`max`/`min`/`pow`/`range`/`signum`/`format`/`parseint` shadow a builtin or another symbol the same module calls — never for style. `pyvider.cty.functions.STDLIB` maps every go-cty name to its implementation regardless of the Python name, so `STDLIB["reverselist"]` reaches the function exported as `reverse`.

Footnotes: **(N)** numeric precision model differs in both directions (see below) — unresolved. **(U)** grapheme-cluster measurement carries a narrow Unicode-version skew against the oracle only, not against go-cty's own current behavior (see below). **(R)** Python's `re` is not RE2 — a superset, not a mismatch (see below). **(W)** parameter type deliberately widened relative to go-cty's own `list(dynamic)` declaration (see below). **(M)** keeps the deep union of element marks where go-cty drops them (see below). **(S)** `sort(list(number))` orders numerically rather than lexicographically as a consequence of (W) (see below). **(D)** deliberately refuses an input go-cty answers (see below). **(L)** refuses past a size limit go-cty does not impose (see below). **(C)** the calendar range `datetime` covers is narrower than Go's `time.Time` (see below). (N) covers how wide a number can be *written* as well as how precisely it is computed.

## (d) The `cty` Package Surfaces

| Surface | go-cty | pyvider.cty | Notes |
|---|---|---|---|
| Conversion | `convert.Convert` | `convert(value, target_type)` | Full parity for every case the tracker's conversion oracle drives, with one accepted divergence for a narrow set-to-list edge case (below). A conversion result's type reflects the converted value rather than a stale constraint: converting to `list(any)` produces a list of the *source's* element type, not `list(dynamic)`. |
| Unification | `convert.Unify` | `unify(types)` | Full parity — see the type-system table above. |
| Deep traversal | `cty.Walk`, `cty.Transform`, `cty.DeepValues` (Go 1.23+ iterator) | `walk(value, visit)`, `transform(value, fn)`, `deep_values(value)` | Full parity, including traversal order: a map's keys and an object's attributes are visited in **sorted** order (go-cty's own reason: "so that results will always be stable given the same input"), not insertion or declaration order. |
| `Value.Range()` / `Refine()` | See value-model table above | See value-model table above | Full parity. |
| `UnknownAsNull` | See value-model table above | See value-model table above | Full parity. |
| Deep, path-aware marks | `cty.UnmarkDeepWithPaths`, `cty.MarkWithPaths` | `unmark_deep_with_paths()`, `mark_with_paths()` | Full parity. |
| `Type.TestConformance` | See type-system table above | `conformance_errors()` | Full parity. |
| `cty/json` value codec | `json.Marshal`, `json.Unmarshal`, `json.ImpliedType` | `cty_to_json()`, `cty_from_json()`, `implied_json_type()` | Full parity as of the last json-to-json byte comparison against the oracle. Distinct from the `jsonencode`/`jsondecode` **stdlib functions**, which operate on a JSON-string-valued `CtyValue` rather than serializing a `CtyValue` itself. Escapes `<`, `>` and `&` as Go's encoder does (Terraform compares state textually, so the escaping changes the bytes even when no value changes). |
| MessagePack codec | `msgpack.Marshal`, `msgpack.Unmarshal` | `cty_to_msgpack()`, `cty_from_msgpack()` | Full parity for every value the tracker's oracle drives, including refined-unknown wire bytes (ext type 12) and infinity. One accepted, byte-level divergence for a set holding a null (below). `cty_from_msgpack()` does not yet wrap every possible decode failure in `DeserializationError` — see [docs/reference/troubleshooting.md](troubleshooting.md#deserializationerror) for what it actually raises today. |
| `Value.Equals` | `Value.Equals(other)` | `value.equals(other)` | Full parity for list and tuple (go-cty is deterministic there). Deliberately diverges for object and map, where go-cty is not deterministic — see below. |

```python
from pyvider.cty import CtyObject, CtyString, cty_to_json, cty_from_json

person_type = CtyObject(attribute_types={"name": CtyString(), "age": CtyString()})
person = person_type.validate({"name": "Alice", "age": "30"})

payload = cty_to_json(person, person_type)
print(payload)  # b'{"age":"30","name":"Alice"}'
print(cty_from_json(payload, person_type).raw_value)  # {'name': 'Alice', 'age': '30'}
```

### The function framework

go-cty's `cty/function` package — `Function`, `Spec`, `Parameter`, `AllowNull`/`AllowUnknown`/`AllowDynamicType`/`AllowMarked`, `RefineResult` — has a full Python port at `pyvider.cty.functions._function` (re-exported from `pyvider.cty.functions`): `CtyFunction`, `CtyFunctionSpec`, `CtyParameter`, `CtyArgumentError` (an index-carrying `CtyFunctionError` subclass), `unpredictable`, `static_return_type`, `return_type()`/`return_type_for_values()`. All 83 stdlib functions declare their parameters through it — every `AllowNull` flag transcribed from go-cty's own `Spec`, not guessed — and the call sequence matches go-cty step for step: arity check, then per-argument unwrap/unmark/null/conformance checks, then the type callback, then marks collected from every argument before the unknown short-circuit, then the implementation, then a result-conformance check.

**The practical consequence**: a null argument is refused rather than silently propagated, for any parameter go-cty itself does not mark `AllowNull`. This governs roughly 35 of the 83 stdlib functions, where returning an unknown for a null argument would invent a fact an unknown does not have.

```python
from pyvider.cty import CtyString
from pyvider.cty.functions import upper

null_val = CtyString().validate(None)
try:
    upper(null_val)
except Exception as e:
    print(f"{type(e).__name__}: {e}")  # CtyArgumentError: upper: argument 0 must not be null
```

## (e) Accepted Divergences

These are not gaps to be closed — each is a deliberate decision, recorded in `.provide/GO-CTY-PARITY.md`, with a reason. This section states each one plainly and says what a caller actually sees.

**Python's `re` is not RE2.** `regex`, `regexall` and `regexreplace` use Python's regex engine. A pattern with a backreference (`(a)\1`) or lookaround (`a(?=b)`) matches here and is *refused* by go-cty's RE2-based implementation ("invalid escape sequence", "invalid or unsupported Perl syntax"). This is a superset, not a mismatch: every pattern valid in both engines behaves identically, including capture-group semantics and Go-style (not Python-style) replacement expansion in `regexreplace`. The consequence for a provider author: a pattern tested only against pyvider.cty can ship, then be rejected the first time the same configuration runs through real Terraform (which links go-cty).

**The numeric precision model differs in both directions.** go-cty holds a number in a 512-bit `big.Float`, giving `divide(1, 3)` about 155 significant digits; this library's `Decimal` context gives 28. go-cty's `pow` and `log` compute in `float64` -- their `Impl` reads both arguments through `gocty.FromCtyValue` into a `float64` and nothing on that path is a `big.Float` -- and **this library now does the same** (2026-08-18). Being more precise than that was not a rounder version of go-cty's answer but a different function: it overflowed to `decimal.Overflow` where go-cty answers `+Inf`, returned exactly `1e400` where go-cty returns `+Inf`, and never made the float64-range refusal that `log` already made on identical input. **`divide` is the half that remains, and it is a closed decision rather than an open question:** matching it is a representation change, not a precision setting -- go-cty's answer ends `...335` because it is a 512-bit *binary* float printed exactly, and a decimal division ends `...333` at any precision -- so it would cost a new dependency and a rewrite of the value payload, to fix a case with no consumer in the workspace. Terraform compares values as they arrive on the wire, so a difference in the trailing digits is a real diff for these three functions, not a cosmetic one.

**Serialization has a different limit, and it is 154 significant digits.** The 28 above bound what a *computation* carries, not what a value renders as. Until 2026-08-19 they were the same number by accident: the text renderer behind `convert(number, string)`, `tostring`, `format("%s", n)`, `jsonencode` and the `cty/json` codec called `Decimal.normalize()`, which honours the active context and therefore rounded, while the msgpack codec did not -- so the two codecs in this library disagreed about the same value, and the lossy one was the one state files are written in. `2**100` reached state as `1267650600228229401496703205000`.

The real ceiling is go-cty's, not this library's. A go-cty number is rendered with `big.Float.Text('f', -1)`, the shortest decimal that reads back as the same 512-bit float, so it spells `floor(512 × log₁₀2) = 154` significant digits and writes zeros past them; a `Decimal` spells every digit it holds. Measured against the harness: `5**220` is 154 digits and the two agree, `5**221` is 155 and is the first that cannot. Magnitude is not the deciding factor -- `10**500` is 501 digits with one of them significant, and both spell it in full. The boundary is held by a strict xfail in the sweep, and it is the width half of the same closed decision as `divide`: matching it means holding numbers as a binary float rather than a `Decimal`.

**Widened parameter types for `distinct`, `chunklist`, `compact` and `sort`.** go-cty declares these with a `list(dynamic)` parameter and relies on HCL to convert the caller's list before the function ever sees it. Nothing in this library's call path performs that conversion, so a verbatim declaration would refuse `sort(list(number))` outright. The parameters here accept the wider input instead. **Consequence**: `sort(list(number))` succeeds here and orders numerically; Terraform's own call site converts to `list(string)` first and sorts lexicographically, so a caller comparing this library's answer for a numeric list directly against Terraform's `sort()` output should expect a different order. Recorded as an open item, not a bug — narrowing it is a decision, not a migration step.

**`flatten` and `length` keep the deep union of element marks; go-cty drops nested marks on both.** Matching go-cty here would mean silently declassifying a nested sensitive value the moment it passes through `flatten` or `length` — this library has made the opposite call before (see the mark-serialization change above) and makes it again here. **Consequence**: a mark that was on an element three levels deep survives a `flatten()` call and lands on the flattened result; a caller diffing behavior against real Terraform should expect this one difference in mark propagation, nothing else.

**GB9c Unicode version skew** affects `strlen`, `substr`, `strrev` and `format`'s width/precision, all of which measure in grapheme clusters (not code points) via a vendored, table-driven segmenter verified equal to the `uniseg` reference at all 1,114,112 code points and against 212,696 test strings. The one place it does not agree with everything is the *oracle* used to verify it: that oracle is built with Go 1.26, which resolves to Unicode 15.0 (pre-GB9c) rather than the Unicode 17 that go-cty itself would use on a newer toolchain, so it reads `क्ष` as two grapheme clusters where a current build reads one. Four cases are held as strict `xfail`s against the oracle specifically because of this, not because this library disagrees with go-cty's real behavior — this library's segmenter already agrees with the *newer* Unicode version go-cty itself carries.

**~~A set holding a null re-encodes with the null first; go-cty writes it last.~~ Closed — and the sentence that followed it was wrong.** The null-rank half was fixed on 2026-08-17. The claim it carried, that "set ordering agrees everywhere else", was true of primitives and untested for composites: go-cty ranks a composite element that has *run out of members* last, where a plain tuple comparison ranks it first, so every set of lists or maps whose elements differed in length re-encoded in a different byte order. `{["a"], ["a","c"]}` is the smallest case; a set holding an empty element is the extreme one. Measured on 2026-08-19 over 300 generated sets, 232 diverged and every one contained a pair where one element was a prefix of another. Both halves are fixed and set ordering now agrees on both sides for every shape tested. Kept on this page because the *consequence* is worth stating: Terraform diffs serialized state as text, and `set(object({...}))` is its nested-block type, so any block set whose members carried different numbers of optional attributes showed a spurious diff on every plan.

**A NaN is refused by both codecs; go-cty cannot hold one at all.** go-cty's number is a `big.Float`, which has `+Inf` and `-Inf` and no NaN — `SetFloat64` panics on one — so `cty.NumberVal` cannot carry a NaN and every string that parses to one is refused. A `Decimal` carries one, and until 2026-08-19 this library *serialized* it, as the msgpack string `"NaN"`, which go-cty reads back as `number is required`. **Consequence**: a value this library could put on the wire that Terraform's own library could not read. Both codecs refuse it now; constructing one is still allowed, because `format` spells one the way Go's `fmt` does and no stdlib function produces one. Infinity is unaffected — go-cty writes the same float64 bytes and reads this library's. A narrower, remaining difference: `Decimal` also parses `Infinity`, `infinity` and `INF` where Go's `big.ParseFloat` takes only `inf`, `+Inf` and `-Inf`, so `convert(string, number)` accepts spellings go-cty refuses. That one has no wire consequence — every spelling accepted produces the same `+Inf` go-cty writes — and narrowing it would break a configuration that spells infinity the long way, so it is recorded rather than matched.

**`formatdate` refuses a Go reference layout; go-cty returns it as literal text.** Marked (D) above and the only place this library declines something go-cty answers *with a plausible-looking value*. Before 0.5.0 this library translated Go's own `2006-01-02` reference layout into `strftime`; go-cty defines its own `YYYY-MM-DD` scheme and reads digits as literal text, so `formatdate("2006-01-02", ts)` returns the string `2006-01-02` there — not an error, not a date, and shaped exactly like the answer the caller wanted. That makes it the worst of the breaking changes in 0.5.0, and the refusal exists so the break is loud. The trigger is narrow: `2006` *plus* a second reference token, each anchored to a whole run of digits, and quoting is the documented escape.

**`setproduct` refuses a product over 1,000,000 elements; go-cty allocates it.** Marked (L) above. go-cty multiplies the argument lengths and allocates two slices sized by the product before producing any element — six ten-element arguments, sixty values in total, allocate just over 500 MB, and eight ask for roughly 50 GB. On a plan runner that is an OOM kill rather than a diagnostic. **Consequence**: a call this library refuses with `CtyFunctionError` is one real Terraform would attempt. The cap applies only where the product would actually be materialized: an argument of unknown length still answers an unknown, which is the shape Terraform sends at plan time.

**`timeadd` covers a narrower calendar range than Go's `time.Time`.** Marked (C) above. Go's `time.Time` runs to year 292277026596 and before year 1; Python's `datetime` stops at 9999 and starts at 1. Past either end go-cty answers a timestamp and this library raises `CtyFunctionError`. Held by two strict xfails. Measured before accepting: replacing `datetime` would buy nanosecond resolution neither side can render, and the year range is the least of what it would cost.

**Converting a set with an unknown-but-not-wholly-unknown length to a list is not matched to go-cty's own answer, because go-cty's own answer is wrong.** This is the narrowest divergence on this page: it applies only when a `CtySet`'s stored elements number more than one, at least one is not wholly known, the set itself is not wholly unknown, and the target of `convert()` is a list. go-cty's converter (`conversion_collection.go`) short-circuits on `!val.Length().IsKnown()` and returns a wholly-unknown value typed from the *source* element type — leaving the requested target element type unused, so a provider decoding into its declared schema can receive a value that does not conform to it. This library returns an unknown *list* of the correct target element type instead, refined `collection_length ∈ [1, store size]` — a set holding an unknown may coalesce (`{1, unknown}` can turn out to be a single element), so the store's size is an upper bound rather than a count. That refinement is what makes `length()` agree on the source and on the result, which is the property a definite-length answer broke. Pinned by six tests in the tracker's conversion oracle, with a docstring noting they should stay red if "fixed" back to matching go-cty.

**`unify` differs when a `dynamic`, a list and a tuple meet — recorded, not yet decided.** Unification decides the element type of `concat`, `flatten` and every set operation, so an element type that differs from go-cty's is a different type on the wire. This surface had no differential coverage at all until 2026-08-19; sweeping every pair and triple of a representative type set now finds **17 divergent combinations out of 969**, in two shapes. All seventeen share three ingredients — a `dynamic` (bare, or as a list's element type), a list or set, and a tuple — and with any two of the three the answers agree.

The first shape is the one with teeth: **this library unifies where go-cty refuses.** `unify(tuple(list(string), number), list(dynamic))` is `list(dynamic)` here and *no common type* in go-cty, so `concat` and `flatten` succeed here on arguments real Terraform rejects. The second loses a concrete element type: `unify(list(list(string)), tuple(), list(dynamic))` is `list(list(string))` in go-cty and `list(dynamic)` here. What makes the case odd is go-cty's own behaviour — adding a `dynamic`, a wildcard that conforms to anything, *changes* its answer, from `list(string)` without it to `list(number)` with it. Matching any of this means reproducing `convert`'s unification order rather than patching a rule, so it is held by seventeen strict xfails and left open.

Two neighbouring surfaces were swept the same way on the same day and are clean: `TestConformance` over all 306 ordered type pairs, and `convert` over all 169 ordered conversions with a representative value each.

**`Value.Equals` is deliberately more deterministic than go-cty's, for object and map.** Confirmed in the tracker by running go-cty itself 1,000 times on identical object and map inputs holding both an unknown and a definite difference: go-cty's answer varied between `false` and `unknown` from one run to the next, because its comparison loop ranges over Go's own randomized map iteration order and returns at the first unknown it happens to visit or the first definite difference, whichever comes first. This library always returns the same, more informative answer (a definite `False` whenever any part of the value already differs, matching what three-valued equality means everywhere else in this library). **Consequence for a Terraform user**: this is a fix, not a cosmetic difference — go-cty's nondeterminism means `==` on such a value can read "known after apply" on one plan and `false` on the next, so a resource keyed on that comparison can succeed on a retry that should have behaved identically to the run that just failed. list and tuple are unaffected: go-cty is itself deterministic there (first-unknown-wins in index order), and this library matches it exactly.

## API Translation Examples

### Creating Types

**Go (go-cty):**
```go
import "github.com/zclconf/go-cty/cty"

// Primitive type
stringType := cty.String

// Object type
personType := cty.Object(map[string]cty.Type{
    "name": cty.String,
    "age":  cty.Number,
})

// List type
listType := cty.List(cty.String)
```

**Python (pyvider.cty):**
```python
from pyvider.cty import CtyString, CtyNumber, CtyObject, CtyList

# Primitive type
string_type = CtyString()

# Object type
person_type = CtyObject(
    attribute_types={
        "name": CtyString(),
        "age": CtyNumber(),
    }
)

# List type
list_type = CtyList(element_type=CtyString())
```

### Creating Values

**Go:**
```go
// String value
strVal := cty.StringVal("hello")

// Number value
numVal := cty.NumberIntVal(42)

// Object value
person := cty.ObjectVal(map[string]cty.Value{
    "name": cty.StringVal("Alice"),
    "age":  cty.NumberIntVal(30),
})

// Null value
nullVal := cty.NullVal(cty.String)

// Unknown value
unknownVal := cty.UnknownVal(cty.String)
```

**Python:**
```python
from pyvider.cty import CtyString, CtyNumber, CtyObject, CtyValue

# Validate data (preferred approach)
str_val = CtyString().validate("hello")
num_val = CtyNumber().validate(42)

# Object value
person_type = CtyObject(
    attribute_types={"name": CtyString(), "age": CtyNumber()}
)
person = person_type.validate({"name": "Alice", "age": 30})

# Null value
null_val = CtyValue.null(CtyString())

# Unknown value
unknown_val = CtyValue.unknown(CtyString())
```

### Accessing Values

**Go:**
```go
// Access raw value
rawStr := strVal.AsString()
rawNum, _ := numVal.AsBigFloat().Int64()

// Access object attribute
nameVal := person.GetAttr("name")

// Check for null/unknown
if person.IsNull() {
    // handle null
}
```

**Python:**
```python
from pyvider.cty import CtyString, CtyNumber, CtyObject

str_val = CtyString().validate("hello")
num_val = CtyNumber().validate(42)
person_type = CtyObject(attribute_types={"name": CtyString(), "age": CtyNumber()})
person = person_type.validate({"name": "Alice", "age": 30})

# Access raw value
raw_str = str_val.raw_value
raw_num = num_val.raw_value

# Access object attribute
name_val = person["name"]

# Check for null/unknown
if person.is_null:
    pass  # handle null
```

### Marks

**Go:**
```go
import "github.com/zclconf/go-cty/cty"

// Create marked value
sensitive := "sensitive"
marked := val.Mark(sensitive)

// Check for marks
if marked.HasMark(sensitive) {
    // handle sensitive data
}

// Remove marks
unmarked, marks := marked.Unmark()
```

**Python:**
```python
from pyvider.cty import CtyString
from pyvider.cty.marks import CtyMark

val = CtyString().validate("hello")

# Create marked value
sensitive = CtyMark("sensitive")
marked = val.mark(sensitive)  # Single mark
# Or: marked = val.with_marks({sensitive})  # Set of marks

# Check for marks
if sensitive in marked.marks:
    pass  # handle sensitive data

# Remove all marks (returns tuple of unmarked value and marks)
unmarked_val, removed_marks = marked.unmark()
```

### Type Conversion

**Go:**
```go
import "github.com/zclconf/go-cty/cty/convert"

// Convert string to number
numVal, err := convert.Convert(strVal, cty.Number)
if err != nil {
    // handle conversion error
}

// Unify types
unified, _ := convert.UnifyUnsafe([]cty.Type{cty.String, cty.Number})
```

**Python:**
```python
from pyvider.cty import CtyString, CtyNumber, convert, unify
from pyvider.cty.exceptions import CtyConversionError

str_val = CtyString().validate("hello")

# Convert string to number (fails here -- "hello" isn't numeric)
try:
    num_val = convert(str_val, CtyNumber())
except CtyConversionError as e:
    pass  # handle conversion error

# Unify types
unified = unify([CtyString(), CtyNumber()])
```

### Serialization

**Go:**
```go
import (
    "github.com/zclconf/go-cty/cty"
    "github.com/zclconf/go-cty/cty/msgpack"
)

// Serialize to MessagePack
bytes, err := msgpack.Marshal(val, valType)

// Deserialize from MessagePack
val, err = msgpack.Unmarshal(bytes, valType)
```

**Python:**
```python
from pyvider.cty import CtyString
from pyvider.cty.codec import cty_to_msgpack, cty_from_msgpack

val_type = CtyString()
val = val_type.validate("hello")

# Serialize to MessagePack
msgpack_bytes = cty_to_msgpack(val, val_type)

# Deserialize from MessagePack
val = cty_from_msgpack(msgpack_bytes, val_type)
```

## Idiom Differences

### Error Handling

**Go:** Uses explicit error returns
```go
val, err := someFunction()
if err != nil {
    return err
}
```

**Python:** Uses exceptions
```python
from pyvider.cty.exceptions import CtyValidationError

def some_function():
    from pyvider.cty import CtyString
    return CtyString().validate("hello")

try:
    val = some_function()
except CtyValidationError as e:
    pass  # handle error
```

### Iteration

**Go:** Range-based for loops
```go
it := listVal.ElementIterator()
for it.Next() {
    _, elemVal := it.Element()
    // process elemVal
}
```

**Python:** Pythonic iteration
```python
from pyvider.cty import CtyList, CtyString

list_val = CtyList(element_type=CtyString()).validate(["a", "b", "c"])

for elem_val in list_val:
    pass  # process elem_val
```

### Optional Attributes

**Go:** Uses `OptionalAttrs` in object definition
```go
objType := cty.ObjectWithOptionalAttrs(
    map[string]cty.Type{
        "name": cty.String,
        "age":  cty.Number,
    },
    []string{"age"}, // optional attributes
)
```

**Python:** Uses `optional_attributes` parameter
```python
from pyvider.cty import CtyObject, CtyString, CtyNumber

obj_type = CtyObject(
    attribute_types={
        "name": CtyString(),
        "age": CtyNumber()
    },
    optional_attributes={"age"}
)
```

Remember that `optional_attributes` only controls which attribute *keys* may be omitted from the input entirely. Every attribute, optional or not, already accepts an explicit `None` for its value — see the type-system notes in [Structural Types](../api/types/structural.md).

## Serialization Compatibility

The MessagePack serialization format is **fully compatible** between go-cty and pyvider.cty, for any value that carries no marks (see the value-model table above for why a marked value cannot serialize at all):

```python
from pyvider.cty import CtyObject, CtyString
from pyvider.cty.codec import cty_to_msgpack

schema = CtyObject(attribute_types={"name": CtyString()})
value = schema.validate({"name": "Alice"})

# Python serializes
python_bytes = cty_to_msgpack(value, schema)

# Go can deserialize the same bytes:
#   val, err := msgpack.Unmarshal(pythonBytes, goSchema)
# And vice versa -- Go serializes, Python deserializes with cty_from_msgpack.
```

This enables true cross-language interoperability for:
- Terraform provider development
- Multi-language systems
- Configuration sharing

## Performance Considerations

**go-cty advantages:**
- Faster execution (compiled vs interpreted)
- Lower memory overhead
- Better for CPU-intensive operations

**pyvider.cty advantages:**
- Rapid development and prototyping
- Rich Python ecosystem integration
- Easier debugging and introspection
- Better for I/O-bound operations

This page does not carry benchmark numbers — none were re-measured while writing it, and a stale number is worse than none. Treat the above as qualitative.

**Performance tips for pyvider.cty:**
```python
from pyvider.cty import CtyObject, CtyString

# Cache schemas -- don't recreate them
config_schema = CtyObject(attribute_types={"field": CtyString()})  # Create once

# Reuse validated values
config = config_schema.validate({"field": "value"})  # Validate once
for _ in range(1000):
    pass  # process(config) -- reuse many times, don't re-validate

# Avoid repeated type construction in loops
large_dataset = [{"field": "a"}, {"field": "b"}]

# Bad: creates a new type each iteration
for data in large_dataset:
    schema = CtyObject(attribute_types={"field": CtyString()})
    value = schema.validate(data)

# Good: create the schema once
schema = CtyObject(attribute_types={"field": CtyString()})
for data in large_dataset:
    value = schema.validate(data)
```

## Migration Checklist

When migrating from go-cty to pyvider.cty:

- [ ] Replace `cty.StringVal()` with the `.validate()` pattern
- [ ] Update `val.AsString()` to `val.raw_value`
- [ ] Change `val.GetAttr("key")` to `val["key"]`
- [ ] Replace `cty.NullVal(type)` with `CtyValue.null(type)`
- [ ] Update error handling from `err` returns to exceptions
- [ ] Convert iterator loops to Python `for` loops
- [ ] Update package imports to `pyvider.cty`
- [ ] Review optional-attribute syntax: it is wire-format metadata, not a "must not be null" rule (see (a) above)
- [ ] If calling `regex`/`regexall`, use the argument order pyvider.cty takes: `(pattern, string)`, matching go-cty — a call written for `(string, pattern)` still type-checks and silently returns the wrong answer
- [ ] If calling any of the ~35 functions where go-cty does not mark the parameter `AllowNull`, expect a `CtyArgumentError` for a null argument (see (d) above)
- [ ] Test MessagePack serialization compatibility, and strip marks with `unmark_deep()` before serializing if the value might carry any
- [ ] Verify mark handling with the new API, especially for `CtySet` (marks are hoisted onto the set, not kept per element)

## Common Migration Patterns

### Pattern 1: Validation Function

**Go:**
```go
func ValidateConfig(raw map[string]interface{}) (cty.Value, error) {
    configType := cty.Object(map[string]cty.Type{
        "host": cty.String,
        "port": cty.Number,
    })

    val, err := gocty.ToCtyValue(raw, configType)
    return val, err
}
```

**Python:**
```python
from pyvider.cty import CtyObject, CtyString, CtyNumber, CtyValue
from pyvider.cty.exceptions import CtyValidationError

def validate_config(raw: dict) -> CtyValue:
    config_type = CtyObject(
        attribute_types={
            "host": CtyString(),
            "port": CtyNumber(),
        }
    )

    try:
        return config_type.validate(raw)
    except CtyValidationError as e:
        # Handle or re-raise
        raise ValueError(f"Invalid config: {e}") from e
```

### Pattern 2: Iterating Collections

**Go:**
```go
func ProcessList(listVal cty.Value) {
    it := listVal.ElementIterator()
    for it.Next() {
        _, val := it.Element()
        process(val)
    }
}
```

**Python:**
```python
from pyvider.cty import CtyValue

def process_list(list_val: CtyValue) -> None:
    for val in list_val:
        process(val)

def process(val: CtyValue) -> None:
    pass
```

### Pattern 3: Working with Marks

**Go:**
```go
func RedactSensitive(val cty.Value) cty.Value {
    val, marks := val.Unmark()
    for mark := range marks {
        if mark == "sensitive" {
            return cty.StringVal("[REDACTED]")
        }
    }
    return val
}
```

**Python:**
```python
from pyvider.cty import CtyString, CtyValue
from pyvider.cty.marks import CtyMark

def redact_sensitive(val: CtyValue) -> CtyValue:
    sensitive = CtyMark("sensitive")
    if sensitive in val.marks:
        return CtyString().validate("[REDACTED]")
    return val.without_all_marks()
```

## Getting Help

If you're migrating from go-cty and need assistance:

- Check the **[How-To: Migrate from go-cty](../how-to/migrate-from-go-cty.md)** guide
- Review the **[API Reference](../api/index.md)** for pyvider.cty equivalents
- Open an issue on [GitHub](https://github.com/provide-io/pyvider-cty/issues)
- Join discussions about migration challenges

## Further Reading

- **[go-cty Documentation](https://pkg.go.dev/github.com/zclconf/go-cty/cty)** - Official go-cty docs
- **[Terraform Type System](https://developer.hashicorp.com/terraform/language/expressions/types)** - Terraform's use of cty
- **[How-To: Work with Terraform](../how-to/work-with-terraform.md)** - Terraform integration guide
- **[Release Notes](release-notes.md)** - The full list of breaking changes between the previous release and `0.5.0`
