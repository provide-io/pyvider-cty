# Handoff — 2026-08-19

Branch `main`, pushed to `gh-origin/main`. Working tree clean — nothing
untracked, nothing staged.

## What was asked

Two requests, in sequence.

1. `/code-review xhigh` over the day's work, then **"take care of all of them"** —
   fix all fifteen findings, not a subset.
2. After that landed: **"continue to analyze"**, which became an open-ended hunt
   for divergences against real go-cty, and then a decision about what to build
   so the hunt keeps paying.

## What was done

Fifteen review findings, then seven further bugs the review did not have, then a
test suite so the class of bug that produced them stops needing a person to go
looking.

### The fifteen review findings — all fixed

`4638fe4` through `f4f5d7d`. The ones with substance:

* **`setproduct` cap ordering.** The 1,000,000-element guard was checked *before*
  the unknown-length branch, so it refused the one shape that cannot be a denial
  of service — the plan-time unknown, which allocates nothing. Moved below.
* **`marks.py`, three faults** from the previous day's two commits: the leaf
  memo stored a mutable `set` (breaking the `frozenset` contract and letting
  `marks.add()` rewrite the answer behind it); the iterative `_strip` rewrite
  memoized only in `_finish`, which a leaf never reaches, so a marked scalar was
  rebuilt on every stdlib call; and `_strip` held per-node bookkeeping for the
  whole walk, 10.8 MB transient to strip a 100k list.
* **`formatdate`'s Go-layout guard** fired on `"2006-2015"`, reading `15` out of
  `2015`. Numeric tokens are now anchored to whole digit runs.
* **`check_docs.py`** executed documentation blocks in the repository root with
  no sandbox — that is where the committed `person.msgpack` came from — and
  skipped every `NameError`, which swallows the commonest form of doc rot.

### Seven further bugs, found by measuring rather than reading

`c62c40a` through `5afc7b9`.

1. **Numbers rounded to 28 digits on every text route.** `_number_to_string`
   called `Decimal.normalize()`, which honours the active context. `2**100`
   reached `terraform show -json` as `…205000`. Four public surfaces; the
   msgpack codec was exact, so the two codecs in this package disagreed about
   the same value and the lossy one was the one state files are written in.
2. **The 154-digit boundary**, characterized while fixing (1). go-cty renders
   through a 512-bit `big.Float`, so it spells `floor(512 × log₁₀2) = 154`
   significant digits. Recorded as a divergence; `5**220` agrees, `5**221` does
   not.
3. **Set composite ordering.** go-cty ranks an element that has run out of
   members *last*; a Python tuple comparison ranks it first. Every set of lists
   or maps with differing lengths re-encoded in a different byte order.
4. **Vacuous refinements written to the wire** — an empty string prefix, a zero
   length lower bound. go-cty records neither.
5. **An unsatisfiable number range accepted** — `3 < x <= 3`.
6. **The sweep parsed go-cty's own numbers through `float64`**, so a go answer of
   `0.1000000000000000055511151231257827` truncated to exactly the `0.1` this
   package returns. It could invent agreement.
7. **A dynamic-position value lost its concrete type**, in two separate places:
   the codec checked knownness before the dynamic branch (unknown), and
   `CtyValue.__attrs_post_init__` cleared the payload of any null (null). go-cty
   writes `[type, value]` for every value at `DynamicPseudoType`.

### The test suite that came out of it

`5afc7b9`. `tests/compatibility/_strategies.py` and
`test_differential_properties.py` — six hypothesis properties driving the live
oracle, `--run-compat` gated, 4.4 s.

## Why this shape

**The gap was structural, not incidental.** `tests/property_based/` had sixteen
hypothesis modules and none drove the oracle; `tests/compatibility/` had ~2,600
tests and none generated an input. A hand-written table only finds a divergence
somebody already suspected, and comparing this package against itself cannot see
a divergence at all — an agreed-upon wrong answer round-trips perfectly. Every
one of bugs 3–7 came from putting the two together.

**Narrow shapes get their own generator and budget.** The first version of the
suite passed the mutation check for two of three reverted fixes and missed the
third: a degenerate refinement is roughly one example in a hundred and twenty
when drawn from the general strategy, so at sixty examples it was a coin flip
dressed as a guard. Sets of sequences and refinements now have dedicated
generators. **Do not fold them back into `cases()`.**

**Verify by mutation, not by assertion.** Each of the three fixes was reverted in
turn to confirm the matching property goes red. A regression suite that cannot
fail is worse than none, because it reads as coverage.

**Measure against Go directly when the harness cannot speak.** Twice the harness
was the wrong instrument and reasoning from its output produced a wrong
conclusion — see the warnings below.

## Traps, all of which cost time here

* **The harness parses every number at 512-bit precision.** `cty msgpack encode`
  uses `big.ParseFloat(text, 10, 512, …)`, so asking it to encode the *text* of a
  `pow` result builds a different value from the precision-53 float `stdlib.Pow`
  actually returns. This produced a confident and wrong conclusion that two
  `KNOWN_DIVERGENCES` entries were false. They are real: go writes nine bytes of
  float64, this package writes nineteen of text. **Probe go-cty directly** —
  `go run` a file inside `tofusoup/src/tofusoup/harness/go/soup-go` picks up the
  right module — before removing a divergence entry.
* **The differential suite cannot see what is lost before the comparison.** It
  spells our value for the harness with `rich`/`dynamic_arg`, so when this
  package drops information at validate time, both sides get the same lossy value
  and agree. `CtyDynamic.validate` discarding a null's concrete type was the
  worked example; `test_dynamic_carries_its_type.py` builds go's side by hand
  because of it. Two guards now cover the gap without an oracle:
  `tests/values/test_nothing_is_lost_before_the_comparison.py` (a `dynamic` must
  keep what it wraps) and `tests/parser/test_a_type_survives_the_wire.py` (a type
  must survive its own wire spelling, which every compat test rests on). Note
  which one has teeth: idempotence alone does *not* catch a stably-lossy value,
  checked by reverting the fix — only the wrapping invariant went red.
* **Two harness-dialect limits are not divergences.** JSON infers `tuple` from an
  array in a dynamic position (use `dynamic_arg`), and a `$`-prefixed map key is
  refused as colliding with the rich sentinel. Both sides encode such a map
  identically.
* **`pre-commit` stashes unstaged files before running `mypy`.** With
  `[tool.uv.sources]` still present at `HEAD`, that reinstated a path pin that
  collides with `provide-testkit`'s own and `uv` refused to resolve. If a commit
  fails in the mypy hook for a dependency reason, check what the stash restored.

## Where things stand

* Gate green: `make lint`, `ruff format --check` (338 files), `mypy src/` (81
  files), `bandit -ll`, `make check-docs`, `make diagrams-check`.
* `uv run pytest tests/` — **2925 passed**.
* `COMPAT_REQUIRE=1 make compat` — **3597 passed, 26 xfailed, 0 XPASS**.
* `VERSION` is `0.5.0`. `CHANGELOG.md` carries 45 breaking changes.

The 26 xfails are 13 distinct divergences, and **none is a bug**: four are GB9c
grapheme cases that resolve themselves when the oracle is rebuilt on Go 1.27
(go-cty already ships the textseg version that agrees with us), five are closed
decisions, two are the accepted `timeadd` calendar range, and one is the
dynamic-null type loss recorded on 2026-08-19.

## Checklist for the next session

1. ~~Decide the debris.~~ **Done 2026-08-19.** Ten `patch_*.py` in the
   repository root (one-shot string-replacement scripts from the 2026-08-18 perf
   work, already applied and superseded) and `scratch/` (a three-file Go probe
   module) are deleted. All eleven were untracked and referenced by nothing, so
   nothing in the build or the suite moved with them.
2. **The release is the only substantive item left**, and it is not local:
   `pyvider` must release at or before `pyvider-cty` 0.5.0, in the wave ordering
   recorded in `GO-CTY-PARITY.md`. Nothing in this repository blocks it.
3. **If hunting more divergences**, run
   `PYVIDER_COMPAT_EXAMPLES=800 COMPAT_REQUIRE=1 make compat`. Both property
   modules read that knob; the committed defaults (60, and 120 for the narrow
   generators) are sized to keep the suite in seconds, and finding something new
   generally means running wider than a regression guard needs to. A run at 800
   takes about two and a half minutes and is clean as of 2026-08-19.

   The semantic surfaces are now covered too — `Value.Equals` and its symmetry,
   `convert` including refusals, `Value.Range`, and the mark-path round trip are
   in `test_differential_semantics.py`, and `unify` is swept at 969 combinations
   in `test_unify_oracle.py` — that sweep found 17 divergences on a surface
   nothing had ever compared, all since fixed.

   **The one substantial gap left**: the 83 stdlib functions are compared only
   against 444 hand-written argument rows, an average of 5.3 each, and 31 of
   them have two or fewer (`log` has one). No generated argument has ever
   reached them. `SIGNATURES` carries each function's parameter types, including
   `var_param` and the null/unknown/dynamic flags, so conforming arguments can
   be generated per function rather than guessed. That is the same technique
   that found every divergence on 2026-08-19, aimed at the last surface it has
   not been aimed at.
4. **Do not file upstream go-cty issues.** Decided 2026-08-19; the item is closed
   in `GO-CTY-PARITY.md`. Three findings were drafted and two of the drafts
   deleted; `UPSTREAM-GO-CTY-EQUALS-NONDETERMINISM.md` is kept as the record of
   why this library diverges deliberately, not as a thing to send.
5. ~~`CtyDynamic.validate` dropping a null's concrete type.~~ **Fixed
   2026-08-19.** The loss was not in `validate` but in
   `CtyValue.__attrs_post_init__`, which clears the payload of any null — and at
   `dynamic` the payload is the type. The invariant now exempts a dynamic
   standing in front of a concrete value. Blast radius turned out to be nil: the
   full suite passed unchanged, and the strict xfail became a passing test.

<!-- 🌊🪢🔚 -->
