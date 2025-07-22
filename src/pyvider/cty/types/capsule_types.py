"""
Defines standard, built-in capsule types for pyvider.cty.
"""
from .capsule import CtyCapsule

BytesCapsule = CtyCapsule("Bytes", bytes)
"""A capsule type for wrapping raw bytes."""
