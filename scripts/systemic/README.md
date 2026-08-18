# The systemic test

Everything else in this repository tests pyvider-cty. This tests the *suite*:
a wheel-built 0.5 stack, a real Terraform binary, a real gRPC plugin
handshake, resources created on disk, and a second plan that has to come back
empty.

It exists because the two things that make day-to-day development pleasant
also make it unrepresentative. Every package here resolves its siblings as an
**editable path dependency**, so a suite run measures the working tree rather
than anything installable; and the parity tracker records that overlay hiding
a live bug in both directions — once making failures invisible, once making a
green run unreproducible for anyone without it. A release carrying forty-three
breaking changes is exactly when that stops being acceptable.

## Running it

```bash
python scripts/systemic/build_stack.py     # build wheels, install into a clean venv
python scripts/systemic/run_fixture.py     # plan, apply, re-plan, destroy
```

`build_stack.py` walks the declared dependencies of `pyvider-cty`, `pyvider`
and `pyvider-components`, finds every workspace package they reach, builds a
wheel for each, and installs those into an empty environment under
`.systemic/`. Anything not developed in this workspace resolves from PyPI at
whatever the current version is — the suite should work against today's
dependencies, not against a lockfile somebody refreshed a year ago. It then
checks that no module imports from a source tree, because an editable install
leaking in makes the whole exercise measure the overlay it was built to avoid.

`run_fixture.py` drives `scripts/systemic/fixture/` against that stack. It
places a `.venv` symlink and a `VERSION` file (the installer runs in
development mode and takes both from the working directory), runs
`pyvider install`, then `init`, `plan`, `apply`, a second `plan`, and
`destroy`, removing its scratch files afterwards. Use `--plan-only` to stop
early, `--keep` to leave the state behind for inspection.

**The second plan is the point.** It reads state back through the wire codec
and compares it with what the resources report. Anything that does not survive
that round trip shows up as a diff that never goes away, and `-detailed-exitcode`
turns it into a failure instead of a paragraph nobody reads.

## What the fixture covers

`fixture/main.tf` is weighted toward behaviour that changed in 0.5, and each
claim is an assertion rather than an output nobody checks:

| Checked | Why it is here |
|---|---|
| `divide(1, 0)` is `+Inf` | Terraform's own operator answers `+Inf`; this was the last disagreement between the components function and the operator |
| `add(0.1, 0.2) == 0.3` | arithmetic is exact `Decimal`, not float64 |
| `length("👨‍👩‍👧‍👦") == 1` | strings measure in grapheme clusters, not code points |
| `upper("straße") == "STRAßE"` | Go's simple case mapping, not Python's full mapping |
| `format("%05.2f\|%s", […])` | printf verbs render rather than reaching state as literal text |
| a resource depending on another's attribute | an unknown at plan time that has to survive the round trip and resolve at apply |

## Two things worth knowing

**An infinity cannot go in an output.** `divide(1, 0)` is a positive infinity,
and serializing one into plan JSON fails with `cannot serialize infinity as
JSON`. That is not a provider limitation: Terraform's own `1 / 0` in an output
fails identically, which is the strongest available confirmation that this
provider's `divide` agrees with the operator. The fixture asserts on the value
and outputs a boolean.

**Do not run this while anything else is writing to the workspace.** Building
picked up a wheel stamped `0.4.0` while a sibling process was mutating a
package mid-build, and a stale `build/` directory produces the same result
silently. `build_stack.py` clears each package's `build/` and `dist/` first and
refuses any wheel whose version does not match its `VERSION` file, but the
underlying rule is the one already written into CONTRIBUTING for test runs: a
run that spans a tree change is void rather than data.
