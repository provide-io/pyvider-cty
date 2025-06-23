#
# pyvider/cty/values/__init__.py
#
"""
CTY Value Representation.

This package defines CtyValue, the runtime representation of values
within the CTY type system. CtyValue instances pair a Python value
with its corresponding CtyType and associated metadata.
"""

from pyvider.cty.values.base import CtyValue

__all__ = [
    "CtyValue",
]

# 🐍🏗️🐣
