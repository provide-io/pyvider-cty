import unittest

from pymath.optimizer import Optimizer
from pymath.parser import Node  # Assuming Node class exists in pymath.parser

class TestOptimizer(unittest.TestCase):
    def setUp(self):
        self.optimizer = Optimizer()

    def test_addition_with_zero_left(self):
        # 0 + x = x
        node = Node("BINARY_OPERATION", op="+", left=Node("NUMBER", value=0), right=Node("VARIABLE", name="x"))
        optimized_node = self.optimizer.optimize(node)
        self.assertEqual(optimized_node.type, "VARIABLE")
        self.assertEqual(optimized_node.name, "x")

    def test_addition_with_zero_right(self):
        # x + 0 = x
        node = Node("BINARY_OPERATION", op="+", left=Node("VARIABLE", name="x"), right=Node("NUMBER", value=0))
        optimized_node = self.optimizer.optimize(node)
        self.assertEqual(optimized_node.type, "VARIABLE")
        self.assertEqual(optimized_node.name, "x")

    def test_subtraction_with_zero_right(self):
        # x - 0 = x
        node = Node("BINARY_OPERATION", op="-", left=Node("VARIABLE", name="x"), right=Node("NUMBER", value=0))
        optimized_node = self.optimizer.optimize(node)
        self.assertEqual(optimized_node.type, "VARIABLE")
        self.assertEqual(optimized_node.name, "x")

    def test_multiplication_by_one_left(self):
        # 1 * x = x
        node = Node("BINARY_OPERATION", op="*", left=Node("NUMBER", value=1), right=Node("VARIABLE", name="x"))
        optimized_node = self.optimizer.optimize(node)
        self.assertEqual(optimized_node.type, "VARIABLE")
        self.assertEqual(optimized_node.name, "x")

    def test_multiplication_by_one_right(self):
        # x * 1 = x
        node = Node("BINARY_OPERATION", op="*", left=Node("VARIABLE", name="x"), right=Node("NUMBER", value=1))
        optimized_node = self.optimizer.optimize(node)
        self.assertEqual(optimized_node.type, "VARIABLE")
        self.assertEqual(optimized_node.name, "x")

    def test_multiplication_by_zero_left(self):
        # 0 * x = 0
        node = Node("BINARY_OPERATION", op="*", left=Node("NUMBER", value=0), right=Node("VARIABLE", name="x"))
        optimized_node = self.optimizer.optimize(node)
        self.assertEqual(optimized_node.type, "NUMBER")
        self.assertEqual(optimized_node.value, 0)

    def test_multiplication_by_zero_right(self):
        # x * 0 = 0
        node = Node("BINARY_OPERATION", op="*", left=Node("VARIABLE", name="x"), right=Node("NUMBER", value=0))
        optimized_node = self.optimizer.optimize(node)
        self.assertEqual(optimized_node.type, "NUMBER")
        self.assertEqual(optimized_node.value, 0)

    def test_division_by_one_right(self):
        # x / 1 = x
        node = Node("BINARY_OPERATION", op="/", left=Node("VARIABLE", name="x"), right=Node("NUMBER", value=1))
        optimized_node = self.optimizer.optimize(node)
        self.assertEqual(optimized_node.type, "VARIABLE")
        self.assertEqual(optimized_node.name, "x")

if __name__ == "__main__":
    unittest.main()
