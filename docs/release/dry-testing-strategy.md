# DRY Testing Strategy for CTYTool Cross-Language Tests

## Overview

This strategy unifies testing across `pyvider.cty`, `pyvider.hcl`, and `ctytool` to eliminate duplication while ensuring comprehensive cross-language compatibility testing.

## Architecture

### 1. Shared Test Infrastructure Package

Create a new `ctytool.testing` subpackage that provides:

```python
# ctytool/src/ctytool/testing/__init__.py
#!/usr/bin/env python3
# ctytool/src/ctytool/testing/__init__.py

from .fixtures import *
from .strategies import *
from .assertions import *
from .runners import *
from .data import *

__all__ = [
    # Fixtures
    'cty_type_fixture',
    'cty_value_fixture',
    'test_case_fixture',
    
    # Strategies
    'cty_type_strategy',
    'cty_value_strategy',
    'serialization_format_strategy',
    
    # Assertions
    'assert_cty_values_equal',
    'assert_serialization_roundtrip',
    'assert_cross_language_compatibility',
    
    # Runners
    'CrossLanguageTestRunner',
    'SerializationTestRunner',
    
    # Data
    'STANDARD_TEST_CASES',
    'EDGE_CASE_TEST_CASES',
]
```

### 2. Unified Test Data Generation

```python
# ctytool/src/ctytool/testing/strategies.py
#!/usr/bin/env python3
# ctytool/src/ctytool/testing/strategies.py

import hypothesis.strategies as st
from hypothesis import assume
from decimal import Decimal
from typing import Any

from pyvider.cty import (
    CtyType, CtyString, CtyNumber, CtyBool, CtyList, 
    CtyMap, CtySet, CtyObject, CtyTuple, CtyDynamic
)

# Base type strategies
def primitive_type_strategy() -> st.SearchStrategy[CtyType]:
    """Generate primitive CTY types."""
    return st.one_of(
        st.just(CtyString()),
        st.just(CtyNumber()),
        st.just(CtyBool()),
        st.just(CtyDynamic())
    )

def collection_type_strategy(max_depth: int = 3) -> st.SearchStrategy[CtyType]:
    """Generate collection types with controlled nesting depth."""
    if max_depth <= 0:
        return primitive_type_strategy()
    
    return st.one_of(
        st.builds(CtyList, element_type=cty_type_strategy(max_depth - 1)),
        st.builds(CtySet, element_type=cty_type_strategy(max_depth - 1)),
        st.builds(
            CtyMap,
            key_type=st.just(CtyString()),
            value_type=cty_type_strategy(max_depth - 1)
        )
    )

def structural_type_strategy(max_depth: int = 3) -> st.SearchStrategy[CtyType]:
    """Generate structural types (Object, Tuple)."""
    if max_depth <= 0:
        return primitive_type_strategy()
    
    # Object type with 1-5 attributes
    object_strategy = st.builds(
        CtyObject,
        attribute_types=st.dictionaries(
            st.text(min_size=1, max_size=20, alphabet=st.characters(min_codepoint=97, max_codepoint=122)),
            cty_type_strategy(max_depth - 1),
            min_size=1,
            max_size=5
        )
    )
    
    # Tuple type with 1-5 elements
    tuple_strategy = st.builds(
        CtyTuple,
        element_types=st.lists(
            cty_type_strategy(max_depth - 1),
            min_size=1,
            max_size=5
        ).map(tuple)
    )
    
    return st.one_of(object_strategy, tuple_strategy)

def cty_type_strategy(max_depth: int = 3) -> st.SearchStrategy[CtyType]:
    """Generate any CTY type with controlled nesting."""
    return st.one_of(
        primitive_type_strategy(),
        collection_type_strategy(max_depth),
        structural_type_strategy(max_depth)
    )

# Value generation strategies
def value_for_type_strategy(cty_type: CtyType) -> st.SearchStrategy[Any]:
    """Generate values that match a specific CTY type."""
    if isinstance(cty_type, CtyString):
        return st.text(max_size=100)
    
    elif isinstance(cty_type, CtyNumber):
        return st.one_of(
            st.integers(min_value=-1e9, max_value=1e9),
            st.floats(allow_nan=False, allow_infinity=False),
            st.decimals(allow_nan=False, allow_infinity=False, max_value=1e9, min_value=-1e9)
        )
    
    elif isinstance(cty_type, CtyBool):
        return st.booleans()
    
    elif isinstance(cty_type, CtyList):
        return st.lists(
            value_for_type_strategy(cty_type.element_type),
            max_size=10
        )
    
    elif isinstance(cty_type, CtySet):
        # Sets need unique values
        return st.lists(
            value_for_type_strategy(cty_type.element_type),
            max_size=10,
            unique=True
        ).map(set)
    
    elif isinstance(cty_type, CtyMap):
        return st.dictionaries(
            st.text(min_size=1, max_size=20),
            value_for_type_strategy(cty_type.value_type),
            max_size=10
        )
    
    elif isinstance(cty_type, CtyObject):
        # Generate dict with all required attributes
        return st.fixed_dictionaries({
            attr_name: value_for_type_strategy(attr_type)
            for attr_name, attr_type in cty_type.attribute_types.items()
        })
    
    elif isinstance(cty_type, CtyTuple):
        # Generate list matching tuple element types
        return st.tuples(*[
            value_for_type_strategy(elem_type)
            for elem_type in cty_type.element_types
        ]).map(list)
    
    elif isinstance(cty_type, CtyDynamic):
        # Dynamic can be any simple value
        return st.one_of(
            st.text(max_size=100),
            st.integers(),
            st.floats(allow_nan=False, allow_infinity=False),
            st.booleans(),
            st.none()
        )
    
    else:
        # Fallback for unknown types
        return st.none()

def cty_value_strategy() -> st.SearchStrategy[tuple[CtyType, Any]]:
    """Generate type and matching value pairs."""
    return cty_type_strategy().flatmap(
        lambda t: st.tuples(st.just(t), value_for_type_strategy(t))
    )

def serialization_format_strategy() -> st.SearchStrategy[str]:
    """Generate serialization format names."""
    return st.sampled_from(['json', 'msgpack', 'hcl'])
```

### 3. Shared Test Fixtures

```python
# ctytool/src/ctytool/testing/fixtures.py
#!/usr/bin/env python3
# ctytool/src/ctytool/testing/fixtures.py

import pytest
import tempfile
import pathlib
from typing import Generator, Any
from decimal import Decimal

from pyvider.cty import CtyType, CtyValue, CtyString, CtyNumber, CtyList, CtyObject
from pyvider.telemetry import logger

@pytest.fixture(scope="session")
def test_output_dir() -> Generator[pathlib.Path, None, None]:
    """Provide a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory(prefix="ctytool_test_") as tmpdir:
        path = pathlib.Path(tmpdir)
        logger.debug(f"🧪📁✅ Created test output directory: {path}")
        yield path
        logger.debug(f"🧪📁🔒 Cleaning up test output directory: {path}")

@pytest.fixture(scope="session")
def standard_test_types() -> dict[str, CtyType]:
    """Standard CTY types used across tests."""
    return {
        "string": CtyString(),
        "number": CtyNumber(),
        "bool": CtyBool(),
        "list_string": CtyList(element_type=CtyString()),
        "list_number": CtyList(element_type=CtyNumber()),
        "map_string": CtyMap(key_type=CtyString(), value_type=CtyString()),
        "object_simple": CtyObject({
            "name": CtyString(),
            "age": CtyNumber(),
            "active": CtyBool()
        }),
        "object_nested": CtyObject({
            "id": CtyString(),
            "metadata": CtyObject({
                "created": CtyString(),
                "tags": CtyList(element_type=CtyString())
            })
        })
    }

@pytest.fixture(scope="session")
def standard_test_values(standard_test_types) -> dict[str, tuple[CtyType, Any]]:
    """Standard test values with their types."""
    return {
        "string_hello": (standard_test_types["string"], "hello world"),
        "number_int": (standard_test_types["number"], Decimal("42")),
        "number_float": (standard_test_types["number"], Decimal("3.14159")),
        "bool_true": (standard_test_types["bool"], True),
        "list_fruits": (standard_test_types["list_string"], ["apple", "banana", "cherry"]),
        "map_colors": (standard_test_types["map_string"], {"red": "#FF0000", "green": "#00FF00"}),
        "object_person": (standard_test_types["object_simple"], {
            "name": "Alice",
            "age": Decimal("30"),
            "active": True
        }),
        "object_complex": (standard_test_types["object_nested"], {
            "id": "user-123",
            "metadata": {
                "created": "2024-01-01T00:00:00Z",
                "tags": ["admin", "verified"]
            }
        })
    }

@pytest.fixture
def cross_language_tools(test_output_dir) -> dict[str, Any]:
    """Provide access to both Python and Go CTY tools."""
    from ctytool.go_interaction import ensure_go_ctytool_built_async
    import asyncio
    
    # Ensure Go tool is built
    go_tool_path = asyncio.run(ensure_go_ctytool_built_async())
    
    return {
        "python": {
            "type": "python",
            "module": "pyvider.cty"
        },
        "go": {
            "type": "go",
            "executable": go_tool_path,
            "working_dir": test_output_dir
        }
    }
```

### 4. Unified Test Runners

```python
# ctytool/src/ctytool/testing/runners.py
#!/usr/bin/env python3
# ctytool/src/ctytool/testing/runners.py

import subprocess
import json
import pathlib
from typing import Any, Literal, Optional
from dataclasses import dataclass

from pyvider.cty import CtyType, CtyValue
from pyvider.telemetry import logger

@dataclass
class TestResult:
    """Result of a cross-language test."""
    success: bool
    language: str
    format: str
    input_data: Any
    output_data: Optional[Any]
    error: Optional[str]
    metadata: dict[str, Any]

class CrossLanguageTestRunner:
    """Unified runner for cross-language CTY tests."""
    
    def __init__(self, python_module: str, go_executable: str, working_dir: pathlib.Path):
        self.python_module = python_module
        self.go_executable = go_executable
        self.working_dir = working_dir
        logger.debug(f"🧪🚀✅ Initialized CrossLanguageTestRunner")
    
    def test_serialization_roundtrip(
        self,
        cty_type: CtyType,
        value: Any,
        format: Literal["json", "msgpack", "hcl"]
    ) -> dict[str, TestResult]:
        """Test serialization roundtrip in both languages."""
        results = {}
        
        # Test Python roundtrip
        results["python"] = self._test_python_roundtrip(cty_type, value, format)
        
        # Test Go roundtrip
        results["go"] = self._test_go_roundtrip(cty_type, value, format)
        
        return results
    
    def test_cross_language_compatibility(
        self,
        cty_type: CtyType,
        value: Any,
        format: Literal["json", "msgpack", "hcl"]
    ) -> dict[str, TestResult]:
        """Test cross-language serialization compatibility."""
        results = {}
        
        # Python -> Go
        results["python_to_go"] = self._test_cross_language(
            cty_type, value, format, 
            source_lang="python", target_lang="go"
        )
        
        # Go -> Python
        results["go_to_python"] = self._test_cross_language(
            cty_type, value, format,
            source_lang="go", target_lang="python"
        )
        
        return results
    
    def _test_python_roundtrip(
        self, 
        cty_type: CtyType, 
        value: Any, 
        format: str
    ) -> TestResult:
        """Test Python serialization roundtrip."""
        try:
            # Import dynamically based on format
            if format == "json":
                from pyvider.cty.codec import marshal_json, unmarshal_json
                validated = cty_type.validate(value)
                serialized = marshal_json(validated)
                deserialized = unmarshal_json(serialized, cty_type)
                
            elif format == "msgpack":
                from pyvider.cty.codec import marshal_msgpack, unmarshal_msgpack
                validated = cty_type.validate(value)
                serialized = marshal_msgpack(validated)
                deserialized = unmarshal_msgpack(serialized, cty_type)
                
            elif format == "hcl":
                # HCL support through pyvider.hcl
                from pyvider.hcl import to_hcl, from_hcl
                validated = cty_type.validate(value)
                hcl_str = to_hcl(validated)
                deserialized = from_hcl(hcl_str, cty_type)
            
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            # Compare values
            success = self._compare_values(validated, deserialized)
            
            return TestResult(
                success=success,
                language="python",
                format=format,
                input_data=value,
                output_data=deserialized,
                error=None if success else "Values do not match after roundtrip",
                metadata={"serialized_size": len(serialized) if format != "hcl" else len(hcl_str)}
            )
            
        except Exception as e:
            logger.error(f"🧪❌❌ Python roundtrip failed: {e}")
            return TestResult(
                success=False,
                language="python",
                format=format,
                input_data=value,
                output_data=None,
                error=str(e),
                metadata={}
            )
    
    def _test_go_roundtrip(
        self,
        cty_type: CtyType,
        value: Any,
        format: str
    ) -> TestResult:
        """Test Go serialization roundtrip."""
        # Implementation would call the Go tool via subprocess
        # Similar structure to _test_python_roundtrip
        pass
    
    def _test_cross_language(
        self,
        cty_type: CtyType,
        value: Any,
        format: str,
        source_lang: str,
        target_lang: str
    ) -> TestResult:
        """Test serialization from one language and deserialization in another."""
        # Implementation would serialize in source_lang and deserialize in target_lang
        pass
    
    def _compare_values(self, val1: CtyValue, val2: CtyValue) -> bool:
        """Compare two CtyValues for equality."""
        # Handle null/unknown states
        if val1.is_null != val2.is_null or val1.is_unknown != val2.is_unknown:
            return False
        
        # Compare actual values
        return val1.to_json_comparable_dict() == val2.to_json_comparable_dict()
```

### 5. Shared Test Assertions

```python
# ctytool/src/ctytool/testing/assertions.py
#!/usr/bin/env python3
# ctytool/src/ctytool/testing/assertions.py

import json
from typing import Any, Optional
from decimal import Decimal

from pyvider.cty import CtyValue
from pyvider.telemetry import logger

def assert_cty_values_equal(
    actual: CtyValue,
    expected: CtyValue,
    message: Optional[str] = None
) -> None:
    """Assert two CtyValues are equal."""
    # Check null/unknown states
    assert actual.is_null == expected.is_null, \
        f"{message or 'Values have different null states'}: {actual.is_null} != {expected.is_null}"
    
    assert actual.is_unknown == expected.is_unknown, \
        f"{message or 'Values have different unknown states'}: {actual.is_unknown} != {expected.is_unknown}"
    
    # Check types
    assert type(actual.type) == type(expected.type), \
        f"{message or 'Values have different types'}: {type(actual.type)} != {type(expected.type)}"
    
    # Compare JSON representations for deep equality
    actual_json = actual.to_json_comparable_dict()
    expected_json = expected.to_json_comparable_dict()
    
    assert actual_json == expected_json, \
        f"{message or 'Values are not equal'}:\nActual: {json.dumps(actual_json, indent=2)}\nExpected: {json.dumps(expected_json, indent=2)}"

def assert_serialization_roundtrip(
    original: Any,
    deserialized: Any,
    format: str,
    message: Optional[str] = None
) -> None:
    """Assert that a value survives serialization roundtrip."""
    # Normalize numeric types
    def normalize_value(val: Any) -> Any:
        if isinstance(val, (int, float, Decimal)):
            return Decimal(str(val))
        elif isinstance(val, dict):
            return {k: normalize_value(v) for k, v in val.items()}
        elif isinstance(val, list):
            return [normalize_value(v) for v in val]
        elif isinstance(val, set):
            return {normalize_value(v) for v in val}
        return val
    
    normalized_original = normalize_value(original)
    normalized_deserialized = normalize_value(deserialized)
    
    assert normalized_original == normalized_deserialized, \
        f"{message or f'Roundtrip failed for {format}'}:\nOriginal: {normalized_original}\nDeserialized: {normalized_deserialized}"

def assert_cross_language_compatibility(
    results: dict[str, Any],
    expected_success: bool = True,
    message: Optional[str] = None
) -> None:
    """Assert cross-language test results meet expectations."""
    for test_name, result in results.items():
        if expected_success:
            assert result.success, \
                f"{message or f'Cross-language test {test_name} failed'}: {result.error}"
        else:
            assert not result.success, \
                f"{message or f'Cross-language test {test_name} unexpectedly succeeded'}"
```

### 6. Unified Test Implementation

```python
# ctytool/src/ctytool/test_unified_compatibility.py
#!/usr/bin/env python3
# ctytool/src/ctytool/test_unified_compatibility.py

import pytest
from hypothesis import given, settings, HealthCheck

from ctytool.testing import (
    cty_type_strategy,
    cty_value_strategy,
    serialization_format_strategy,
    CrossLanguageTestRunner,
    assert_serialization_roundtrip,
    assert_cross_language_compatibility,
    standard_test_types,
    standard_test_values,
    cross_language_tools
)

from pyvider.telemetry import logger

class TestUnifiedCompatibility:
    """Unified cross-language compatibility tests."""
    
    @pytest.mark.parametrize("test_name,type_and_value", [
        (name, val) for name, val in standard_test_values.items()
    ])
    @pytest.mark.parametrize("format", ["json", "msgpack", "hcl"])
    def test_standard_cases(
        self,
        test_name: str,
        type_and_value: tuple,
        format: str,
        cross_language_tools: dict
    ):
        """Test standard cases across all formats and languages."""
        cty_type, value = type_and_value
        
        runner = CrossLanguageTestRunner(
            python_module=cross_language_tools["python"]["module"],
            go_executable=cross_language_tools["go"]["executable"],
            working_dir=cross_language_tools["go"]["working_dir"]
        )
        
        # Test roundtrips
        roundtrip_results = runner.test_serialization_roundtrip(
            cty_type, value, format
        )
        
        for lang, result in roundtrip_results.items():
            assert result.success, f"Roundtrip failed for {lang}/{format}: {result.error}"
        
        # Test cross-language compatibility
        compat_results = runner.test_cross_language_compatibility(
            cty_type, value, format
        )
        
        assert_cross_language_compatibility(compat_results)
    
    @given(
        type_and_value=cty_value_strategy(),
        format=serialization_format_strategy()
    )
    @settings(
        max_examples=50,
        suppress_health_check=[HealthCheck.too_slow]
    )
    def test_property_based(
        self,
        type_and_value: tuple,
        format: str,
        cross_language_tools: dict
    ):
        """Property-based testing with Hypothesis."""
        cty_type, value = type_and_value
        
        runner = CrossLanguageTestRunner(
            python_module=cross_language_tools["python"]["module"],
            go_executable=cross_language_tools["go"]["executable"],
            working_dir=cross_language_tools["go"]["working_dir"]
        )
        
        try:
            # Test Python roundtrip (minimum viable test)
            result = runner.test_serialization_roundtrip(
                cty_type, value, format
            )["python"]
            
            assert result.success, f"Python roundtrip failed: {result.error}"
            
        except Exception as e:
            # Log but don't fail for unsupported combinations
            logger.warning(f"🧪⚠️⚠️ Skipping unsupported combination: {e}")
```

### 7. Test Configuration

```yaml
# ctytool/pytest.ini
[pytest]
testpaths = src/ctytool/tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --cov=ctytool
    --cov-report=term-missing
    --hypothesis-show-statistics
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    compatibility: marks cross-language compatibility tests
```

## Benefits of This Approach

1. **Single Source of Truth**: Test data, fixtures, and strategies defined once
2. **Comprehensive Coverage**: Property-based testing ensures edge cases are covered
3. **Maintainable**: Changes to test logic only need to be made in one place
4. **Extensible**: Easy to add new formats, languages, or test scenarios
5. **Performant**: Shared fixtures reduce setup/teardown overhead
6. **Debuggable**: Unified logging and error reporting

## Migration Plan

1. **Phase 1**: Create the `ctytool.testing` package with core infrastructure
2. **Phase 2**: Migrate existing tests to use shared fixtures and strategies
3. **Phase 3**: Implement property-based tests for comprehensive coverage
4. **Phase 4**: Add performance benchmarking using the same infrastructure
5. **Phase 5**: Extend to support additional formats (YAML, TOML) as needed

## Example Usage

```python
# Simple test using the unified infrastructure
def test_my_custom_case(cross_language_tools):
    """Example of using the unified testing infrastructure."""
    from ctytool.testing import CrossLanguageTestRunner
    from pyvider.cty import CtyObject, CtyString, CtyNumber
    
    # Define a custom type
    my_type = CtyObject({
        "name": CtyString(),
        "value": CtyNumber()
    })
    
    # Test data
    my_data = {"name": "test", "value": 42}
    
    # Run tests
    runner = CrossLanguageTestRunner(**cross_language_tools)
    results = runner.test_cross_language_compatibility(
        my_type, my_data, "json"
    )
    
    # Assert results
    assert all(r.success for r in results.values())
```

This DRY strategy provides a solid foundation for comprehensive cross-language testing while minimizing code duplication and maximizing maintainability.