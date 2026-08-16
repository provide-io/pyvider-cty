# Adversarial review prompt

Paste everything below the line into a fresh agent session with no prior context.

---

You are reviewing a branch adversarially. Your job is to find what is wrong with it, not to confirm that it is right. A review that finds nothing is only useful if you can show what you tried.

## The work

Repository: `/Volumes/data/pyv/pyvider-cty`
Branch: `feat/go-cty-parity` (local only, never pushed, no PR)
Base: `gh-origin/main`

Reference implementation: a `go-cty` checkout at `/Users/tim/code/tf/go-cty`, at `v1.19.0-1-g0d1eb26`. This project aims to be a Python implementation of it.

**There is a live oracle.** `/tmp/soup-go cty call <function> '<arg-json>' ...` runs the real go-cty and prints its answer as JSON. `/tmp/soup-go cty call --help` documents the argument format, which can express unknown, null and marked values. Use it constantly — it settles behavioural questions that reading cannot. The compat suite runs with `SOUP_GO_BIN=/tmp/soup-go uv run pytest tests/compatibility/ -q --run-compat`.

Start with `git log --oneline gh-origin/main..HEAD` and `git diff gh-origin/main...HEAD`.

The branch has two halves.

**Marks** — the mechanism cty uses to flag a value as sensitive. Terraform relies on marks to redact secrets from plan output, logs and state display, so **the failure that matters is a value entering a path marked and leaving it unmarked**. That is a disclosure bug, not a tidiness bug. Over-marking fails safe. Claims: stdlib functions no longer discard argument marks; `validate()` no longer discards element marks; the recursion guard's exits carry marks; the deep-mark walk covers sets and exists in one copy; set elements no longer carry marks (hoisted onto the set, as go-cty's `SetVal` does); serializing a marked value now raises rather than silently dropping.

**go-cty behavioural parity** — six stdlib functions rewritten to answer what go-cty answers, and a new traversal module. Claims:

1. `regex`/`regexall` take `(pattern, string)`, not `(string, pattern)`; return capture groups typed from the pattern (string / tuple / object); raise on a non-match; refuse mixed named and unnamed groups.
2. `indent` takes a *number of spaces*, not a prefix string, and does not indent the first line.
3. `flatten` returns a tuple, recurses, keeps nulls, passes non-sequences through.
4. `chunklist` preserves the element type and accepts a size of 0.
5. `length` refuses a string and accepts a dynamic wrapping a collection.
6. New `src/pyvider/cty/walk.py`: `deep_values`, `walk`, `transform` — go-cty's `cty/walk.go`.
7. `CtyPath` is frozen and hashable; `KeyStep` now applies through a set.

## Ground rules

**Trust nothing in the repository's own account of itself.** `.provide/GO-CTY-PARITY.md`, the commit messages, and the code comments were all written by the implementer and are part of what you are reviewing, not evidence about it. Where they assert a behaviour, go and run that behaviour. Several commit messages quote go-cty documentation as justification — check the quotes are real and that they say what the message claims.

**Prefer the interpreter to reading.** Every serious error on this branch came from reasoning about code instead of executing it. `uv run python -c "..."` against real values is worth more than any amount of careful reading. The suite runs with `uv run pytest -q` in about 3.5 minutes (1523 tests).

**Differential testing is the highest-yield technique.** Export the base tree (`git archive gh-origin/main | tar -x -C <scratch>`) and run the same scenario matrix against both. Write your mark detector *independently* — do not use `pyvider.cty.marks` to check whether `pyvider.cty.marks` is right.

**Compare against go-cty directly**, via the oracle first and the source second. Note that Go sometimes needs an explicit branch where Python gets the same result implicitly — a missing code path is not by itself a defect.

## Known failure modes on this branch

Six review rounds have happened. Every one found real bugs, and **most found bugs introduced by the previous round's fix**. Assume that pattern continues into whatever you are looking at.

**Claimed a gap that did not exist — five times now.** Three "behavioural fixes" were filed from go-cty's CHANGELOG describing bugs *go-cty* had. `RawEquals`, `PathSet` and `NormalizeString` were filed from reading go-cty's public API and turned out to be already present, unnecessary in Python, or both.
→ *Check the inverse, in both directions.* Is something on the tracker's "Confirmed parity" list in fact broken? And **are the three phase-3 cuts wrong?** The claims are: `__eq__` is a true structural equality and `.equals()` a true three-valued one; a `set[CtyPath]` is a sufficient `PathSet`; pyvider NFC-normalizes everywhere go-cty does. Each was verified by the implementer alone. Break them.

**Built a value directly to dodge a validator, and nearly shipped a hole.** `regex` with named groups constructs its object result as `CtyValue(vtype=..., value=FrozenDict(...))` rather than through `CtyObject.validate`, because that validator refuses a null attribute and a non-participating capture group is null. `flatten` and `transform` do the same for perf.
→ *Every direct construction skips every invariant the validator enforces.* Enumerate them (`rg 'CtyValue\(vtype='`) and for each, find an invariant `validate` would have enforced that the direct path now misses. Marks, normalization, type conformance of children, set hoisting.

**Fixed correctness and introduced a performance cliff, twice.** Collecting marks before the no-marks fast path took `length()` on a 200k list from 0.005 ms to 41 ms. `flatten` re-validated its result and got 117% slower on 10k elements. Both were caught only by `scripts/perf/benchmark.py`, never by the suite.
→ *Measure.* `make perf-report` compares against a base ref. `transform` has the same shape as the `flatten` bug — it rebuilds containers through `validate` — and is guarded only by an identity shortcut. Defeat that shortcut and see what it costs.

**Relied on `==` where `==` does not mean what it looks like.** `_strip` decided "did anything change" by comparing values; `CtyValue.__eq__` delegates to a `CtyCapsuleWithOps`' `equal_fn`, which ignores marks. Now uses identity — and `transform`'s new shortcut uses identity for the same stated reason.
→ *Look for other places where `==`, `in`, or a set/dict operation on `CtyValue` assumes what equality includes.* `KeyStep._apply_to_set` uses `self.key in elements`. What does that comparison include, and what should it?

**Matched on the container types that came to mind.** The deep walk matched `tuple` and `dict` and skipped every set — a validated `CtySet` holds a `frozenset`. Three copies of the walk, each wrong differently.
→ **There is now a fourth traversal**, `walk.py:_child_steps`, deliberately not merged with the mark walk. Enumerate every payload shape a `CtyValue` can hold and check it against all of them. Does it agree with `marks._children` about what a container is? Where they disagree, which one is wrong?

**Wrote down an invariant that was not true.** The memo was justified as "CtyValue is immutable, so the answer cannot go stale" — freezing an attrs class freezes the reference, not the payload.
→ *Attack the replacements.* Map and object payloads are now `FrozenDict`. Can a mutable payload still reach a memo? Can a cached descendant answer for a subtree that has since moved?

**Let a value through a numeric check that could not hold it.** `indent(2**70, s)` passed a whole-number test and then tried to build a 10^21-character string; `Decimal("Infinity")` passed because infinity equals itself. Fixed by `functions/_args.py:whole_number`, which bounds to int64.
→ *Is int64 the right bound everywhere it is used? Is there another numeric argument that does not go through it?*

## Specific things to attack

**`src/pyvider/cty/walk.py` — entirely new, the most complex thing here**

- The load-bearing claim is that **every path `deep_values` emits re-applies to the value it came from**. Break it. Try: an object whose payload key is absent from its type, a map with a key needing NFC normalization, a set containing unknown or null elements, a set of objects, nested dynamics, a capsule.
- `_child_steps` treats `CtyDynamic` as transparent and emits no step for it. Find a value where that produces a path that reaches the wrong thing, or where two distinct locations produce the same path.
- Set traversal sorts by `_canonical_sort_key()`. What happens when elements are unknown, null, or of a type that key does not handle? Is the order actually stable across processes (`PYTHONHASHSEED`)?
- `transform` returns the container untouched when every child is identical. Construct a case where a child *should* be considered changed but is identical — for example a callback that mutates something reachable rather than returning a new value.
- `_rebuilt_type` derives a new type for tuples but keeps the original for every other container. Is that right for a set whose elements changed type? For an object? Show what go-cty does.
- `transform` re-validates on rebuild. Does that re-normalize, re-hoist set marks, or re-order anything such that an identity-ish transform is not identity?
- Both are iterative with an explicit stack. Find an input where the frame bookkeeping desynchronizes — `done` popping the wrong count, a container whose child count changes between the two `_child_steps` calls.

**`src/pyvider/cty/path/base.py` — `CtyPath` is now frozen, `KeyStep` now applies to sets**

- `steps` changed from `list` to `tuple`. Find a caller anywhere under `/Volumes/data/pyv/` that mutates it or concatenates a list onto it.
- `KeyStep` now holds either a `str` map key or a whole `CtyValue` set element. Find code that assumes the first — `pyvider`'s `cty_path_to_proto_path` does `str(key)`, which is recorded as latent. Is it actually unreachable?
- `_apply_to_set` returns unknown when the set holds any unknown element. Compare against go-cty's `IndexStep.Apply` set branch (`cty/path.go`). Does it agree on marks, on a null key, on an unknown key, on a set that is itself unknown?
- `CtyPath` is hashable only if every step is. A `KeyStep` holding an unhashable key breaks that. Can one be constructed?

**`src/pyvider/cty/functions/string_functions.py` — `regex`, `regexall`, `indent`**

- Result type is decided from the *pattern* before matching. Find a pattern where Python's `re` and Go's RE2 disagree about the number or names of capture groups.
- `_capture_names` maps `groupindex` back to positions. Verify against a pattern with duplicate group names (`(?P<x>a)|(?P<x>b)` — Python refuses; what about `(?:(?P<x>a))`), and nested or optional groups.
- Python `re` is a superset of RE2 (backreferences, lookahead). This is recorded as accepted. Confirm the *direction* — is there anything RE2 accepts that Python refuses? That would be a real break.
- `indent` refuses a negative count where go-cty panics. Is refusing actually equivalent for a caller, and is the count bound correct?

**`src/pyvider/cty/functions/collection_functions.py` — `flatten`, `chunklist`, `length`**

- `flatten` builds its result directly rather than validating. Feed it marked elements, unknown elements, nested dynamics, a set inside a tuple. Does anything lose a mark?
- `_flatten_elements` decides "unknown enough to abort" from the element's type. Compare against go-cty's `flattener` for an unknown *object* or *map* element.
- `length` now unwraps dynamic then type-checks. Oracle a dynamic wrapping a dynamic, an unknown dynamic, a null dynamic, a capsule.
- `chunklist` accepts a tuple where go-cty's `list(dynamic)` parameter refuses one. That is claimed as a harmless superset. Is the unified element type ever wrong?

**`src/pyvider/cty/marks.py` — everything still depends on this one walk**

- `_walk_marks` decides both the marks and whether the answer is memoizable. Find a value where those two answers disagree with reality.
- `_children()` infers container shape from the runtime payload. A capsule wrapping a Python tuple, dict or frozenset is indistinguishable from a collection by that test. Construct one.
- `_strip` rebuilds a set payload with `frozenset(...)`, which can drop elements differing only by marks. Reach that path.

**`src/pyvider/cty/validation/recursion.py`**

- Mark re-application happens in two places for stack-depth reasons. Find a `validate` reached through neither.
- `except RecursionError` is scoped by `MIN_DEPTH_TO_OWN_RECURSION_ERROR`. Can a genuine validator overflow occur below that depth and be re-raised as a crash, or unrelated code overflow above it and be swallowed into an unknown?
- What is the measured maximum nesting depth now? `walk.py` and the frozen `CtyPath` both touch the validation path.

**The tests**

- Are any fixtures degenerate — arguments that short-circuit before the interesting path, so the test passes without exercising anything?
- Revert a production hunk and run the suite. Anything still green was not testing that hunk. Do this for `walk.py`'s identity shortcut and for `length`'s dynamic unwrapping.
- `tests/compatibility/test_stdlib_oracle.py` compares *answers*, not wire bytes. Is that comparison strong enough — does it distinguish a tuple from a list, a null from a missing element, a mark from no mark?
- The mark tests assert marks are *present*. Do any pass because something over-marks rather than because the value is correct?

## What is deliberately not done

Do not report these as omissions; do challenge the reasoning if it is wrong.

- `contains` and `length` on a null collection return unknown where go-cty raises. Deferred together as one strictness change.
- `CtyObject.validate` refuses a null attribute; go-cty has no such rule. Changing it touches every object validation.
- A `CtySet` cannot hold a list, because a `CtyValue` with a list payload is unhashable.
- `strlen`, `SafeKnownPrefix` and grapheme-cluster counting are absent, blocked on an undecided UAX#29 dependency.
- `MarkWithPaths` / `UnmarkDeepWithPaths` are not built. The reasoning is that sensitivity reaches Terraform through the wire schema rather than the value — **this one is worth attacking**, because phase 4 is scheduled on the assumption it is right.
- The validation depth ceiling is derived rather than a flat 500 (issue #17).

## Deliverable

For each finding: the file and line, what breaks, and a concrete reproduction — input, expected, actual. Rank by whether it can produce a wrong answer in production, not by how untidy it looks. A dropped mark outranks everything else; a wrong answer that still type-checks outranks a crash.

State plainly what you executed. If you only read the code, say so, and treat your own findings as unconfirmed.

If you believe the branch is sound, list the specific attacks you ran that failed to break it. That is the useful form of a clean review.
