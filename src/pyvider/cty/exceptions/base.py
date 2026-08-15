#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from __future__ import annotations

from typing import Any

from provide.foundation.errors import FoundationError

#
# pyvider/cty/exceptions/base.py
#
"""
Defines the base exception for the CTY type system.
"""


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

    def __init__(self, message: str = "An error occurred in the cty type system", **kwargs: Any) -> None:
        self.message = message
        super().__init__(self.message, **kwargs)

    def _default_code(self) -> str:
        return "CTY_ERROR"


class CtyMarksSerializationError(CtyError):
    """Raised when a value carrying marks is serialized.

    Marks have no wire representation. `tfplugin6.DynamicValue` carries only
    `msgpack` and `json` -- there is no channel for them -- so serializing a
    marked value would silently drop the flag and hand Terraform a sensitive
    value it no longer knows is sensitive.

    go-cty refuses the same way (`cty/msgpack/marshal.go`: "value has marks, so
    it cannot be serialized"), and for the same reason: dropping a mark is not
    a degradation the caller can detect, so it has to be an error rather than a
    silent success.

    Sensitivity reaches Terraform through the *schema* -- `Schema.Attribute.
    sensitive` -- not through the value, so unmark before serializing.

    Attributes:
        message: A human-readable error description
        path: Where in the value the mark was found, if known
    """

    def __init__(
        self,
        message: str = "value has marks, so it cannot be serialized",
        *,
        path: str | None = None,
        **kwargs: Any,
    ) -> None:
        self.path = path
        if path:
            message = f"{message} (at {path})"
        super().__init__(message, **kwargs)

    def _default_code(self) -> str:
        return "CTY_MARKS_NOT_SERIALIZABLE"


class CtyFunctionError(CtyError):
    """
    Exception raised for errors during the execution of a CTY standard library function.

    Enhanced with rich context support for function name, arguments, and execution details.

    Attributes:
        message: A human-readable error description
        function_name: Name of the CTY function that failed
    """

    def __init__(
        self,
        message: str = "An error occurred during CTY function execution",
        *,
        function_name: str | None = None,
        input_types: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        self.function_name = function_name
        self.input_types = input_types or []

        # Add function-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "function_execution"
        context["cty.operation"] = "cty_function"

        if function_name:
            context["cty.function_name"] = function_name

        if input_types:
            context["cty.function_input_types"] = input_types
            context["cty.function_arity"] = len(input_types)

        # Enhance message if function name available
        if function_name:
            message = f"CTY function '{function_name}' failed: {message}"

        super().__init__(message, **kwargs)

    def _default_code(self) -> str:
        return "CTY_FUNCTION_ERROR"


# 🌊🪢🔚
