#!/usr/bin/env python3
# ctytool/src/ctytool/testing/implementation_example.py

"""
Complete implementation example showing how to use the DRY testing infrastructure
for cross-language CTY compatibility testing.
"""

from decimal import Decimal
import json
import pathlib
import subprocess
import tempfile
from typing import Any

from hypothesis import given, settings, strategies as st
import pytest

from pyvider.cty import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtyString,
    CtyTuple,
    CtyType,
)
from pyvider.telemetry import logger

# ============================================================================
# PART 1: Shared Test Data Registry
# ============================================================================

class TestDataRegistry:
    """Central registry for all test data to ensure consistency."""

    # Standard test cases used across all tests
    STANDARD_CASES = {
        # Primitive types
        "string_empty": ("string", ""),
        "string_simple": ("string", "hello world"),
        "string_unicode": ("string", "Hello 世界 🌍"),
        "string_special": ("string", "Line1\nLine2\tTab"),

        "number_zero": ("number", Decimal("0")),
        "number_positive_int": ("number", Decimal("42")),
        "number_negative_int": ("number", Decimal("-42")),
        "number_float": ("number", Decimal("3.14159")),
        "number_scientific": ("number", Decimal("1.23e-4")),

        "bool_true": ("bool", True),
        "bool_false": ("bool", False),

        # Collection types
        "list_empty": ("list(string)", []),
        "list_strings": ("list(string)", ["apple", "banana", "cherry"]),
        "list_numbers": ("list(number)", [Decimal("1"), Decimal("2"), Decimal("3")]),
        "list_mixed_types": ("list(dynamic)", ["string", 42, True, None]),

        "map_empty": ("map(string)", {}),
        "map_simple": ("map(string)", {"key1": "value1", "key2": "value2"}),
        "map_nested": ("map(list(string))", {
            "fruits": ["apple", "banana"],
            "colors": ["red", "green", "blue"]
        }),

        "set_empty": ("set(string)", set()),
        "set_strings": ("set(string)", {"apple", "banana", "cherry"}),
        "set_numbers": ("set(number)", {Decimal("1"), Decimal("2"), Decimal("3")}),

        # Structural types
        "object_simple": ("object({name=string,age=number})", {
            "name": "Alice",
            "age": Decimal("30")
        }),
        "object_complex": ("object({id=string,data=object({values=list(number)})})", {
            "id": "test-123",
            "data": {
                "values": [Decimal("1"), Decimal("2"), Decimal("3")]
            }
        }),

        "tuple_simple": ("tuple([string,number,bool])", ["hello", Decimal("42"), True]),
        "tuple_nested": ("tuple([string,list(string)])", ["prefix", ["a", "b", "c"]]),

        # Edge cases
        "null_string": ("string", None),
        "null_object": ("object({name=string})", None),
    }

    # Format-specific test cases
    HCL_SPECIFIC_CASES = {
        "hcl_resource": (
            "object({resource=object({type=string,name=string,config=map(string)})})",
            {
                "resource": {
                    "type": "aws_instance",
                    "name": "example",
                    "config": {
                        "ami": "ami-123456",
                        "instance_type": "t2.micro"
                    }
                }
            }
        ),
    }

    @classmethod
    def get_all_cases(cls) -> dict[str, tuple[str, Any]]:
        """Get all test cases."""
        return {**cls.STANDARD_CASES, **cls.HCL_SPECIFIC_CASES}

    @classmethod
    def get_case_by_format(cls, format: str) -> dict[str, tuple[str, Any]]:
        """Get test cases appropriate for a specific format."""
        if format == "hcl":
            return {**cls.STANDARD_CASES, **cls.HCL_SPECIFIC_CASES}
        return cls.STANDARD_CASES


# ============================================================================
# PART 2: Tool Abstraction Layer
# ============================================================================

class LanguageToolAdapter:
    """Abstract interface for language-specific tools."""

    def serialize(self, value: Any, cty_type: CtyType, format: str) -> bytes:
        """Serialize a value to the specified format."""
        raise NotImplementedError

    def deserialize(self, data: bytes, cty_type: CtyType, format: str) -> Any:
        """Deserialize data from the specified format."""
        raise NotImplementedError


class PythonToolAdapter(LanguageToolAdapter):
    """Adapter for Python pyvider.cty implementation."""

    def __init__(self):
        logger.debug("🔧🐍✅ Initialized Python tool adapter")

    def serialize(self, value: Any, cty_type: CtyType, format: str) -> bytes:
        """Serialize using pyvider.cty."""
        # Validate the value first
        cty_value = cty_type.validate(value)

        if format == "json":
            from pyvider.cty.codec import marshal_json
            return marshal_json(cty_value)

        elif format == "msgpack":
            from pyvider.cty.codec import marshal_msgpack
            return marshal_msgpack(cty_value)

        elif format == "hcl":
            # Use pyvider.hcl if available
            try:
                from pyvider.hcl import dumps as hcl_dumps
                return hcl_dumps(cty_value).encode('utf-8')
            except ImportError:
                logger.warning("🔧🐍⚠️ pyvider.hcl not available, using JSON fallback")
                from pyvider.cty.codec import marshal_json
                return marshal_json(cty_value)

        else:
            raise ValueError(f"Unsupported format: {format}")

    def deserialize(self, data: bytes, cty_type: CtyType, format: str) -> Any:
        """Deserialize using pyvider.cty."""
        if format == "json":
            from pyvider.cty.codec import unmarshal_json
            cty_value = unmarshal_json(data, cty_type)

        elif format == "msgpack":
            from pyvider.cty.codec import unmarshal_msgpack
            cty_value = unmarshal_msgpack(data, cty_type)

        elif format == "hcl":
            try:
                from pyvider.hcl import loads as hcl_loads
                cty_value = hcl_loads(data.decode('utf-8'), cty_type)
            except ImportError:
                logger.warning("🔧🐍⚠️ pyvider.hcl not available, using JSON fallback")
                from pyvider.cty.codec import unmarshal_json
                cty_value = unmarshal_json(data, cty_type)

        else:
            raise ValueError(f"Unsupported format: {format}")

        # Extract the actual value
        return cty_value.value if not cty_value.is_null else None


class GoToolAdapter(LanguageToolAdapter):
    """Adapter for Go go-cty implementation."""

    def __init__(self, executable_path: str, working_dir: pathlib.Path):
        self.executable = executable_path
        self.working_dir = working_dir
        logger.debug(f"🔧🐹✅ Initialized Go tool adapter: {executable_path}")

    def serialize(self, value: Any, cty_type: CtyType, format: str) -> bytes:
        """Serialize using go-ctytool."""
        # Create temporary files
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.yaml',
            dir=self.working_dir,
            delete=False
        ) as yaml_file:
            # Write test case YAML
            import yaml
            yaml_data = {
                "name": "test_case",
                "type_definition": self._type_to_string(cty_type),
                "raw_input": self._prepare_value_for_go(value)
            }
            yaml.dump(yaml_data, yaml_file)
            yaml_path = yaml_file.name

        output_file = self.working_dir / f"output.{format}"

        try:
            # Run Go tool
            cmd = [
                self.executable,
                yaml_path,
                "--format", format,
                "--stdout"
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                cwd=str(self.working_dir),
                timeout=10
            )

            if result.returncode != 0:
                raise RuntimeError(f"Go tool failed: {result.stderr.decode()}")

            return result.stdout

        finally:
            # Cleanup
            pathlib.Path(yaml_path).unlink(missing_ok=True)
            output_file.unlink(missing_ok=True)

    def deserialize(self, data: bytes, cty_type: CtyType, format: str) -> Any:
        """Deserialize using go-ctytool."""
        # Write data to temporary file
        input_file = self.working_dir / f"input.{format}"
        input_file.write_bytes(data)

        try:
            # Run Go tool
            cmd = [
                self.executable,
                "--inputFile", str(input_file),
                "--inputFileFormat", format,
                "--targetTypeString", self._type_to_string(cty_type),
                "--format", "json",  # Always output JSON for parsing
                "--stdout"
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                cwd=str(self.working_dir),
                timeout=10
            )

            if result.returncode != 0:
                raise RuntimeError(f"Go tool failed: {result.stderr.decode()}")

            # Parse JSON output
            json_data = json.loads(result.stdout)
            return self._extract_value_from_json_comparable(json_data)

        finally:
            input_file.unlink(missing_ok=True)

    def _type_to_string(self, cty_type: CtyType) -> str:
        """Convert CtyType to string representation."""
        # This is a simplified version - real implementation would be more complete
        if isinstance(cty_type, CtyString):
            return "string"
        elif isinstance(cty_type, CtyNumber):
            return "number"
        elif isinstance(cty_type, CtyBool):
            return "bool"
        elif isinstance(cty_type, CtyList):
            return f"list({self._type_to_string(cty_type.element_type)})"
        elif isinstance(cty_type, CtyMap):
            return f"map({self._type_to_string(cty_type.value_type)})"
        elif isinstance(cty_type, CtyObject):
            attrs = ",".join(
                f"{k}={self._type_to_string(v)}"
                for k, v in cty_type.attribute_types.items()
            )
            return f"object({{{attrs}}})"
        else:
            return "dynamic"

    def _prepare_value_for_go(self, value: Any) -> Any:
        """Prepare Python value for Go consumption."""
        if isinstance(value, Decimal):
            return str(value)
        elif isinstance(value, set):
            return list(value)
        elif isinstance(value, dict):
            return {k: self._prepare_value_for_go(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._prepare_value_for_go(v) for v in value]
        return value

    def _extract_value_from_json_comparable(self, data: dict) -> Any:
        """Extract value from JSON comparable format."""
        if data.get("is_null"):
            return None
        return data.get("value")


# ============================================================================
# PART 3: Unified Test Executor
# ============================================================================

class UnifiedTestExecutor:
    """Executes tests across languages and formats in a DRY manner."""

    def __init__(self, python_adapter: PythonToolAdapter, go_adapter: GoToolAdapter):
        self.adapters = {
            "python": python_adapter,
            "go": go_adapter
        }
        logger.debug("🧪🔧✅ Initialized unified test executor")

    def test_roundtrip(
        self,
        test_name: str,
        type_str: str,
        value: Any,
        format: str,
        language: str
    ) -> TestResult:
        """Test serialization roundtrip for a single language."""
        try:
            # Parse type string
            cty_type = self._parse_type_string(type_str)
            adapter = self.adapters[language]

            # Serialize
            serialized = adapter.serialize(value, cty_type, format)

            # Deserialize
            deserialized = adapter.deserialize(serialized, cty_type, format)

            # Compare
            success = self._compare_values(value, deserialized)

            return TestResult(
                test_name=test_name,
                success=success,
                language=language,
                format=format,
                operation="roundtrip",
                error=None if success else "Values don't match"
            )

        except Exception as e:
            logger.error(f"🧪❌❌ Roundtrip test failed: {e}")
            return TestResult(
                test_name=test_name,
                success=False,
                language=language,
                format=format,
                operation="roundtrip",
                error=str(e)
            )

    def test_cross_language(
        self,
        test_name: str,
        type_str: str,
        value: Any,
        format: str,
        source_lang: str,
        target_lang: str
    ) -> TestResult:
        """Test cross-language compatibility."""
        try:
            cty_type = self._parse_type_string(type_str)

            # Serialize in source language
            source_adapter = self.adapters[source_lang]
            serialized = source_adapter.serialize(value, cty_type, format)

            # Deserialize in target language
            target_adapter = self.adapters[target_lang]
            deserialized = target_adapter.deserialize(serialized, cty_type, format)

            # Compare
            success = self._compare_values(value, deserialized)

            return TestResult(
                test_name=test_name,
                success=success,
                language=f"{source_lang}->{target_lang}",
                format=format,
                operation="cross-language",
                error=None if success else "Values don't match"
            )

        except Exception as e:
            logger.error(f"🧪❌❌ Cross-language test failed: {e}")
            return TestResult(
                test_name=test_name,
                success=False,
                language=f"{source_lang}->{target_lang}",
                format=format,
                operation="cross-language",
                error=str(e)
            )

    def _parse_type_string(self, type_str: str) -> CtyType:
        """Parse type string to CtyType."""
        # Simplified parser - real implementation would be more robust
        type_str = type_str.strip()

        if type_str == "string":
            return CtyString()
        elif type_str == "number":
            return CtyNumber()
        elif type_str == "bool":
            return CtyBool()
        elif type_str == "dynamic":
            return CtyDynamic()
        elif type_str.startswith("list("):
            inner = type_str[5:-1]
            return CtyList(element_type=self._parse_type_string(inner))
        elif type_str.startswith("map("):
            inner = type_str[4:-1]
            return CtyMap(key_type=CtyString(), value_type=self._parse_type_string(inner))
        elif type_str.startswith("set("):
            inner = type_str[4:-1]
            return CtySet(element_type=self._parse_type_string(inner))
        elif type_str.startswith("object({"):
            # Parse object attributes
            attrs_str = type_str[8:-2]
            attrs = {}
            # Simple parser for object attributes
            for pair in attrs_str.split(","):
                key, val = pair.split("=")
                attrs[key.strip()] = self._parse_type_string(val.strip())
            return CtyObject(attrs)
        elif type_str.startswith("tuple(["):
            # Parse tuple elements
            elems_str = type_str[7:-2]
            elems = []
            # Simple parser for tuple elements
            for elem in elems_str.split(","):
                elems.append(self._parse_type_string(elem.strip()))
            return CtyTuple(tuple(elems))
        else:
            raise ValueError(f"Unknown type: {type_str}")

    def _compare_values(self, expected: Any, actual: Any) -> bool:
        """Compare two values for equality."""
        # Normalize numeric values
        def normalize(val):
            if isinstance(val, (int, float)):
                return Decimal(str(val))
            elif isinstance(val, dict):
                return {k: normalize(v) for k, v in val.items()}
            elif isinstance(val, list):
                return [normalize(v) for v in val]
            elif isinstance(val, set):
                return {normalize(v) for v in val}
            return val

        return normalize(expected) == normalize(actual)


# ============================================================================
# PART 4: Test Result Tracking
# ============================================================================

@dataclass
class TestResult:
    """Result of a single test execution."""
    test_name: str
    success: bool
    language: str
    format: str
    operation: str
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class TestResultCollector:
    """Collects and reports test results."""

    def __init__(self):
        self.results: list[TestResult] = []

    def add(self, result: TestResult):
        """Add a test result."""
        self.results.append(result)

        # Log result
        status = "✅" if result.success else "❌"
        logger.info(
            f"🧪{status} {result.test_name} | {result.language} | "
            f"{result.format} | {result.operation}"
        )
        if not result.success:
            logger.error(f"   Error: {result.error}")

    def get_summary(self) -> dict[str, Any]:
        """Get summary of all results."""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.success)
        failed = total - passed

        # Group by various dimensions
        by_language = {}
        by_format = {}
        by_operation = {}

        for result in self.results:
            # By language
            if result.language not in by_language:
                by_language[result.language] = {"passed": 0, "failed": 0}
            by_language[result.language]["passed" if result.success else "failed"] += 1

            # By format
            if result.format not in by_format:
                by_format[result.format] = {"passed": 0, "failed": 0}
            by_format[result.format]["passed" if result.success else "failed"] += 1

            # By operation
            if result.operation not in by_operation:
                by_operation[result.operation] = {"passed": 0, "failed": 0}
            by_operation[result.operation]["passed" if result.success else "failed"] += 1

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "success_rate": f"{(passed/total)*100:.1f}%" if total > 0 else "N/A",
            "by_language": by_language,
            "by_format": by_format,
            "by_operation": by_operation,
            "failures": [r for r in self.results if not r.success]
        }

    def print_report(self):
        """Print a formatted test report."""
        summary = self.get_summary()

        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"Total Tests: {summary['total']}")
        print(f"Passed: {summary['passed']} ({summary['success_rate']})")
        print(f"Failed: {summary['failed']}")

        print("\nBy Language:")
        for lang, stats in summary['by_language'].items():
            print(f"  {lang}: {stats['passed']} passed, {stats['failed']} failed")

        print("\nBy Format:")
        for fmt, stats in summary['by_format'].items():
            print(f"  {fmt}: {stats['passed']} passed, {stats['failed']} failed")

        if summary['failures']:
            print("\nFailed Tests:")
            for failure in summary['failures']:
                print(f"  - {failure.test_name} ({failure.language}, {failure.format})")
                print(f"    Error: {failure.error}")

        print("="*80)


# ============================================================================
# PART 5: Example Test Suite
# ============================================================================

class TestCrossLanguageCompatibility:
    """Example test suite using the DRY infrastructure."""

    @pytest.fixture(scope="class")
    def test_executor(self, tmp_path_factory):
        """Set up test executor with both language adapters."""
        working_dir = tmp_path_factory.mktemp("test_run")

        # Initialize adapters
        python_adapter = PythonToolAdapter()

        # Build/find Go tool
        go_executable = self._ensure_go_tool()
        go_adapter = GoToolAdapter(go_executable, working_dir)

        # Create executor
        return UnifiedTestExecutor(python_adapter, go_adapter)

    @pytest.fixture(scope="class")
    def result_collector(self):
        """Create result collector for the test run."""
        return TestResultCollector()

    def _ensure_go_tool(self) -> str:
        """Ensure Go tool is available."""
        # This would use the actual go_interaction module
        # For now, return a placeholder
        return "/path/to/go-ctytool"

    @pytest.mark.parametrize("test_name,type_and_value",
        [(name, (type_str, value)) for name, (type_str, value)
         in TestDataRegistry.STANDARD_CASES.items()]
    )
    @pytest.mark.parametrize("format", ["json", "msgpack"])
    @pytest.mark.parametrize("language", ["python", "go"])
    def test_roundtrips(
        self,
        test_executor: UnifiedTestExecutor,
        result_collector: TestResultCollector,
        test_name: str,
        type_and_value: tuple[str, Any],
        format: str,
        language: str
    ):
        """Test serialization roundtrips for each language."""
        type_str, value = type_and_value

        result = test_executor.test_roundtrip(
            test_name, type_str, value, format, language
        )

        result_collector.add(result)
        assert result.success, f"Roundtrip failed: {result.error}"

    @pytest.mark.parametrize("test_name,type_and_value",
        [(name, (type_str, value)) for name, (type_str, value)
         in TestDataRegistry.STANDARD_CASES.items()]
    )
    @pytest.mark.parametrize("format", ["json", "msgpack"])
    def test_cross_language(
        self,
        test_executor: UnifiedTestExecutor,
        result_collector: TestResultCollector,
        test_name: str,
        type_and_value: tuple[str, Any],
        format: str
    ):
        """Test cross-language compatibility."""
        type_str, value = type_and_value

        # Python -> Go
        result_py_go = test_executor.test_cross_language(
            test_name, type_str, value, format, "python", "go"
        )
        result_collector.add(result_py_go)

        # Go -> Python
        result_go_py = test_executor.test_cross_language(
            test_name, type_str, value, format, "go", "python"
        )
        result_collector.add(result_go_py)

        assert result_py_go.success, f"Python->Go failed: {result_py_go.error}"
        assert result_go_py.success, f"Go->Python failed: {result_go_py.error}"

    def test_print_summary(self, result_collector: TestResultCollector):
        """Print test summary at the end."""
        result_collector.print_report()


# ============================================================================
# PART 6: Property-Based Testing Integration
# ============================================================================

class TestPropertyBased:
    """Property-based tests using Hypothesis."""

    @given(
        type_str=st.sampled_from(["string", "number", "bool"]),
        format=st.sampled_from(["json", "msgpack"])
    )
    @settings(max_examples=20)
    def test_primitive_types(
        self,
        test_executor: UnifiedTestExecutor,
        type_str: str,
        format: str
    ):
        """Test primitive types with generated values."""
        # Generate appropriate value for type
        if type_str == "string":
            value = st.text(max_size=100).example()
        elif type_str == "number":
            value = st.decimals(
                min_value=-1e6,
                max_value=1e6,
                allow_nan=False,
                allow_infinity=False
            ).example()
        else:  # bool
            value = st.booleans().example()

        # Test Python roundtrip
        result = test_executor.test_roundtrip(
            "hypothesis_test", type_str, value, format, "python"
        )

        assert result.success, f"Property test failed: {result.error}"


if __name__ == "__main__":
    # Example of running tests programmatically

    # Set up test infrastructure
    working_dir = pathlib.Path("/tmp/cty_test_run")
    working_dir.mkdir(exist_ok=True)

    python_adapter = PythonToolAdapter()
    go_adapter = GoToolAdapter("/path/to/go-ctytool", working_dir)

    executor = UnifiedTestExecutor(python_adapter, go_adapter)
    collector = TestResultCollector()

    # Run a few example tests
    for test_name, (type_str, value) in list(TestDataRegistry.STANDARD_CASES.items())[:5]:
        for format in ["json", "msgpack"]:
            # Test roundtrips
            for language in ["python", "go"]:
                result = executor.test_roundtrip(
                    test_name, type_str, value, format, language
                )
                collector.add(result)

            # Test cross-language
            result = executor.test_cross_language(
                test_name, type_str, value, format, "python", "go"
            )
            collector.add(result)

    # Print results
    collector.print_report()
