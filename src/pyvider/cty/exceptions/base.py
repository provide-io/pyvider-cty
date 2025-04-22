#
# pyvider/cty/exceptions/base.py
#

class CtyError(Exception):
    """
    Base exception for all pyvider.cty errors.

    This is the root exception for all errors that occur within the cty type
    system. It provides a foundation for more specific error types and can
    be used to catch any cty-related error.

    Attributes:
        message: A human-readable error description
    """
    def __init__(self, message: str = "An error occurred in the cty type system"):
        self.message = message
        super().__init__(self.message)

# 🐍🏗️🐣
