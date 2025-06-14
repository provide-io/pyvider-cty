from pymath.optimizer.identity_optimizer import IdentityOptimizer

class Optimizer:
    def __init__(self):
        self.optimizers = [
            IdentityOptimizer()
        ]

    def optimize(self, node):
        for optimizer in self.optimizers:
            node = optimizer.optimize(node)
        return node
