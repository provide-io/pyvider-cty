# go-cty Parity Tracker

Living document. Updated as work lands — do not let it drift.

| | |
|---|---|
| **go-cty baseline** | `v1.19.0-1-g0d1eb26` (`/Users/tim/code/tf/go-cty`) |
| **pyvider-cty baseline** | `main @ fa0ba5e` |
| **Last full review** | 2026-08-16 |
| **Next review trigger** | go-cty tags v1.19.1+, or any phase completing |

---

## Status at a glance

| Phase | Scope | State |
|---|---|---|
| 0 | Unknown-marker fixes (#3, PR #4) | ✅ Done |
| 1 | Correctness bugs | ✅ Done, #16 included (paired change landed in `pyvider`) |
| 2 | Verification infrastructure (tofusoup) | ✅ Done — go-cty 1.19 + `soup-go cty call` oracle |
| 3 | Foundations | ✅ Done — 3 of 5 items were not gaps; `SafeKnownPrefix` deferred on the Unicode decision |
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
- [x] **#16 — `cty_to_msgpack` silently drops marks instead of refusing to serialize**
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
- [x] **Five stdlib functions answered differently from go-cty** — *breaking*
  Found by the oracle, not by reading: `regex`, `regexall`, `indent`, `flatten`, `chunklist`.
  - `regex`/`regexall` took `(string, pattern)` where go-cty takes `(pattern, string)`. Both are strings, so a call written for one order type-checks against the other and silently returns a wrong answer.
  - `regex` returned the whole match and discarded capture groups. go-cty's result type *is* the capture groups (`regexPatternResultType`): no groups → the whole match as a string; unnamed groups → a tuple in order; named groups → an object; mixing the two kinds → refused. A group that did not participate is null, not `""`.
  - `regex` returned `""` for a non-match where go-cty raises. `""` is a legitimate match for plenty of patterns, so the caller could not tell the two apart.
  - `indent` took a prefix *string* where go-cty takes a *count of spaces*, and indented the first line, which go-cty deliberately does not — the function exists to line a multi-line value up under something already on the first line. Deliberate divergence kept: a negative count raises cleanly rather than reproducing go-cty's `strings.Repeat` panic.
  - `flatten` returned a `list` with a unified element type where go-cty returns a `tuple`, which is why go-cty need not widen a mixture to dynamic. It also flattened one level where go-cty recurses, dropped null elements go-cty keeps, and raised on a non-sequence element go-cty passes through.
  - `chunklist` erased the chunk element type to dynamic (go-cty's return type is `cty.List(args[0].Type())`), and refused a size of 0 that go-cty reads as one chunk holding everything. Kept as a superset: a tuple argument is accepted, with its element types unified, where go-cty's `list(dynamic)` parameter refuses one outright.

  Zero callers anywhere in the workspace, so nothing broke — but all of it is a breaking API change for anyone outside it, and belongs in the same release as the other three.
  Now covered by `tests/compatibility/test_stdlib_oracle.py`, which compares **answers** rather than wire bytes: 27 calls agreeing on type and value, plus 5 that both implementations must refuse. That file is the thing that was missing. Every one of these divergences survived because every test asserted what the code did, so nothing could notice.

  Three pre-existing gaps surfaced while implementing them. None is fixed here; each is wider than this item.
  - [ ] **`CtyObject.validate` refuses a null attribute** unless it is declared optional. go-cty has no such rule — nullability is not part of an object type there. This is not hypothetical: a named capture group that does not participate in a match is null, so `regex("(?P<x>a)|(?P<y>z)", "a")` crashed until the result was built directly rather than through `validate`. Declaring the attributes optional is not the fix, because that adds go-cty's third wire element to the type. Changing the rule touches every object validation in the package.
  - [ ] **Python `re` is not RE2.** `regex(r"(a)\1", "aa")` and `regex("a(?=b)", "ab")` both succeed here and are *refused* by go-cty ("invalid escape sequence in \1", "invalid or unsupported Perl syntax in (?="). Superset, so patterns valid in both behave identically — but a provider whose pattern is only tested here can ship one Terraform then rejects.
  - [ ] **A `CtySet` cannot hold a list**, because a `CtyValue` with a list payload is unhashable. go-cty has no such limit.

## Phase 2 — verification infrastructure

Runs parallel with phase 1. Repo: `provide-io/tofusoup` (`/Volumes/data/pyv/tofusoup`).

- [x] **tofusoup#2a — bump go-cty 1.14.1 → 1.19.x** — *done*
  `go.mod:13` reads `github.com/zclconf/go-cty v1.19.0`, matching the reference checkout (`v1.19.0-1-g0d1eb26`, one commit ahead of the tag). The "five-version-stale oracle" warning this entry used to carry was itself stale; every differential result on this branch is measured against 1.19.0.
- [x] **tofusoup#2b — `soup-go cty call` subcommand** — *done, and it exposes 74 of go-cty's 83 stdlib functions*
- [ ] **tofusoup#2c — the nine stdlib functions `cty call` cannot reach**
  Enumerated from `var *Func = function.New` across `cty/function/stdlib/`, minus the two that are the same function under a different Go var name (`AbsoluteFunc` is `abs`, `ReverseFunc` is `strrev`):
  `assertnotnull`, `byteslen`, `bytesslice`, `sethaselement`, `setsymmetricdifference`, `strlen`, `tobool`, `tonumber`, `tostring`.
  **Seven of those nine are implemented here and therefore have no differential verification at all** — `byteslen`, `bytesslice`, `sethaselement`, `setsymmetricdifference`, `tobool`, `tonumber`, `tostring`. They are checked against a reading of go-cty's source, which is precisely the method that produced the two non-existent gaps recorded at the top of this file. The other two, `strlen` and `assertnotnull`, are not ported yet.
  The sweep reports 100% of what the harness exposes, so this gap is invisible from inside pyvider-cty. That is the same shape as the `NAME_MAP` bug: coverage measured against the wrong denominator.
- [ ] **Regenerate pyvider fixtures from the harness**
  `compatibility/tests/fixtures/go-cty/*.msgpack` is 17 checked-in binaries with no Go-side generator in the repo. Cannot be rebuilt when go-cty moves.

## Phase 3 — foundations

Not user-visible. All of it unblocks later phases.

**Three of the five items were not gaps.** Each was filed from reading go-cty's public API rather than from running pyvider — the same mistake the "Verify before filing" section above was written about, repeated verbatim one phase later. Each cut below records what was run to disprove it, so nobody re-files them.

- [x] **#6 — `walk` / `transform` / `deep_values`** — landed in `src/pyvider/cty/walk.py`
  Real, and already being paid for badly: pyvider's `conversion/marshaler.py` hand-rolls two iterative deep traversals of a value tree (`_apply_schema_marks_iterative`, `_unmark_deep`), and its own comment records that a recursive version "did raise RecursionError at a nesting depth pyvider-cty advertises as supported". So all three entry points are iterative, and a 400-deep test pins it.
  Shaped for Python rather than transliterated: `deep_values` is a generator, which is what go-cty itself recommends once Go grew iterators. `walk` exists only for the pruning `deep_values` cannot express.
  Both watch-items held. Set elements are addressed by themselves — go-cty puts that on `IndexStep`, pyvider on `KeyStep`, because pyvider split go-cty's one index step into an int-keyed and a key-keyed one. Parent marks cannot reach child callbacks here, since marks live on the value and a child is a separate value; pinned anyway, because go-cty 1.15.0 shows the bug is reachable by other designs.
  Also required extending `KeyStep` to apply through a set — otherwise `walk` emits set-element paths it cannot then follow. That is #14 item 7, landed early because it is a prerequisite rather than a phase-4 nicety.
- [x] **#14 item 1 — `PathSet`** — cut; `CtyPath` made hashable instead
  go-cty needs a dedicated type with crc64 hashing rules only because Go cannot hash a slice. Python's `set[CtyPath]` is the same thing once `CtyPath` is frozen, which it now is (`steps` is a tuple; the converter still accepts the list callers pass). Verified before: `hash(CtyPath.get_attr("a"))` raised `unhashable type`.
  Its only stated dependent — `MarkWithPaths` / `UnmarkDeepWithPaths` in phase 4 — rests on an assumption this document already retracted: sensitivity reaches Terraform through the wire schema, not through the value. `PathSet` also has zero callers inside go-cty itself.
- [x] **#14 item 4 — `RawEquals`** — cut; already present under two names
  The item's own justification was that "`__eq__` cannot serve both the cty-semantic and structural-identity roles". pyvider already split them: `__eq__` is the structural one (`marked != unmarked`, `null(string) != null(number)`, `unknown == unknown`), and `.equals()` returns the three-valued cty answer. Landed in `f4a1d90`, before the item was filed.
- [x] **#14 item 6 — `NormalizeString`** — cut; the behaviour is already there
  go-cty's own docs say `Normalize` "achieves the same effect as wrapping a string in a value using `cty.StringVal` and then unwrapping it again" — i.e. cty normalizes at construction. pyvider does too, deliberately: `types/primitives/string.py:51`, `types/collections/map.py:71,98`, `conversion/raw_to_cty.py:245`. Verified: NFD `"é"` is stored as one code point, compares equal to the precomposed form, and collides with it as a map key — matching the oracle.
  The standalone helper exists in go-cty because Go has no stdlib NFC and needs `golang.org/x/text`. Python's is `unicodedata.normalize("NFC", s)`. A wrapper would add a name, not a capability.
- [ ] **#14 item 6 — `SafeKnownPrefix`** — still open, still blocked
  The half of `ctystrings` that is a real gap. Needs UAX#29 grapheme segmentation. Blocks `strlen` (#9) and `StringPrefix` (#10).
  ⚠️ Requires the Unicode-segmentation dependency decision — see below. **Deferred deliberately** (2026-08-16): nothing exports `strlen` today, so nothing is blocked by waiting.

## Phase 4 — marks, properly

- [ ] **#8 — deep mark operations + a real `ValueMarks` type**
  Unblocked by #6. `PathSet` was cut in phase 3 — a `set[CtyPath]` is the Python equivalent now that `CtyPath` is hashable — so `MarkWithPaths` / `UnmarkDeepWithPaths` need no new container. Re-check whether they are wanted at all before building them: sensitivity reaches Terraform through the wire schema, not the value. Keep go-cty's fast paths: identity return when nothing is marked, no-op on empty path-marks.
- [x] **#14 item 7 — step through a set** (go-cty 1.18.0) — landed in phase 3
  Landed early because #6's traversal is what produces these paths, so `walk` could not emit an applicable set-element path without it. On `KeyStep` rather than `IndexStep`, because pyvider split go-cty's single index step in two.
- [ ] **#14 item 3 — `UnknownAsNull`**
  Including the 1.16.4 mark-preservation behaviour.

## Phase 5 — breadth

Mutually independent. Parallelizable across whoever is free.

- [ ] **#9 — remaining stdlib ports**
  - [x] **bool ops, the five set ops and `range`.** These were exactly what `tests/compatibility/test_stdlib_sweep.py` skipped, and the sweep now has no skips at all. Exported as `and_fn` / `or_fn` / `not_fn` / `range_fn`, since all four names are Python keywords or builtins — the same reason `max_fn` carries a suffix, and more fuel for the naming decision below.
    `and` and `or` deliberately do **not** short-circuit: `and(unknown, false)` is unknown, not false, because go-cty's framework returns an unknown result for any unknown argument before the implementation is reached and so never notices that one operand already settles it. Answering `false` here while Terraform answers unknown would be a plan that disagrees with itself.
    The set ops follow go-cty's `allowUnknowns` split — only union tolerates an unknown element, because for the others learning what it is can remove elements or change the result's length. `setsymmetricdifference` and `sethaselement` are ported too, though the oracle harness does not expose them, so they are checked against `set.go` rather than against a running go-cty.
    Two deliberate divergences, both recorded below: a zero step, and mixed element types.
  - [ ] Still open: `assertnotnull`, `strlen` (needs ctystrings), generalized `MakeToFunc`.
- [ ] **`unify` has no primitive widening rule** — the one gap the set ports exposed
  go-cty unifies a mixture of primitives with `convert.UnifyUnsafe`, which widens everything to string: `setunion(set(string), set(bool))` is a `set(string)` containing `"true"`. This package's `unify` answers `dynamic` for any mixture it cannot handle structurally, and `convert` has no set→set element-wise conversion either. So the union keeps both elements at their original types in a `set(dynamic)`.
  Not fixed inside the set operations, because `unify` is shared with `chunklist`, `concat`, `flatten` and the collection constructors, and widening it changes all of them. Pinned as two strict xfails in the sweep so it cannot be forgotten.
- [x] **`range`'s zero-step guard, kept as a clean refusal**
  go-cty tests `step == cty.Zero`, comparing two structs holding different `big.Float` pointers, so it never fires: `range(0, 10, 0)` loops until the 1024 cap and reports *that* instead. Refused directly here with "step must not be zero". Both implementations refuse, so the sweep agrees; only the message differs. Same call already made for `indent`'s negative count.
- [x] **Divergences the sweep found, each reproduced against the oracle** — *breaking*
  Held as strict xfails in `KNOWN_DIVERGENCES`, so fixing one turns its entry red and forces it out of the list rather than letting it rot. All five are now fixed; the only entries left are the two halves of the numeric precision decision below, which are not bugs.
  - `merge` returned an object type where go-cty returns `map(string)`. The result type was inferred from the merged *payload*, so it changed shape with the data and a merge of maps could not be composed with anything expecting a map back. go-cty's rule is that arguments all of one type keep that type, and only a genuine mixture collapses to an object.
  - `jsondecode` returned a `dynamic` wrapping the value; go-cty returns the type the document implies — an object for a JSON object, a *tuple* for an array, since JSON promises nothing about an array's members sharing a type. Same for `csvdecode`, which is `list(object(...))` with every column a string. This one reaches the wire, so Terraform was seeing `dynamic` where go-cty describes the value. Numbers now decode via `Decimal` rather than through float64 first.
  - `timeadd` rendered the offset as `+00:00` where go-cty writes `Z`. Both are valid RFC3339, but Terraform compares strings, so it was a perpetual diff.
  - `formatdate` implemented **the wrong dialect entirely**. It translated Go's own `2006-01-02` reference layout, where go-cty defines its own `YYYY-MM-DD` scheme with quoted literals — so every existing call was writing a format string this package understood and go-cty does not, and vice versa. Ported the tokenizer and all eleven verbs from `datetime.go`.
  - Both datetime functions parsed timestamps with `datetime.fromisoformat`, which accepts a bare date, a space in place of the `T`, and an offset without its colon. go-cty deliberately keeps its own RFC3339 definition rather than inheriting the host language's (`datetime_rfc3339.go` says so in as many words), so that grammar is now parsed here rather than delegated.

  Also fixed the mechanism itself: `KNOWN_DIVERGENCES` was applied with `pytest.xfail()`, which aborts the test where it stands, so a fixed divergence could never XPASS and the list could rot exactly the way it exists to prevent. It adds a strict `xfail` marker now and the body runs.
- [x] **Public function names do not match Terraform's** — *settled by the registry, not by renaming*
  `pyvider.cty.functions.STDLIB` maps go-cty's own name for each function onto this package's implementation, declared at the function by `@stdlib_function("...")` rather than in a table beside it. 79 entries; the only go-cty names absent are `format` and `formatlist`, which are not ported yet.
  Renaming was considered and rejected on evidence, and the evidence is pinned as tests so it does not get re-litigated from a comment:
  - **3 names can never be Python functions.** `and`, `or`, `not` are keywords.
  - **7 more shadow builtins the modules call.** `numeric_functions.py:315` calls builtin `max`; `collection_functions.py:555` and `:712` call builtin `range`. `slice` already shadows, and only gets away with it because that module never calls the builtin.
  - **The 11 that are free to rename are the ones where Terraform's spelling is worse.** `greater_than_or_equal_to` → `greaterthanorequalto`, `not_equal` → `notequal`. Renaming would make the Python API less readable to reach a name the registry supplies anyway.
  So renaming is 0-for-20: impossible, breaking, or a downgrade. 56 of 79 already carry go-cty's name; the registry covers the rest and reaches 100% where renaming tops out around 96% with breakage.
  The sweep now reads `STDLIB` instead of keeping its own `NAME_MAP` — that copy is what silently skipped fourteen functions while reporting them covered, and it no longer exists.
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

## Cross-repo follow-ups — not this repo, do not lose

Found while doing parity work here. Each belongs to another repository and is recorded only so it is not rediscovered from scratch.

- [ ] **`pyvider-components` stdlib functions disagree with Terraform's builtins of the same name.** `pyvider-components/src/pyvider/components/functions/` registers 20 provider functions, of which ~16 duplicate a `pyvider-cty` stdlib name with an independent plain-Python implementation. They import nothing from `pyvider.cty.functions`.
  Confirmed divergence: `provider::pyvider::length("👨‍👩‍👧‍👦")` returns **7** (Python `len`, code points). Terraform's own `length` returns **1** (grapheme clusters). pyvider-cty's now refuses the call. Three implementations, three answers — and the components one is what practitioners actually call, shadowing a builtin's name while disagreeing with it.
  **Do not fix by rerouting components through `pyvider.cty.functions`.** The boundary in `pyvider/protocols/tfprotov6/handlers/call_function.py` converts to native Python before dispatch (`unmarshal` → `cty_to_native` → the function → `marshal`), so a component function never sees a `CtyValue`; rerouting means changing pyvider's function-call protocol, not editing components. Unknowns are already short-circuited at that boundary (`call_function.py:50`), and marks cannot cross the wire, so cty's per-function unknown and mark handling would be dead code there.
  The two sets of functions have genuinely different contracts: components' should track **Terraform's** stdlib, pyvider-cty's should track **go-cty's**, and `length` is exactly where those differ.
  Blocked on the same UAX#29 decision as `SafeKnownPrefix` below. Note `"café"` returns 4 only because that literal is NFC-composed; the NFD spelling returns 5, which is the case normalization exists for.

- [ ] **Latent, not yet live: `pyvider`'s `cty_path_to_proto_path` will render a set-element path badly.** `pyvider/src/pyvider/protocols/tfprotov6/handlers/utils.py:385` maps a `KeyStep` to `element_key_string=str(key)`. Phase 3 gave `KeyStep` a second role — a set element keys itself — so that `key` can now be a whole `CtyValue`, and `str()` of one is its repr. Unreachable today: validation only ever builds a `KeyStep` for a map key (`types/collections/map.py:76`), and nothing yet feeds `walk`-produced paths into diagnostics. It becomes reachable the moment something does.

- [ ] **143 of the 197 `ERR_*` constants in `config/defaults.py` are never used** — the function raises a hardcoded copy of the same text instead. `divide` raises `"divide by zero"` while `ERR_DIVIDE_BY_ZERO` sits unused; `upper` builds an f-string while `ERR_UPPER_MUST_BE_STRING` sits unused. Found three times now as a side effect of other work (`length`, `regexreplace` twice), each time by noticing the constant while editing the function.
  Mechanical, no behavioural change, touches most of the stdlib — which is why it is filed rather than folded into a fix commit, where it would bury the change under noise. Worth one dedicated pass. Note the detection is crude (a name occurring once in `src/` and `tests/` is assumed dead), so verify each before deleting; the ratio is too large to be measurement error but individual entries may not be.

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

- [ ] **Release notes must name thirteen breaking changes**, not one:
  1. Set elements no longer carry marks; read them off the set (go-cty's `SetVal` behaviour).
  2. Serializing a marked value now raises instead of silently dropping the marks.
  3. **Map and object payloads are immutable.** `value.value[k] = x` now raises `TypeError`. Nothing in the workspace does it any more, but external provider code might, and the failure is loud and at the point of the mistake -- which is the intent, since the silent alternative corrupted sensitivity tracking.
  4. **`regex` and `regexall` take `(pattern, string)`**, not `(string, pattern)`. Lead with this one. Both arguments are strings, so an un-updated call keeps type-checking and quietly returns a wrong answer — the only change here with no failure mode to warn the caller.
  5. `regex` returns capture groups (a tuple, or an object for named groups) rather than the whole match, and raises on a non-match rather than returning `""`. `regexall`'s elements have the same shape.
  6. `indent` takes a number of spaces rather than a prefix string, and no longer indents the first line.
  7. `flatten` returns a tuple rather than a list, recurses through nested sequences, keeps null elements, and passes non-sequence elements through instead of raising. `chunklist` preserves the element type and accepts a size of 0.
  8. **`length` refuses a string.** It counted code points, which agreed with neither go-cty (which refuses the call, leaving strings to `strlen`) nor Terraform (which counts grapheme clusters — 1 for a four-person family emoji where this said 7). It now also accepts a dynamic wrapping a collection, which it previously refused; that half is a widening and breaks nobody. Callers wanting the old answer have `len(value.value)`; `strlen` is not available yet, since it needs the deferred UAX#29 decision.
  9. **`regexreplace` expands the replacement by Go's rules, not Python's.** The two dialects are inverses: Go reads `$1` and `${name}` and passes `\1` through as literal text; Python's `re.sub` does exactly the reverse. Every replacement referring to a capture group was therefore silently wrong in one direction or the other — a Go-style `${1}W` came out as the literal text `${1}W`, and a Python-style `\1` substituted where go-cty would have emitted it verbatim. Confirmed against the oracle in both directions and pinned by a 612-case differential sweep.
  10. **`values` returns a map's values in key order, and both `keys` and `values` return a tuple for an object.** `values` used insertion order while `keys` sorted, so the two no longer corresponded and `zipmap(keys(m), values(m))` — the ordinary way to rebuild a map — silently paired every value with the wrong key. The object result type also changed: go-cty returns a tuple, since an object's attributes have differing types and a list would widen them all to dynamic. No caller anywhere in the workspace, and neither is a registered provider function.
  11. **`formatdate` uses go-cty's format dialect, not Go's layout strings.** This is the widest of the thirteen. The old implementation translated Go's own `2006-01-02` reference layout into `strftime`; go-cty defines its own scheme — `YYYY`, `MM`, `DD`, `EEEE`, `hh`, `AA`, `ZZZZZ`, with `'...'` quoting literals — and reads digits as literal text. So `formatdate("2006-01-02", ts)` now returns the string `2006-01-02` rather than a formatted date, and `formatdate("YYYY-MM-DD", ts)`, which used to pass through unchanged, now works. Both directions fail silently: the old dialect still returns *a* string. Every call site needs rewriting.
  12. **`formatdate` and `timeadd` parse RFC3339 strictly**, where they used `datetime.fromisoformat` and so accepted a bare date, a space in place of the `T`, a lowercase `t` or `z`, and an offset without its colon. go-cty carries its own RFC3339 parser precisely so this does not vary with the host language. `timeadd` also renders a zero offset as `Z` rather than `+00:00` — same instant, different string, and Terraform compares strings.
  13. **`jsondecode`, `csvdecode` and `merge` return concrete types.** `jsondecode` gave a `dynamic` wrapper; it now returns the type the document implies, which for a JSON array is a **tuple**, not a list. `csvdecode` returns `list(object(...))` with every column a string, and now refuses a missing header line, a duplicate column name, or a ragged row, all of which it used to accept. `merge` keeps the argument type when the arguments all share one — so merging maps yields a map instead of an object — and returns an empty object for no arguments. The decoders' types cross the wire, so this is what Terraform sees.
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

**Status:** partly resolved, 2026-08-16. The seam exists and every one of the 79 stdlib functions goes through it: `@stdlib_function("<go-cty name>")` in `functions/_framework.py`, which registers the name and applies the mark policy. Two properties of *being* a stdlib function now live in one place instead of being re-derived per function.

What is still hand-rolled is the argument policy — **146 null/unknown checks across the function modules, no two quite alike**, where go-cty declares each parameter's type and whether it accepts null, unknown or marked values and enforces it before `Impl` runs. That is the root cause of most divergences found so far: `contains`, `equal`, `length`, `merge` and both decoders each failed by re-deriving policy rather than declaring it. Moving it behind the decorator makes the class of bug unrepresentable rather than fixed one at a time.

**Open sub-decision:** whether that move happens **before** 0.5.0. It is breaking (it settles the null-argument question below), so doing it after means two breaking releases where one would do.

### 3. Numeric precision model

Found by the stdlib sweep, and it differs in *both* directions.

go-cty holds a number in a 512-bit `big.Float`, so `divide(1, 3)` comes back with 155 significant digits against this package's 28 (Decimal's default context). But its transcendental functions compute in `float64` first, so `pow(2, 0.5)` comes back with 17 significant digits, and there this package is the **more** accurate of the two.

Neither is a wrong answer. Matching go-cty means both widening the Decimal context *and* deliberately reproducing its float64 rounding step in `pow` and `log` — that is, making the implementation less accurate on purpose so that a value round-trips identically. That is a decision about what parity means here, not a bug fix.

Terraform compares values as they arrive on the wire, so a difference in the last digits is a real diff, not a cosmetic one.

**Status:** unresolved. Held as xfails in the sweep so it stays visible.

### 4. Null arguments: raise or return unknown?

go-cty refuses a null for any parameter not declared `AllowNull`, and none of the stdlib's are. This package mostly returns unknown instead. The nine functions added on 2026-08-16 follow go-cty and raise, so the package currently has both conventions.

Deliberate, and recorded rather than papered over: the new functions have no callers, so following go-cty from the start costs nothing, while converting the other ~70 is a behavioural break for every one of them.

**Impact:** settling it is one declaration per parameter *if* the function framework lands first, and ~70 individual edits if it does not. That is the real argument for sequencing the framework before 0.5.0.

**Status:** unresolved, and coupled to decision 1.

### 2. Unicode segmentation dependency (gates phase 3 item 2)

`Strlen` and `SafeKnownPrefix` need real UAX#29 grapheme cluster segmentation. go-cty tracks Unicode 17 on Go 1.27+, Unicode 15 below.

Options: take a dependency (`uniseg`-equivalent), vendor the tables, or document an explicit deviation and use code points.

This is a question about pyvider-cty's dependency posture more than a technical one. Gates `strlen` (#9) and `StringPrefix` (#10).

**Status:** **deferred, 2026-08-16.** `NormalizeString` turned out not to need it (pyvider already normalizes at construction — see phase 3), and nothing exports `strlen` today, so nothing is blocked by waiting. Still gates `SafeKnownPrefix`, `strlen` (#9), `StringPrefix` (#10), and the `pyvider-components` divergence recorded under cross-repo follow-ups. Revisit when the first of those is actually wanted.

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
| 2026-08-16 | **The stdlib is now reachable by go-cty's own function names, and the naming decision is closed without renaming anything.** `@stdlib_function("<name>")` replaces `@preserve_marks` on all 79 functions and populates `pyvider.cty.functions.STDLIB`. Renaming was rejected on evidence, now pinned as tests: 3 names are Python keywords and can never be functions; 7 shadow builtins the modules actually call (`numeric_functions.py:315` calls builtin `max`, `collection_functions.py:555`/`:712` call builtin `range`, and `slice` already shadows); and the 11 that *are* free to rename are exactly the ones where Terraform's spelling is worse — `greater_than_or_equal_to` → `greaterthanorequalto`. 0-for-20. 56 of 79 already match, and the registry covers the remainder. The sweep's hand-maintained `NAME_MAP` is deleted and it reads the registry instead: that copy is precisely what silently skipped fourteen functions while reporting them covered, and the fix is that the name now lives at the function where it cannot drift from it. The decorator is deliberately shaped to take the argument policy next — 146 hand-rolled null/unknown checks, no two alike, which is the root cause of most divergences found this session. **A separate finding while surveying for this:** nothing in the workspace imports `pyvider.cty.functions` at all. pyvider-components reimplements the same functions independently on native Python types via `@register_function(name=...)`, which is why its `length("👨‍👩‍👧‍👦")` returns 7 where cty refuses and Terraform says 1 — three implementations because there are three implementations. The thirteen breaking changes therefore have zero internal blast radius, and the largest remaining parity win is in components, not here. |
| 2026-08-16 | **Phase 5's bool ops, five set ops and `range` ported; the sweep now has no skips.** These nine were exactly what the sweep was skipping, so it went from 118 comparisons with 8 skips to 137 with none, across 71 functions. `and`/`or` deliberately do not short-circuit — `and(unknown, false)` is unknown, not false — because go-cty's framework returns unknown for any unknown argument before the implementation runs, and answering `false` here while Terraform answers unknown is a plan disagreeing with itself. The set ops follow go-cty's `allowUnknowns` split: only union computes with an unknown element present. Two divergences came out of it. `range`'s zero-step guard in go-cty tests `step == cty.Zero`, comparing structs holding different `big.Float` pointers, so it never fires and a zero step instead loops to the 1024 cap; refused cleanly here, the same call already made for `indent`. The other is not in these functions at all: `unify` has no primitive widening rule, so where go-cty's `UnifyUnsafe` makes `setunion(set(string), set(bool))` a `set(string)` holding `"true"`, this gives a `set(dynamic)` holding both originals. Left alone rather than widened under `chunklist`, `concat` and `flatten`, and pinned as two strict xfails. A guard test — every exported function needs a mark-propagation fixture — caught all nine on the first run, which is the second time this session an existing guard has done its job unprompted. |
| 2026-08-16 | **All five sweep divergences closed, and the divergence list itself turned out to be broken.** `KNOWN_DIVERGENCES` was applied with `pytest.xfail()`, which aborts the test at the call — so a fixed divergence could never XPASS, and the list would have quietly gone on claiming five open bugs after they were fixed. It was the exact rot it was written to prevent, in the mechanism rather than the data. A strict marker now, with the body actually running. On the fixes: `merge` inferred its result type from the merged payload, so the type changed shape with the data and a merge of maps came back an object; it now follows go-cty's rule that arguments sharing a type keep it. `jsondecode` and `csvdecode` returned `dynamic` wrappers where go-cty returns the implied type — an object for a JSON object, a **tuple** for an array, `list(object(...))` of strings for CSV — and that type is what crosses the wire, so Terraform was being told `dynamic`. `timeadd` wrote `+00:00` for a zero offset where Go's RFC3339 layout writes `Z`. The largest was `formatdate`, which was not merely unimplemented as recorded here but implemented in **the wrong dialect**: it translated Go's own `2006-01-02` reference layout, where go-cty defines its own `YYYY-MM-DD` scheme with `'...'` quoting. Both dialects return a plausible string for the other's input, so every call was silently wrong. Ported the tokenizer and all eleven verbs, plus go-cty's deliberately-own RFC3339 parser, which is stricter than `datetime.fromisoformat` in six ways. Sweep grew 84 → 110 comparisons; three test files that asserted the old behaviour were corrected, one of which mocked `csv.DictReader` and had gone on passing after the implementation stopped using it. |
| 2026-08-16 | **Systematic sweep of the stdlib against the oracle, and it found what the reviewer's method predicted it would.** The `regexreplace` finding came from looking past the branch diff, so the same move was generalised: `tests/compatibility/test_stdlib_sweep.py` drives every function the oracle exposes from one table, writing each case once so the two implementations cannot drift apart in the test itself. First run: six divergences in 46 calls. The worst was `values`, which returned a map's values in insertion order while `keys` returned them sorted — so `zipmap(keys(m), values(m))`, the ordinary way to rebuild a map, silently paired every value with the wrong key, with a result that still type-checked and still looked like a map. Fixed, along with both functions returning a list where go-cty returns a tuple for an object input. Adding a name map (`max` is exported as `max_fn`, `notequal` as `not_equal`, sixteen in all) took the sweep from 60 comparisons to 82 and surfaced `pow`'s precision divergence, which had been hidden behind a skip that read as coverage. Five divergences remain as strict xfails so that fixing one forces its entry out; the eight skips are exactly the phase 5 port list, arrived at independently. |
| 2026-08-16 | **Seventh review round, external. One real finding, and it was the same class as the five already fixed.** `regexreplace` was never touched by the regex work and still used `re.sub` with the caller's template handed straight to Python. Go and Python expand opposite syntaxes, so each engine emitted the other's placeholder as literal text: `${1}W` produced the literal `${1}W` here against `-W-xxW-` in go-cty, and `\1` substituted here where go-cty passes it through. Wrong in both directions, type-checking the whole way — the same failure mode as the `regex` argument swap. Its one existing test used `\d` → `*`, no capture group, so it passed throughout. Fixed by expanding the template with Go's own rules (longest run of letters/digits/underscores for a name, so `$1W` is the group named "1W"; unresolved references expand to nothing; malformed ones emit a bare `$`), verified by a 612-case differential sweep across 6 texts x 6 patterns x 17 templates, all agreeing. Eight new oracle cases. The review's second finding — that `regex`/`regexall` accept RE2-incompatible syntax — was already recorded here as an accepted divergence, and its suggested fix rested on a misreading: `_compile_pattern` is `re.compile` plus a better error message, not an RE2-compatible path, so routing through it buys error consistency and nothing more. |
| 2026-08-16 | **Phase 3 done — and three of its five items were not gaps.** `RawEquals` already existed as the `__eq__` / `.equals()` split; `PathSet` is a Go workaround for unhashable slices, so `CtyPath` was made hashable and a `set[CtyPath]` stands in; `NormalizeString`'s behaviour was already present, since pyvider NFC-normalizes at construction exactly as go-cty does. All three were filed from reading go-cty's public API rather than running pyvider — the same mistake "Verify before filing" was written about one phase earlier. What did land: `walk` / `deep_values` / `transform` in `src/pyvider/cty/walk.py`, all iterative, because pyvider's own marshaler records that the recursive version of this shape "did raise RecursionError at a nesting depth pyvider-cty advertises as supported". `deep_values` is a generator, which is what go-cty recommends now that Go has iterators; `walk` exists only for the pruning a generator cannot express. Extending `KeyStep` to apply through a set came with it — #14 item 7, landed early because `walk` would otherwise emit set-element paths it could not follow. 37 tests, the load-bearing one being that every emitted path re-applies to the value it came from. |
| 2026-08-16 | **`length` diverged three ways, and nothing had listed it.** Found by running the oracle while checking whether phase 3's items were real. It accepted a string and counted code points (go-cty refuses; Terraform counts grapheme clusters — three implementations, three answers for one emoji); it refused a dynamic that go-cty accepts; and go-cty's own error text names three collection types where its check names four. Fixed, with six new oracle cases. The null-collection case is left returning unknown, to move together with the same deferred strictness change in `contains`. Also recorded a cross-repo follow-up: `pyvider-components` registers ~16 provider functions that shadow pyvider-cty stdlib names with independent plain-Python implementations, and `provider::pyvider::length` disagrees with Terraform's builtin of the same name. That one is not fixable by rerouting through pyvider-cty — the function-call boundary converts to native Python before dispatch — and is blocked on the same UAX#29 decision. |
| 2026-08-15 | Initial review against go-cty `v1.19.0-1-g0d1eb26`. Filed #5–#14 and tofusoup#2. PR #4 merged (rebase), closing #3. |
| 2026-08-15 | #5 implemented on `feat/go-cty-parity` (local, unpushed). Filed #15 — collection `validate()` discards element marks — discovered while testing #5. |
| 2026-08-15 | #15 implemented. Filed #16 — msgpack silently drops marks where go-cty errors — discovered verifying #15. Marks now survive validation at every level; they still do not survive serialization, which is #16. |
| 2026-08-15 | #16 decision recorded: match go-cty and raise. Established that sensitivity travels via the wire *schema*, not the value, so #16 does not depend on #8 as first assumed — but pyvider's `_apply_schema_marks_iterative` is dead work that must be deleted first or the new error crashes every sensitive attribute. |
| 2026-08-15 | Phase 1 closed except #16. Adversarial review of the branch found a third mark-dropping path (the recursion guard's early exits); fixed. Filed #17 — `MAX_VALIDATION_DEPTH` is 500 but validation crashes above 495, pre-existing and verified against a clean `gh-origin/main` worktree. Review prompt kept at `.provide/ADVERSARIAL-REVIEW-PROMPT.md`. |
| 2026-08-15 | **Fifth round: two independent adversarial reviewers, twelve findings, all twelve fixed.** Two were silent declassification. The worst was mine and rested on a claim I made without checking -- the deep-mark memo's immutability gate had been removed for speed on the stated grounds that nothing in the workspace mutates a payload in place, which was false (`pyvider` did it in three places) and reproducibly dropped a `sensitive` mark. Rather than choose between the gate and the 96,401% cost of keeping it, the invariant is now **enforced**: map and object payloads are built as `FrozenDict`, a `dict` subclass that refuses mutation, so they are memoizable because they genuinely cannot change. Also fixed: `cty_to_msgpack` still serialized marked values inside containers that were unknown *because of* their elements; `equals` answered definitely against unknowns of dynamic type; `contains`' `==` shortcut disagreed with `equals` on cross-type nulls; `contains` returned unknown for a list holding both a match and an unknown, where go-cty answers true; the `RecursionError` window failed in both directions and was re-keyed on where the stack ran out rather than how deep the path was; the depth ceiling was per-thread and stale; `CtyDynamic` reached one level less than advertised; `reapply_marks` duck-typed on a `marks` attribute; and `CtySet`'s pass-through skipped its own hoisting. The marked path was ~9,000x slower than the unmarked one (40 ms per stdlib call on a marked 50k list) and the benchmark contained **no marked fixtures at all**, so the tool built to catch regressions could not see the one on the path every sensitive attribute takes. Now 0.007 ms, and the fixtures exist. |
| 2026-08-15 | Cross-language compatibility is real for the first time. The `--run-compat` test was a placeholder reading a checked-in fixture, failing on `main` with `msgpack ExtraData` -- 10 of the 17 fixtures were written with a trailing newline appended to the msgpack bytes. It now runs values through actual go-cty via the soup-go harness in three directions, including **byte-for-byte** agreement, which is what Terraform compares. Its first run flagged a disagreement on 2^53+1 that turned out to be the harness rounding JSON numbers through a float64 -- fixed in tofusoup, because an oracle that quietly loses precision does not merely fail, it accuses the implementation under test. 36 cases agree. |
| 2026-08-15 | Verified across **every** consumer in the workspace against this branch: `pyvider` 1421 (identical against published 0.4.0), `pyvider-rpcplugin` 555, `terraform-provider-tofusoup` 280, `plating` 217, `pyvider-components` 116, `pyvider-hcl` 88, `tofusoup` 48 -- 2,725 tests, zero failures. A grep across all nine for the payload mutation `FrozenDict` now refuses returns zero. The reviewer's own end-to-end harness, which originally caught the apply crash, passes for all six attribute shapes with no secret in any diagnostic. |
| 2026-08-15 | **#16 done, and verified against the real provider.** Serializing a marked value now raises, as go-cty does, with the path to the offending value. Six existing codec tests asserted the old behaviour — four unmarked *both sides* before comparing, which is the bug written down as a test — and now assert the refusal. Paired change in `pyvider` on `fix/cty-marks-not-serializable`: the outbound schema-marking pass is gone, and `marshal` now unmarks at the wire boundary. That second half was **not** in the original plan and the provider suite is what found it: the inbound path deliberately hands resource code marked config, so a resource building its state from `ctx.config_cty` sends a marked value to `marshal`, which would have crashed at plan or apply on exactly the resources handling secrets. Verified 1420 passing against **both** 0.4.0 and this branch, so the two repos can release in either order — the sequencing hazard is gone. `pyvider-components` needed no change (116 passing). |
| 2026-08-15 | **tofusoup#2 done** (`feat/go-cty-1.19-and-cty-call`): go-cty 1.14.1 → 1.19.0, plus `soup-go cty call`, which turns the harness into an oracle — arguments carry an explicit type and may be unknown, null or marked, and the result reports those states separately from the value. A 25-case differential run of pyvider against **real go-cty** agrees on 24. The one disagreement is the already-deferred `contains` on a null collection. It also confirmed from the running implementation, not from reading it, that marks propagate through `upper`/`join`/`length`/`add` and that `contains`/`equal` go unknown rather than false. This is the tool that would have prevented the two non-existent gaps filed from reading go-cty's CHANGELOG. |
| 2026-08-15 | Benchmarked eighteen hot paths against `gh-origin/main` and found the mark work had made several far slower — worst was `length()` on a 20k map at **+96,401%**, caused by skipping the deep-mark memo for mutable payloads, a change measured only on 10–1000 entry maps where it looked free. Memo restored with the immutability requirement documented as the contract it always was. Also fixed: `preserve_marks` walking leaf arguments, `contains` routing fully-known elements through three-valued equality, `equals` setting up the mark protocol to compare two scalars, `CtySet.validate` unmark-deeping every element, and `reapply_marks` running a module import per element validated. Final position: nothing above +38%, large-absolute cases 4–14%, `equal(scalar)` and `join` faster than base. **No perf regression guard exists** — `tests/performance/` is `--run-benchmarks` gated so CI never runs it. |
| 2026-08-15 | Three-valued equality implemented as `CtyValue.equals()` (go-cty `Value.Equals`), and `contains`, `equal` and `not_equal` all moved onto it — three approximations of the same comparison replaced by one implementation, the same consolidation that fixed the mark bugs. It is strictly more precise than the conservative stopgap it replaces: a known attribute that differs rules a value out even when a sibling attribute is unknown. Not implemented: refinement-bound disqualification (`Value.Range().Includes`), pending fuller refinement support — those return unknown, which is the safe direction. |
| 2026-08-15 | #17 closed. The limit is derived from the recursion limit rather than asserted as a flat 500, because the frame cost per level (two, measured) makes 500 undeliverable under CPython's 1000-frame default. 480 promised and 480 delivered; tracks a raised recursion limit; pinnable via `PYVIDER_CTY_MAX_VALIDATION_DEPTH`. Also removed a **second `MAX_VALIDATION_DEPTH = 500`** in `pyvider.cty.context` that governed nothing but was the one the docs cited — the same duplicate-source-of-truth pattern that produced the mark bugs, found a third time. Four docs corrected. `equal`/`not_equal` fixed for nested unknowns in the same session, found by sweeping for the `contains` bug's shape rather than waiting for a report. |
| 2026-08-15 | Fourth round, security-focused, against the whole branch. Differential matrix over 51 mark-flow scenarios, run against both `gh-origin/main` and HEAD with an independent detector: base lost the mark in **34 of 51**, HEAD in **0**. No declassification found, so no security finding. It did disprove a claim this branch had written down — the memo was justified as "CtyValue is immutable, so the answer cannot go stale", but freezing an attrs class freezes the *reference* to the payload, not the payload, and map/object payloads are plain dicts. A stale under-reporting memo was reproducible by in-place mutation. Rather than assert an immutability nothing enforces, the walk now reports whether it saw a mutable container anywhere in the subtree and the memo is skipped if it did. The staleness class is gone by construction; the 200k-list memo is unaffected, and dict-payload values re-walk at 6-18 us for realistic sizes. Also recorded the release gate: the set change is breaking and all five consumers pin unbounded. |
| 2026-08-15 | Third review round (`/code-review high`), seven findings, all seven reproduced and fixed. Two were performance regressions introduced by the mark work itself: `preserve_marks` deep-walked every argument *before* its no-marks fast path, taking `length()` on a 200k list from 0.005 ms to 41 ms **per call**; and the guard's stop path re-walked the input at every unwinding frame, making abort O(depth x size). Both are now fixed by memoizing the deep walk on the value (`CtyValue._deep_marks`) — 20 calls went 799 ms to 40 ms, and a single fresh walk is back to the pre-regression 41 ms. The walk itself was consolidated into `pyvider.cty.marks`: **three divergent copies of it were the root cause of this entire class of bug**, each having guessed at a different set of container types. Also: set elements no longer carry marks (go-cty parity, above); `contains` reads unknown deeply; the blanket `except RecursionError` is now scoped by depth so unrelated recursion bugs surface instead of becoming an unknown; a log field that was always empty now reports depth; and a comment justifying deleted mark-restoring code named only one of the two mechanisms that replaced it. |
| 2026-08-15 | Second adversarial review round. Found the deep-mark walk matched only `tuple` and `dict`, so it skipped every **set** — a validated `CtySet` stores a `frozenset`. Present in two places, and the one the reviewer did not reach was the worse of the two: `functions/_marks.py` is the production path, where a sensitive set element was dropped from the result of every stdlib call *and* handed to the implementation the strip was meant to shield. Also found the guard collected marks only when its input was already a `CtyValue`, losing them for the raw `list`/`dict` inputs `validate` is normally given. Both fixed; the collector is now iterative, because it runs precisely when the value is too deep or too cyclic to recurse over. #17's crash half fixed in the same pass. |
