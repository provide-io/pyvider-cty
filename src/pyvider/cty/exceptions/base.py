#
# pyvider/cty/exceptions/base.py
#
"""
Defines the base exception for the CTY type system.
"""

from provide.foundation.errors import FoundationError


class CtyError(FoundationError):
    """
    Base exception for all pyvider.cty errors.

    This is the root exception for all errors that occur within the cty type
    system. It provides a foundation for more specific error types and can
    be used to catch any cty-related error.

    Now inherits from FoundationError to provide rich context support,
    telemetry integration, and enhanced diagnostics.

    Attributes:
        message: A human-readable error description
    """

    def __init__(
        self, message: str = "An error occurred in the cty type system", **kwargs
    ) -> None:
        self.message = message
        super().__init__(self.message, **kwargs)
    
    def _default_code(self) -> str:
        return "CTY_ERROR"


class CtyFunctionError(CtyError):
    """
    Exception raised for errors during the execution of a CTY standard library function.

    Attributes:
        message: A human-readable error description
    """

    def __init__(
        self, message: str = "An error occurred during CTY function execution"
    ) -> None:
        super().__init__(message)


# 🐍🏗️🐣
