# src/pyvider/cty/marks.py
# 🐍✨


from attrs import define, field


@define(frozen=True, slots=True)
class CtyMark:
    """
    Represents a mark that can be applied to a cty.Value.
    Marks are used to attach metadata or annotations to values as they
    flow through a system, often indicating attributes like sensitivity,
    provenance, or other operational concerns.
    """
    name: str = field()
    details: object | None = field(default=None)

    def __repr__(self) -> str:
        if self.details is not None:
            return f"CtyMark({self.name!r}, {self.details!r})"
        return f"CtyMark({self.name!r})"

# ✨🔧
