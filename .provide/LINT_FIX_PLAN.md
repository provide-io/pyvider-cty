# Lint Fix Plan: pyvider-cty

**Total Violations:** 57
**Generated:** 2025-11-16
**Priority:** HIGH (core type system)

---

## Violation Summary

| Code | Count | Description | Auto-fixable |
|------|-------|-------------|--------------|
| E741 | 33 | Ambiguous variable name (`l`) | Manual |
| RUF043 | 5 | Regex pattern metacharacter issues | Manual |
| SIM108 | 3 | Use ternary operator | Yes (unsafe) |
| SIM105 | 2 | Use contextlib.suppress | Yes (unsafe) |
| F841 | 2 | Unused variable assigned | Manual |
| B007 | 2 | Unused loop control variable | Manual |
| ANN201 | 2 | Missing return type annotation | Manual |
| SIM118 | 1 | Use key in dict | Yes (unsafe) |
| RUF005 | 1 | Collection literal concatenation | Yes (unsafe) |
| F821 | 1 | Undefined name | Manual |
| C901 | 1 | Function too complex | Manual |
| B905 | 1 | zip() without explicit strict | Manual |
| B017 | 1 | Blind exception assertion | Manual |
| B004 | 1 | Using hasattr with __call__ | Manual |
| ANN001 | 1 | Missing type annotation | Manual |

---

## Primary Issue: Ambiguous Variable Names (E741)

**33 violations - ALL for variable `l` (lowercase L)**

The `l` variable looks like `1` (one) in many fonts, causing readability issues.

### Location

All in test files under `tests/functions/`:
- `test_collection_creation_functions.py`
- Other function test files

### Fix Pattern

```python
# BEFORE - Ambiguous 'l' looks like '1'
l = CtyList(element_type=CtyString()).validate(["a", "b", "c"])
assert element(l, CtyNumber().validate(1)).raw_value == "b"

# AFTER - Clear variable name
test_list = CtyList(element_type=CtyString()).validate(["a", "b", "c"])
assert element(test_list, CtyNumber().validate(1)).raw_value == "b"

# OR use more descriptive names:
cty_list = CtyList(...)
string_list = CtyList(...)
items = CtyList(...)
```

### Bulk Fix Command

```bash
# Find and replace in test files (review before applying!)
cd pyvider-cty/tests
# Rename 'l' to 'test_list' in collection tests
sed -i '' 's/\bl = /test_list = /g' functions/*.py
sed -i '' 's/\bl,/test_list,/g' functions/*.py
sed -i '' 's/(l)/test_list)/g' functions/*.py
sed -i '' 's/(l,/(test_list,/g' functions/*.py
```

**Estimated time:** 15-20 minutes

---

## Fix Strategy by Category

### Phase 1: Quick Wins (Auto-fixable)

**Estimated time:** 5 minutes

```bash
cd /Users/tim/code/gh/provide-io/pyvider-cty
ruff check --fix .
ruff check --fix --unsafe-fixes .
```

Auto-fixes:
- SIM108 (3) - Ternary operators
- SIM105 (2) - contextlib.suppress
- SIM118 (1) - dict key membership
- RUF005 (1) - Collection concatenation

**Expected reduction:** ~7 violations (12%)

---

### Phase 2: Rename Ambiguous Variables (E741)

**Estimated time:** 20 minutes
**33 violations**

**Systematic rename:**
1. `l` → `test_list` or `cty_list` or `items`
2. Ensure all references are updated
3. Run tests to verify

**Files:**
- `tests/functions/test_collection_creation_functions.py`

---

### Phase 3: Regex Pattern Issues (RUF043)

**Location:** `tests/coverage/test_final_hardening_suite.py`
**Estimated time:** 10 minutes

```python
# BEFORE - Metacharacters in match string
with pytest.raises(
    TypeError,
    match="'<' not supported between instances of 'str' and 'decimal.Decimal'",
)

# AFTER - Use raw string for regex pattern
with pytest.raises(
    TypeError,
    match=r"'<' not supported between instances of 'str' and 'decimal\.Decimal'",
)
# Note: . needs escaping in regex
```

**5 occurrences** - Review each pattern and add `r""` prefix or escape metacharacters.

---

### Phase 4: Actual Bugs (F821, B017)

**Estimated time:** 15 minutes

**F821 - Undefined name:**
```python
# In examples/run_all_examples.py:30
def print_result(..., exit_code: int) -> None:
    print(f"... {status} ...")  # 'status' is not defined!

# Fix: Add status parameter or derive from success
def print_result(..., success: bool, ...) -> None:
    status = "PASS" if success else "FAIL"
    print(f"... {status} ...")
```

**B017 - Blind exception:**
Same pattern as other repos - use specific exception class.

---

### Phase 5: Type Annotations (ANN*)

**Location:** `.mutmut-config.py`, `compatibility/python/generator.py`
**Estimated time:** 10 minutes

```python
# BEFORE
def pre_mutation(context):
def main():

# AFTER
def pre_mutation(context: Any) -> None:
def main() -> None:
```

---

### Phase 6: Loop Variables (B007)

**Location:** `examples/run_all_examples.py`
**Estimated time:** 5 minutes

```python
# BEFORE - Unused loop variable
for name, success, _, _, _ in results:
    if success:
        count += 1

# AFTER - Use underscore prefix
for _name, success, _, _, _ in results:
    if success:
        count += 1
```

---

## Recommended Execution Order

1. **Run auto-fix** - Quick wins
2. **Rename ambiguous variables** - Primary issue (33 of 57)
3. **Fix F821 undefined name** - Actual bug
4. **Fix regex patterns** - RUF043
5. **Add type annotations** - Code quality
6. **Fix loop variables** - Clean code

---

## Commands

```bash
# Check current state
cd /Users/tim/code/gh/provide-io/pyvider-cty
ruff check . 2>&1 | tail -10

# Auto-fix
ruff check --fix .
ruff check --fix --unsafe-fixes .

# Run tests after renaming variables
uv run pytest tests/functions/

# Format
ruff format .

# Verify
ruff check . 2>&1 | grep "Found"
```

---

## Alternative: Relax Rules

If renaming all `l` variables is too disruptive:

```toml
[tool.ruff.lint]
ignore = [
    "E741",  # Allow ambiguous variable names
]

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["E741", "RUF043", "B017"]
"examples/**" = ["F821", "B007"]
".mutmut-config.py" = ["ANN001", "ANN201"]
```

---

## Success Criteria

- [ ] Zero F821 (undefined names) - Bug fix
- [ ] All `l` variables renamed or explicitly ignored
- [ ] Regex patterns properly escaped or marked raw
- [ ] All auto-fixable issues resolved
- [ ] Type annotations added to config files
- [ ] Total violations: 0 or documented exceptions
