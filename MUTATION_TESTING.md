# Mutation Testing with Mutmut

This document describes how to run mutation testing on the pyvider-cty codebase to verify test quality beyond code coverage.

## What is Mutation Testing?

Mutation testing introduces small changes (mutations) to your code and checks if your tests catch them. If a test fails when the code is mutated, the mutation is "killed" (good). If all tests pass despite the mutation, it's "survived" (indicates a gap in test quality).

## Setup

Mutation testing is already configured via `.mutmut-config.py`. The configuration:
- Skips test files (no need to mutate tests)
- Skips generated files (_version.py)
- Skips __init__.py files (mostly imports)

## Running Mutation Tests

### Full Mutation Test Suite

To run mutation testing on the entire codebase:

```bash
# Initialize (creates .mutmut-cache directory)
mutmut run

# This will take several hours for the full codebase!
# Progress is saved, so you can interrupt and resume
```

### Targeted Mutation Testing

For faster feedback, target specific modules:

```bash
# Test a single module
PYTHONPATH=src mutmut run tests/types/primitives/test_bool.py

# View results
mutmut results

# Show surviving mutants (these indicate test gaps)
mutmut show all
```

### Interpreting Results

- **Killed**: Mutation was caught by tests ✅
- **Survived**: Mutation not caught - test gap ⚠️
- **Timeout**: Mutation caused infinite loop/hang
- **Suspicious**: Mutation made tests faster (weird)

### Example Workflow

```bash
# 1. Run mutation tests on a critical module
cd /Users/tim/code/gh/provide-io/pyvider-cty
source env.sh
PYTHONPATH=src mutmut run tests/types/primitives/test_bool.py

# 2. Check results
mutmut results

# 3. View surviving mutants
mutmut show all

# 4. For each survivor, add a test that would kill it
# 5. Re-run mutation testing to verify
mutmut run

# 6. Clean up for next run
rm -rf .mutmut-cache
```

## Current Test Quality Metrics

Based on code coverage analysis:

- **Overall Coverage**: 93% (line coverage)
- **Branch Coverage**: Tracked and reported
- **Test Count**: 1,050 tests
- **Test Categories**:
  - Unit tests
  - Property-based tests (Hypothesis)
  - Integration tests
  - Cross-language compatibility tests

### Files with Coverage < 95%

Priority targets for additional mutation testing:

1. `functions/numeric_functions.py` - 85% (arithmetic operations)
2. `functions/comparison_functions.py` - 85% (comparison logic)
3. `types/base.py` - 84% (type protocol)
4. `types/capsule.py` - 86% (opaque types)
5. `types/collections/map.py` - 85% (map validation)

## Recommended Mutation Testing Strategy

### Phase 1: High-Value Modules (Week 1)
Focus on core type system and validation:
- `src/pyvider/cty/types/primitives/`
- `src/pyvider/cty/values/base.py`
- `src/pyvider/cty/conversion/`

### Phase 2: Functions (Week 2)
Test standard library functions:
- `src/pyvider/cty/functions/numeric_functions.py`
- `src/pyvider/cty/functions/comparison_functions.py`
- `src/pyvider/cty/functions/collection_functions.py`

### Phase 3: Codec & Serialization (Week 3)
Critical for cross-language compatibility:
- `src/pyvider/cty/codec.py`
- `src/pyvider/cty/conversion/type_encoder.py`

## Expected Mutation Score

For high-quality test suites:
- **Excellent**: > 80% mutation score
- **Good**: 60-80% mutation score
- **Needs Work**: < 60% mutation score

## Notes

- Mutation testing is computationally expensive
- Run on CI for critical modules only
- Use coverage as initial filter - don't mutate uncovered code
- Focus on business logic, not boilerplate

## Integration with CI

Add to `.github/workflows/mutation-testing.yml`:

```yaml
name: Mutation Testing

on:
  schedule:
    - cron: '0 2 * * 0'  # Weekly on Sunday at 2 AM
  workflow_dispatch:  # Manual trigger

jobs:
  mutmut:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install uv
          uv sync --all-groups
          pip install mutmut
      - name: Run mutation tests
        run: |
          source env.sh
          mutmut run --max-children=4
      - name: Generate report
        run: mutmut html
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: mutation-report
          path: html/
```

## Resources

- [Mutmut Documentation](https://mutmut.readthedocs.io/)
- [Mutation Testing Best Practices](https://testing.googleblog.com/2021/04/mutation-testing.html)
- [Understanding Mutation Scores](https://medium.com/@piotr.sakowicz/mutation-testing-35b43c67ff56)

---

🧬 Generated for provide-io/pyvider-cty
