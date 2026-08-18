# Release Notes

This page orients you to what a release changes from a caller's point of view. For the complete, itemized list of every change — the canonical record — see [CHANGELOG.md](https://github.com/provide-io/pyvider-cty/blob/main/CHANGELOG.md) in the repository root. This page will not duplicate that list; it explains the shape of it.

## 0.5.0

This release brings `pyvider.cty` to feature parity with go-cty `v1.19.0`. All 83 of go-cty's stdlib functions are implemented and declared through a full Python port of go-cty's own `cty/function` framework (`CtyFunction`, `CtyFunctionSpec`, `CtyParameter`, `CtyArgumentError`, `SIGNATURES`, `STDLIB`), rather than through hand-rolled null/unknown checks that had drifted apart function by function. Alongside the function port, this release adds a refinement builder (`refine()`, `value_range()`, `safe_known_prefix()`), deep traversal (`walk()`, `deep_values()`, `transform()`), grapheme-cluster-aware string handling, and a long list of correctness fixes — most of them in mark handling, null handling, and set semantics.

Every change was verified against a live go-cty oracle — the `soup-go` differential test harness — rather than against go-cty's documentation. That means this release corrects a number of long-standing behaviors that never matched go-cty in the first place, alongside adopting genuinely new go-cty v1.19.0 behavior. See [Comparison with go-cty](go-cty-comparison.md) for the parity matrix this release achieves, function by function and surface by surface.

**This is a breaking release**, with 43 catalogued breaking changes. They fall into a handful of themes:

- **Marks and value mutability.** A `CtySet`'s marks live on the set, not on its elements. Serializing a marked value raises instead of silently dropping the marks. `value.value` is no longer mutable in place.
- **Nulls inside containers.** A `CtyList` and object attributes now accept an explicit `null` where they used to refuse it on read — state real Terraform writes constantly. The flip side is that `CtyObject.validate()` no longer treats "attribute is present but null" as a validation failure; only a genuinely *missing* required key is refused.
- **Stdlib function signatures and return types.** A cluster of individual functions — `regex`/`regexall` (argument order), `indent`, `flatten`, `chunklist`, `regexreplace`, `keys`/`values` ordering, `formatdate`/`timeadd`, the JSON/CSV decoders, `merge`, and string functions that now measure in grapheme clusters rather than code points — changed to match go-cty's actual behavior. Several of these fail silently rather than raising, so they need a manual audit rather than a test-suite run.
- **The function framework itself.** Every stdlib function now validates its arguments the way go-cty's `cty/function` framework does. The single widest consequence: roughly 35 functions that used to return an unknown for a null argument now raise `CtyArgumentError` instead, since inventing an unknown from a null invents a fact the null doesn't have.
- **Conversion and the value model.** A conversion result's type now reflects the converted value rather than carrying over a stale constraint. A container holding an unknown element is now itself a known container — a fix, since the old behavior degraded a perfectly good value to a bare unknown on the wire. Refinements now survive `validate()` and a msgpack round-trip. Wire bytes changed in a few places to match go-cty exactly, which matters because Terraform compares serialized state, not just decoded values.

## Who is affected, and what to do

If you call `pyvider.cty` only through `validate()`, basic type construction, and straightforward stdlib calls with known, non-null arguments, most of this release is invisible to you. The changes concentrate in three places: **code that passes `null` to stdlib functions** (audit call sites — the new behavior is a raised `CtyArgumentError`, not a returned unknown), **code that parses `formatdate`/`regex`/`regexreplace` format strings or patterns** (these fail silently on the wrong dialect, so re-test rather than trust an absence of exceptions), and **code with byte-exact expectations of serialized output** (msgpack fixtures for unknown or refined-unknown values need regenerating).

Read the full breaking-changes list in [CHANGELOG.md](https://github.com/provide-io/pyvider-cty/blob/main/CHANGELOG.md) before upgrading — each entry there carries its own migration note. For the underlying rationale and the complete function-by-function and surface-by-surface parity status, see [Comparison with go-cty](go-cty-comparison.md).

## Earlier releases

See [CHANGELOG.md](https://github.com/provide-io/pyvider-cty/blob/main/CHANGELOG.md) for the history before 0.5.0.
