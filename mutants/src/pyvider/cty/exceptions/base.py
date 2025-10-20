# pyvider/cty/exceptions/base.py
#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Any

from provide.foundation.errors import FoundationError

#
# pyvider/cty/exceptions/base.py
#
"""
Defines the base exception for the CTY type system.
"""
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


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

    def xǁCtyErrorǁ__init____mutmut_orig(self, message: str = "An error occurred in the cty type system", **kwargs: Any) -> None:
        self.message = message
        super().__init__(self.message, **kwargs)

    def xǁCtyErrorǁ__init____mutmut_1(self, message: str = "XXAn error occurred in the cty type systemXX", **kwargs: Any) -> None:
        self.message = message
        super().__init__(self.message, **kwargs)

    def xǁCtyErrorǁ__init____mutmut_2(self, message: str = "an error occurred in the cty type system", **kwargs: Any) -> None:
        self.message = message
        super().__init__(self.message, **kwargs)

    def xǁCtyErrorǁ__init____mutmut_3(self, message: str = "AN ERROR OCCURRED IN THE CTY TYPE SYSTEM", **kwargs: Any) -> None:
        self.message = message
        super().__init__(self.message, **kwargs)

    def xǁCtyErrorǁ__init____mutmut_4(self, message: str = "An error occurred in the cty type system", **kwargs: Any) -> None:
        self.message = None
        super().__init__(self.message, **kwargs)

    def xǁCtyErrorǁ__init____mutmut_5(self, message: str = "An error occurred in the cty type system", **kwargs: Any) -> None:
        self.message = message
        super().__init__(None, **kwargs)

    def xǁCtyErrorǁ__init____mutmut_6(self, message: str = "An error occurred in the cty type system", **kwargs: Any) -> None:
        self.message = message
        super().__init__(**kwargs)

    def xǁCtyErrorǁ__init____mutmut_7(self, message: str = "An error occurred in the cty type system", **kwargs: Any) -> None:
        self.message = message
        super().__init__(self.message, )
    
    xǁCtyErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCtyErrorǁ__init____mutmut_1': xǁCtyErrorǁ__init____mutmut_1, 
        'xǁCtyErrorǁ__init____mutmut_2': xǁCtyErrorǁ__init____mutmut_2, 
        'xǁCtyErrorǁ__init____mutmut_3': xǁCtyErrorǁ__init____mutmut_3, 
        'xǁCtyErrorǁ__init____mutmut_4': xǁCtyErrorǁ__init____mutmut_4, 
        'xǁCtyErrorǁ__init____mutmut_5': xǁCtyErrorǁ__init____mutmut_5, 
        'xǁCtyErrorǁ__init____mutmut_6': xǁCtyErrorǁ__init____mutmut_6, 
        'xǁCtyErrorǁ__init____mutmut_7': xǁCtyErrorǁ__init____mutmut_7
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCtyErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁCtyErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁCtyErrorǁ__init____mutmut_orig)
    xǁCtyErrorǁ__init____mutmut_orig.__name__ = 'xǁCtyErrorǁ__init__'

    def xǁCtyErrorǁ_default_code__mutmut_orig(self) -> str:
        return "CTY_ERROR"

    def xǁCtyErrorǁ_default_code__mutmut_1(self) -> str:
        return "XXCTY_ERRORXX"

    def xǁCtyErrorǁ_default_code__mutmut_2(self) -> str:
        return "cty_error"
    
    xǁCtyErrorǁ_default_code__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCtyErrorǁ_default_code__mutmut_1': xǁCtyErrorǁ_default_code__mutmut_1, 
        'xǁCtyErrorǁ_default_code__mutmut_2': xǁCtyErrorǁ_default_code__mutmut_2
    }
    
    def _default_code(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCtyErrorǁ_default_code__mutmut_orig"), object.__getattribute__(self, "xǁCtyErrorǁ_default_code__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _default_code.__signature__ = _mutmut_signature(xǁCtyErrorǁ_default_code__mutmut_orig)
    xǁCtyErrorǁ_default_code__mutmut_orig.__name__ = 'xǁCtyErrorǁ_default_code'


class CtyFunctionError(CtyError):
    """
    Exception raised for errors during the execution of a CTY standard library function.

    Enhanced with rich context support for function name, arguments, and execution details.

    Attributes:
        message: A human-readable error description
        function_name: Name of the CTY function that failed
    """

    def xǁCtyFunctionErrorǁ__init____mutmut_orig(
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

    def xǁCtyFunctionErrorǁ__init____mutmut_1(
        self,
        message: str = "XXAn error occurred during CTY function executionXX",
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

    def xǁCtyFunctionErrorǁ__init____mutmut_2(
        self,
        message: str = "an error occurred during cty function execution",
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

    def xǁCtyFunctionErrorǁ__init____mutmut_3(
        self,
        message: str = "AN ERROR OCCURRED DURING CTY FUNCTION EXECUTION",
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

    def xǁCtyFunctionErrorǁ__init____mutmut_4(
        self,
        message: str = "An error occurred during CTY function execution",
        *,
        function_name: str | None = None,
        input_types: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        self.function_name = None
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

    def xǁCtyFunctionErrorǁ__init____mutmut_5(
        self,
        message: str = "An error occurred during CTY function execution",
        *,
        function_name: str | None = None,
        input_types: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        self.function_name = function_name
        self.input_types = None

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

    def xǁCtyFunctionErrorǁ__init____mutmut_6(
        self,
        message: str = "An error occurred during CTY function execution",
        *,
        function_name: str | None = None,
        input_types: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        self.function_name = function_name
        self.input_types = input_types and []

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

    def xǁCtyFunctionErrorǁ__init____mutmut_7(
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
        context: dict[str, Any] = None
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

    def xǁCtyFunctionErrorǁ__init____mutmut_8(
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
        context: dict[str, Any] = kwargs.setdefault(None, {})
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

    def xǁCtyFunctionErrorǁ__init____mutmut_9(
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
        context: dict[str, Any] = kwargs.setdefault("context", None)
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

    def xǁCtyFunctionErrorǁ__init____mutmut_10(
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
        context: dict[str, Any] = kwargs.setdefault({})
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

    def xǁCtyFunctionErrorǁ__init____mutmut_11(
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
        context: dict[str, Any] = kwargs.setdefault("context", )
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

    def xǁCtyFunctionErrorǁ__init____mutmut_12(
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
        context: dict[str, Any] = kwargs.setdefault("XXcontextXX", {})
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

    def xǁCtyFunctionErrorǁ__init____mutmut_13(
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
        context: dict[str, Any] = kwargs.setdefault("CONTEXT", {})
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

    def xǁCtyFunctionErrorǁ__init____mutmut_14(
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
        context["cty.error_category"] = None
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

    def xǁCtyFunctionErrorǁ__init____mutmut_15(
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
        context["XXcty.error_categoryXX"] = "function_execution"
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

    def xǁCtyFunctionErrorǁ__init____mutmut_16(
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
        context["CTY.ERROR_CATEGORY"] = "function_execution"
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

    def xǁCtyFunctionErrorǁ__init____mutmut_17(
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
        context["cty.error_category"] = "XXfunction_executionXX"
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

    def xǁCtyFunctionErrorǁ__init____mutmut_18(
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
        context["cty.error_category"] = "FUNCTION_EXECUTION"
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

    def xǁCtyFunctionErrorǁ__init____mutmut_19(
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
        context["cty.operation"] = None

        if function_name:
            context["cty.function_name"] = function_name

        if input_types:
            context["cty.function_input_types"] = input_types
            context["cty.function_arity"] = len(input_types)

        # Enhance message if function name available
        if function_name:
            message = f"CTY function '{function_name}' failed: {message}"

        super().__init__(message, **kwargs)

    def xǁCtyFunctionErrorǁ__init____mutmut_20(
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
        context["XXcty.operationXX"] = "cty_function"

        if function_name:
            context["cty.function_name"] = function_name

        if input_types:
            context["cty.function_input_types"] = input_types
            context["cty.function_arity"] = len(input_types)

        # Enhance message if function name available
        if function_name:
            message = f"CTY function '{function_name}' failed: {message}"

        super().__init__(message, **kwargs)

    def xǁCtyFunctionErrorǁ__init____mutmut_21(
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
        context["CTY.OPERATION"] = "cty_function"

        if function_name:
            context["cty.function_name"] = function_name

        if input_types:
            context["cty.function_input_types"] = input_types
            context["cty.function_arity"] = len(input_types)

        # Enhance message if function name available
        if function_name:
            message = f"CTY function '{function_name}' failed: {message}"

        super().__init__(message, **kwargs)

    def xǁCtyFunctionErrorǁ__init____mutmut_22(
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
        context["cty.operation"] = "XXcty_functionXX"

        if function_name:
            context["cty.function_name"] = function_name

        if input_types:
            context["cty.function_input_types"] = input_types
            context["cty.function_arity"] = len(input_types)

        # Enhance message if function name available
        if function_name:
            message = f"CTY function '{function_name}' failed: {message}"

        super().__init__(message, **kwargs)

    def xǁCtyFunctionErrorǁ__init____mutmut_23(
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
        context["cty.operation"] = "CTY_FUNCTION"

        if function_name:
            context["cty.function_name"] = function_name

        if input_types:
            context["cty.function_input_types"] = input_types
            context["cty.function_arity"] = len(input_types)

        # Enhance message if function name available
        if function_name:
            message = f"CTY function '{function_name}' failed: {message}"

        super().__init__(message, **kwargs)

    def xǁCtyFunctionErrorǁ__init____mutmut_24(
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
            context["cty.function_name"] = None

        if input_types:
            context["cty.function_input_types"] = input_types
            context["cty.function_arity"] = len(input_types)

        # Enhance message if function name available
        if function_name:
            message = f"CTY function '{function_name}' failed: {message}"

        super().__init__(message, **kwargs)

    def xǁCtyFunctionErrorǁ__init____mutmut_25(
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
            context["XXcty.function_nameXX"] = function_name

        if input_types:
            context["cty.function_input_types"] = input_types
            context["cty.function_arity"] = len(input_types)

        # Enhance message if function name available
        if function_name:
            message = f"CTY function '{function_name}' failed: {message}"

        super().__init__(message, **kwargs)

    def xǁCtyFunctionErrorǁ__init____mutmut_26(
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
            context["CTY.FUNCTION_NAME"] = function_name

        if input_types:
            context["cty.function_input_types"] = input_types
            context["cty.function_arity"] = len(input_types)

        # Enhance message if function name available
        if function_name:
            message = f"CTY function '{function_name}' failed: {message}"

        super().__init__(message, **kwargs)

    def xǁCtyFunctionErrorǁ__init____mutmut_27(
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
            context["cty.function_input_types"] = None
            context["cty.function_arity"] = len(input_types)

        # Enhance message if function name available
        if function_name:
            message = f"CTY function '{function_name}' failed: {message}"

        super().__init__(message, **kwargs)

    def xǁCtyFunctionErrorǁ__init____mutmut_28(
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
            context["XXcty.function_input_typesXX"] = input_types
            context["cty.function_arity"] = len(input_types)

        # Enhance message if function name available
        if function_name:
            message = f"CTY function '{function_name}' failed: {message}"

        super().__init__(message, **kwargs)

    def xǁCtyFunctionErrorǁ__init____mutmut_29(
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
            context["CTY.FUNCTION_INPUT_TYPES"] = input_types
            context["cty.function_arity"] = len(input_types)

        # Enhance message if function name available
        if function_name:
            message = f"CTY function '{function_name}' failed: {message}"

        super().__init__(message, **kwargs)

    def xǁCtyFunctionErrorǁ__init____mutmut_30(
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
            context["cty.function_arity"] = None

        # Enhance message if function name available
        if function_name:
            message = f"CTY function '{function_name}' failed: {message}"

        super().__init__(message, **kwargs)

    def xǁCtyFunctionErrorǁ__init____mutmut_31(
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
            context["XXcty.function_arityXX"] = len(input_types)

        # Enhance message if function name available
        if function_name:
            message = f"CTY function '{function_name}' failed: {message}"

        super().__init__(message, **kwargs)

    def xǁCtyFunctionErrorǁ__init____mutmut_32(
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
            context["CTY.FUNCTION_ARITY"] = len(input_types)

        # Enhance message if function name available
        if function_name:
            message = f"CTY function '{function_name}' failed: {message}"

        super().__init__(message, **kwargs)

    def xǁCtyFunctionErrorǁ__init____mutmut_33(
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
            message = None

        super().__init__(message, **kwargs)

    def xǁCtyFunctionErrorǁ__init____mutmut_34(
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

        super().__init__(None, **kwargs)

    def xǁCtyFunctionErrorǁ__init____mutmut_35(
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

        super().__init__(**kwargs)

    def xǁCtyFunctionErrorǁ__init____mutmut_36(
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

        super().__init__(message, )
    
    xǁCtyFunctionErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCtyFunctionErrorǁ__init____mutmut_1': xǁCtyFunctionErrorǁ__init____mutmut_1, 
        'xǁCtyFunctionErrorǁ__init____mutmut_2': xǁCtyFunctionErrorǁ__init____mutmut_2, 
        'xǁCtyFunctionErrorǁ__init____mutmut_3': xǁCtyFunctionErrorǁ__init____mutmut_3, 
        'xǁCtyFunctionErrorǁ__init____mutmut_4': xǁCtyFunctionErrorǁ__init____mutmut_4, 
        'xǁCtyFunctionErrorǁ__init____mutmut_5': xǁCtyFunctionErrorǁ__init____mutmut_5, 
        'xǁCtyFunctionErrorǁ__init____mutmut_6': xǁCtyFunctionErrorǁ__init____mutmut_6, 
        'xǁCtyFunctionErrorǁ__init____mutmut_7': xǁCtyFunctionErrorǁ__init____mutmut_7, 
        'xǁCtyFunctionErrorǁ__init____mutmut_8': xǁCtyFunctionErrorǁ__init____mutmut_8, 
        'xǁCtyFunctionErrorǁ__init____mutmut_9': xǁCtyFunctionErrorǁ__init____mutmut_9, 
        'xǁCtyFunctionErrorǁ__init____mutmut_10': xǁCtyFunctionErrorǁ__init____mutmut_10, 
        'xǁCtyFunctionErrorǁ__init____mutmut_11': xǁCtyFunctionErrorǁ__init____mutmut_11, 
        'xǁCtyFunctionErrorǁ__init____mutmut_12': xǁCtyFunctionErrorǁ__init____mutmut_12, 
        'xǁCtyFunctionErrorǁ__init____mutmut_13': xǁCtyFunctionErrorǁ__init____mutmut_13, 
        'xǁCtyFunctionErrorǁ__init____mutmut_14': xǁCtyFunctionErrorǁ__init____mutmut_14, 
        'xǁCtyFunctionErrorǁ__init____mutmut_15': xǁCtyFunctionErrorǁ__init____mutmut_15, 
        'xǁCtyFunctionErrorǁ__init____mutmut_16': xǁCtyFunctionErrorǁ__init____mutmut_16, 
        'xǁCtyFunctionErrorǁ__init____mutmut_17': xǁCtyFunctionErrorǁ__init____mutmut_17, 
        'xǁCtyFunctionErrorǁ__init____mutmut_18': xǁCtyFunctionErrorǁ__init____mutmut_18, 
        'xǁCtyFunctionErrorǁ__init____mutmut_19': xǁCtyFunctionErrorǁ__init____mutmut_19, 
        'xǁCtyFunctionErrorǁ__init____mutmut_20': xǁCtyFunctionErrorǁ__init____mutmut_20, 
        'xǁCtyFunctionErrorǁ__init____mutmut_21': xǁCtyFunctionErrorǁ__init____mutmut_21, 
        'xǁCtyFunctionErrorǁ__init____mutmut_22': xǁCtyFunctionErrorǁ__init____mutmut_22, 
        'xǁCtyFunctionErrorǁ__init____mutmut_23': xǁCtyFunctionErrorǁ__init____mutmut_23, 
        'xǁCtyFunctionErrorǁ__init____mutmut_24': xǁCtyFunctionErrorǁ__init____mutmut_24, 
        'xǁCtyFunctionErrorǁ__init____mutmut_25': xǁCtyFunctionErrorǁ__init____mutmut_25, 
        'xǁCtyFunctionErrorǁ__init____mutmut_26': xǁCtyFunctionErrorǁ__init____mutmut_26, 
        'xǁCtyFunctionErrorǁ__init____mutmut_27': xǁCtyFunctionErrorǁ__init____mutmut_27, 
        'xǁCtyFunctionErrorǁ__init____mutmut_28': xǁCtyFunctionErrorǁ__init____mutmut_28, 
        'xǁCtyFunctionErrorǁ__init____mutmut_29': xǁCtyFunctionErrorǁ__init____mutmut_29, 
        'xǁCtyFunctionErrorǁ__init____mutmut_30': xǁCtyFunctionErrorǁ__init____mutmut_30, 
        'xǁCtyFunctionErrorǁ__init____mutmut_31': xǁCtyFunctionErrorǁ__init____mutmut_31, 
        'xǁCtyFunctionErrorǁ__init____mutmut_32': xǁCtyFunctionErrorǁ__init____mutmut_32, 
        'xǁCtyFunctionErrorǁ__init____mutmut_33': xǁCtyFunctionErrorǁ__init____mutmut_33, 
        'xǁCtyFunctionErrorǁ__init____mutmut_34': xǁCtyFunctionErrorǁ__init____mutmut_34, 
        'xǁCtyFunctionErrorǁ__init____mutmut_35': xǁCtyFunctionErrorǁ__init____mutmut_35, 
        'xǁCtyFunctionErrorǁ__init____mutmut_36': xǁCtyFunctionErrorǁ__init____mutmut_36
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCtyFunctionErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁCtyFunctionErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁCtyFunctionErrorǁ__init____mutmut_orig)
    xǁCtyFunctionErrorǁ__init____mutmut_orig.__name__ = 'xǁCtyFunctionErrorǁ__init__'

    def xǁCtyFunctionErrorǁ_default_code__mutmut_orig(self) -> str:
        return "CTY_FUNCTION_ERROR"

    def xǁCtyFunctionErrorǁ_default_code__mutmut_1(self) -> str:
        return "XXCTY_FUNCTION_ERRORXX"

    def xǁCtyFunctionErrorǁ_default_code__mutmut_2(self) -> str:
        return "cty_function_error"
    
    xǁCtyFunctionErrorǁ_default_code__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCtyFunctionErrorǁ_default_code__mutmut_1': xǁCtyFunctionErrorǁ_default_code__mutmut_1, 
        'xǁCtyFunctionErrorǁ_default_code__mutmut_2': xǁCtyFunctionErrorǁ_default_code__mutmut_2
    }
    
    def _default_code(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCtyFunctionErrorǁ_default_code__mutmut_orig"), object.__getattribute__(self, "xǁCtyFunctionErrorǁ_default_code__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _default_code.__signature__ = _mutmut_signature(xǁCtyFunctionErrorǁ_default_code__mutmut_orig)
    xǁCtyFunctionErrorǁ_default_code__mutmut_orig.__name__ = 'xǁCtyFunctionErrorǁ_default_code'


# 🐍🏗️🐣
# 🌊🪢🏗️🪄
