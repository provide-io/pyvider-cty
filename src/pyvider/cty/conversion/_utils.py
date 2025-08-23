# pyvider-cty/src/pyvider/cty/conversion/_utils.py
"""Internal conversion utilities to avoid circular dependencies."""
from typing import Any


def _attrs_to_dict_safe(inst: Any) -> dict[str, Any]:
    """
    Safely converts an attrs instance to a dict, raising TypeError for CTY
    framework types to prevent accidental misuse during type inference.
    """
    # Local imports to prevent circular dependencies at module load time.
    from pyvider.cty.types import CtyType
    from pyvider.cty.values import CtyValue

    if isinstance(inst, CtyType):
        raise TypeError(
            f"Cannot infer data type from a CtyType instance: {type(inst).__name__}"
        )
    if isinstance(inst, CtyValue):
        raise TypeError(
            f"Cannot infer data type from a CtyValue instance: {type(inst).__name__}"
        )

    res = {}
    # Use getattr to safely access __attrs_attrs__ which may not exist.
    for a in getattr(type(inst), "__attrs_attrs__", []):
        res[a.name] = getattr(inst, a.name)
    return res
