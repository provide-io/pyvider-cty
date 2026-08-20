# Handoff — 2026-08-20 (security review, CI red, and the named follow-ups)

Branch `main`, clean at `e59104b`. Everything below is landed and pushed.

## What was asked

A `/security-review` of the 0.5.0 branch, then — in the user's order — the
recursion bug it led to, the `/tmp` cleanup, the four items the previous
handoff named as future work, and an explanation of the `CtyObject`
required-attribute question. One item is deliberately not done and needs a
decision; it is the last section.

## The security review

One candidate, investigated and then filtered out as a security finding while
still being a real defect: `convert()` into a `CtyCapsuleWithOps` declaring
`convert_to_fn` dropped the source's marks. It was the only one of sixteen
returns in that function that did — `convert_to_fn` hands back a raw Python
object, so `@preserves_marks` had nothing to copy from.

Not exploitable — no attacker-controlled trigger, no non-test callers, capsules
are not wire-schema-representable — but the consequence was real and measured:
`cty_to_msgpack` emitted `b'\xc4\x07hunter2'` for a value it had been refusing.
Fixed in `897c95b`, and the invariant is now held by a parametrized sweep over
fifteen source/target shapes reaching every return in `convert()`, rather than
by the comment three branches above it that had not been enough.

## CI had been red on every run, for two unrelated reasons

Worth stating plainly: the local gate was green throughout and nobody had looked
at Actions.

**One was ours and is fixed.** `CtyTuple.equal` and `CtyObject.equal` recursed
at two frames a level, and `equal` is on the *construction* path, so a 400-deep
tuple could not be built. It raised on Python 3.11 and passed on 3.13 — 800
frames against a limit of 1000 — and `requires-python` is 3.11.

The collection types had met this and half-fixed it, flattening the linear chain
of same-kind containers and recording that branching shapes were "bounded by the
schema's own breadth". A single-element tuple nested 400 deep is not. All five
container types now go through `base.equal_iteratively`, an explicit-stack walk,
with each type answering `_equal_shallow` for the part of its equality that is
not a child comparison.

`tests/types/test_type_equality_is_iterative.py` does not depend on the
interpreter: it lowers the recursion limit to just above the stack the test is
standing on, so a recursive implementation fails everywhere.

**The other is in `tofusoup` and is the open decision.** See the last section.

## The four named follow-ups

**Generated coverage at the traversal surfaces.** `walk`, `transform`,
`unknown_as_null` and `mark_paths` were the last four held by tables alone.
`test_traversal_properties.py` drives all of them from `_strategies.cases()`.

No library divergence — the traversals were right — but the run found a
comparison-channel fault, the fourth here and the reason it is worth recording:
`test_walk_oracle`'s `upper` rewrite used `str.upper()`, and Python applies full
case mapping where Go maps one code point at a time, so the `fi` ligature
expanded to `FI` here and stayed put there. The library's own `upper` had always
used `simple_upper`; only the test's stand-in was wrong, and no hand-written
table contains a ligature.

Two normalisations were needed to ask both sides the same question: a `dynamic`
position is unwrapped, and a result type is compared as `ImpliedType()` spells
it. Both are written down where they are made.

**Paired arguments in the stdlib fuzz.** Measured first: `setintersection`
answered non-empty in 12% of 400 draws, `setsubtract` 16%, `equal` True in 11%.
Sets now come from a shared pool half the time, `equal` pairs a value with a
rebuilt copy, `merge` collides keys, `distinct` draws from a small pool.
Re-measured at 25%, 25%, 45%. Clean at 200 examples per function.

**The `timeadd` residual is closed.** The instant is a whole-second `datetime`
plus an integer nanosecond remainder, the shift is an integer nanosecond count,
and nothing rounds. Verified against the oracle on the cases that used to
differ.

**The examples went from 11 files / 723 lines to 17 / 1491.** The gap was in the
middle: nothing covered unknowns and refinements, nothing covered conversion or
unification, and one file demonstrated one stdlib function out of 83. The runner
discovers files now instead of carrying a hand-maintained list.

## The `CtyObject` question, answered

A *missing* required attribute is still rejected (`object.py:118`). What is
deliberately not rejected is a **present-but-null** non-optional attribute, and
`object.py:137-152` gives the reason: go-cty has no nullability in object types,
and everything crossing the provider protocol is marshalled with
`ImpliedType()`, which strips optional attributes recursively — so nulls arrive
for unset attributes constantly and restoring the check would reject state
go-cty itself writes. The "four of five validation paths" from the review is
about **pyvider**, not this package. Correct as written; the enforcement gap to
chase is next door.

## The one open decision, which is cross-repo

The `compat` CI job cannot build the harness:

```
main.go:9:2: github.com/hashicorp/go-plugin@v1.7.0:
  replacement directory /Users/tim/code/gh/hashicorp/go-plugin does not exist
```

tofusoup `main` carries a `replace` pointing at a laptop. The local
`feat/tfplugin-driver` branch has already dropped it — its only `replace` is the
relative `../../proto/kv`.

Underneath that is a bigger mismatch. `cty_call.go`, `cty_ops.go`, `cty_rich.go`
and `cty_unify.go` — 2,645 lines, the entire surface this suite calls — exist
**only on the feature branch**. Local `make compat` (3,691 passed) measures
against `feat/tfplugin-driver`; CI checks out a `main` from 2026-04-23 that has
none of it.

So the workflow's unpinned `provide-io/tofusoup` checkout is a symptom, not the
cause, and pinning a SHA now would pin the wrong oracle. The order has to be:
land the harness work on tofusoup `main` (or drop the `replace` there), then pin
the checkout in `.github/workflows/ci.yml:54`. Both are Tim's calls.

## Smaller things done on the way

* The harness binary moved out of `/tmp`. `_oracle.py` used to *execute*
  `/tmp/soup-go` as a last resort — no file created, so the sticky bit does not
  help — and anyone on a shared machine could have planted one. Both it and
  `run_compat.py` use `.compat/soup-go` now, gitignored.
* `_traversal.py` holds the vocabulary two oracle modules had each copied; the
  copies had already drifted on whether a map key's number was normalised.
* `_oracle.examples()` replaces three copies of the example-budget helper.
* The stale worktree at `provide-workspace/repos/pyvider-cty` was confirmed
  merged and clean, and removed, along with the merged `feat/go-cty-parity`
  branch.

## For the next session

1. **The cross-repo blocker above.** Nothing else in CI moves until it does.
2. **The 0.5.0 release**, once CI is green. VERSION already reads `0.5.0` and the
   CHANGELOG is closed out. Still cross-repo: `pyvider` releases at or before
   `pyvider-cty`.
3. **Four more recursive surfaces**, same class as the one fixed here, measured
   at depth 400 on 3.11 and still failing: `CtyType.__eq__` (attrs-generated, so
   it does not route through `equal`), `usable_as`, `__str__`/`__repr__`, and
   `CtyValue.__eq__`. None is on the construction path, so none is failing CI —
   but `usable_as` and value equality are hot, and a deeply nested value can
   still raise from them.
