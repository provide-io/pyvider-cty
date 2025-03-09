"""Terraform type system."""

from .collections import (
    TFList,
    TFMap,
    TFSet,
)
from .primitives import (
    TFBool,
    TFNumber,
    TFString,
)
from .structural import (
    TFDynamic,
    TFObject,
    TFTuple,
)
from .type import (
    TFType,
)

__all__ = [
    "TFType",

    "TFBool",
    "TFNumber",
    "TFString",

    "TFList",
    "TFMap",
    "TFSet",

    "TFDynamic",
    "TFObject",
    "TFTuple",
]
