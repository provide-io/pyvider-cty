# DRY Testing Migration Guide

## Quick Start

### Step 1: Install the Testing Infrastructure

```bash
# Create the testing package structure
mkdir -p ctytool/src/ctytool/testing
touch ctytool/src/ctytool/testing/__init__.py

# Copy the implementation files
cp dry_testing_*.py ctytool/src/ctytool/testing/
```

### Step 2: Update Dependencies

Add to `ctytool/pyproject.toml`:

```toml
[project.optional-dependencies]
testing = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.25.0",
    "pytest-cov>=6.0.0",
    "pytest-xdist>=3.6.0",
    "hypothesis>=6.131.0",
    "pytest-benchmark>=4.0.0",  # For performance tests
]
```

### Step 3: Create Unified Test File

Replace scattered test files with a unified approach:

```python
# ctytool/src/ctytool/test_unified_all.py
#!/usr/bin/env python3
# ctytool/src/ctytool/test_unified_all.py

"""
Unified test suite for all cross-language CTY compatibility testing.
This replaces:
- test_cty_compatibility.py
- test_hcl_compatibility.py
- test_convert_commands.py (partially)
"""

import pytest
from ctytool.testing import (
    TestDataRegistry,
    UnifiedTestExecutor,
    TestResultCollector,
    standard_test_fixtures
)

# All tests now use the unified infrastructure
pytestmark = pytest.mark.compatibility


class TestAllFormats:
    """Single test class for all format compatibility tests."""
    
    @pytest.mark.parametrize(
        "test_case",
        TestDataRegistry.get_all_cases().items(),
        ids=lambda x: x[0]
    )
    @pytest.mark.parametrize("format", ["json", "msgpack", "hcl"])
    def test_compatibility(
        self,
        test_case,
        format,
        unified_executor,
        result_collector
    ):
        """Single test method that handles all cases."""
        test_name, (type_str, value) = test_case
        
        # Skip HCL-specific tests for non-HCL formats
        if test_name.startswith("hcl_") and format != "hcl":
            pytest.skip("HCL-specific test")
        
        # Run all compatibility tests
        results = unified_executor.run_full_compatibility_suite(
            test_name, type_str, value, format
        )
        
        # Collect results
        for result in results:
            result_collector.add(result)
            assert result.success, f"{result.operation} failed: {result.error}"
```

## Migration Checklist

### Phase 1: Preparation (1 day)
- [ ] Create `ctytool.testing` package structure
- [ ] Copy shared infrastructure code
- [ ] Update project dependencies
- [ ] Set up test configuration

### Phase 2: Test Migration (2-3 days)
- [ ] Identify all existing test files:
  - [ ] `test_cty_compatibility.py`
  - [ ] `test_hcl_compatibility.py`
  - [ ] `test_convert_commands.py`
  - [ ] CLI command tests
- [ ] Extract test data into `TestDataRegistry`
- [ ] Convert test functions to use `UnifiedTestExecutor`
- [ ] Remove duplicated helper functions

### Phase 3: Integration (1 day)
- [ ] Update CI/CD pipeline to use new tests
- [ ] Add test result reporting
- [ ] Configure parallel test execution
- [ ] Set up performance benchmarking

### Phase 4: Validation (1 day)
- [ ] Run full test suite
- [ ] Compare coverage with old tests
- [ ] Verify all edge cases covered
- [ ] Performance comparison

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/cross-language-tests.yml
name: Cross-Language Compatibility Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.13"]
        go-version: ["1.21"]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Set up Go
      uses: actions/setup-go@v4
      with:
        go-version: ${{ matrix.go-version }}
    
    - name: Install dependencies
      run: |
        pip install -e ".[testing]"
        cd ctytool/go-ctytool && go mod download
    
    - name: Build Go tool
      run: |
        cd ctytool/go-ctytool
        go build -o ../../.venv/bin/go-ctytool
    
    - name: Run unified tests
      run: |
        pytest ctytool/src/ctytool/test_unified_all.py \
          -v \
          --cov=ctytool \
          --cov-report=xml \
          --junit-xml=test-results.xml \
          -n auto  # Parallel execution
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
    
    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-results
        path: test-results.xml
```

## Performance Testing Integration

Add performance benchmarks using the same infrastructure:

```python
# ctytool/src/ctytool/test_performance.py
#!/usr/bin/env python3
# ctytool/src/ctytool/test_performance.py

import pytest
from ctytool.testing import TestDataRegistry, UnifiedTestExecutor


class TestPerformance:
    """Performance benchmarks for serialization."""
    
    @pytest.mark.benchmark
    @pytest.mark.parametrize("format", ["json", "msgpack"])
    def test_serialization_speed(
        self,
        benchmark,
        unified_executor,
        format
    ):
        """Benchmark serialization performance."""
        # Use a complex test case
        type_str, value = TestDataRegistry.STANDARD_CASES["object_complex"]
        
        def run_serialization():
            return unified_executor.adapters["python"].serialize(
                value, 
                unified_executor._parse_type_string(type_str),
                format
            )
        
        # Run benchmark
        result = benchmark(run_serialization)
        
        # Add assertions on performance
        assert benchmark.stats["mean"] < 0.001  # Less than 1ms
```

## Debugging Failed Tests

The unified infrastructure provides better debugging:

```python
# Run with detailed logging
pytest -v --log-cli-level=DEBUG

# Run specific test case
pytest -k "test_name and format"

# Generate detailed HTML report
pytest --html=report.html --self-contained-html

# Run with test result analysis
pytest --result-log=results.log
```

## Benefits After Migration

1. **Reduced Test Code**: ~60% less code to maintain
2. **Faster Execution**: Parallel execution, shared fixtures
3. **Better Coverage**: Property-based testing finds edge cases
4. **Easier Debugging**: Unified logging and error reporting
5. **Performance Tracking**: Built-in benchmarking
6. **Format Agnostic**: Easy to add new formats (YAML, TOML)

## Common Pitfalls to Avoid

1. **Don't migrate all at once**: Do it incrementally
2. **Keep old tests temporarily**: Run both until confident
3. **Monitor coverage**: Ensure no tests are lost
4. **Update documentation**: Team needs to know new structure
5. **Train team**: Everyone should understand new approach

## Next Steps

After migration:

1. Add performance regression tests
2. Implement fuzz testing with Hypothesis
3. Add visual test reports
4. Create test data generators for specific domains
5. Build automated compatibility matrix dashboard

This migration will significantly improve the maintainability and effectiveness of your cross-language testing infrastructure.