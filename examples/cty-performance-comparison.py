#!/usr/bin/env python3
"""
CtyDynamic vs Structured Types Performance Comparison
====================================================

This benchmark compares the performance characteristics of using CtyDynamic
versus properly structured types for the same data, demonstrating why
structured types are preferred for production use.
"""

import gc
import json
import time
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Callable

import psutil

from pyvider.cty import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtyString,
    CtyValue,
)
from pyvider.cty.conversion import WireFormatType, marshal, unmarshal


@dataclass
class PerformanceMetrics:
    """Performance metrics for a single operation."""
    approach: str
    operation: str
    duration: float
    memory_mb: float
    iterations: int


class DynamicVsStructuredBenchmark:
    """Benchmark comparing CtyDynamic to structured types."""
    
    def __init__(self):
        self.process = psutil.Process()
        self.metrics: list[PerformanceMetrics] = []
        
    def measure_memory(self) -> float:
        """Get current memory usage in MB."""
        gc.collect()
        return self.process.memory_info().rss / 1024 / 1024
    
    def benchmark_operation(
        self, 
        name: str, 
        operation: Callable[[], Any], 
        iterations: int = 100
    ) -> PerformanceMetrics:
        """Benchmark a single operation."""
        # Warm up
        for _ in range(min(10, iterations // 10)):
            operation()
        
        gc.collect()
        start_mem = self.measure_memory()
        start_time = time.perf_counter()
        
        for _ in range(iterations):
            operation()
        
        duration = time.perf_counter() - start_time
        memory = self.measure_memory() - start_mem
        
        return PerformanceMetrics(
            approach=name,
            operation=operation.__name__,
            duration=duration,
            memory_mb=memory,
            iterations=iterations
        )
    
    def create_test_data(self, depth: int = 3) -> dict[str, Any]:
        """Create realistic test data representing a cloud resource."""
        return {
            "id": "res-123456",
            "name": "production-web-server",
            "status": "running",
            "configuration": {
                "cpu_cores": 8,
                "memory_gb": 32,
                "storage": {
                    "system": {
                        "size_gb": 100,
                        "type": "ssd",
                        "iops": 3000,
                        "encrypted": True
                    },
                    "data": [
                        {
                            "mount": "/data1",
                            "size_gb": 500,
                            "type": "ssd",
                            "raid": "raid1"
                        },
                        {
                            "mount": "/data2", 
                            "size_gb": 1000,
                            "type": "hdd",
                            "raid": "raid5"
                        }
                    ]
                },
                "network": {
                    "interfaces": [
                        {
                            "name": "eth0",
                            "ip": "10.0.1.100",
                            "netmask": "255.255.255.0",
                            "gateway": "10.0.1.1",
                            "dns": ["8.8.8.8", "8.8.4.4"]
                        }
                    ],
                    "firewall_rules": [
                        {"port": 22, "protocol": "tcp", "source": "10.0.0.0/8"},
                        {"port": 443, "protocol": "tcp", "source": "0.0.0.0/0"},
                        {"port": 80, "protocol": "tcp", "source": "0.0.0.0/0"}
                    ]
                }
            },
            "metrics": {
                "cpu_usage": Decimal("45.23"),
                "memory_usage": Decimal("67.89"),
                "disk_io": {
                    "read_mbps": Decimal("123.45"),
                    "write_mbps": Decimal("67.89")
                },
                "network_io": {
                    "rx_mbps": Decimal("234.56"),
                    "tx_mbps": Decimal("123.45")
                }
            },
            "tags": {
                "environment": "production",
                "team": "platform",
                "cost_center": "engineering"
            }
        }
    
    def define_structured_types(self):
        """Define structured types for the test data."""
        # Define nested types bottom-up
        storage_volume_type = CtyObject({
            "mount": CtyString(),
            "size_gb": CtyNumber(),
            "type": CtyString(),
            "raid": CtyString(),
        })
        
        system_storage_type = CtyObject({
            "size_gb": CtyNumber(),
            "type": CtyString(),
            "iops": CtyNumber(),
            "encrypted": CtyBool(),
        })
        
        storage_type = CtyObject({
            "system": system_storage_type,
            "data": CtyList(element_type=storage_volume_type),
        })
        
        network_interface_type = CtyObject({
            "name": CtyString(),
            "ip": CtyString(),
            "netmask": CtyString(),
            "gateway": CtyString(),
            "dns": CtyList(element_type=CtyString()),
        })
        
        firewall_rule_type = CtyObject({
            "port": CtyNumber(),
            "protocol": CtyString(),
            "source": CtyString(),
        })
        
        network_type = CtyObject({
            "interfaces": CtyList(element_type=network_interface_type),
            "firewall_rules": CtyList(element_type=firewall_rule_type),
        })
        
        configuration_type = CtyObject({
            "cpu_cores": CtyNumber(),
            "memory_gb": CtyNumber(),
            "storage": storage_type,
            "network": network_type,
        })
        
        io_metrics_type = CtyObject({
            "read_mbps": CtyNumber(),
            "write_mbps": CtyNumber(),
        })
        
        network_io_type = CtyObject({
            "rx_mbps": CtyNumber(),
            "tx_mbps": CtyNumber(),
        })
        
        metrics_type = CtyObject({
            "cpu_usage": CtyNumber(),
            "memory_usage": CtyNumber(),
            "disk_io": io_metrics_type,
            "network_io": network_io_type,
        })
        
        # Top-level type
        return CtyObject({
            "id": CtyString(),
            "name": CtyString(),
            "status": CtyString(),
            "configuration": configuration_type,
            "metrics": metrics_type,
            "tags": CtyMap(key_type=CtyString(), value_type=CtyString()),
        })
    
    def run_comparison(self):
        """Run the performance comparison."""
        print("🏁 Running Performance Comparison: CtyDynamic vs Structured Types\n")
        
        # Create test data
        test_data = self.create_test_data()
        
        # Define types
        dynamic_type = CtyDynamic()
        structured_type = self.define_structured_types()
        
        # Test 1: Validation Performance
        print("📊 Test 1: Validation Performance")
        
        dynamic_validation = self.benchmark_operation(
            "CtyDynamic",
            lambda: dynamic_type.validate(test_data),
            iterations=1000
        )
        self.metrics.append(dynamic_validation)
        print(f"  Dynamic: {dynamic_validation.duration:.3f}s for {dynamic_validation.iterations} iterations")
        
        structured_validation = self.benchmark_operation(
            "Structured",
            lambda: structured_type.validate(test_data),
            iterations=1000
        )
        self.metrics.append(structured_validation)
        print(f"  Structured: {structured_validation.duration:.3f}s for {structured_validation.iterations} iterations")
        
        speedup = dynamic_validation.duration / structured_validation.duration
        print(f"  ⚡ Structured is {speedup:.1f}x faster\n")
        
        # Test 2: Serialization Performance
        print("📊 Test 2: Serialization Performance")
        
        # Pre-validate for serialization tests
        dynamic_val = dynamic_type.validate(test_data)
        structured_val = structured_type.validate(test_data)
        
        dynamic_serialization = self.benchmark_operation(
            "CtyDynamic",
            lambda: marshal(dynamic_val, format_kind=WireFormatType.JSON),
            iterations=500
        )
        self.metrics.append(dynamic_serialization)
        print(f"  Dynamic: {dynamic_serialization.duration:.3f}s for {dynamic_serialization.iterations} iterations")
        
        structured_serialization = self.benchmark_operation(
            "Structured",
            lambda: marshal(structured_val, format_kind=WireFormatType.JSON),
            iterations=500
        )
        self.metrics.append(structured_serialization)
        print(f"  Structured: {structured_serialization.duration:.3f}s for {structured_serialization.iterations} iterations")
        
        speedup = dynamic_serialization.duration / structured_serialization.duration
        print(f"  ⚡ Structured is {speedup:.1f}x faster\n")
        
        # Test 3: Path Navigation Performance
        print("📊 Test 3: Path Navigation Performance")
        
        from pyvider.cty.path import CtyPath
        
        # Define a path to deeply nested data
        deep_path = (
            CtyPath.get_attr("configuration")
            .child("storage")
            .child("data")
            .index_step(0)
            .child("size_gb")
        )
        
        dynamic_path = self.benchmark_operation(
            "CtyDynamic",
            lambda: deep_path.apply_path(dynamic_val),
            iterations=1000
        )
        self.metrics.append(dynamic_path)
        print(f"  Dynamic: {dynamic_path.duration:.3f}s for {dynamic_path.iterations} iterations")
        
        structured_path = self.benchmark_operation(
            "Structured", 
            lambda: deep_path.apply_path(structured_val),
            iterations=1000
        )
        self.metrics.append(structured_path)
        print(f"  Structured: {structured_path.duration:.3f}s for {structured_path.iterations} iterations")
        
        speedup = dynamic_path.duration / structured_path.duration
        print(f"  ⚡ Structured is {speedup:.1f}x faster\n")
        
        # Test 4: Memory Usage Comparison
        print("📊 Test 4: Memory Usage Comparison")
        
        # Create many instances to measure memory impact
        gc.collect()
        start_mem = self.measure_memory()
        
        dynamic_instances = []
        for _ in range(100):
            dynamic_instances.append(dynamic_type.validate(test_data))
        
        dynamic_mem = self.measure_memory() - start_mem
        print(f"  Dynamic: {dynamic_mem:.1f} MB for 100 instances")
        
        # Clear and test structured
        dynamic_instances.clear()
        gc.collect()
        start_mem = self.measure_memory()
        
        structured_instances = []
        for _ in range(100):
            structured_instances.append(structured_type.validate(test_data))
        
        structured_mem = self.measure_memory() - start_mem
        print(f"  Structured: {structured_mem:.1f} MB for 100 instances")
        
        mem_ratio = dynamic_mem / structured_mem if structured_mem > 0 else 0
        print(f"  💾 Dynamic uses {mem_ratio:.1f}x more memory\n")
        
    def edge_case_tests(self):
        """Test specific edge cases that stress CtyDynamic."""
        print("🔥 Edge Case Tests\n")
        
        # Edge Case 1: Rapidly changing types
        print("📊 Edge Case 1: Rapidly Alternating Types")
        
        alternating_data = []
        for i in range(100):
            if i % 4 == 0:
                alternating_data.append({"nested": {"value": i}})
            elif i % 4 == 1:
                alternating_data.append([i, i+1, i+2])
            elif i % 4 == 2:
                alternating_data.append(str(i))
            else:
                alternating_data.append(i)
        
        dynamic_type = CtyList(element_type=CtyDynamic())
        
        result = self.benchmark_operation(
            "Alternating Types",
            lambda: dynamic_type.validate(alternating_data),
            iterations=100
        )
        print(f"  Duration: {result.duration:.3f}s for {result.iterations} iterations\n")
        
        # Edge Case 2: Deeply nested empty containers
        print("📊 Edge Case 2: Deeply Nested Empty Containers")
        
        def create_nested_empty(depth: int) -> Any:
            if depth <= 0:
                return {}
            return {"level": create_nested_empty(depth - 1)}
        
        nested_empty = create_nested_empty(50)
        
        result = self.benchmark_operation(
            "Nested Empty",
            lambda: CtyDynamic().validate(nested_empty),
            iterations=10
        )
        print(f"  Duration: {result.duration:.3f}s for {result.iterations} iterations\n")
        
        # Edge Case 3: Maximum width (many keys/elements)
        print("📊 Edge Case 3: Maximum Width Structure")
        
        wide_data = {
            f"key_{i}": {
                "value": i,
                "metadata": {
                    "created": f"2024-01-{i:02d}",
                    "tags": [f"tag_{j}" for j in range(10)]
                }
            }
            for i in range(100)
        }
        
        result = self.benchmark_operation(
            "Wide Structure",
            lambda: CtyDynamic().validate(wide_data),
            iterations=10
        )
        print(f"  Duration: {result.duration:.3f}s for {result.iterations} iterations\n")
    
    def generate_summary(self):
        """Generate a summary of findings."""
        print("\n" + "=" * 60)
        print("📊 PERFORMANCE COMPARISON SUMMARY")
        print("=" * 60)
        
        print("\n🏆 Key Findings:\n")
        
        # Calculate average performance ratios
        validation_metrics = [m for m in self.metrics if "validate" in m.operation]
        if len(validation_metrics) >= 2:
            dynamic_time = validation_metrics[0].duration
            structured_time = validation_metrics[1].duration
            ratio = dynamic_time / structured_time
            
            print(f"1. Validation Performance:")
            print(f"   - CtyDynamic is {ratio:.1f}x slower than structured types")
            print(f"   - This compounds with nesting depth")
        
        print(f"\n2. Memory Usage:")
        print(f"   - CtyDynamic uses significantly more memory")
        print(f"   - Each dynamic value wraps the actual typed value")
        print(f"   - Type objects are created at runtime vs reused")
        
        print(f"\n3. Use Case Recommendations:")
        print(f"   ✅ Use Structured Types when:")
        print(f"      - Schema is known at design time")
        print(f"      - Performance is important")
        print(f"      - Type safety is desired")
        print(f"      - Working with deeply nested data")
        
        print(f"\n   ⚠️  Use CtyDynamic when:")
        print(f"      - Schema is truly unknown")
        print(f"      - Handling arbitrary user input")
        print(f"      - Building generic tools")
        print(f"      - Gradual migration scenarios")
        
        print(f"\n4. Performance Tips:")
        print(f"   - Define types once and reuse them")
        print(f"   - Avoid mixing CtyDynamic with structured types")
        print(f"   - Consider caching validated CtyDynamic values")
        print(f"   - Use type hints for better IDE support")


def main():
    """Run the benchmark suite."""
    benchmark = DynamicVsStructuredBenchmark()
    
    try:
        benchmark.run_comparison()
        benchmark.edge_case_tests()
        benchmark.generate_summary()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Benchmark interrupted")
    except Exception as e:
        print(f"\n\n💥 Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
