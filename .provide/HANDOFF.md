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

## The cross-repo blocker, closed

CI is green for the first time, differential job included: **3,691 passed, 26
xfailed** on the runner, matching the local number exactly.

Two things were wrong and the unpinned checkout was hiding the second.

`soup-go`'s `go.mod` carried `replace github.com/hashicorp/go-plugin =>
/Users/tim/code/gh/hashicorp/go-plugin`, a module path pointing at one laptop,
so `go build` succeeded there and nowhere else. The replaced checkout was v1.7.0
plus three upstream chore commits and one *uncommitted* six-line patch to
`server.go` — extracting a server certificate from a custom TLSProvider so
AutoMTLS clients can use one. Nothing in the `cty` commands touches it; it is
the tfplugin driver's path. Stashed (`stash@{0}` on branch
`fixing-up-cert-handling`) rather than forked, on Tim's call, and upstream
v1.7.0 builds clean with `go test ./...` passing. Fixed in tofusoup `9d31249`.

Underneath: `cty_call.go`, `cty_ops.go`, `cty_rich.go` and `cty_unify.go` —
2,645 lines, every command this suite drives — exist only on
`feat/tfplugin-driver`. So CI had been pointed at an April harness that could
not have answered the suite even if it had compiled, while local runs measured
against a working one. **The two were never checking the same thing.**

`feat/tfplugin-driver` has since landed on tofusoup `main` (PR #3, merge commit
`32c0a10`), and `.github/workflows/ci.yml` pins that. A commit, not a branch,
for the reason the Go version pin beside it gives: the oracle decides what
parity *means*, so a suite measuring against a moving harness has answers that
change with no commit here to say which. Bump it deliberately, together with
whatever divergence a new harness reveals.

Two things had to be fixed in tofusoup before that merge, and neither had ever
been seen because its CI triggers only on `main`/`develop` and PRs to them --
so twenty commits had accumulated without CI once running on them. `uv sync`
failed outright on the sibling path dependencies (`no-sources: true` now, the
same flag and the same reason as here), and bandit failed the Security job on a
hardcoded `/tmp` fallback for a subprocess's `TMPDIR` (`tempfile.gettempdir()`
now). tofusoup's CI is green.

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

1. **The 0.5.0 release.** Nothing blocks it now: VERSION reads `0.5.0`, the
   CHANGELOG is closed out, and CI is green end to end. Still cross-repo —
   `pyvider` releases at or before `pyvider-cty` — so the ordering is Tim's.
2. **Bump the harness pin** when the oracle gains a command or a fix worth
   measuring against -- deliberately, with whatever it reveals.
3. **Done, on 2026-08-20**: the five further recursive surfaces are closed —
   `CtyType.__eq__`, `CtyType.__hash__`, `usable_as`, `__str__`, and both
   `__eq__` and `__hash__` on `CtyValue`. Only `__repr__` is left recursive, on
   purpose and with a test saying so. Folding the value hash also turned up a
   live bug: a tuple was not counted as a container there, so its payload
   skipped the element-hashing that routes a capsule through its `hash_fn`.
