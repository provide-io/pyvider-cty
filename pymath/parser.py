class Node:
    def __init__(self, type, **kwargs):
        self.type = type
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        attrs = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items() if k != "type")
        return f"Node({self.type!r}, {attrs})"

    def __eq__(self, other):
        if not isinstance(other, Node):
            return NotImplemented
        return self.__dict__ == other.__dict__
