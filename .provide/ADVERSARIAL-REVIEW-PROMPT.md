# Adversarial review prompt

Paste everything below the line into a fresh agent session with no prior context.

---

You are reviewing a branch adversarially. Your job is to find what is wrong with it, not to confirm that it is right. A review that finds nothing is only useful if you can show what you tried.

## The work

Repository: `/Volumes/data/pyv/pyvider-cty`
Branch: `feat/go-cty-parity` (local only, never pushed, no PR)
Base: `gh-origin/main`

Reference implementation for comparison: a `go-cty` checkout at `/Users/tim/code/tf/go-cty`, at `v1.19.0-1-g0d1eb26`. This project aims to be a Python implementation of it.

Start with `git log --oneline gh-origin/main..HEAD` and `git diff gh-origin/main...HEAD`.

The branch is about *marks* — the mechanism cty uses to flag a value as sensitive. Terraform relies on marks to redact secrets from plan output, logs and state display, so **the failure that matters is a value entering a path marked and leaving it unmarked**. That is a disclosure bug, not a tidiness bug. Over-marking fails safe.

It claims to fix:

1. Stdlib functions discarded the marks their arguments carried, so a sensitive value run through `upper()` or `join()` came back unflagged.
2. `validate()` discarded marks on collection elements, so a sensitive value placed inside a list lost its flag at construction.
3. `contains()` returned a definite `False` for a collection whose contents are not fully known.
4. The recursion guard's early exits returned unmarked unknowns.
5. The deep-mark walk skipped sets entirely, and existed in three divergent copies.
6. Set elements could carry marks, which de-duplication then silently discarded.

## Ground rules

**Trust nothing in the repository's own account of itself.** `.provide/GO-CTY-PARITY.md`, the commit messages, and the code comments were all written by the implementer and are part of what you are reviewing, not evidence about it. Where they assert a behaviour, go and run that behaviour.

**Prefer the interpreter to reading.** Every serious error on this branch came from reasoning about code instead of executing it. `uv run python -c "..."` against real values is worth more than any amount of careful reading. The suite runs with `uv run pytest -q` in about 3.5 minutes.

**Differential testing is the highest-yield technique here.** Export the base tree (`git archive gh-origin/main | tar -x -C <scratch>`) and run the same scenario matrix against both trees. Write your mark detector *independently* — do not use `pyvider.cty.marks` to check whether `pyvider.cty.marks` is right.

**Compare against go-cty directly.** For any behavioural claim, find the corresponding code in `/Users/tim/code/tf/go-cty` and check it yourself. Note that Go sometimes needs an explicit branch where Python gets the same result implicitly — a missing code path is not by itself a defect.

## Known failure modes on this branch

Four review rounds have already happened. Every one found real bugs, and **three of the four found bugs introduced by the previous round's fix**. Assume that pattern continues into whatever you are looking at.

**Claimed a gap that did not exist.** Several "behavioural fixes" were filed from go-cty's CHANGELOG describing bugs *go-cty* had; pyvider is an independent implementation and never had them. All withdrawn.
→ *Check the inverse: is something on the tracker's "Confirmed parity" list in fact broken?* It is a list of assertions, mostly without tests proving them.

**Broke a distant thing with a local change.** Adding a decorator to `validate` put an extra frame on the recursive descent and cut maximum nesting depth from 493 to 329, under the 500 the config advertises. Mark handling now lives inside `with_recursion_detection` for recursing types while leaf types keep a standalone decorator.
→ *Attack that split.* Is there a type that recurses but is treated as a leaf, or vice versa? What is the depth limit now, measured rather than claimed?

**Relied on `==` where `==` does not mean what it looks like.** `_strip` decided "did anything change" by comparing values. `CtyValue.__eq__` delegates to a `CtyCapsuleWithOps`' custom `equal_fn`, which ignores marks, so it reported "unchanged" for a capsule whose mark had just been stripped. Now uses identity.
→ *Look for other places where `==`, `in`, or a set/dict operation on `CtyValue` assumes what equality includes.*

**Matched on the container types that came to mind.** The deep walk matched `tuple` and `dict` and therefore skipped every set — a validated `CtySet` holds a `frozenset`. The same blindspot existed in three separate copies of the walk, each wrong differently.
→ *Enumerate every payload shape a `CtyValue` can actually hold and check the walk against all of them, rather than against the ones the code names.*

**Fixed correctness and introduced a performance cliff.** Collecting marks before the no-marks fast path took `length()` on a 200k list from 0.005 ms to 41 ms per call, across ~60 functions. Fixed by memoizing on `CtyValue._deep_marks`.
→ *Measure. Are there other paths where the mark work made an O(1) operation O(n)?*

**Wrote down an invariant that was not true.** The memo was justified as "CtyValue is immutable, so the answer cannot go stale". Freezing an attrs class freezes the reference to the payload, not the payload — maps and objects hold plain dicts. A stale under-reporting memo was reproducible. The walk now refuses to memoize any subtree containing a mutable container.
→ *Attack the replacement.* Is `_MUTABLE_CONTAINERS` complete? Can a memo still be taken over something that can change? Can a cached descendant answer for a subtree that has since moved?

## Specific things to attack

**`src/pyvider/cty/marks.py` — everything now depends on this one walk**

- `_walk_marks` decides both the marks and whether the answer is memoizable. Find a value where those two answers disagree with reality.
- A cached descendant short-circuits the walk and answers for its whole subtree. Can a value be cached and then reused inside a *different* parent whose contents changed?
- `_children()` infers container shape from the runtime payload. A capsule wrapping a Python tuple, dict or frozenset is indistinguishable from a collection by that test. Construct one. What happens?
- `_strip` rebuilds a set payload with `frozenset(...)`, which can silently drop elements that differed only by their marks. Reach that path and show whether it can change a result.

**`src/pyvider/cty/types/collections/set.py` — behavioural change**

- Set elements no longer carry marks; the union is hoisted onto the set, as go-cty's `SetVal` does. Verify against `cty/value_init.go` and `cty/set_internals.go`.
- Find a consumer anywhere under `/Volumes/data/pyv/` that reads sensitivity off a set's *elements*. If one exists on a redaction path, this change declassifies it.
- Does anything else construct a `CtyValue` with a set payload while bypassing `CtySet.validate`, and so keep marked elements?

**`src/pyvider/cty/validation/recursion.py`**

- Mark re-application happens in two places for stack-depth reasons. Find a `validate` reached through neither.
- Every guard exit is supposed to carry the input's deep marks. Enumerate the exits and drive each one.
- `except RecursionError` is scoped by `MIN_DEPTH_TO_OWN_RECURSION_ERROR`. Can a genuine validator overflow occur *below* that depth and get re-raised as a crash, or unrelated code overflow above it and be swallowed into an unknown?
- What happens when `validate` raises a normal validation error? Are marks handled consistently on the error path?

**`src/pyvider/cty/functions/_marks.py`**

- Is there an exported function for which stripping marks from arguments is *wrong* — one that legitimately needs to see them?
- Can a result escape without the union re-applied? Non-`CtyValue` returns, containers, generators, in-place mutation of an argument.

**`src/pyvider/cty/functions/collection_functions.py` — `contains`**

- Compare line by line against `ContainsFunc` in `cty/function/stdlib/collection.go`. Two differences are deliberate (null collection: go-cty raises; partially-unknown elements: this is vaguer than go-cty's three-valued `Equals`). Is anything *else* different?
- `is_wholly_known()` is new. Does it agree with go-cty's `IsWhollyKnown` on nulls, capsules, and dynamic values?

**The tests**

- Are any fixtures degenerate — arguments that short-circuit before the interesting path, so the test passes without exercising anything?
- Revert a production hunk and run the suite. Anything still green was not testing that hunk.
- The mark tests assert marks are *present*. Do any of them pass because something over-marks rather than because the value is correct?

## What is deliberately not done

Do not report these as omissions; do challenge the reasoning if it is wrong.

- Serializing a marked value still silently drops marks, where go-cty raises. Needs a one-line change in the `pyvider` repo first (`src/pyvider/conversion/marshaler.py:118`), or every sensitive attribute crashes at `terraform apply`.
- `contains` on a null collection returns unknown where go-cty raises. Deferred to the same strictness work.
- `contains` is vaguer than go-cty for elements that are known but hold unknowns. Closing it needs a three-valued `Equals`.
- The validation depth ceiling is ~495 against a documented 500 (issue #17). The crash was fixed; the shortfall was not.
- No `MarkWithPaths`, no `PathSet`, no `Walk`/`Transform`. Separate unstarted issues.

## Deliverable

For each finding: the file and line, what breaks, and a concrete reproduction — input, expected, actual. Rank by whether it can produce a wrong answer in production, not by how untidy it looks. A dropped mark outranks everything else.

State plainly what you executed. If you only read the code, say so, and treat your own findings as unconfirmed.

If you believe the branch is sound, list the specific attacks you ran that failed to break it. That is the useful form of a clean review.
