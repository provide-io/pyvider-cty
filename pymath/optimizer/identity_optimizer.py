class IdentityOptimizer:
    def optimize(self, node):
        if node.type == "BINARY_OPERATION":
            if node.op == "+":
                if node.left.type == "NUMBER" and node.left.value == 0:
                    return node.right
                if node.right.type == "NUMBER" and node.right.value == 0:
                    return node.left
            elif node.op == "-":
                if node.right.type == "NUMBER" and node.right.value == 0:
                    return node.left
            elif node.op == "*":
                if node.left.type == "NUMBER" and node.left.value == 1:
                    return node.right
                if node.right.type == "NUMBER" and node.right.value == 1:
                    return node.left
                if node.left.type == "NUMBER" and node.left.value == 0:
                    return node.left
                if node.right.type == "NUMBER" and node.right.value == 0:
                    return node.right
            elif node.op == "/":
                if node.right.type == "NUMBER" and node.right.value == 1:
                    return node.left
        return node
