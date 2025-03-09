"""Terraform type system."""

from .bool import TFBool
from .number import TFNumber
from .string import TFString

__all__ = [
    'TFBool',
    'TFNumber',
    'TFString',
]
