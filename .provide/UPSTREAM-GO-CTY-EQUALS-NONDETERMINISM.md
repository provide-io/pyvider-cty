# Upstream issue draft — go-cty `Value.Equals` non-determinism

Target: https://github.com/zclconf/go-cty/issues (not yet filed).
Found 2026-08-17 during the parity work on `feat/go-cty-parity`; measured against
go-cty at `v1.19.0-1-g0d1eb26`. pyvider-cty's position is recorded at the bottom.
Everything between the rules is the issue body, ready to paste.

---

## `Value.Equals` is non-deterministic for objects and maps holding both an unknown and a definite difference

### Summary

When an object or map value contains at least one unknown member *and* at least
one member that definitely differs, `Value.Equals` returns either
`cty.False` or an unknown `cty.Bool` depending on Go's randomized map iteration
order. The same two values, compared twice in the same process, can give
different answers.

### Reproduction

```go
package main

import (
	"fmt"

	"github.com/zclconf/go-cty/cty"
)

func describe(v cty.Value) string {
	if !v.IsKnown() {
		return "unknown"
	}
	return fmt.Sprintf("%v", v.True())
}

func main() {
	objLeft := cty.ObjectVal(map[string]cty.Value{
		"a": cty.UnknownVal(cty.String),
		"b": cty.StringVal("z"),
	})
	objRight := cty.ObjectVal(map[string]cty.Value{
		"a": cty.StringVal("x"),
		"b": cty.StringVal("y"),
	})

	mapLeft := cty.MapVal(map[string]cty.Value{
		"a": cty.UnknownVal(cty.String),
		"b": cty.StringVal("z"),
	})
	mapRight := cty.MapVal(map[string]cty.Value{
		"a": cty.StringVal("x"),
		"b": cty.StringVal("y"),
	})

	objCounts := map[string]int{}
	mapCounts := map[string]int{}
	for i := 0; i < 1000; i++ {
		objCounts[describe(objLeft.Equals(objRight))]++
		mapCounts[describe(mapLeft.Equals(mapRight))]++
	}
	fmt.Println("object:", objCounts)
	fmt.Println("map:   ", mapCounts)
}
```

Observed on v1.19.0 (darwin/arm64, single process):

```
object: map[false:124 unknown:876]
map:    map[false:129 unknown:871]
```

### Cause

In `cty/value_ops.go`, the object arm of `Equals` iterates
`for attr, aty := range oty.AttrTypes` and the map arm iterates
`for k := range val.v.(map[string]any)` — both randomized Go map iteration.
Inside the loop, the first *unknown* member comparison returns
`UnknownVal(Bool)` immediately, while the first *definitely unequal* member
sets `result = false` and breaks:

```go
eq := lhs.Equals(rhs)
if !eq.IsKnown() {
    return unknownResult()
}
if eq.False() {
    result = false
    break
}
```

Whichever kind of member the randomized order visits first decides the answer.
The list and tuple arms have the same early returns but iterate in index order,
so they are deterministic (an unknown at a lower index wins over a definite
difference at a higher one).

### Impact

`Equals` backs `stdlib.Equal`, which backs `==`/`!=` in HCL. In Terraform, a
config expression comparing two such values can evaluate to `false` on one plan
and `(known after apply)` on the next, with identical state and configuration.
If the result feeds `count` or `for_each`, one plan run errors with "Invalid
count argument … known after apply" and the retry succeeds. Both answers are
individually sound; the flip between them is the problem.

### Suggested fix

Let a definite difference win. A member that definitely differs cannot be
undone by whatever the unknown members resolve to, so `False` is correct
whenever any member comparison is definitely false, regardless of visit order:

```go
result = true
sawUnknown := false
for attr, aty := range oty.AttrTypes {
    // ...
    eq := lhs.Equals(rhs)
    if !eq.IsKnown() {
        sawUnknown = true
        continue
    }
    if eq.False() {
        result = false
        break
    }
}
if result && sawUnknown {
    return unknownResult()
}
```

This removes the non-determinism without ever producing an answer the current
code cannot produce — it deterministically selects the more informative member
of the existing answer set. The same change to the map arm.

Related but deliberately out of scope: the list/tuple arms deterministically
return unknown at the first unknown index even when a later index definitely
differs. Applying difference-wins there too would be more consistent, but it
changes a currently-deterministic behaviour, so this issue only proposes fixing
the arms that are random today.

---

## pyvider-cty's position (not part of the issue)

Decided 2026-08-17: pyvider-cty answers **deterministic false** for the
object/map case — the suggested-fix semantics — because matching a coin flip is
not parity, and false is the more informative sound member of go-cty's answer
set. `tests/compatibility/test_equality_oracle.py::
test_an_object_with_both_an_unknown_and_a_difference` pins exactly that: go-cty
never answers true, this library is deterministic, and its answer is one go-cty
also gives.

For lists and tuples go-cty *is* deterministic (first-unknown-wins in index
order), so there parity is well-defined and pyvider-cty should match it
exactly. That work is tracked in `GO-CTY-PARITY.md` with the container
unknown-collapse fix, which currently prevents these comparisons from being
reached at all.
