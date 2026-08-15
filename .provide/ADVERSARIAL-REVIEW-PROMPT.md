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

The branch claims to fix three bugs, all in the handling of *marks* — the mechanism cty uses to flag values as sensitive:

1. Stdlib functions discarded the marks their arguments carried, so a sensitive value run through `upper()` or `join()` came back unflagged.
2. `validate()` discarded marks on collection elements, so a sensitive value placed inside a list lost its flag at construction.
3. `contains()` returned a definite `False` for a collection containing unknown elements, where the honest answer is unknown.

## Ground rules

**Trust nothing in the repository's own account of itself.** `.provide/GO-CTY-PARITY.md`, the commit messages, and the code comments were all written by the implementer and are part of what you are reviewing, not evidence about it. Where they assert a behaviour, go and run that behaviour.

**Prefer the interpreter to reading.** The implementer's two worst errors on this branch both came from reasoning about code instead of executing it. `uv run python -c "..."` against real values is worth more than any amount of careful reading. The test suite runs with `uv run pytest -q` and takes about 3.5 minutes.

**Compare against go-cty directly.** For any behavioural claim, find the corresponding code in `/Users/tim/code/tf/go-cty` and check it yourself rather than accepting a summary. Note that go-cty's Go implementation sometimes needs an explicit branch where Python gets the same result implicitly — a missing code path in the Python is not by itself a defect.

## Known failure modes on this branch

These are areas where the implementer has already been wrong at least once. Assume the same class of error recurs elsewhere.

**Claimed a gap that did not exist.** Three "behavioural fixes" (`Contains` null argument, `Merge` all-null, `element` negative tuple index) were filed from go-cty's CHANGELOG describing bugs *go-cty* had. pyvider is an independent implementation and never had them. A msgpack infinity gap was filed the same way. Both were withdrawn.
→ *Check the inverse: did the implementer declare something already-correct that is in fact broken?* The "Confirmed parity" list in the tracker is the obvious place to attack — it is a list of things asserted to work, mostly without tests written to prove it.

**Broke a distant test with a local change.** Adding a decorator to `validate` put an extra Python frame on the recursive descent, cutting maximum nesting depth from 493 to 329 and breaking a deep-nesting test. The fix moves mark handling inside `with_recursion_detection` for recursing types while leaf types keep a standalone decorator.
→ *Attack that split.* Is it actually correct for every type? Is there a type that recurses but is treated as a leaf, or vice versa? What is the depth limit now, measured rather than claimed?

**Relied on `==` where `==` does not mean what it looks like.** `_strip` in `src/pyvider/cty/functions/_marks.py` originally decided "did anything change" by comparing values. `CtyValue.__eq__` delegates to a `CtyCapsuleWithOps`' custom `equal_fn`, which ignores marks — so the comparison reported "unchanged" for a capsule whose mark had just been stripped. Now uses identity.
→ *Look for other places on this branch where `==`, `in`, or a set/dict operation on `CtyValue` carries an assumption about what equality includes.* Marks and unknown-ness both participate in `__eq__` for most types and not for capsules with custom ops.

## Specific things to attack

**`src/pyvider/cty/functions/_marks.py`**

- `_children()` decides what is a container by looking at the runtime payload — `tuple`, `dict`, or a nested `CtyValue`. A capsule wrapping a Python tuple or dict is indistinguishable from a collection by that test. Construct one. What happens? Is the claimed harmlessness real?
- `_collect()` walks the entire argument structure on every stdlib call, including when nothing is marked. Measure the cost on a large nested value. Is it acceptable, and does the codebase have a benchmark that would have caught a regression?
- The decorator is applied to all 68 exported functions. Is there an exported function for which stripping marks from arguments is *wrong* — one that legitimately needs to see them?

**`src/pyvider/cty/validation/marks.py` and `recursion.py`**

- Mark re-application happens in two places for stack-depth reasons. Find a code path where a `validate` is reached through neither.
- `preserves_marks` is typed as an identity on the function type. Does that actually preserve the signature for every decorated method, or does it silently widen something?
- What happens when `validate` raises? Are marks handled consistently on the error path?

**`src/pyvider/cty/functions/collection_functions.py` — `contains`**

- Compare line by line against `ContainsFunc` in `cty/function/stdlib/collection.go`. The implementations differ deliberately in one place (null collection: go-cty raises, this returns unknown). Is anything *else* different, and was that difference intended?
- Sets, tuples, and lists all reach this code. Does the unknown-tracking logic hold for a set, where element identity works differently?

**The tests themselves**

- `tests/functions/test_mark_propagation.py` builds a fixture table of one call per exported function and marks the first argument. Are any of those fixtures degenerate — arguments that make the function short-circuit before the interesting path, so the test passes without exercising anything?
- Are there tests that would still pass if the production fix were reverted? Revert a hunk and run the suite; anything still green was not testing that hunk.
- `test_every_exported_function_has_a_fixture` asserts the table covers `__all__`. Does that actually prevent a gap, or can a function be covered by a fixture that never reaches it?

## What is deliberately not done

Do not report these as omissions; do challenge the reasoning if it is wrong.

- Serializing a marked value still silently drops the marks, where go-cty raises. Deferred: it needs a one-line change in the `pyvider` repo first (`src/pyvider/conversion/marshaler.py:118`), or every sensitive attribute crashes at `terraform apply`.
- `contains` on a null collection returns unknown where go-cty raises. Deferred to the same strictness work.
- No deep mark operations (`UnmarkDeep`, `MarkWithPaths`), no `PathSet`, no `Walk`/`Transform`. Those are separate unstarted issues.

## Deliverable

For each finding: the file and line, what breaks, and a concrete reproduction — input, expected, actual. Rank by whether it can produce a wrong answer in production, not by how untidy it looks.

State plainly what you executed. If you only read the code, say so, and treat your own findings as unconfirmed.

If you believe the branch is sound, list the specific attacks you ran that failed to break it. That is the useful form of a clean review.
