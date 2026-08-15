# go-cty Parity Tracker

Living document. Updated as work lands — do not let it drift.

| | |
|---|---|
| **go-cty baseline** | `v1.19.0-1-g0d1eb26` (`/Users/tim/code/tf/go-cty`) |
| **pyvider-cty baseline** | `main @ fa0ba5e` |
| **Last full review** | 2026-08-15 |
| **Next review trigger** | go-cty tags v1.19.1+, or any phase completing |

---

## Status at a glance

| Phase | Scope | State |
|---|---|---|
| 0 | Unknown-marker fixes (#3, PR #4) | ✅ Done |
| 1 | Correctness bugs | ✅ Done except #16, which is sequenced behind a pyvider change |
| 2 | Verification infrastructure (tofusoup) | ⬜ Not started |
| 3 | Foundations | ⬜ Not started |
| 4 | Marks, properly | ⬜ Not started |
| 5 | Breadth | ⬜ Not started |
| 6 | Refinements | ⬜ Not started |
| 7 | Architecture | ⬜ Not started |
| — | Docs (#13) | 🔄 Continuous |

---

## Working agreement

- **All work lands on the single local branch `feat/go-cty-parity`.** Not one branch per issue — splitting the work across branches complicates the review.
- **Nothing is pushed and no PR is opened.** The branch stays local until the whole implementation is done.
- **Do not close issues automatically.** No `Closes #N` in commit messages.
- **An adversarial review happens after implementation, performed by someone other than the implementing agent.** Commit in coherent, self-describing increments so that review has something readable to work against.

## Verify before filing

Two of the five items in phase 1 turned out not to be gaps at all. Both were filed from reading go-cty — its CHANGELOG in one case, the shape of its source in the other — rather than from running pyvider:

- The three `Contains` / `Merge` / `element` "behavioural fixes" described bugs **go-cty** had. pyvider is an independent implementation and never had them.
- msgpack `±Inf` was filed because `codec.py` has no infinity branch. It does not need one; Python reaches the same bytes implicitly.

Meanwhile the sweep that disproved them turned up a real bug nobody had listed (`contains` returning a definite `False` for partially-unknown collections).

**So: run the behaviour before believing the gap.** Absence of a code path in pyvider is not absence of the behaviour, and a go-cty bugfix is not evidence pyvider shares the bug. This applies directly to the remaining phases — several items in #14 were filed from grep results and should be re-checked empirically before any work starts on them.

## Structural notes

Two things shape the ordering below.

**Issue #14 is not a unit of work.** It is ten unrelated items grouped for filing convenience. Each is scheduled individually in the phase where its dependents need it. When closing #14, close it as a tracker — the items land across phases 1, 3, 4, 5, 6, and 7.

**tofusoup#2 is a different repository.** It runs in parallel with phase 1, not after it.

---

## Phase 1 — correctness bugs

Wrong today. Verifiable with in-repo tests. No dependencies.

- [x] **#5 — stdlib functions silently drop marks**
  `functions/_marks.py` adds `@preserve_marks`, applied to all 68 exported functions. Collects marks deeply (matching go-cty's `UnmarkDeep`), calls the impl with unmarked arguments, re-applies the union to the result.
  Tests: `tests/functions/test_mark_propagation.py` — 119 cases, parametrized over every export, plus nested/deep cases and a fixture-completeness guard so a new export cannot skip coverage.
  Widened `CtyValue.with_marks` to `AbstractSet[Any]` (it always accepted frozensets; the annotation was too narrow) and dropped the now-redundant `type: ignore` in `object.py:129`.
  The decorator is the **seam** #12 fills in behind later.
- [x] **#15 — collection `validate()` discards marks on already-validated elements**
  Root cause was not the containers: they delegate to `self.element_type.validate(item)`, and the *element* type unwrapped `.value` and rebuilt a fresh `CtyValue`. `CtyObject` was the only type re-applying marks, by hand.
  `validation/marks.py` adds `@preserves_marks`, applied to all ten `validate` implementations outermost of `@with_recursion_detection`. Stated once, like `CtyType.unknown_marker`, rather than ten times. `CtyObject`'s hand-rolled copy deleted.
  Typed as an identity on the function type (`TypeVar` bound to `Callable`), so each `validate` keeps its own signature — a concrete signature flattens `CtyValue[str]` / `CtyValue[tuple[T, ...]]` / `CtyValue[Any]` together and shifts inference at every call site in the package.
  Tests: `tests/types/test_validate_preserves_marks.py`, 12 cases across every container and primitive. The `listval` workaround is gone from the #5 tests, which now use `validate()`.
- [ ] **#16 — `cty_to_msgpack` silently drops marks instead of refusing to serialize**
  Found verifying #15. go-cty errors (`marshal.go:49`, "value has marks, so it cannot be serialized"); pyvider writes the value and discards the flag. Pre-existing, but #15 widens the exposure by making nested marks real.
  **Decision: match go-cty. Not blocked on #8.** Sensitivity reaches Terraform through `tfplugin6.Schema.Attribute.sensitive` (field 7), not through the value — `DynamicValue` carries only `msgpack`/`json` and has no mark channel. So no caller on this path needs `UnmarkDeepWithPaths` to comply.
  **Sequencing: the pyvider-side change must land first.** `pyvider/conversion/marshaler.py:118` applies schema marks and serializes on the next line, so those marks are already discarded; with a strict serializer it becomes a crash on every sensitive attribute. Remove that one call.
  **Do not remove `_apply_schema_marks_iterative` itself.** It has two other call sites — `plan_resource_change.py:237` and `apply_resource_change.py:268` — both *inbound*, after `unmarshal`. Marks cannot cross the wire, so the handlers re-derive them from the schema and hand the marked value to the resource as `ctx.config_cty`. `pyvider-components/tests/resources/test_tdd_resource_context_contract.py:139` is a live contract on that path.
  **Blast radius, from a full `/Volumes/data/pyv` sweep:** `pyvider` is the only production consumer that marks. `pyvider-components` reads marks in tests on the inbound path. `tofusoup`'s `*_with_marks` tests assert in memory and never serialize a marked value. Nothing else marks. One line of production code changes outside this repo.
  Breaking change for any other caller that marks and serializes: needs a release note, not a patch release.
- [x] **~~#14 item 9 — msgpack `±Inf` handling~~ — already correct**
  Filed because `codec.py` has no infinity branch. It does not need one: `float(Decimal("Infinity"))` is already `inf`, and msgpack encodes that as float64 infinity — byte for byte what go-cty's explicit `EncodeFloat64(math.Inf(...))` produces (`cb7ff0000000000000` / `cbfff0000000000000`). Go needed the special case; Python does not.
  Pinned with `tests/codec/test_msgpack_infinity.py` so the encoding cannot drift onto the large-number-as-string path.
- [x] **~~Split out of #9 — behavioural fixes to shipped functions~~ — not needed**
  All three were derived from go-cty's CHANGELOG rather than from running pyvider, and all three were already correct on `main`. pyvider's implementations are independent re-writes; they never had go-cty's specific bugs.
  - `Contains` with a null second argument — already accepted, finds null elements correctly
  - `Merge` on all-null args — already returns `{}` without raising
  - `element` negative index into a tuple — already returns the right element
  **Lesson for the rest of this work: test the behaviour before filing it as a gap.** A CHANGELOG entry describes a bug *go-cty* had, which says nothing about whether a separate implementation shares it.
- [x] **`contains` returned a definite `False` for partially-unknown collections**
  Found by the sweep above — not on any list. An unknown element could still be the value being searched for, so a miss is undecided rather than false. An exact match still wins outright. Mirrors go-cty's `ContainsFunc`.
  Same class as #5 and #15: claiming certainty that is not there.
- [x] **#17 — `MAX_VALIDATION_DEPTH` advertised a depth it could not deliver**
  **Closed.** Root cause measured, not guessed: validation costs exactly **two Python frames per level** (the `with_recursion_detection` wrapper, then the `validate` it wraps) — stack depth at the innermost leaf is `2 × levels + 2`. Against CPython's 1000-frame limit, 500 levels needs the entire stack with nothing left for the caller, so the real ceiling was **496** and input nested 497–500 deep returned a silent unknown from inside the documented limit.
  The limit is now **derived**: `(sys.getrecursionlimit() − VALIDATION_STACK_MARGIN) // FRAMES_PER_VALIDATION_LEVEL`, giving 480 at the default recursion limit — 480 promised, 480 delivered, verified by binary search. It tracks a raised recursion limit (3000 → 1480, also verified) and is pinnable via `PYVIDER_CTY_MAX_VALIDATION_DEPTH` through the existing `CtyConfig`/`env_field` pattern. Derived per context, so it follows a limit changed after import.
  The guard now stops *before* Python does, so exceeding the limit is a controlled unknown rather than a `RecursionError` thrown in the caller's stack. The attribution threshold for owning a `RecursionError` is taken from the live limit rather than its own constant, so the two cannot drift.
  Found while fixing it: **`pyvider.cty.context` declared a second `MAX_VALIDATION_DEPTH = 500`** that governed nothing — its depth mechanism (`deeper_validation`, `get_validation_depth`) has no callers in the validator, only its own tests — yet it was the constant the documentation pointed readers at. Two same-named constants that disagree is how the 500 came to be believed. Now re-exported from the real one.
  Four documentation files that promised a flat 500, one of them stating the limit was *not* runtime-configurable, corrected.
  Pre-existing, not a regression from this branch — verified against a clean `gh-origin/main` worktree before any of it was touched.
- [x] **Set elements carried marks; go-cty forbids that**
  `CtySet.validate` now deep-unmarks each element and hoists the union onto the set, as `SetVal` does (`cty/value_init.go:270`). go-cty goes further and panics on hashing a marked element (`cty/set_internals.go:39`) rather than trust the invariant to callers.
  Not cosmetic: de-duplication keys on the element's value, which is mark-blind, so a sensitive element colliding with an equal unmarked one was overwritten and its mark lost outright. **Behavioural change** — `set.value[i].marks` is now always empty and the marks are on the set.
- [x] **`equal` / `not_equal` decided comparisons they could not see**
  Same class as `contains`, found by sweeping for it after fixing that one. Both tested only top-level `is_unknown`, so an object with an unknown attribute reached `==` and got a plain bool: `equal(obj{a: unknown}, obj{a: "z"})` returned a definite `False` and `not_equal` a definite `True`, when that attribute could still resolve to `"z"`.
  Only objects were affected, and the reason is worth remembering: **containers are inconsistent about propagating element unknowns**. A list built from an unknown element reports itself unknown; an object with an unknown attribute does not. Anything reading `is_unknown` to decide whether a value is usable inherits that inconsistency.
  Swept the rest of the stdlib for the same shape. No other case found: the other `is_unknown` guards are conservative (unknown in, unknown out), `index` is index-by-key and matches go-cty's `IndexFunc`, and `distinct` on objects fails on hashability, which is a separate pre-existing limit.
- [x] **Three-valued equality — `CtyValue.equals()`, go-cty's `Value.Equals`**
  `==` returns a plain bool, so it must decide even when the data cannot support a decision. `equals()` can return unknown, and `contains`, `equal` and `not_equal` now all route through it instead of each carrying their own approximation.
  This replaces the earlier conservative stopgap, which called anything containing an unknown undecided. That was safe but needlessly vague: a known attribute that differs still rules a value out no matter what the unknown resolves to. `obj{a: unknown, b: "x"} == obj{a: "z", b: "DIFFERENT"}` is now a definite `False` where it used to be unknown, while `obj{a: unknown, b: "x"} == obj{a: "z", b: "x"}` stays correctly undecided.
  Covers the ordering go-cty is careful about — unknowns are examined *before* nulls, because an unrefined unknown may yet become null and nulls of any type are equal — plus mark propagation (compare unmarked, union onto the result, top-level-only marks when exactly one side is null), dynamic unwrapping, and structural recursion for list, tuple, set, map and object.
  **Not implemented**: go-cty disqualifies some comparisons early from an unknown's refinement bounds (`Value.Range().Includes`). pyvider.cty has only partial refinement support, so those return unknown here. Safe direction — vaguer, never wrong.
  `CtyValue.is_wholly_known()` (go-cty's `Value.IsWhollyKnown`) landed alongside it and remains the right test wherever a value has to be *usable*, as opposed to compared.
- [ ] **`contains` on a null collection returns unknown; go-cty raises**
  `collection.go:340`, "cannot search a nil list or set". Deliberately not fixed with the above: turning a return into a raise is a behavioural break that belongs with #16's strictness work. Much weaker case than #16 — nothing leaks, the caller just gets a vaguer answer.

## Phase 2 — verification infrastructure

Runs parallel with phase 1. Repo: `provide-io/tofusoup` (`/Volumes/data/pyv/tofusoup`).

- [ ] **tofusoup#2a — bump go-cty 1.14.1 → 1.19.x**
  `src/tofusoup/harness/go/soup-go/go.mod:13`. Cheap. Until this lands, every differential result is measured against a five-version-stale oracle.
- [ ] **tofusoup#2b — `soup-go cty call` subcommand**
  Highest-leverage single addition. Covers ~70 existing functions plus everything still to port. Emit `{type, value, marks}` so #5 becomes assertable against Go rather than against a reading of the source.
- [ ] **Regenerate pyvider fixtures from the harness**
  `compatibility/tests/fixtures/go-cty/*.msgpack` is 17 checked-in binaries with no Go-side generator in the repo. Cannot be rebuilt when go-cty moves.

## Phase 3 — foundations

Not user-visible. All of it unblocks later phases.

- [ ] **#6 — `walk` / `transform` / `deep_values`**
  Blocks phase 4 entirely and `UnknownAsNull`.
  Watch: set elements use an `IndexStep` keyed by the element value; do not propagate parent marks down to child callbacks (go-cty 1.15.0 fixed exactly that bug).
- [ ] **#14 item 6 — `ctystrings`**
  `NormalizeString` + `SafeKnownPrefix`. Blocks `strlen` (#9) and `StringPrefix` (#10).
  ⚠️ Requires the Unicode-segmentation dependency decision — see below.
- [ ] **#14 item 1 — `PathSet`**
  Needed by `MarkWithPaths` / `UnmarkDeepWithPaths` in phase 4. Requires `CtyPath` to be hashable — verify.
- [ ] **#14 item 4 — `RawEquals`**
  Small. Tests in every later phase want it. `__eq__` cannot serve both the cty-semantic and structural-identity roles.

## Phase 4 — marks, properly

- [ ] **#8 — deep mark operations + a real `ValueMarks` type**
  Unblocked by #6 and `PathSet`. Keep go-cty's fast paths: identity return when nothing is marked, no-op on empty path-marks.
- [ ] **#14 item 7 — `IndexStep.Apply` through a set** (go-cty 1.18.0)
  Belongs here: #6's traversal is what produces these paths.
- [ ] **#14 item 3 — `UnknownAsNull`**
  Including the 1.16.4 mark-preservation behaviour.

## Phase 5 — breadth

Mutually independent. Parallelizable across whoever is free.

- [ ] **#9 — remaining stdlib ports**
  bool ops (`not`/`and`/`or`), five set ops, `range`, `assertnotnull`, `strlen` (needs ctystrings), generalized `MakeToFunc`.
- [ ] **#7 — `format` / `formatlist`**
  Largest single port. Hand-write the verb tokeniser from `format_fsm.rl`; do not bend Python `%`/`str.format` (no positional `%[2]s`, wrong number rendering). Verify numeric verbs against the Go harness.
- [ ] **#11 — `cty/json` value codec**
  `Marshal` / `Unmarshal` / `ImpliedType`. Not the same as the `jsonencode`/`jsondecode` functions.
- [ ] **#14 item 8 — capsule ops gaps**
  `GoString`, `TypeGoString`, `RawEquals`, `ExtensionData`, split `ConversionFrom`/`ConversionTo` (needed for the 1.16.0 capsule↔capsule fallback).

## Phase 6 — refinements

- [ ] **#10 — `Refine` builder + consistency assertions**
  Needs `ctystrings` from phase 3 for `StringPrefix` vs `StringPrefixFull`.
  The validation is the point, not the API shape: inconsistent bounds, refining a known value, prefix-on-a-number, narrowing-never-widening.
- [ ] **#14 item 2 — `Value.Range` / `ValueRange`**
  Needs #10.

## Phase 7 — architecture

- [ ] **#12 — the `cty/function` framework**
  `Function`, `Spec`, `Parameter`, `Unpredictable`, `ArgError`, `RefineResult`. Migrate stdlib behind the existing public names. Absorbs #5's decorator.
- [ ] **#14 item 5 — `Type.TestConformance`**
  Distinct from the existing `usable_as` (= go-cty `UsableAs`): allows `DynamicPseudoType` wildcards, returns path-tagged errors rather than a bool.

## Continuous

- [ ] **#13 — docs: `docs/reference/go-cty-comparison.md` parity matrix**
  Five rows currently overstate coverage (Marks, Refined Unknowns, Capsule Types, Standard Library, JSON). Eight features have no row at all.
  **Update the relevant row as each phase lands.** Doing it once at the end guarantees it goes stale again. Add the go-cty version the matrix was last checked against.

---

## Release gate — must be done before this branch ships

This branch carries a **breaking behavioural change**: `CtySet.validate` hoists element marks onto the set, so `set.value[i].marks` is now always empty and sensitivity has to be read off the set itself. go-cty behaves the same way (`SetVal`), but any consumer reading marks per element would silently conclude "not sensitive".

Every consumer in the workspace declares an **unbounded** dependency, with no `tool.uv.sources` override:

| Repo | Declares |
|---|---|
| `pyvider` | `pyvider-cty>=0.4.0` |
| `pyvider-components` | `pyvider-cty>=0.4.0` |
| `pyvider-hcl` | `pyvider-cty>=0.4.0` |
| `tofusoup` | `pyvider-cty>=0.4.0` |
| `provide-workspace` | `pyvider-cty>=0.4.0` |

So the moment `0.5.0` is published, all five absorb the change with no signal. A security review confirmed no consumer currently reads sensitivity off collection *elements*, so today the blast radius is zero — but the pin is what makes it silent, and that outlives the audit.

- [ ] **Cap the five consumers at `>=0.4,<0.5` before publishing `0.5.0`**, then bump each one deliberately.
  Not done on this branch on purpose: the consumer repos are all sitting on unrelated branches (`adminy/main`, `chore/use-reusable-release`), and a cap committed to a branch that never merges is worse than no cap, because it looks done. Apply this to whichever branch actually ships.
- [ ] **Cut `0.4.0` → `0.5.0`**, not a patch. The set change is breaking, and the mark fixes change what `validate` returns for every marked input.
- [ ] Only `pyvider-cty` needs a release. Nothing else in the workspace changes.

---

## Open decisions

### 1. When does #12 (function framework) land?

Real rework tension. If the framework lands *after* #7 and #9, those functions get written hand-rolled and then migrated.

**Current plan:** make #5's decorator the seam. Define the wrapper interface in phase 1, write everything in #7/#9 against it, let #12 fill in behind it in phase 7 without touching function bodies. Correctness lands immediately; rework avoided. Cost: the decorator is slightly over-designed for what phase 1 alone needs.

**Alternative:** do the big refactor up front — moves #12 to phase 3 and delays phases 4–6 by its duration.

**Status:** unresolved. Defaulting to the seam approach.

### 2. Unicode segmentation dependency (gates phase 3 item 2)

`Strlen` and `SafeKnownPrefix` need real UAX#29 grapheme cluster segmentation. go-cty tracks Unicode 17 on Go 1.27+, Unicode 15 below.

Options: take a dependency (`uniseg`-equivalent), vendor the tables, or document an explicit deviation and use code points.

This is a question about pyvider-cty's dependency posture more than a technical one. Gates `strlen` (#9) and `StringPrefix` (#10).

**Status:** unresolved. Needs an owner decision.

---

## Confirmed parity (no action)

Verified accurate against go-cty `v1.19.0-1-g0d1eb26`:

primitives · List/Map/Set · Object/Tuple · Dynamic · Capsule (base) · optional object attributes incl. wire form · null/unknown semantics · shallow marks · refined-unknown **data model and msgpack `0x0c` wire codec** (all six keys) · msgpack marshal/unmarshal incl. big-int-as-string (1.14.4) · type wire JSON encode/decode · `convert` · `unify` · path steps GetAttr/Index/Key with `apply` and `apply_type` · Go-native bridge analog (`raw_to_cty` / `cty_to_native`) · cross-language fixture harness

## Not applicable

- **`cty/gocty`** — Go reflection bridge. Python analog is `conversion/raw_to_cty.py` + `conversion/adapter.py`, already present.

---

## Issue index

| Issue | Title | Phase |
|---|---|---|
| [#5](https://github.com/provide-io/pyvider-cty/issues/5) | stdlib functions silently drop marks | 1 |
| [#6](https://github.com/provide-io/pyvider-cty/issues/6) | Walk / Transform / DeepValues | 3 |
| [#7](https://github.com/provide-io/pyvider-cty/issues/7) | Format and FormatList | 5 |
| [#8](https://github.com/provide-io/pyvider-cty/issues/8) | Deep mark operations | 4 |
| [#9](https://github.com/provide-io/pyvider-cty/issues/9) | Remaining stdlib functions | 1 (fixes) + 5 (ports) |
| [#10](https://github.com/provide-io/pyvider-cty/issues/10) | Refine builder API | 6 |
| [#11](https://github.com/provide-io/pyvider-cty/issues/11) | cty/json value codec | 5 |
| [#12](https://github.com/provide-io/pyvider-cty/issues/12) | cty/function framework | 7 |
| [#13](https://github.com/provide-io/pyvider-cty/issues/13) | docs: parity matrix overstates | continuous |
| [#14](https://github.com/provide-io/pyvider-cty/issues/14) | Assorted core gaps (tracker) | 1,3,4,5,6,7 |
| [#15](https://github.com/provide-io/pyvider-cty/issues/15) | `validate()` discards element marks | 1 |
| [#16](https://github.com/provide-io/pyvider-cty/issues/16) | msgpack silently drops marks | 1 |
| [tofusoup#2](https://github.com/provide-io/tofusoup/issues/2) | go-cty bump + harness surface | 2 |

### #14 item → phase map

| Item | Phase |
|---|---|
| 1. `PathSet` | 3 |
| 2. `Value.Range` / `ValueRange` | 6 |
| 3. `UnknownAsNull` | 4 |
| 4. `RawEquals` | 3 |
| 5. `Type.TestConformance` | 7 |
| 6. `ctystrings` | 3 |
| 7. `IndexStep.Apply` through a set | 4 |
| 8. Capsule ops gaps | 5 |
| 9. msgpack infinity | 1 |
| 10. `ValueMarks.Has` / `Insert` | 4 (folded into #8) |

---

## Changelog

| Date | Change |
|---|---|
| 2026-08-15 | Initial review against go-cty `v1.19.0-1-g0d1eb26`. Filed #5–#14 and tofusoup#2. PR #4 merged (rebase), closing #3. |
| 2026-08-15 | #5 implemented on `feat/go-cty-parity` (local, unpushed). Filed #15 — collection `validate()` discards element marks — discovered while testing #5. |
| 2026-08-15 | #15 implemented. Filed #16 — msgpack silently drops marks where go-cty errors — discovered verifying #15. Marks now survive validation at every level; they still do not survive serialization, which is #16. |
| 2026-08-15 | #16 decision recorded: match go-cty and raise. Established that sensitivity travels via the wire *schema*, not the value, so #16 does not depend on #8 as first assumed — but pyvider's `_apply_schema_marks_iterative` is dead work that must be deleted first or the new error crashes every sensitive attribute. |
| 2026-08-15 | Phase 1 closed except #16. Adversarial review of the branch found a third mark-dropping path (the recursion guard's early exits); fixed. Filed #17 — `MAX_VALIDATION_DEPTH` is 500 but validation crashes above 495, pre-existing and verified against a clean `gh-origin/main` worktree. Review prompt kept at `.provide/ADVERSARIAL-REVIEW-PROMPT.md`. |
| 2026-08-15 | Three-valued equality implemented as `CtyValue.equals()` (go-cty `Value.Equals`), and `contains`, `equal` and `not_equal` all moved onto it — three approximations of the same comparison replaced by one implementation, the same consolidation that fixed the mark bugs. It is strictly more precise than the conservative stopgap it replaces: a known attribute that differs rules a value out even when a sibling attribute is unknown. Not implemented: refinement-bound disqualification (`Value.Range().Includes`), pending fuller refinement support — those return unknown, which is the safe direction. |
| 2026-08-15 | #17 closed. The limit is derived from the recursion limit rather than asserted as a flat 500, because the frame cost per level (two, measured) makes 500 undeliverable under CPython's 1000-frame default. 480 promised and 480 delivered; tracks a raised recursion limit; pinnable via `PYVIDER_CTY_MAX_VALIDATION_DEPTH`. Also removed a **second `MAX_VALIDATION_DEPTH = 500`** in `pyvider.cty.context` that governed nothing but was the one the docs cited — the same duplicate-source-of-truth pattern that produced the mark bugs, found a third time. Four docs corrected. `equal`/`not_equal` fixed for nested unknowns in the same session, found by sweeping for the `contains` bug's shape rather than waiting for a report. |
| 2026-08-15 | Fourth round, security-focused, against the whole branch. Differential matrix over 51 mark-flow scenarios, run against both `gh-origin/main` and HEAD with an independent detector: base lost the mark in **34 of 51**, HEAD in **0**. No declassification found, so no security finding. It did disprove a claim this branch had written down — the memo was justified as "CtyValue is immutable, so the answer cannot go stale", but freezing an attrs class freezes the *reference* to the payload, not the payload, and map/object payloads are plain dicts. A stale under-reporting memo was reproducible by in-place mutation. Rather than assert an immutability nothing enforces, the walk now reports whether it saw a mutable container anywhere in the subtree and the memo is skipped if it did. The staleness class is gone by construction; the 200k-list memo is unaffected, and dict-payload values re-walk at 6-18 us for realistic sizes. Also recorded the release gate: the set change is breaking and all five consumers pin unbounded. |
| 2026-08-15 | Third review round (`/code-review high`), seven findings, all seven reproduced and fixed. Two were performance regressions introduced by the mark work itself: `preserve_marks` deep-walked every argument *before* its no-marks fast path, taking `length()` on a 200k list from 0.005 ms to 41 ms **per call**; and the guard's stop path re-walked the input at every unwinding frame, making abort O(depth x size). Both are now fixed by memoizing the deep walk on the value (`CtyValue._deep_marks`) — 20 calls went 799 ms to 40 ms, and a single fresh walk is back to the pre-regression 41 ms. The walk itself was consolidated into `pyvider.cty.marks`: **three divergent copies of it were the root cause of this entire class of bug**, each having guessed at a different set of container types. Also: set elements no longer carry marks (go-cty parity, above); `contains` reads unknown deeply; the blanket `except RecursionError` is now scoped by depth so unrelated recursion bugs surface instead of becoming an unknown; a log field that was always empty now reports depth; and a comment justifying deleted mark-restoring code named only one of the two mechanisms that replaced it. |
| 2026-08-15 | Second adversarial review round. Found the deep-mark walk matched only `tuple` and `dict`, so it skipped every **set** — a validated `CtySet` stores a `frozenset`. Present in two places, and the one the reviewer did not reach was the worse of the two: `functions/_marks.py` is the production path, where a sensitive set element was dropped from the result of every stdlib call *and* handed to the implementation the strip was meant to shield. Also found the guard collected marks only when its input was already a `CtyValue`, losing them for the raw `list`/`dict` inputs `validate` is normally given. Both fixed; the collector is now iterative, because it runs precisely when the value is too deep or too cyclic to recurse over. #17's crash half fixed in the same pass. |
