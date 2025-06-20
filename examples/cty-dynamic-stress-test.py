#!/usr/bin/env python3
"""
CtyDynamic Stress Test Suite
============================

This test suite deliberately uses deeply nested CtyDynamic types to:
1. Benchmark performance under extreme conditions
2. Detect recursion limits and stack overflow issues  
3. Identify memory usage patterns and potential leaks
4. Find edge cases in type inference and validation
5. Test serialization/deserialization robustness

These are NOT recommended patterns for production use, but excellent
for finding implementation limits and optimization opportunities.
"""

import gc
import json
import sys
import time
import traceback
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Callable

import psutil

from pyvider.cty import (
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtyString,
    CtyValue,
)
from pyvider.cty.conversion import WireFormatType, marshal, unmarshal
from pyvider.cty.exceptions import CtyValidationError


@dataclass
class BenchmarkResult:
    """Results from a benchmark run."""
    name: str
    depth: int
    validation_time: float
    serialization_time: float
    deserialization_time: float
    memory_used: float
    error: str | None = None
    stack_depth: int = 0


class CtyDynamicStressTest:
    """Stress testing suite for CtyDynamic with deep nesting."""
    
    def __init__(self):
        self.results: list[BenchmarkResult] = []
        self.process = psutil.Process()
        
    def measure_memory(self) -> float:
        """Get current memory usage in MB."""
        gc.collect()  # Force garbage collection for accurate measurement
        return self.process.memory_info().rss / 1024 / 1024
        
    def create_deeply_nested_dict(self, depth: int, width: int = 2) -> dict[str, Any]:
        """Create a deeply nested dictionary structure."""
        if depth <= 0:
            return {"leaf": "value", "number": 42, "decimal": Decimal("3.14")}
        
        result = {}
        for i in range(width):
            result[f"level_{depth}_item_{i}"] = self.create_deeply_nested_dict(depth - 1, width)
        
        # Add some variety
        result["list_data"] = [
            self.create_deeply_nested_dict(max(0, depth - 2), width=1) 
            for _ in range(min(width, 3))
        ]
        
        return result
    
    def create_deeply_nested_mixed(self, depth: int) -> Any:
        """Create a mixed deeply nested structure with lists and dicts."""
        if depth <= 0:
            return ["final", 123, True, None, {"end": "yes"}]
        
        if depth % 2 == 0:
            # Even depths: return a dict
            return {
                "nested_list": [self.create_deeply_nested_mixed(depth - 1) for _ in range(2)],
                "nested_dict": self.create_deeply_nested_mixed(depth - 1),
                "metadata": {
                    "depth": depth,
                    "values": [1.1, 2.2, 3.3],
                }
            }
        else:
            # Odd depths: return a list
            return [
                self.create_deeply_nested_mixed(depth - 1),
                {"inline": "dict", "depth": depth},
                [i * 1.5 for i in range(3)],
            ]
    
    def test_pure_dynamic_validation(self, depth: int) -> BenchmarkResult:
        """Test validation with pure CtyDynamic."""
        name = f"pure_dynamic_depth_{depth}"
        print(f"\n🧪 Testing {name}...")
        
        try:
            # Create test data
            test_data = self.create_deeply_nested_dict(depth)
            
            # Measure validation
            start_mem = self.measure_memory()
            start_time = time.perf_counter()
            
            dynamic_type = CtyDynamic()
            validated = dynamic_type.validate(test_data)
            
            validation_time = time.perf_counter() - start_time
            validation_mem = self.measure_memory() - start_mem
            
            # Test serialization
            start_time = time.perf_counter()
            serialized = marshal(validated, format_kind=WireFormatType.JSON)
            serialization_time = time.perf_counter() - start_time
            
            # Test deserialization  
            start_time = time.perf_counter()
            deserialized = unmarshal(serialized, format_kind=WireFormatType.JSON, expected_type=dynamic_type)
            deserialization_time = time.perf_counter() - start_time
            
            # Get stack depth estimate
            stack_depth = self._estimate_stack_depth(validated)
            
            result = BenchmarkResult(
                name=name,
                depth=depth,
                validation_time=validation_time,
                serialization_time=serialization_time,
                deserialization_time=deserialization_time,
                memory_used=validation_mem,
                stack_depth=stack_depth,
            )
            
            print(f"✅ Success: val={validation_time:.3f}s, ser={serialization_time:.3f}s, "
                  f"deser={deserialization_time:.3f}s, mem={validation_mem:.1f}MB")
            
            return result
            
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            print(f"❌ Failed: {error_msg}")
            
            return BenchmarkResult(
                name=name,
                depth=depth,
                validation_time=0,
                serialization_time=0,
                deserialization_time=0,
                memory_used=0,
                error=error_msg,
            )
    
    def test_dynamic_in_structures(self, depth: int) -> BenchmarkResult:
        """Test CtyDynamic embedded in structured types."""
        name = f"dynamic_in_structures_depth_{depth}"
        print(f"\n🧪 Testing {name}...")
        
        try:
            # Create a structure with CtyDynamic fields
            structure_type = CtyObject({
                "id": CtyString(),
                "dynamic_data": CtyDynamic(),  # This will hold deep nesting
                "dynamic_list": CtyList(element_type=CtyDynamic()),
                "dynamic_map": CtyMap(key_type=CtyString(), value_type=CtyDynamic()),
            })
            
            # Create test data
            nested_data = self.create_deeply_nested_dict(depth - 1) if depth > 0 else "leaf"
            test_data = {
                "id": "test_entity",
                "dynamic_data": nested_data,
                "dynamic_list": [
                    self.create_deeply_nested_mixed(max(0, depth - 2)) 
                    for _ in range(3)
                ],
                "dynamic_map": {
                    f"key_{i}": self.create_deeply_nested_dict(max(0, depth - 2), width=1)
                    for i in range(3)
                },
            }
            
            # Measure validation
            start_mem = self.measure_memory()
            start_time = time.perf_counter()
            
            validated = structure_type.validate(test_data)
            
            validation_time = time.perf_counter() - start_time
            validation_mem = self.measure_memory() - start_mem
            
            # Test serialization
            start_time = time.perf_counter()
            serialized = marshal(validated, format_kind=WireFormatType.JSON)
            serialization_time = time.perf_counter() - start_time
            
            # Test deserialization
            start_time = time.perf_counter()
            deserialized = unmarshal(serialized, format_kind=WireFormatType.JSON, expected_type=structure_type)
            deserialization_time = time.perf_counter() - start_time
            
            result = BenchmarkResult(
                name=name,
                depth=depth,
                validation_time=validation_time,
                serialization_time=serialization_time,
                deserialization_time=deserialization_time,
                memory_used=validation_mem,
            )
            
            print(f"✅ Success: val={validation_time:.3f}s, ser={serialization_time:.3f}s, "
                  f"deser={deserialization_time:.3f}s, mem={validation_mem:.1f}MB")
            
            return result
            
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            print(f"❌ Failed: {error_msg}")
            
            return BenchmarkResult(
                name=name,
                depth=depth,
                validation_time=0,
                serialization_time=0,
                deserialization_time=0,
                memory_used=0,
                error=error_msg,
            )
    
    def test_pathological_case(self) -> BenchmarkResult:
        """Test a pathological case designed to stress the system."""
        name = "pathological_mixed_depth"
        print(f"\n🧪 Testing {name}...")
        
        try:
            # Create a structure that alternates between different types
            # This forces constant type switching and inference
            def create_pathological(depth: int) -> Any:
                if depth <= 0:
                    return [{"a": 1}, "string", [1, 2, 3], True, None, Decimal("99.99")]
                
                return {
                    "list_of_mixed": [
                        create_pathological(depth - 1),
                        {"inline_dict": create_pathological(depth - 2)},
                        [create_pathological(depth - 2) for _ in range(2)],
                    ],
                    "dict_of_mixed": {
                        f"key_{i}": create_pathological(depth - 1 - i)
                        for i in range(min(depth, 3))
                    },
                    "direct": create_pathological(depth - 1),
                }
            
            test_data = create_pathological(10)
            
            # Test with pure dynamic
            start_mem = self.measure_memory()
            start_time = time.perf_counter()
            
            dynamic_type = CtyDynamic()
            validated = dynamic_type.validate(test_data)
            
            validation_time = time.perf_counter() - start_time
            validation_mem = self.measure_memory() - start_mem
            
            # Test serialization
            start_time = time.perf_counter()
            serialized = marshal(validated, format_kind=WireFormatType.JSON)
            serialization_time = time.perf_counter() - start_time
            
            # Verify JSON size
            json_size = len(serialized) / 1024  # KB
            print(f"  JSON size: {json_size:.1f} KB")
            
            # Test deserialization
            start_time = time.perf_counter()
            deserialized = unmarshal(serialized, format_kind=WireFormatType.JSON, expected_type=dynamic_type)
            deserialization_time = time.perf_counter() - start_time
            
            result = BenchmarkResult(
                name=name,
                depth=10,  # nominal depth
                validation_time=validation_time,
                serialization_time=serialization_time,
                deserialization_time=deserialization_time,
                memory_used=validation_mem,
            )
            
            print(f"✅ Success: val={validation_time:.3f}s, ser={serialization_time:.3f}s, "
                  f"deser={deserialization_time:.3f}s, mem={validation_mem:.1f}MB")
            
            return result
            
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            print(f"❌ Failed: {error_msg}")
            traceback.print_exc()
            
            return BenchmarkResult(
                name=name,
                depth=10,
                validation_time=0,
                serialization_time=0,
                deserialization_time=0,
                memory_used=0,
                error=error_msg,
            )
    
    def _estimate_stack_depth(self, value: CtyValue) -> int:
        """Estimate the maximum stack depth of a CtyValue structure."""
        if value.is_null or value.is_unknown:
            return 0
            
        if isinstance(value.type, CtyDynamic) and isinstance(value.value, CtyValue):
            # Dynamic wrapping another value
            return 1 + self._estimate_stack_depth(value.value)
        
        max_depth = 0
        
        # Check collections
        if hasattr(value, 'value') and isinstance(value.value, list):
            for item in value.value:
                if isinstance(item, CtyValue):
                    max_depth = max(max_depth, self._estimate_stack_depth(item))
        elif hasattr(value, 'value') and isinstance(value.value, dict):
            for v in value.value.values():
                if isinstance(v, CtyValue):
                    max_depth = max(max_depth, self._estimate_stack_depth(v))
        
        return 1 + max_depth
    
    def find_limits(self):
        """Find the depth limits where things start breaking."""
        print("\n🔍 Finding depth limits...\n")
        
        # Test pure dynamic at increasing depths
        depths = [1, 5, 10, 20, 30, 40, 50, 75, 100, 150, 200]
        
        print("Pure CtyDynamic validation:")
        for depth in depths:
            result = self.test_pure_dynamic_validation(depth)
            self.results.append(result)
            
            if result.error:
                print(f"  → Limit found at depth {depth}")
                break
        
        print("\nCtyDynamic in structures:")
        for depth in depths[:6]:  # Test fewer depths for structured
            result = self.test_dynamic_in_structures(depth)
            self.results.append(result)
            
            if result.error:
                print(f"  → Limit found at depth {depth}")
                break
        
        # Test pathological case
        pathological_result = self.test_pathological_case()
        self.results.append(pathological_result)
    
    def analyze_performance_scaling(self):
        """Analyze how performance scales with depth."""
        print("\n📊 Performance Scaling Analysis\n")
        
        # Filter successful results
        successful = [r for r in self.results if not r.error and "pure_dynamic" in r.name]
        
        if len(successful) >= 2:
            # Calculate scaling factors
            depths = [r.depth for r in successful]
            val_times = [r.validation_time for r in successful]
            
            # Simple scaling analysis
            if len(depths) > 1:
                depth_ratio = depths[-1] / depths[0]
                time_ratio = val_times[-1] / val_times[0] if val_times[0] > 0 else 0
                
                print(f"Depth increased by {depth_ratio:.1f}x")
                print(f"Validation time increased by {time_ratio:.1f}x")
                
                if time_ratio > depth_ratio ** 2:
                    print("⚠️  Performance appears to scale worse than O(n²)")
                elif time_ratio > depth_ratio:
                    print("⚠️  Performance appears to scale worse than O(n)")
                else:
                    print("✅ Performance scales linearly or better")
    
    def generate_report(self):
        """Generate a summary report of findings."""
        print("\n" + "=" * 60)
        print("📋 STRESS TEST SUMMARY REPORT")
        print("=" * 60)
        
        # Find maximum successful depth
        max_depth = 0
        for r in self.results:
            if not r.error and "pure_dynamic" in r.name:
                max_depth = max(max_depth, r.depth)
        
        print(f"\n✅ Maximum successful depth: {max_depth}")
        
        # Find failure points
        failures = [r for r in self.results if r.error]
        if failures:
            print(f"\n❌ Failures detected at depths: {[f.depth for f in failures]}")
            for f in failures:
                print(f"  - Depth {f.depth}: {f.error}")
        
        # Memory usage analysis
        print("\n💾 Memory Usage:")
        for r in self.results:
            if not r.error:
                print(f"  - {r.name}: {r.memory_used:.1f} MB")
        
        # Performance bottlenecks
        print("\n⏱️  Performance Bottlenecks:")
        slow_results = [r for r in self.results if r.validation_time > 1.0]
        if slow_results:
            for r in slow_results:
                print(f"  - {r.name}: {r.validation_time:.2f}s validation")
        else:
            print("  - No operations exceeded 1 second")
        
        # Recommendations
        print("\n💡 Recommendations:")
        print("  1. Consider adding recursion depth limits to prevent stack overflow")
        print("  2. Implement type caching for repeated CtyDynamic inference")
        print("  3. Add early termination for pathological nesting patterns")
        print("  4. Consider lazy evaluation for deeply nested structures")
        
        self.analyze_performance_scaling()


def main():
    """Run the stress test suite."""
    print("🚀 CtyDynamic Deep Nesting Stress Test Suite")
    print("=" * 60)
    
    # Check current recursion limit
    current_limit = sys.getrecursionlimit()
    print(f"Current recursion limit: {current_limit}")
    
    # Optionally increase it for testing (be careful!)
    # sys.setrecursionlimit(min(3000, current_limit * 2))
    
    # Run tests
    tester = CtyDynamicStressTest()
    
    try:
        tester.find_limits()
        tester.generate_report()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        tester.generate_report()
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {type(e).__name__}: {e}")
        traceback.print_exc()
        tester.generate_report()


if __name__ == "__main__":
    main()
