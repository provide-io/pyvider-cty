# pyvider/cty/context/__init__.py
"""
Provides context management for CTY operations.

This package includes tools for managing and retrieving the current operational
context within the CTY system, which can influence how types and values are
processed or validated.
"""


from pyvider.cty.context.validation_context import (
    MAX_VALIDATION_DEPTH,
    deeper_validation,
    get_validation_depth,
)

__all__ = [
    "MAX_VALIDATION_DEPTH",
    "deeper_validation",
    "get_validation_depth",
]
