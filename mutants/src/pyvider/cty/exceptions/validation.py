# pyvider/cty/exceptions/validation.py
#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from provide.foundation.errors import ValidationError as FoundationValidationError

if TYPE_CHECKING:
    from pyvider.cty.path import CtyPath
    from pyvider.cty.types import CtyType
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


class CtyValidationError(FoundationValidationError):
    """Base exception for all validation errors.

    Inherits from foundation's ValidationError for enhanced diagnostics
    and automatic retry/circuit breaker support where applicable.
    """

    def xǁCtyValidationErrorǁ__init____mutmut_orig(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_1(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = None
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_2(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = None
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_3(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = None
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_4(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = None

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_5(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = None

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_6(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault(None, {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_7(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", None)

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_8(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault({})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_9(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", )

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_10(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("XXcontextXX", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_11(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("CONTEXT", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_12(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = None
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_13(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["XXcty.typeXX"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_14(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["CTY.TYPE"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_15(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = None
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_16(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["XXcty.pathXX"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_17(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["CTY.PATH"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_18(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(None)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_19(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = None

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_20(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["XXcty.path_depthXX"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_21(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["CTY.PATH_DEPTH"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_22(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 1

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_23(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_24(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = None
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_25(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["XXcty.value_typeXX"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_26(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["CTY.VALUE_TYPE"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_27(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(None).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_28(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = None
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_29(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(None)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_30(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = None
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_31(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["XXcty.value_reprXX"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_32(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["CTY.VALUE_REPR"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_33(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] - "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_34(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:201] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_35(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "XX...XX" if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_36(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) >= 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_37(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 201 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_38(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = None

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_39(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["XXcty.value_reprXX"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_40(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["CTY.VALUE_REPR"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_41(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(None).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_42(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = None

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_43(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["XXcty.validation_stageXX"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_44(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["CTY.VALIDATION_STAGE"] = "type_validation"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_45(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "XXtype_validationXX"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_46(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "TYPE_VALIDATION"

        super().__init__(self.message, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_47(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(None, **kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_48(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(**kwargs)

    def xǁCtyValidationErrorǁ__init____mutmut_49(
        self,
        message: str,
        value: object = None,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.value = value
        self.type_name = type_name
        self.path = path
        self.message = message

        # Add rich context to foundation error with more detailed information
        context = kwargs.setdefault("context", {})

        # Core CTY context
        if type_name:
            context["cty.type"] = type_name
        if path:
            context["cty.path"] = str(path)
            context["cty.path_depth"] = len(path.steps) if path else 0

        # Value context with safe representation
        if value is not None:
            context["cty.value_type"] = type(value).__name__
            # Safe value representation for debugging (truncated to avoid huge objects)
            try:
                value_repr = repr(value)
                context["cty.value_repr"] = value_repr[:200] + "..." if len(value_repr) > 200 else value_repr
            except Exception:
                context["cty.value_repr"] = f"<repr failed for {type(value).__name__}>"

        # Add validation context if available
        context["cty.validation_stage"] = "type_validation"

        super().__init__(self.message, )
    
    xǁCtyValidationErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCtyValidationErrorǁ__init____mutmut_1': xǁCtyValidationErrorǁ__init____mutmut_1, 
        'xǁCtyValidationErrorǁ__init____mutmut_2': xǁCtyValidationErrorǁ__init____mutmut_2, 
        'xǁCtyValidationErrorǁ__init____mutmut_3': xǁCtyValidationErrorǁ__init____mutmut_3, 
        'xǁCtyValidationErrorǁ__init____mutmut_4': xǁCtyValidationErrorǁ__init____mutmut_4, 
        'xǁCtyValidationErrorǁ__init____mutmut_5': xǁCtyValidationErrorǁ__init____mutmut_5, 
        'xǁCtyValidationErrorǁ__init____mutmut_6': xǁCtyValidationErrorǁ__init____mutmut_6, 
        'xǁCtyValidationErrorǁ__init____mutmut_7': xǁCtyValidationErrorǁ__init____mutmut_7, 
        'xǁCtyValidationErrorǁ__init____mutmut_8': xǁCtyValidationErrorǁ__init____mutmut_8, 
        'xǁCtyValidationErrorǁ__init____mutmut_9': xǁCtyValidationErrorǁ__init____mutmut_9, 
        'xǁCtyValidationErrorǁ__init____mutmut_10': xǁCtyValidationErrorǁ__init____mutmut_10, 
        'xǁCtyValidationErrorǁ__init____mutmut_11': xǁCtyValidationErrorǁ__init____mutmut_11, 
        'xǁCtyValidationErrorǁ__init____mutmut_12': xǁCtyValidationErrorǁ__init____mutmut_12, 
        'xǁCtyValidationErrorǁ__init____mutmut_13': xǁCtyValidationErrorǁ__init____mutmut_13, 
        'xǁCtyValidationErrorǁ__init____mutmut_14': xǁCtyValidationErrorǁ__init____mutmut_14, 
        'xǁCtyValidationErrorǁ__init____mutmut_15': xǁCtyValidationErrorǁ__init____mutmut_15, 
        'xǁCtyValidationErrorǁ__init____mutmut_16': xǁCtyValidationErrorǁ__init____mutmut_16, 
        'xǁCtyValidationErrorǁ__init____mutmut_17': xǁCtyValidationErrorǁ__init____mutmut_17, 
        'xǁCtyValidationErrorǁ__init____mutmut_18': xǁCtyValidationErrorǁ__init____mutmut_18, 
        'xǁCtyValidationErrorǁ__init____mutmut_19': xǁCtyValidationErrorǁ__init____mutmut_19, 
        'xǁCtyValidationErrorǁ__init____mutmut_20': xǁCtyValidationErrorǁ__init____mutmut_20, 
        'xǁCtyValidationErrorǁ__init____mutmut_21': xǁCtyValidationErrorǁ__init____mutmut_21, 
        'xǁCtyValidationErrorǁ__init____mutmut_22': xǁCtyValidationErrorǁ__init____mutmut_22, 
        'xǁCtyValidationErrorǁ__init____mutmut_23': xǁCtyValidationErrorǁ__init____mutmut_23, 
        'xǁCtyValidationErrorǁ__init____mutmut_24': xǁCtyValidationErrorǁ__init____mutmut_24, 
        'xǁCtyValidationErrorǁ__init____mutmut_25': xǁCtyValidationErrorǁ__init____mutmut_25, 
        'xǁCtyValidationErrorǁ__init____mutmut_26': xǁCtyValidationErrorǁ__init____mutmut_26, 
        'xǁCtyValidationErrorǁ__init____mutmut_27': xǁCtyValidationErrorǁ__init____mutmut_27, 
        'xǁCtyValidationErrorǁ__init____mutmut_28': xǁCtyValidationErrorǁ__init____mutmut_28, 
        'xǁCtyValidationErrorǁ__init____mutmut_29': xǁCtyValidationErrorǁ__init____mutmut_29, 
        'xǁCtyValidationErrorǁ__init____mutmut_30': xǁCtyValidationErrorǁ__init____mutmut_30, 
        'xǁCtyValidationErrorǁ__init____mutmut_31': xǁCtyValidationErrorǁ__init____mutmut_31, 
        'xǁCtyValidationErrorǁ__init____mutmut_32': xǁCtyValidationErrorǁ__init____mutmut_32, 
        'xǁCtyValidationErrorǁ__init____mutmut_33': xǁCtyValidationErrorǁ__init____mutmut_33, 
        'xǁCtyValidationErrorǁ__init____mutmut_34': xǁCtyValidationErrorǁ__init____mutmut_34, 
        'xǁCtyValidationErrorǁ__init____mutmut_35': xǁCtyValidationErrorǁ__init____mutmut_35, 
        'xǁCtyValidationErrorǁ__init____mutmut_36': xǁCtyValidationErrorǁ__init____mutmut_36, 
        'xǁCtyValidationErrorǁ__init____mutmut_37': xǁCtyValidationErrorǁ__init____mutmut_37, 
        'xǁCtyValidationErrorǁ__init____mutmut_38': xǁCtyValidationErrorǁ__init____mutmut_38, 
        'xǁCtyValidationErrorǁ__init____mutmut_39': xǁCtyValidationErrorǁ__init____mutmut_39, 
        'xǁCtyValidationErrorǁ__init____mutmut_40': xǁCtyValidationErrorǁ__init____mutmut_40, 
        'xǁCtyValidationErrorǁ__init____mutmut_41': xǁCtyValidationErrorǁ__init____mutmut_41, 
        'xǁCtyValidationErrorǁ__init____mutmut_42': xǁCtyValidationErrorǁ__init____mutmut_42, 
        'xǁCtyValidationErrorǁ__init____mutmut_43': xǁCtyValidationErrorǁ__init____mutmut_43, 
        'xǁCtyValidationErrorǁ__init____mutmut_44': xǁCtyValidationErrorǁ__init____mutmut_44, 
        'xǁCtyValidationErrorǁ__init____mutmut_45': xǁCtyValidationErrorǁ__init____mutmut_45, 
        'xǁCtyValidationErrorǁ__init____mutmut_46': xǁCtyValidationErrorǁ__init____mutmut_46, 
        'xǁCtyValidationErrorǁ__init____mutmut_47': xǁCtyValidationErrorǁ__init____mutmut_47, 
        'xǁCtyValidationErrorǁ__init____mutmut_48': xǁCtyValidationErrorǁ__init____mutmut_48, 
        'xǁCtyValidationErrorǁ__init____mutmut_49': xǁCtyValidationErrorǁ__init____mutmut_49
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCtyValidationErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁCtyValidationErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁCtyValidationErrorǁ__init____mutmut_orig)
    xǁCtyValidationErrorǁ__init____mutmut_orig.__name__ = 'xǁCtyValidationErrorǁ__init__'

    def xǁCtyValidationErrorǁ_default_code__mutmut_orig(self) -> str:
        return "CTY_VALIDATION_ERROR"

    def xǁCtyValidationErrorǁ_default_code__mutmut_1(self) -> str:
        return "XXCTY_VALIDATION_ERRORXX"

    def xǁCtyValidationErrorǁ_default_code__mutmut_2(self) -> str:
        return "cty_validation_error"
    
    xǁCtyValidationErrorǁ_default_code__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCtyValidationErrorǁ_default_code__mutmut_1': xǁCtyValidationErrorǁ_default_code__mutmut_1, 
        'xǁCtyValidationErrorǁ_default_code__mutmut_2': xǁCtyValidationErrorǁ_default_code__mutmut_2
    }
    
    def _default_code(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCtyValidationErrorǁ_default_code__mutmut_orig"), object.__getattribute__(self, "xǁCtyValidationErrorǁ_default_code__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _default_code.__signature__ = _mutmut_signature(xǁCtyValidationErrorǁ_default_code__mutmut_orig)
    xǁCtyValidationErrorǁ_default_code__mutmut_orig.__name__ = 'xǁCtyValidationErrorǁ_default_code'

    def xǁCtyValidationErrorǁ__str____mutmut_orig(self) -> str:
        """Creates a user-friendly, path-aware error message."""
        path_str = str(self.path) if self.path and self.path.steps else ""
        core_message = self.message

        if path_str and path_str != "(root)":
            return f"At {path_str}: {core_message}"

        return core_message

    def xǁCtyValidationErrorǁ__str____mutmut_1(self) -> str:
        """Creates a user-friendly, path-aware error message."""
        path_str = None
        core_message = self.message

        if path_str and path_str != "(root)":
            return f"At {path_str}: {core_message}"

        return core_message

    def xǁCtyValidationErrorǁ__str____mutmut_2(self) -> str:
        """Creates a user-friendly, path-aware error message."""
        path_str = str(None) if self.path and self.path.steps else ""
        core_message = self.message

        if path_str and path_str != "(root)":
            return f"At {path_str}: {core_message}"

        return core_message

    def xǁCtyValidationErrorǁ__str____mutmut_3(self) -> str:
        """Creates a user-friendly, path-aware error message."""
        path_str = str(self.path) if self.path or self.path.steps else ""
        core_message = self.message

        if path_str and path_str != "(root)":
            return f"At {path_str}: {core_message}"

        return core_message

    def xǁCtyValidationErrorǁ__str____mutmut_4(self) -> str:
        """Creates a user-friendly, path-aware error message."""
        path_str = str(self.path) if self.path and self.path.steps else "XXXX"
        core_message = self.message

        if path_str and path_str != "(root)":
            return f"At {path_str}: {core_message}"

        return core_message

    def xǁCtyValidationErrorǁ__str____mutmut_5(self) -> str:
        """Creates a user-friendly, path-aware error message."""
        path_str = str(self.path) if self.path and self.path.steps else ""
        core_message = None

        if path_str and path_str != "(root)":
            return f"At {path_str}: {core_message}"

        return core_message

    def xǁCtyValidationErrorǁ__str____mutmut_6(self) -> str:
        """Creates a user-friendly, path-aware error message."""
        path_str = str(self.path) if self.path and self.path.steps else ""
        core_message = self.message

        if path_str or path_str != "(root)":
            return f"At {path_str}: {core_message}"

        return core_message

    def xǁCtyValidationErrorǁ__str____mutmut_7(self) -> str:
        """Creates a user-friendly, path-aware error message."""
        path_str = str(self.path) if self.path and self.path.steps else ""
        core_message = self.message

        if path_str and path_str == "(root)":
            return f"At {path_str}: {core_message}"

        return core_message

    def xǁCtyValidationErrorǁ__str____mutmut_8(self) -> str:
        """Creates a user-friendly, path-aware error message."""
        path_str = str(self.path) if self.path and self.path.steps else ""
        core_message = self.message

        if path_str and path_str != "XX(root)XX":
            return f"At {path_str}: {core_message}"

        return core_message

    def xǁCtyValidationErrorǁ__str____mutmut_9(self) -> str:
        """Creates a user-friendly, path-aware error message."""
        path_str = str(self.path) if self.path and self.path.steps else ""
        core_message = self.message

        if path_str and path_str != "(ROOT)":
            return f"At {path_str}: {core_message}"

        return core_message
    
    xǁCtyValidationErrorǁ__str____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCtyValidationErrorǁ__str____mutmut_1': xǁCtyValidationErrorǁ__str____mutmut_1, 
        'xǁCtyValidationErrorǁ__str____mutmut_2': xǁCtyValidationErrorǁ__str____mutmut_2, 
        'xǁCtyValidationErrorǁ__str____mutmut_3': xǁCtyValidationErrorǁ__str____mutmut_3, 
        'xǁCtyValidationErrorǁ__str____mutmut_4': xǁCtyValidationErrorǁ__str____mutmut_4, 
        'xǁCtyValidationErrorǁ__str____mutmut_5': xǁCtyValidationErrorǁ__str____mutmut_5, 
        'xǁCtyValidationErrorǁ__str____mutmut_6': xǁCtyValidationErrorǁ__str____mutmut_6, 
        'xǁCtyValidationErrorǁ__str____mutmut_7': xǁCtyValidationErrorǁ__str____mutmut_7, 
        'xǁCtyValidationErrorǁ__str____mutmut_8': xǁCtyValidationErrorǁ__str____mutmut_8, 
        'xǁCtyValidationErrorǁ__str____mutmut_9': xǁCtyValidationErrorǁ__str____mutmut_9
    }
    
    def __str__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCtyValidationErrorǁ__str____mutmut_orig"), object.__getattribute__(self, "xǁCtyValidationErrorǁ__str____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __str__.__signature__ = _mutmut_signature(xǁCtyValidationErrorǁ__str____mutmut_orig)
    xǁCtyValidationErrorǁ__str____mutmut_orig.__name__ = 'xǁCtyValidationErrorǁ__str__'


def x__get_type_name_from_original__mutmut_orig(original_exc: CtyValidationError | None, default: str) -> str:
    """Helper to safely extract type_name from an original exception."""
    if original_exc and original_exc.type_name:
        return original_exc.type_name
    return default


def x__get_type_name_from_original__mutmut_1(original_exc: CtyValidationError | None, default: str) -> str:
    """Helper to safely extract type_name from an original exception."""
    if original_exc or original_exc.type_name:
        return original_exc.type_name
    return default

x__get_type_name_from_original__mutmut_mutants : ClassVar[MutantDict] = {
'x__get_type_name_from_original__mutmut_1': x__get_type_name_from_original__mutmut_1
}

def _get_type_name_from_original(*args, **kwargs):
    result = _mutmut_trampoline(x__get_type_name_from_original__mutmut_orig, x__get_type_name_from_original__mutmut_mutants, args, kwargs)
    return result 

_get_type_name_from_original.__signature__ = _mutmut_signature(x__get_type_name_from_original__mutmut_orig)
x__get_type_name_from_original__mutmut_orig.__name__ = 'x__get_type_name_from_original'


# --- Primitive Validation Errors ---
class CtyBoolValidationError(CtyValidationError):
    def xǁCtyBoolValidationErrorǁ__init____mutmut_orig(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add bool-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "bool"
        context["cty.validation_stage"] = "bool_validation"

        super().__init__(f"Boolean validation error: {message}", value, "Boolean", path, **kwargs)
    def xǁCtyBoolValidationErrorǁ__init____mutmut_1(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add bool-specific context
        context = None
        context["cty.primitive_type"] = "bool"
        context["cty.validation_stage"] = "bool_validation"

        super().__init__(f"Boolean validation error: {message}", value, "Boolean", path, **kwargs)
    def xǁCtyBoolValidationErrorǁ__init____mutmut_2(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add bool-specific context
        context = kwargs.setdefault(None, {})
        context["cty.primitive_type"] = "bool"
        context["cty.validation_stage"] = "bool_validation"

        super().__init__(f"Boolean validation error: {message}", value, "Boolean", path, **kwargs)
    def xǁCtyBoolValidationErrorǁ__init____mutmut_3(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add bool-specific context
        context = kwargs.setdefault("context", None)
        context["cty.primitive_type"] = "bool"
        context["cty.validation_stage"] = "bool_validation"

        super().__init__(f"Boolean validation error: {message}", value, "Boolean", path, **kwargs)
    def xǁCtyBoolValidationErrorǁ__init____mutmut_4(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add bool-specific context
        context = kwargs.setdefault({})
        context["cty.primitive_type"] = "bool"
        context["cty.validation_stage"] = "bool_validation"

        super().__init__(f"Boolean validation error: {message}", value, "Boolean", path, **kwargs)
    def xǁCtyBoolValidationErrorǁ__init____mutmut_5(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add bool-specific context
        context = kwargs.setdefault("context", )
        context["cty.primitive_type"] = "bool"
        context["cty.validation_stage"] = "bool_validation"

        super().__init__(f"Boolean validation error: {message}", value, "Boolean", path, **kwargs)
    def xǁCtyBoolValidationErrorǁ__init____mutmut_6(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add bool-specific context
        context = kwargs.setdefault("XXcontextXX", {})
        context["cty.primitive_type"] = "bool"
        context["cty.validation_stage"] = "bool_validation"

        super().__init__(f"Boolean validation error: {message}", value, "Boolean", path, **kwargs)
    def xǁCtyBoolValidationErrorǁ__init____mutmut_7(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add bool-specific context
        context = kwargs.setdefault("CONTEXT", {})
        context["cty.primitive_type"] = "bool"
        context["cty.validation_stage"] = "bool_validation"

        super().__init__(f"Boolean validation error: {message}", value, "Boolean", path, **kwargs)
    def xǁCtyBoolValidationErrorǁ__init____mutmut_8(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add bool-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = None
        context["cty.validation_stage"] = "bool_validation"

        super().__init__(f"Boolean validation error: {message}", value, "Boolean", path, **kwargs)
    def xǁCtyBoolValidationErrorǁ__init____mutmut_9(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add bool-specific context
        context = kwargs.setdefault("context", {})
        context["XXcty.primitive_typeXX"] = "bool"
        context["cty.validation_stage"] = "bool_validation"

        super().__init__(f"Boolean validation error: {message}", value, "Boolean", path, **kwargs)
    def xǁCtyBoolValidationErrorǁ__init____mutmut_10(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add bool-specific context
        context = kwargs.setdefault("context", {})
        context["CTY.PRIMITIVE_TYPE"] = "bool"
        context["cty.validation_stage"] = "bool_validation"

        super().__init__(f"Boolean validation error: {message}", value, "Boolean", path, **kwargs)
    def xǁCtyBoolValidationErrorǁ__init____mutmut_11(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add bool-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "XXboolXX"
        context["cty.validation_stage"] = "bool_validation"

        super().__init__(f"Boolean validation error: {message}", value, "Boolean", path, **kwargs)
    def xǁCtyBoolValidationErrorǁ__init____mutmut_12(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add bool-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "BOOL"
        context["cty.validation_stage"] = "bool_validation"

        super().__init__(f"Boolean validation error: {message}", value, "Boolean", path, **kwargs)
    def xǁCtyBoolValidationErrorǁ__init____mutmut_13(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add bool-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "bool"
        context["cty.validation_stage"] = None

        super().__init__(f"Boolean validation error: {message}", value, "Boolean", path, **kwargs)
    def xǁCtyBoolValidationErrorǁ__init____mutmut_14(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add bool-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "bool"
        context["XXcty.validation_stageXX"] = "bool_validation"

        super().__init__(f"Boolean validation error: {message}", value, "Boolean", path, **kwargs)
    def xǁCtyBoolValidationErrorǁ__init____mutmut_15(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add bool-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "bool"
        context["CTY.VALIDATION_STAGE"] = "bool_validation"

        super().__init__(f"Boolean validation error: {message}", value, "Boolean", path, **kwargs)
    def xǁCtyBoolValidationErrorǁ__init____mutmut_16(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add bool-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "bool"
        context["cty.validation_stage"] = "XXbool_validationXX"

        super().__init__(f"Boolean validation error: {message}", value, "Boolean", path, **kwargs)
    def xǁCtyBoolValidationErrorǁ__init____mutmut_17(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add bool-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "bool"
        context["cty.validation_stage"] = "BOOL_VALIDATION"

        super().__init__(f"Boolean validation error: {message}", value, "Boolean", path, **kwargs)
    def xǁCtyBoolValidationErrorǁ__init____mutmut_18(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add bool-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "bool"
        context["cty.validation_stage"] = "bool_validation"

        super().__init__(None, value, "Boolean", path, **kwargs)
    def xǁCtyBoolValidationErrorǁ__init____mutmut_19(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add bool-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "bool"
        context["cty.validation_stage"] = "bool_validation"

        super().__init__(f"Boolean validation error: {message}", None, "Boolean", path, **kwargs)
    def xǁCtyBoolValidationErrorǁ__init____mutmut_20(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add bool-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "bool"
        context["cty.validation_stage"] = "bool_validation"

        super().__init__(f"Boolean validation error: {message}", value, None, path, **kwargs)
    def xǁCtyBoolValidationErrorǁ__init____mutmut_21(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add bool-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "bool"
        context["cty.validation_stage"] = "bool_validation"

        super().__init__(f"Boolean validation error: {message}", value, "Boolean", None, **kwargs)
    def xǁCtyBoolValidationErrorǁ__init____mutmut_22(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add bool-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "bool"
        context["cty.validation_stage"] = "bool_validation"

        super().__init__(value, "Boolean", path, **kwargs)
    def xǁCtyBoolValidationErrorǁ__init____mutmut_23(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add bool-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "bool"
        context["cty.validation_stage"] = "bool_validation"

        super().__init__(f"Boolean validation error: {message}", "Boolean", path, **kwargs)
    def xǁCtyBoolValidationErrorǁ__init____mutmut_24(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add bool-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "bool"
        context["cty.validation_stage"] = "bool_validation"

        super().__init__(f"Boolean validation error: {message}", value, path, **kwargs)
    def xǁCtyBoolValidationErrorǁ__init____mutmut_25(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add bool-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "bool"
        context["cty.validation_stage"] = "bool_validation"

        super().__init__(f"Boolean validation error: {message}", value, "Boolean", **kwargs)
    def xǁCtyBoolValidationErrorǁ__init____mutmut_26(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add bool-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "bool"
        context["cty.validation_stage"] = "bool_validation"

        super().__init__(f"Boolean validation error: {message}", value, "Boolean", path, )
    def xǁCtyBoolValidationErrorǁ__init____mutmut_27(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add bool-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "bool"
        context["cty.validation_stage"] = "bool_validation"

        super().__init__(f"Boolean validation error: {message}", value, "XXBooleanXX", path, **kwargs)
    def xǁCtyBoolValidationErrorǁ__init____mutmut_28(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add bool-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "bool"
        context["cty.validation_stage"] = "bool_validation"

        super().__init__(f"Boolean validation error: {message}", value, "boolean", path, **kwargs)
    def xǁCtyBoolValidationErrorǁ__init____mutmut_29(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add bool-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "bool"
        context["cty.validation_stage"] = "bool_validation"

        super().__init__(f"Boolean validation error: {message}", value, "BOOLEAN", path, **kwargs)
    
    xǁCtyBoolValidationErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCtyBoolValidationErrorǁ__init____mutmut_1': xǁCtyBoolValidationErrorǁ__init____mutmut_1, 
        'xǁCtyBoolValidationErrorǁ__init____mutmut_2': xǁCtyBoolValidationErrorǁ__init____mutmut_2, 
        'xǁCtyBoolValidationErrorǁ__init____mutmut_3': xǁCtyBoolValidationErrorǁ__init____mutmut_3, 
        'xǁCtyBoolValidationErrorǁ__init____mutmut_4': xǁCtyBoolValidationErrorǁ__init____mutmut_4, 
        'xǁCtyBoolValidationErrorǁ__init____mutmut_5': xǁCtyBoolValidationErrorǁ__init____mutmut_5, 
        'xǁCtyBoolValidationErrorǁ__init____mutmut_6': xǁCtyBoolValidationErrorǁ__init____mutmut_6, 
        'xǁCtyBoolValidationErrorǁ__init____mutmut_7': xǁCtyBoolValidationErrorǁ__init____mutmut_7, 
        'xǁCtyBoolValidationErrorǁ__init____mutmut_8': xǁCtyBoolValidationErrorǁ__init____mutmut_8, 
        'xǁCtyBoolValidationErrorǁ__init____mutmut_9': xǁCtyBoolValidationErrorǁ__init____mutmut_9, 
        'xǁCtyBoolValidationErrorǁ__init____mutmut_10': xǁCtyBoolValidationErrorǁ__init____mutmut_10, 
        'xǁCtyBoolValidationErrorǁ__init____mutmut_11': xǁCtyBoolValidationErrorǁ__init____mutmut_11, 
        'xǁCtyBoolValidationErrorǁ__init____mutmut_12': xǁCtyBoolValidationErrorǁ__init____mutmut_12, 
        'xǁCtyBoolValidationErrorǁ__init____mutmut_13': xǁCtyBoolValidationErrorǁ__init____mutmut_13, 
        'xǁCtyBoolValidationErrorǁ__init____mutmut_14': xǁCtyBoolValidationErrorǁ__init____mutmut_14, 
        'xǁCtyBoolValidationErrorǁ__init____mutmut_15': xǁCtyBoolValidationErrorǁ__init____mutmut_15, 
        'xǁCtyBoolValidationErrorǁ__init____mutmut_16': xǁCtyBoolValidationErrorǁ__init____mutmut_16, 
        'xǁCtyBoolValidationErrorǁ__init____mutmut_17': xǁCtyBoolValidationErrorǁ__init____mutmut_17, 
        'xǁCtyBoolValidationErrorǁ__init____mutmut_18': xǁCtyBoolValidationErrorǁ__init____mutmut_18, 
        'xǁCtyBoolValidationErrorǁ__init____mutmut_19': xǁCtyBoolValidationErrorǁ__init____mutmut_19, 
        'xǁCtyBoolValidationErrorǁ__init____mutmut_20': xǁCtyBoolValidationErrorǁ__init____mutmut_20, 
        'xǁCtyBoolValidationErrorǁ__init____mutmut_21': xǁCtyBoolValidationErrorǁ__init____mutmut_21, 
        'xǁCtyBoolValidationErrorǁ__init____mutmut_22': xǁCtyBoolValidationErrorǁ__init____mutmut_22, 
        'xǁCtyBoolValidationErrorǁ__init____mutmut_23': xǁCtyBoolValidationErrorǁ__init____mutmut_23, 
        'xǁCtyBoolValidationErrorǁ__init____mutmut_24': xǁCtyBoolValidationErrorǁ__init____mutmut_24, 
        'xǁCtyBoolValidationErrorǁ__init____mutmut_25': xǁCtyBoolValidationErrorǁ__init____mutmut_25, 
        'xǁCtyBoolValidationErrorǁ__init____mutmut_26': xǁCtyBoolValidationErrorǁ__init____mutmut_26, 
        'xǁCtyBoolValidationErrorǁ__init____mutmut_27': xǁCtyBoolValidationErrorǁ__init____mutmut_27, 
        'xǁCtyBoolValidationErrorǁ__init____mutmut_28': xǁCtyBoolValidationErrorǁ__init____mutmut_28, 
        'xǁCtyBoolValidationErrorǁ__init____mutmut_29': xǁCtyBoolValidationErrorǁ__init____mutmut_29
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCtyBoolValidationErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁCtyBoolValidationErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁCtyBoolValidationErrorǁ__init____mutmut_orig)
    xǁCtyBoolValidationErrorǁ__init____mutmut_orig.__name__ = 'xǁCtyBoolValidationErrorǁ__init__'


class CtyNumberValidationError(CtyValidationError):
    def xǁCtyNumberValidationErrorǁ__init____mutmut_orig(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add number-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "number"
        context["cty.validation_stage"] = "number_validation"

        # Add numeric value analysis if applicable
        if isinstance(value, (int, float)):
            context["cty.numeric_value"] = str(value)
            context["cty.numeric_type"] = type(value).__name__

        super().__init__(f"Number validation error: {message}", value, "Number", path, **kwargs)
    def xǁCtyNumberValidationErrorǁ__init____mutmut_1(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add number-specific context
        context = None
        context["cty.primitive_type"] = "number"
        context["cty.validation_stage"] = "number_validation"

        # Add numeric value analysis if applicable
        if isinstance(value, (int, float)):
            context["cty.numeric_value"] = str(value)
            context["cty.numeric_type"] = type(value).__name__

        super().__init__(f"Number validation error: {message}", value, "Number", path, **kwargs)
    def xǁCtyNumberValidationErrorǁ__init____mutmut_2(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add number-specific context
        context = kwargs.setdefault(None, {})
        context["cty.primitive_type"] = "number"
        context["cty.validation_stage"] = "number_validation"

        # Add numeric value analysis if applicable
        if isinstance(value, (int, float)):
            context["cty.numeric_value"] = str(value)
            context["cty.numeric_type"] = type(value).__name__

        super().__init__(f"Number validation error: {message}", value, "Number", path, **kwargs)
    def xǁCtyNumberValidationErrorǁ__init____mutmut_3(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add number-specific context
        context = kwargs.setdefault("context", None)
        context["cty.primitive_type"] = "number"
        context["cty.validation_stage"] = "number_validation"

        # Add numeric value analysis if applicable
        if isinstance(value, (int, float)):
            context["cty.numeric_value"] = str(value)
            context["cty.numeric_type"] = type(value).__name__

        super().__init__(f"Number validation error: {message}", value, "Number", path, **kwargs)
    def xǁCtyNumberValidationErrorǁ__init____mutmut_4(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add number-specific context
        context = kwargs.setdefault({})
        context["cty.primitive_type"] = "number"
        context["cty.validation_stage"] = "number_validation"

        # Add numeric value analysis if applicable
        if isinstance(value, (int, float)):
            context["cty.numeric_value"] = str(value)
            context["cty.numeric_type"] = type(value).__name__

        super().__init__(f"Number validation error: {message}", value, "Number", path, **kwargs)
    def xǁCtyNumberValidationErrorǁ__init____mutmut_5(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add number-specific context
        context = kwargs.setdefault("context", )
        context["cty.primitive_type"] = "number"
        context["cty.validation_stage"] = "number_validation"

        # Add numeric value analysis if applicable
        if isinstance(value, (int, float)):
            context["cty.numeric_value"] = str(value)
            context["cty.numeric_type"] = type(value).__name__

        super().__init__(f"Number validation error: {message}", value, "Number", path, **kwargs)
    def xǁCtyNumberValidationErrorǁ__init____mutmut_6(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add number-specific context
        context = kwargs.setdefault("XXcontextXX", {})
        context["cty.primitive_type"] = "number"
        context["cty.validation_stage"] = "number_validation"

        # Add numeric value analysis if applicable
        if isinstance(value, (int, float)):
            context["cty.numeric_value"] = str(value)
            context["cty.numeric_type"] = type(value).__name__

        super().__init__(f"Number validation error: {message}", value, "Number", path, **kwargs)
    def xǁCtyNumberValidationErrorǁ__init____mutmut_7(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add number-specific context
        context = kwargs.setdefault("CONTEXT", {})
        context["cty.primitive_type"] = "number"
        context["cty.validation_stage"] = "number_validation"

        # Add numeric value analysis if applicable
        if isinstance(value, (int, float)):
            context["cty.numeric_value"] = str(value)
            context["cty.numeric_type"] = type(value).__name__

        super().__init__(f"Number validation error: {message}", value, "Number", path, **kwargs)
    def xǁCtyNumberValidationErrorǁ__init____mutmut_8(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add number-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = None
        context["cty.validation_stage"] = "number_validation"

        # Add numeric value analysis if applicable
        if isinstance(value, (int, float)):
            context["cty.numeric_value"] = str(value)
            context["cty.numeric_type"] = type(value).__name__

        super().__init__(f"Number validation error: {message}", value, "Number", path, **kwargs)
    def xǁCtyNumberValidationErrorǁ__init____mutmut_9(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add number-specific context
        context = kwargs.setdefault("context", {})
        context["XXcty.primitive_typeXX"] = "number"
        context["cty.validation_stage"] = "number_validation"

        # Add numeric value analysis if applicable
        if isinstance(value, (int, float)):
            context["cty.numeric_value"] = str(value)
            context["cty.numeric_type"] = type(value).__name__

        super().__init__(f"Number validation error: {message}", value, "Number", path, **kwargs)
    def xǁCtyNumberValidationErrorǁ__init____mutmut_10(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add number-specific context
        context = kwargs.setdefault("context", {})
        context["CTY.PRIMITIVE_TYPE"] = "number"
        context["cty.validation_stage"] = "number_validation"

        # Add numeric value analysis if applicable
        if isinstance(value, (int, float)):
            context["cty.numeric_value"] = str(value)
            context["cty.numeric_type"] = type(value).__name__

        super().__init__(f"Number validation error: {message}", value, "Number", path, **kwargs)
    def xǁCtyNumberValidationErrorǁ__init____mutmut_11(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add number-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "XXnumberXX"
        context["cty.validation_stage"] = "number_validation"

        # Add numeric value analysis if applicable
        if isinstance(value, (int, float)):
            context["cty.numeric_value"] = str(value)
            context["cty.numeric_type"] = type(value).__name__

        super().__init__(f"Number validation error: {message}", value, "Number", path, **kwargs)
    def xǁCtyNumberValidationErrorǁ__init____mutmut_12(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add number-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "NUMBER"
        context["cty.validation_stage"] = "number_validation"

        # Add numeric value analysis if applicable
        if isinstance(value, (int, float)):
            context["cty.numeric_value"] = str(value)
            context["cty.numeric_type"] = type(value).__name__

        super().__init__(f"Number validation error: {message}", value, "Number", path, **kwargs)
    def xǁCtyNumberValidationErrorǁ__init____mutmut_13(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add number-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "number"
        context["cty.validation_stage"] = None

        # Add numeric value analysis if applicable
        if isinstance(value, (int, float)):
            context["cty.numeric_value"] = str(value)
            context["cty.numeric_type"] = type(value).__name__

        super().__init__(f"Number validation error: {message}", value, "Number", path, **kwargs)
    def xǁCtyNumberValidationErrorǁ__init____mutmut_14(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add number-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "number"
        context["XXcty.validation_stageXX"] = "number_validation"

        # Add numeric value analysis if applicable
        if isinstance(value, (int, float)):
            context["cty.numeric_value"] = str(value)
            context["cty.numeric_type"] = type(value).__name__

        super().__init__(f"Number validation error: {message}", value, "Number", path, **kwargs)
    def xǁCtyNumberValidationErrorǁ__init____mutmut_15(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add number-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "number"
        context["CTY.VALIDATION_STAGE"] = "number_validation"

        # Add numeric value analysis if applicable
        if isinstance(value, (int, float)):
            context["cty.numeric_value"] = str(value)
            context["cty.numeric_type"] = type(value).__name__

        super().__init__(f"Number validation error: {message}", value, "Number", path, **kwargs)
    def xǁCtyNumberValidationErrorǁ__init____mutmut_16(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add number-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "number"
        context["cty.validation_stage"] = "XXnumber_validationXX"

        # Add numeric value analysis if applicable
        if isinstance(value, (int, float)):
            context["cty.numeric_value"] = str(value)
            context["cty.numeric_type"] = type(value).__name__

        super().__init__(f"Number validation error: {message}", value, "Number", path, **kwargs)
    def xǁCtyNumberValidationErrorǁ__init____mutmut_17(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add number-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "number"
        context["cty.validation_stage"] = "NUMBER_VALIDATION"

        # Add numeric value analysis if applicable
        if isinstance(value, (int, float)):
            context["cty.numeric_value"] = str(value)
            context["cty.numeric_type"] = type(value).__name__

        super().__init__(f"Number validation error: {message}", value, "Number", path, **kwargs)
    def xǁCtyNumberValidationErrorǁ__init____mutmut_18(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add number-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "number"
        context["cty.validation_stage"] = "number_validation"

        # Add numeric value analysis if applicable
        if isinstance(value, (int, float)):
            context["cty.numeric_value"] = None
            context["cty.numeric_type"] = type(value).__name__

        super().__init__(f"Number validation error: {message}", value, "Number", path, **kwargs)
    def xǁCtyNumberValidationErrorǁ__init____mutmut_19(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add number-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "number"
        context["cty.validation_stage"] = "number_validation"

        # Add numeric value analysis if applicable
        if isinstance(value, (int, float)):
            context["XXcty.numeric_valueXX"] = str(value)
            context["cty.numeric_type"] = type(value).__name__

        super().__init__(f"Number validation error: {message}", value, "Number", path, **kwargs)
    def xǁCtyNumberValidationErrorǁ__init____mutmut_20(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add number-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "number"
        context["cty.validation_stage"] = "number_validation"

        # Add numeric value analysis if applicable
        if isinstance(value, (int, float)):
            context["CTY.NUMERIC_VALUE"] = str(value)
            context["cty.numeric_type"] = type(value).__name__

        super().__init__(f"Number validation error: {message}", value, "Number", path, **kwargs)
    def xǁCtyNumberValidationErrorǁ__init____mutmut_21(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add number-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "number"
        context["cty.validation_stage"] = "number_validation"

        # Add numeric value analysis if applicable
        if isinstance(value, (int, float)):
            context["cty.numeric_value"] = str(None)
            context["cty.numeric_type"] = type(value).__name__

        super().__init__(f"Number validation error: {message}", value, "Number", path, **kwargs)
    def xǁCtyNumberValidationErrorǁ__init____mutmut_22(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add number-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "number"
        context["cty.validation_stage"] = "number_validation"

        # Add numeric value analysis if applicable
        if isinstance(value, (int, float)):
            context["cty.numeric_value"] = str(value)
            context["cty.numeric_type"] = None

        super().__init__(f"Number validation error: {message}", value, "Number", path, **kwargs)
    def xǁCtyNumberValidationErrorǁ__init____mutmut_23(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add number-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "number"
        context["cty.validation_stage"] = "number_validation"

        # Add numeric value analysis if applicable
        if isinstance(value, (int, float)):
            context["cty.numeric_value"] = str(value)
            context["XXcty.numeric_typeXX"] = type(value).__name__

        super().__init__(f"Number validation error: {message}", value, "Number", path, **kwargs)
    def xǁCtyNumberValidationErrorǁ__init____mutmut_24(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add number-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "number"
        context["cty.validation_stage"] = "number_validation"

        # Add numeric value analysis if applicable
        if isinstance(value, (int, float)):
            context["cty.numeric_value"] = str(value)
            context["CTY.NUMERIC_TYPE"] = type(value).__name__

        super().__init__(f"Number validation error: {message}", value, "Number", path, **kwargs)
    def xǁCtyNumberValidationErrorǁ__init____mutmut_25(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add number-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "number"
        context["cty.validation_stage"] = "number_validation"

        # Add numeric value analysis if applicable
        if isinstance(value, (int, float)):
            context["cty.numeric_value"] = str(value)
            context["cty.numeric_type"] = type(None).__name__

        super().__init__(f"Number validation error: {message}", value, "Number", path, **kwargs)
    def xǁCtyNumberValidationErrorǁ__init____mutmut_26(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add number-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "number"
        context["cty.validation_stage"] = "number_validation"

        # Add numeric value analysis if applicable
        if isinstance(value, (int, float)):
            context["cty.numeric_value"] = str(value)
            context["cty.numeric_type"] = type(value).__name__

        super().__init__(None, value, "Number", path, **kwargs)
    def xǁCtyNumberValidationErrorǁ__init____mutmut_27(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add number-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "number"
        context["cty.validation_stage"] = "number_validation"

        # Add numeric value analysis if applicable
        if isinstance(value, (int, float)):
            context["cty.numeric_value"] = str(value)
            context["cty.numeric_type"] = type(value).__name__

        super().__init__(f"Number validation error: {message}", None, "Number", path, **kwargs)
    def xǁCtyNumberValidationErrorǁ__init____mutmut_28(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add number-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "number"
        context["cty.validation_stage"] = "number_validation"

        # Add numeric value analysis if applicable
        if isinstance(value, (int, float)):
            context["cty.numeric_value"] = str(value)
            context["cty.numeric_type"] = type(value).__name__

        super().__init__(f"Number validation error: {message}", value, None, path, **kwargs)
    def xǁCtyNumberValidationErrorǁ__init____mutmut_29(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add number-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "number"
        context["cty.validation_stage"] = "number_validation"

        # Add numeric value analysis if applicable
        if isinstance(value, (int, float)):
            context["cty.numeric_value"] = str(value)
            context["cty.numeric_type"] = type(value).__name__

        super().__init__(f"Number validation error: {message}", value, "Number", None, **kwargs)
    def xǁCtyNumberValidationErrorǁ__init____mutmut_30(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add number-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "number"
        context["cty.validation_stage"] = "number_validation"

        # Add numeric value analysis if applicable
        if isinstance(value, (int, float)):
            context["cty.numeric_value"] = str(value)
            context["cty.numeric_type"] = type(value).__name__

        super().__init__(value, "Number", path, **kwargs)
    def xǁCtyNumberValidationErrorǁ__init____mutmut_31(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add number-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "number"
        context["cty.validation_stage"] = "number_validation"

        # Add numeric value analysis if applicable
        if isinstance(value, (int, float)):
            context["cty.numeric_value"] = str(value)
            context["cty.numeric_type"] = type(value).__name__

        super().__init__(f"Number validation error: {message}", "Number", path, **kwargs)
    def xǁCtyNumberValidationErrorǁ__init____mutmut_32(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add number-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "number"
        context["cty.validation_stage"] = "number_validation"

        # Add numeric value analysis if applicable
        if isinstance(value, (int, float)):
            context["cty.numeric_value"] = str(value)
            context["cty.numeric_type"] = type(value).__name__

        super().__init__(f"Number validation error: {message}", value, path, **kwargs)
    def xǁCtyNumberValidationErrorǁ__init____mutmut_33(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add number-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "number"
        context["cty.validation_stage"] = "number_validation"

        # Add numeric value analysis if applicable
        if isinstance(value, (int, float)):
            context["cty.numeric_value"] = str(value)
            context["cty.numeric_type"] = type(value).__name__

        super().__init__(f"Number validation error: {message}", value, "Number", **kwargs)
    def xǁCtyNumberValidationErrorǁ__init____mutmut_34(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add number-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "number"
        context["cty.validation_stage"] = "number_validation"

        # Add numeric value analysis if applicable
        if isinstance(value, (int, float)):
            context["cty.numeric_value"] = str(value)
            context["cty.numeric_type"] = type(value).__name__

        super().__init__(f"Number validation error: {message}", value, "Number", path, )
    def xǁCtyNumberValidationErrorǁ__init____mutmut_35(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add number-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "number"
        context["cty.validation_stage"] = "number_validation"

        # Add numeric value analysis if applicable
        if isinstance(value, (int, float)):
            context["cty.numeric_value"] = str(value)
            context["cty.numeric_type"] = type(value).__name__

        super().__init__(f"Number validation error: {message}", value, "XXNumberXX", path, **kwargs)
    def xǁCtyNumberValidationErrorǁ__init____mutmut_36(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add number-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "number"
        context["cty.validation_stage"] = "number_validation"

        # Add numeric value analysis if applicable
        if isinstance(value, (int, float)):
            context["cty.numeric_value"] = str(value)
            context["cty.numeric_type"] = type(value).__name__

        super().__init__(f"Number validation error: {message}", value, "number", path, **kwargs)
    def xǁCtyNumberValidationErrorǁ__init____mutmut_37(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add number-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "number"
        context["cty.validation_stage"] = "number_validation"

        # Add numeric value analysis if applicable
        if isinstance(value, (int, float)):
            context["cty.numeric_value"] = str(value)
            context["cty.numeric_type"] = type(value).__name__

        super().__init__(f"Number validation error: {message}", value, "NUMBER", path, **kwargs)
    
    xǁCtyNumberValidationErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCtyNumberValidationErrorǁ__init____mutmut_1': xǁCtyNumberValidationErrorǁ__init____mutmut_1, 
        'xǁCtyNumberValidationErrorǁ__init____mutmut_2': xǁCtyNumberValidationErrorǁ__init____mutmut_2, 
        'xǁCtyNumberValidationErrorǁ__init____mutmut_3': xǁCtyNumberValidationErrorǁ__init____mutmut_3, 
        'xǁCtyNumberValidationErrorǁ__init____mutmut_4': xǁCtyNumberValidationErrorǁ__init____mutmut_4, 
        'xǁCtyNumberValidationErrorǁ__init____mutmut_5': xǁCtyNumberValidationErrorǁ__init____mutmut_5, 
        'xǁCtyNumberValidationErrorǁ__init____mutmut_6': xǁCtyNumberValidationErrorǁ__init____mutmut_6, 
        'xǁCtyNumberValidationErrorǁ__init____mutmut_7': xǁCtyNumberValidationErrorǁ__init____mutmut_7, 
        'xǁCtyNumberValidationErrorǁ__init____mutmut_8': xǁCtyNumberValidationErrorǁ__init____mutmut_8, 
        'xǁCtyNumberValidationErrorǁ__init____mutmut_9': xǁCtyNumberValidationErrorǁ__init____mutmut_9, 
        'xǁCtyNumberValidationErrorǁ__init____mutmut_10': xǁCtyNumberValidationErrorǁ__init____mutmut_10, 
        'xǁCtyNumberValidationErrorǁ__init____mutmut_11': xǁCtyNumberValidationErrorǁ__init____mutmut_11, 
        'xǁCtyNumberValidationErrorǁ__init____mutmut_12': xǁCtyNumberValidationErrorǁ__init____mutmut_12, 
        'xǁCtyNumberValidationErrorǁ__init____mutmut_13': xǁCtyNumberValidationErrorǁ__init____mutmut_13, 
        'xǁCtyNumberValidationErrorǁ__init____mutmut_14': xǁCtyNumberValidationErrorǁ__init____mutmut_14, 
        'xǁCtyNumberValidationErrorǁ__init____mutmut_15': xǁCtyNumberValidationErrorǁ__init____mutmut_15, 
        'xǁCtyNumberValidationErrorǁ__init____mutmut_16': xǁCtyNumberValidationErrorǁ__init____mutmut_16, 
        'xǁCtyNumberValidationErrorǁ__init____mutmut_17': xǁCtyNumberValidationErrorǁ__init____mutmut_17, 
        'xǁCtyNumberValidationErrorǁ__init____mutmut_18': xǁCtyNumberValidationErrorǁ__init____mutmut_18, 
        'xǁCtyNumberValidationErrorǁ__init____mutmut_19': xǁCtyNumberValidationErrorǁ__init____mutmut_19, 
        'xǁCtyNumberValidationErrorǁ__init____mutmut_20': xǁCtyNumberValidationErrorǁ__init____mutmut_20, 
        'xǁCtyNumberValidationErrorǁ__init____mutmut_21': xǁCtyNumberValidationErrorǁ__init____mutmut_21, 
        'xǁCtyNumberValidationErrorǁ__init____mutmut_22': xǁCtyNumberValidationErrorǁ__init____mutmut_22, 
        'xǁCtyNumberValidationErrorǁ__init____mutmut_23': xǁCtyNumberValidationErrorǁ__init____mutmut_23, 
        'xǁCtyNumberValidationErrorǁ__init____mutmut_24': xǁCtyNumberValidationErrorǁ__init____mutmut_24, 
        'xǁCtyNumberValidationErrorǁ__init____mutmut_25': xǁCtyNumberValidationErrorǁ__init____mutmut_25, 
        'xǁCtyNumberValidationErrorǁ__init____mutmut_26': xǁCtyNumberValidationErrorǁ__init____mutmut_26, 
        'xǁCtyNumberValidationErrorǁ__init____mutmut_27': xǁCtyNumberValidationErrorǁ__init____mutmut_27, 
        'xǁCtyNumberValidationErrorǁ__init____mutmut_28': xǁCtyNumberValidationErrorǁ__init____mutmut_28, 
        'xǁCtyNumberValidationErrorǁ__init____mutmut_29': xǁCtyNumberValidationErrorǁ__init____mutmut_29, 
        'xǁCtyNumberValidationErrorǁ__init____mutmut_30': xǁCtyNumberValidationErrorǁ__init____mutmut_30, 
        'xǁCtyNumberValidationErrorǁ__init____mutmut_31': xǁCtyNumberValidationErrorǁ__init____mutmut_31, 
        'xǁCtyNumberValidationErrorǁ__init____mutmut_32': xǁCtyNumberValidationErrorǁ__init____mutmut_32, 
        'xǁCtyNumberValidationErrorǁ__init____mutmut_33': xǁCtyNumberValidationErrorǁ__init____mutmut_33, 
        'xǁCtyNumberValidationErrorǁ__init____mutmut_34': xǁCtyNumberValidationErrorǁ__init____mutmut_34, 
        'xǁCtyNumberValidationErrorǁ__init____mutmut_35': xǁCtyNumberValidationErrorǁ__init____mutmut_35, 
        'xǁCtyNumberValidationErrorǁ__init____mutmut_36': xǁCtyNumberValidationErrorǁ__init____mutmut_36, 
        'xǁCtyNumberValidationErrorǁ__init____mutmut_37': xǁCtyNumberValidationErrorǁ__init____mutmut_37
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCtyNumberValidationErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁCtyNumberValidationErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁCtyNumberValidationErrorǁ__init____mutmut_orig)
    xǁCtyNumberValidationErrorǁ__init____mutmut_orig.__name__ = 'xǁCtyNumberValidationErrorǁ__init__'


class CtyStringValidationError(CtyValidationError):
    def xǁCtyStringValidationErrorǁ__init____mutmut_orig(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add string-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "string"
        context["cty.validation_stage"] = "string_validation"

        # Add string analysis if applicable
        if isinstance(value, str):
            context["cty.string_length"] = len(value)
            context["cty.string_encoding"] = "utf-8"  # Assumed for Python strings

        super().__init__(f"String validation error: {message}", value, "String", path, **kwargs)
    def xǁCtyStringValidationErrorǁ__init____mutmut_1(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add string-specific context
        context = None
        context["cty.primitive_type"] = "string"
        context["cty.validation_stage"] = "string_validation"

        # Add string analysis if applicable
        if isinstance(value, str):
            context["cty.string_length"] = len(value)
            context["cty.string_encoding"] = "utf-8"  # Assumed for Python strings

        super().__init__(f"String validation error: {message}", value, "String", path, **kwargs)
    def xǁCtyStringValidationErrorǁ__init____mutmut_2(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add string-specific context
        context = kwargs.setdefault(None, {})
        context["cty.primitive_type"] = "string"
        context["cty.validation_stage"] = "string_validation"

        # Add string analysis if applicable
        if isinstance(value, str):
            context["cty.string_length"] = len(value)
            context["cty.string_encoding"] = "utf-8"  # Assumed for Python strings

        super().__init__(f"String validation error: {message}", value, "String", path, **kwargs)
    def xǁCtyStringValidationErrorǁ__init____mutmut_3(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add string-specific context
        context = kwargs.setdefault("context", None)
        context["cty.primitive_type"] = "string"
        context["cty.validation_stage"] = "string_validation"

        # Add string analysis if applicable
        if isinstance(value, str):
            context["cty.string_length"] = len(value)
            context["cty.string_encoding"] = "utf-8"  # Assumed for Python strings

        super().__init__(f"String validation error: {message}", value, "String", path, **kwargs)
    def xǁCtyStringValidationErrorǁ__init____mutmut_4(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add string-specific context
        context = kwargs.setdefault({})
        context["cty.primitive_type"] = "string"
        context["cty.validation_stage"] = "string_validation"

        # Add string analysis if applicable
        if isinstance(value, str):
            context["cty.string_length"] = len(value)
            context["cty.string_encoding"] = "utf-8"  # Assumed for Python strings

        super().__init__(f"String validation error: {message}", value, "String", path, **kwargs)
    def xǁCtyStringValidationErrorǁ__init____mutmut_5(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add string-specific context
        context = kwargs.setdefault("context", )
        context["cty.primitive_type"] = "string"
        context["cty.validation_stage"] = "string_validation"

        # Add string analysis if applicable
        if isinstance(value, str):
            context["cty.string_length"] = len(value)
            context["cty.string_encoding"] = "utf-8"  # Assumed for Python strings

        super().__init__(f"String validation error: {message}", value, "String", path, **kwargs)
    def xǁCtyStringValidationErrorǁ__init____mutmut_6(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add string-specific context
        context = kwargs.setdefault("XXcontextXX", {})
        context["cty.primitive_type"] = "string"
        context["cty.validation_stage"] = "string_validation"

        # Add string analysis if applicable
        if isinstance(value, str):
            context["cty.string_length"] = len(value)
            context["cty.string_encoding"] = "utf-8"  # Assumed for Python strings

        super().__init__(f"String validation error: {message}", value, "String", path, **kwargs)
    def xǁCtyStringValidationErrorǁ__init____mutmut_7(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add string-specific context
        context = kwargs.setdefault("CONTEXT", {})
        context["cty.primitive_type"] = "string"
        context["cty.validation_stage"] = "string_validation"

        # Add string analysis if applicable
        if isinstance(value, str):
            context["cty.string_length"] = len(value)
            context["cty.string_encoding"] = "utf-8"  # Assumed for Python strings

        super().__init__(f"String validation error: {message}", value, "String", path, **kwargs)
    def xǁCtyStringValidationErrorǁ__init____mutmut_8(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add string-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = None
        context["cty.validation_stage"] = "string_validation"

        # Add string analysis if applicable
        if isinstance(value, str):
            context["cty.string_length"] = len(value)
            context["cty.string_encoding"] = "utf-8"  # Assumed for Python strings

        super().__init__(f"String validation error: {message}", value, "String", path, **kwargs)
    def xǁCtyStringValidationErrorǁ__init____mutmut_9(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add string-specific context
        context = kwargs.setdefault("context", {})
        context["XXcty.primitive_typeXX"] = "string"
        context["cty.validation_stage"] = "string_validation"

        # Add string analysis if applicable
        if isinstance(value, str):
            context["cty.string_length"] = len(value)
            context["cty.string_encoding"] = "utf-8"  # Assumed for Python strings

        super().__init__(f"String validation error: {message}", value, "String", path, **kwargs)
    def xǁCtyStringValidationErrorǁ__init____mutmut_10(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add string-specific context
        context = kwargs.setdefault("context", {})
        context["CTY.PRIMITIVE_TYPE"] = "string"
        context["cty.validation_stage"] = "string_validation"

        # Add string analysis if applicable
        if isinstance(value, str):
            context["cty.string_length"] = len(value)
            context["cty.string_encoding"] = "utf-8"  # Assumed for Python strings

        super().__init__(f"String validation error: {message}", value, "String", path, **kwargs)
    def xǁCtyStringValidationErrorǁ__init____mutmut_11(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add string-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "XXstringXX"
        context["cty.validation_stage"] = "string_validation"

        # Add string analysis if applicable
        if isinstance(value, str):
            context["cty.string_length"] = len(value)
            context["cty.string_encoding"] = "utf-8"  # Assumed for Python strings

        super().__init__(f"String validation error: {message}", value, "String", path, **kwargs)
    def xǁCtyStringValidationErrorǁ__init____mutmut_12(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add string-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "STRING"
        context["cty.validation_stage"] = "string_validation"

        # Add string analysis if applicable
        if isinstance(value, str):
            context["cty.string_length"] = len(value)
            context["cty.string_encoding"] = "utf-8"  # Assumed for Python strings

        super().__init__(f"String validation error: {message}", value, "String", path, **kwargs)
    def xǁCtyStringValidationErrorǁ__init____mutmut_13(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add string-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "string"
        context["cty.validation_stage"] = None

        # Add string analysis if applicable
        if isinstance(value, str):
            context["cty.string_length"] = len(value)
            context["cty.string_encoding"] = "utf-8"  # Assumed for Python strings

        super().__init__(f"String validation error: {message}", value, "String", path, **kwargs)
    def xǁCtyStringValidationErrorǁ__init____mutmut_14(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add string-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "string"
        context["XXcty.validation_stageXX"] = "string_validation"

        # Add string analysis if applicable
        if isinstance(value, str):
            context["cty.string_length"] = len(value)
            context["cty.string_encoding"] = "utf-8"  # Assumed for Python strings

        super().__init__(f"String validation error: {message}", value, "String", path, **kwargs)
    def xǁCtyStringValidationErrorǁ__init____mutmut_15(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add string-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "string"
        context["CTY.VALIDATION_STAGE"] = "string_validation"

        # Add string analysis if applicable
        if isinstance(value, str):
            context["cty.string_length"] = len(value)
            context["cty.string_encoding"] = "utf-8"  # Assumed for Python strings

        super().__init__(f"String validation error: {message}", value, "String", path, **kwargs)
    def xǁCtyStringValidationErrorǁ__init____mutmut_16(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add string-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "string"
        context["cty.validation_stage"] = "XXstring_validationXX"

        # Add string analysis if applicable
        if isinstance(value, str):
            context["cty.string_length"] = len(value)
            context["cty.string_encoding"] = "utf-8"  # Assumed for Python strings

        super().__init__(f"String validation error: {message}", value, "String", path, **kwargs)
    def xǁCtyStringValidationErrorǁ__init____mutmut_17(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add string-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "string"
        context["cty.validation_stage"] = "STRING_VALIDATION"

        # Add string analysis if applicable
        if isinstance(value, str):
            context["cty.string_length"] = len(value)
            context["cty.string_encoding"] = "utf-8"  # Assumed for Python strings

        super().__init__(f"String validation error: {message}", value, "String", path, **kwargs)
    def xǁCtyStringValidationErrorǁ__init____mutmut_18(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add string-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "string"
        context["cty.validation_stage"] = "string_validation"

        # Add string analysis if applicable
        if isinstance(value, str):
            context["cty.string_length"] = None
            context["cty.string_encoding"] = "utf-8"  # Assumed for Python strings

        super().__init__(f"String validation error: {message}", value, "String", path, **kwargs)
    def xǁCtyStringValidationErrorǁ__init____mutmut_19(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add string-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "string"
        context["cty.validation_stage"] = "string_validation"

        # Add string analysis if applicable
        if isinstance(value, str):
            context["XXcty.string_lengthXX"] = len(value)
            context["cty.string_encoding"] = "utf-8"  # Assumed for Python strings

        super().__init__(f"String validation error: {message}", value, "String", path, **kwargs)
    def xǁCtyStringValidationErrorǁ__init____mutmut_20(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add string-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "string"
        context["cty.validation_stage"] = "string_validation"

        # Add string analysis if applicable
        if isinstance(value, str):
            context["CTY.STRING_LENGTH"] = len(value)
            context["cty.string_encoding"] = "utf-8"  # Assumed for Python strings

        super().__init__(f"String validation error: {message}", value, "String", path, **kwargs)
    def xǁCtyStringValidationErrorǁ__init____mutmut_21(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add string-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "string"
        context["cty.validation_stage"] = "string_validation"

        # Add string analysis if applicable
        if isinstance(value, str):
            context["cty.string_length"] = len(value)
            context["cty.string_encoding"] = None  # Assumed for Python strings

        super().__init__(f"String validation error: {message}", value, "String", path, **kwargs)
    def xǁCtyStringValidationErrorǁ__init____mutmut_22(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add string-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "string"
        context["cty.validation_stage"] = "string_validation"

        # Add string analysis if applicable
        if isinstance(value, str):
            context["cty.string_length"] = len(value)
            context["XXcty.string_encodingXX"] = "utf-8"  # Assumed for Python strings

        super().__init__(f"String validation error: {message}", value, "String", path, **kwargs)
    def xǁCtyStringValidationErrorǁ__init____mutmut_23(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add string-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "string"
        context["cty.validation_stage"] = "string_validation"

        # Add string analysis if applicable
        if isinstance(value, str):
            context["cty.string_length"] = len(value)
            context["CTY.STRING_ENCODING"] = "utf-8"  # Assumed for Python strings

        super().__init__(f"String validation error: {message}", value, "String", path, **kwargs)
    def xǁCtyStringValidationErrorǁ__init____mutmut_24(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add string-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "string"
        context["cty.validation_stage"] = "string_validation"

        # Add string analysis if applicable
        if isinstance(value, str):
            context["cty.string_length"] = len(value)
            context["cty.string_encoding"] = "XXutf-8XX"  # Assumed for Python strings

        super().__init__(f"String validation error: {message}", value, "String", path, **kwargs)
    def xǁCtyStringValidationErrorǁ__init____mutmut_25(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add string-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "string"
        context["cty.validation_stage"] = "string_validation"

        # Add string analysis if applicable
        if isinstance(value, str):
            context["cty.string_length"] = len(value)
            context["cty.string_encoding"] = "UTF-8"  # Assumed for Python strings

        super().__init__(f"String validation error: {message}", value, "String", path, **kwargs)
    def xǁCtyStringValidationErrorǁ__init____mutmut_26(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add string-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "string"
        context["cty.validation_stage"] = "string_validation"

        # Add string analysis if applicable
        if isinstance(value, str):
            context["cty.string_length"] = len(value)
            context["cty.string_encoding"] = "utf-8"  # Assumed for Python strings

        super().__init__(None, value, "String", path, **kwargs)
    def xǁCtyStringValidationErrorǁ__init____mutmut_27(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add string-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "string"
        context["cty.validation_stage"] = "string_validation"

        # Add string analysis if applicable
        if isinstance(value, str):
            context["cty.string_length"] = len(value)
            context["cty.string_encoding"] = "utf-8"  # Assumed for Python strings

        super().__init__(f"String validation error: {message}", None, "String", path, **kwargs)
    def xǁCtyStringValidationErrorǁ__init____mutmut_28(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add string-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "string"
        context["cty.validation_stage"] = "string_validation"

        # Add string analysis if applicable
        if isinstance(value, str):
            context["cty.string_length"] = len(value)
            context["cty.string_encoding"] = "utf-8"  # Assumed for Python strings

        super().__init__(f"String validation error: {message}", value, None, path, **kwargs)
    def xǁCtyStringValidationErrorǁ__init____mutmut_29(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add string-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "string"
        context["cty.validation_stage"] = "string_validation"

        # Add string analysis if applicable
        if isinstance(value, str):
            context["cty.string_length"] = len(value)
            context["cty.string_encoding"] = "utf-8"  # Assumed for Python strings

        super().__init__(f"String validation error: {message}", value, "String", None, **kwargs)
    def xǁCtyStringValidationErrorǁ__init____mutmut_30(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add string-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "string"
        context["cty.validation_stage"] = "string_validation"

        # Add string analysis if applicable
        if isinstance(value, str):
            context["cty.string_length"] = len(value)
            context["cty.string_encoding"] = "utf-8"  # Assumed for Python strings

        super().__init__(value, "String", path, **kwargs)
    def xǁCtyStringValidationErrorǁ__init____mutmut_31(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add string-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "string"
        context["cty.validation_stage"] = "string_validation"

        # Add string analysis if applicable
        if isinstance(value, str):
            context["cty.string_length"] = len(value)
            context["cty.string_encoding"] = "utf-8"  # Assumed for Python strings

        super().__init__(f"String validation error: {message}", "String", path, **kwargs)
    def xǁCtyStringValidationErrorǁ__init____mutmut_32(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add string-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "string"
        context["cty.validation_stage"] = "string_validation"

        # Add string analysis if applicable
        if isinstance(value, str):
            context["cty.string_length"] = len(value)
            context["cty.string_encoding"] = "utf-8"  # Assumed for Python strings

        super().__init__(f"String validation error: {message}", value, path, **kwargs)
    def xǁCtyStringValidationErrorǁ__init____mutmut_33(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add string-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "string"
        context["cty.validation_stage"] = "string_validation"

        # Add string analysis if applicable
        if isinstance(value, str):
            context["cty.string_length"] = len(value)
            context["cty.string_encoding"] = "utf-8"  # Assumed for Python strings

        super().__init__(f"String validation error: {message}", value, "String", **kwargs)
    def xǁCtyStringValidationErrorǁ__init____mutmut_34(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add string-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "string"
        context["cty.validation_stage"] = "string_validation"

        # Add string analysis if applicable
        if isinstance(value, str):
            context["cty.string_length"] = len(value)
            context["cty.string_encoding"] = "utf-8"  # Assumed for Python strings

        super().__init__(f"String validation error: {message}", value, "String", path, )
    def xǁCtyStringValidationErrorǁ__init____mutmut_35(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add string-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "string"
        context["cty.validation_stage"] = "string_validation"

        # Add string analysis if applicable
        if isinstance(value, str):
            context["cty.string_length"] = len(value)
            context["cty.string_encoding"] = "utf-8"  # Assumed for Python strings

        super().__init__(f"String validation error: {message}", value, "XXStringXX", path, **kwargs)
    def xǁCtyStringValidationErrorǁ__init____mutmut_36(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add string-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "string"
        context["cty.validation_stage"] = "string_validation"

        # Add string analysis if applicable
        if isinstance(value, str):
            context["cty.string_length"] = len(value)
            context["cty.string_encoding"] = "utf-8"  # Assumed for Python strings

        super().__init__(f"String validation error: {message}", value, "string", path, **kwargs)
    def xǁCtyStringValidationErrorǁ__init____mutmut_37(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add string-specific context
        context = kwargs.setdefault("context", {})
        context["cty.primitive_type"] = "string"
        context["cty.validation_stage"] = "string_validation"

        # Add string analysis if applicable
        if isinstance(value, str):
            context["cty.string_length"] = len(value)
            context["cty.string_encoding"] = "utf-8"  # Assumed for Python strings

        super().__init__(f"String validation error: {message}", value, "STRING", path, **kwargs)
    
    xǁCtyStringValidationErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCtyStringValidationErrorǁ__init____mutmut_1': xǁCtyStringValidationErrorǁ__init____mutmut_1, 
        'xǁCtyStringValidationErrorǁ__init____mutmut_2': xǁCtyStringValidationErrorǁ__init____mutmut_2, 
        'xǁCtyStringValidationErrorǁ__init____mutmut_3': xǁCtyStringValidationErrorǁ__init____mutmut_3, 
        'xǁCtyStringValidationErrorǁ__init____mutmut_4': xǁCtyStringValidationErrorǁ__init____mutmut_4, 
        'xǁCtyStringValidationErrorǁ__init____mutmut_5': xǁCtyStringValidationErrorǁ__init____mutmut_5, 
        'xǁCtyStringValidationErrorǁ__init____mutmut_6': xǁCtyStringValidationErrorǁ__init____mutmut_6, 
        'xǁCtyStringValidationErrorǁ__init____mutmut_7': xǁCtyStringValidationErrorǁ__init____mutmut_7, 
        'xǁCtyStringValidationErrorǁ__init____mutmut_8': xǁCtyStringValidationErrorǁ__init____mutmut_8, 
        'xǁCtyStringValidationErrorǁ__init____mutmut_9': xǁCtyStringValidationErrorǁ__init____mutmut_9, 
        'xǁCtyStringValidationErrorǁ__init____mutmut_10': xǁCtyStringValidationErrorǁ__init____mutmut_10, 
        'xǁCtyStringValidationErrorǁ__init____mutmut_11': xǁCtyStringValidationErrorǁ__init____mutmut_11, 
        'xǁCtyStringValidationErrorǁ__init____mutmut_12': xǁCtyStringValidationErrorǁ__init____mutmut_12, 
        'xǁCtyStringValidationErrorǁ__init____mutmut_13': xǁCtyStringValidationErrorǁ__init____mutmut_13, 
        'xǁCtyStringValidationErrorǁ__init____mutmut_14': xǁCtyStringValidationErrorǁ__init____mutmut_14, 
        'xǁCtyStringValidationErrorǁ__init____mutmut_15': xǁCtyStringValidationErrorǁ__init____mutmut_15, 
        'xǁCtyStringValidationErrorǁ__init____mutmut_16': xǁCtyStringValidationErrorǁ__init____mutmut_16, 
        'xǁCtyStringValidationErrorǁ__init____mutmut_17': xǁCtyStringValidationErrorǁ__init____mutmut_17, 
        'xǁCtyStringValidationErrorǁ__init____mutmut_18': xǁCtyStringValidationErrorǁ__init____mutmut_18, 
        'xǁCtyStringValidationErrorǁ__init____mutmut_19': xǁCtyStringValidationErrorǁ__init____mutmut_19, 
        'xǁCtyStringValidationErrorǁ__init____mutmut_20': xǁCtyStringValidationErrorǁ__init____mutmut_20, 
        'xǁCtyStringValidationErrorǁ__init____mutmut_21': xǁCtyStringValidationErrorǁ__init____mutmut_21, 
        'xǁCtyStringValidationErrorǁ__init____mutmut_22': xǁCtyStringValidationErrorǁ__init____mutmut_22, 
        'xǁCtyStringValidationErrorǁ__init____mutmut_23': xǁCtyStringValidationErrorǁ__init____mutmut_23, 
        'xǁCtyStringValidationErrorǁ__init____mutmut_24': xǁCtyStringValidationErrorǁ__init____mutmut_24, 
        'xǁCtyStringValidationErrorǁ__init____mutmut_25': xǁCtyStringValidationErrorǁ__init____mutmut_25, 
        'xǁCtyStringValidationErrorǁ__init____mutmut_26': xǁCtyStringValidationErrorǁ__init____mutmut_26, 
        'xǁCtyStringValidationErrorǁ__init____mutmut_27': xǁCtyStringValidationErrorǁ__init____mutmut_27, 
        'xǁCtyStringValidationErrorǁ__init____mutmut_28': xǁCtyStringValidationErrorǁ__init____mutmut_28, 
        'xǁCtyStringValidationErrorǁ__init____mutmut_29': xǁCtyStringValidationErrorǁ__init____mutmut_29, 
        'xǁCtyStringValidationErrorǁ__init____mutmut_30': xǁCtyStringValidationErrorǁ__init____mutmut_30, 
        'xǁCtyStringValidationErrorǁ__init____mutmut_31': xǁCtyStringValidationErrorǁ__init____mutmut_31, 
        'xǁCtyStringValidationErrorǁ__init____mutmut_32': xǁCtyStringValidationErrorǁ__init____mutmut_32, 
        'xǁCtyStringValidationErrorǁ__init____mutmut_33': xǁCtyStringValidationErrorǁ__init____mutmut_33, 
        'xǁCtyStringValidationErrorǁ__init____mutmut_34': xǁCtyStringValidationErrorǁ__init____mutmut_34, 
        'xǁCtyStringValidationErrorǁ__init____mutmut_35': xǁCtyStringValidationErrorǁ__init____mutmut_35, 
        'xǁCtyStringValidationErrorǁ__init____mutmut_36': xǁCtyStringValidationErrorǁ__init____mutmut_36, 
        'xǁCtyStringValidationErrorǁ__init____mutmut_37': xǁCtyStringValidationErrorǁ__init____mutmut_37
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCtyStringValidationErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁCtyStringValidationErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁCtyStringValidationErrorǁ__init____mutmut_orig)
    xǁCtyStringValidationErrorǁ__init____mutmut_orig.__name__ = 'xǁCtyStringValidationErrorǁ__init__'


# --- Collection Validation Errors ---
class CtyCollectionValidationError(CtyValidationError):
    """Base for collection-related validation errors."""


class CtyListValidationError(CtyCollectionValidationError):
    def xǁCtyListValidationErrorǁ__init____mutmut_orig(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add list-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "list"

        if isinstance(value, (list, tuple)):
            context["cty.collection_length"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "List"),
            path,
            **kwargs,
        )
    def xǁCtyListValidationErrorǁ__init____mutmut_1(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add list-specific context
        context = None
        context["cty.collection_type"] = "list"

        if isinstance(value, (list, tuple)):
            context["cty.collection_length"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "List"),
            path,
            **kwargs,
        )
    def xǁCtyListValidationErrorǁ__init____mutmut_2(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add list-specific context
        context = kwargs.setdefault(None, {})
        context["cty.collection_type"] = "list"

        if isinstance(value, (list, tuple)):
            context["cty.collection_length"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "List"),
            path,
            **kwargs,
        )
    def xǁCtyListValidationErrorǁ__init____mutmut_3(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add list-specific context
        context = kwargs.setdefault("context", None)
        context["cty.collection_type"] = "list"

        if isinstance(value, (list, tuple)):
            context["cty.collection_length"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "List"),
            path,
            **kwargs,
        )
    def xǁCtyListValidationErrorǁ__init____mutmut_4(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add list-specific context
        context = kwargs.setdefault({})
        context["cty.collection_type"] = "list"

        if isinstance(value, (list, tuple)):
            context["cty.collection_length"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "List"),
            path,
            **kwargs,
        )
    def xǁCtyListValidationErrorǁ__init____mutmut_5(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add list-specific context
        context = kwargs.setdefault("context", )
        context["cty.collection_type"] = "list"

        if isinstance(value, (list, tuple)):
            context["cty.collection_length"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "List"),
            path,
            **kwargs,
        )
    def xǁCtyListValidationErrorǁ__init____mutmut_6(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add list-specific context
        context = kwargs.setdefault("XXcontextXX", {})
        context["cty.collection_type"] = "list"

        if isinstance(value, (list, tuple)):
            context["cty.collection_length"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "List"),
            path,
            **kwargs,
        )
    def xǁCtyListValidationErrorǁ__init____mutmut_7(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add list-specific context
        context = kwargs.setdefault("CONTEXT", {})
        context["cty.collection_type"] = "list"

        if isinstance(value, (list, tuple)):
            context["cty.collection_length"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "List"),
            path,
            **kwargs,
        )
    def xǁCtyListValidationErrorǁ__init____mutmut_8(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add list-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = None

        if isinstance(value, (list, tuple)):
            context["cty.collection_length"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "List"),
            path,
            **kwargs,
        )
    def xǁCtyListValidationErrorǁ__init____mutmut_9(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add list-specific context
        context = kwargs.setdefault("context", {})
        context["XXcty.collection_typeXX"] = "list"

        if isinstance(value, (list, tuple)):
            context["cty.collection_length"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "List"),
            path,
            **kwargs,
        )
    def xǁCtyListValidationErrorǁ__init____mutmut_10(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add list-specific context
        context = kwargs.setdefault("context", {})
        context["CTY.COLLECTION_TYPE"] = "list"

        if isinstance(value, (list, tuple)):
            context["cty.collection_length"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "List"),
            path,
            **kwargs,
        )
    def xǁCtyListValidationErrorǁ__init____mutmut_11(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add list-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "XXlistXX"

        if isinstance(value, (list, tuple)):
            context["cty.collection_length"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "List"),
            path,
            **kwargs,
        )
    def xǁCtyListValidationErrorǁ__init____mutmut_12(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add list-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "LIST"

        if isinstance(value, (list, tuple)):
            context["cty.collection_length"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "List"),
            path,
            **kwargs,
        )
    def xǁCtyListValidationErrorǁ__init____mutmut_13(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add list-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "list"

        if isinstance(value, (list, tuple)):
            context["cty.collection_length"] = None

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "List"),
            path,
            **kwargs,
        )
    def xǁCtyListValidationErrorǁ__init____mutmut_14(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add list-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "list"

        if isinstance(value, (list, tuple)):
            context["XXcty.collection_lengthXX"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "List"),
            path,
            **kwargs,
        )
    def xǁCtyListValidationErrorǁ__init____mutmut_15(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add list-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "list"

        if isinstance(value, (list, tuple)):
            context["CTY.COLLECTION_LENGTH"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "List"),
            path,
            **kwargs,
        )
    def xǁCtyListValidationErrorǁ__init____mutmut_16(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add list-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "list"

        if isinstance(value, (list, tuple)):
            context["cty.collection_length"] = len(value)

        if original_exception:
            context["cty.nested_error"] = None

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "List"),
            path,
            **kwargs,
        )
    def xǁCtyListValidationErrorǁ__init____mutmut_17(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add list-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "list"

        if isinstance(value, (list, tuple)):
            context["cty.collection_length"] = len(value)

        if original_exception:
            context["XXcty.nested_errorXX"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "List"),
            path,
            **kwargs,
        )
    def xǁCtyListValidationErrorǁ__init____mutmut_18(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add list-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "list"

        if isinstance(value, (list, tuple)):
            context["cty.collection_length"] = len(value)

        if original_exception:
            context["CTY.NESTED_ERROR"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "List"),
            path,
            **kwargs,
        )
    def xǁCtyListValidationErrorǁ__init____mutmut_19(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add list-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "list"

        if isinstance(value, (list, tuple)):
            context["cty.collection_length"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(None).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "List"),
            path,
            **kwargs,
        )
    def xǁCtyListValidationErrorǁ__init____mutmut_20(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add list-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "list"

        if isinstance(value, (list, tuple)):
            context["cty.collection_length"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            None,
            value,
            _get_type_name_from_original(original_exception, "List"),
            path,
            **kwargs,
        )
    def xǁCtyListValidationErrorǁ__init____mutmut_21(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add list-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "list"

        if isinstance(value, (list, tuple)):
            context["cty.collection_length"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            None,
            _get_type_name_from_original(original_exception, "List"),
            path,
            **kwargs,
        )
    def xǁCtyListValidationErrorǁ__init____mutmut_22(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add list-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "list"

        if isinstance(value, (list, tuple)):
            context["cty.collection_length"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            None,
            path,
            **kwargs,
        )
    def xǁCtyListValidationErrorǁ__init____mutmut_23(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add list-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "list"

        if isinstance(value, (list, tuple)):
            context["cty.collection_length"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "List"),
            None,
            **kwargs,
        )
    def xǁCtyListValidationErrorǁ__init____mutmut_24(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add list-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "list"

        if isinstance(value, (list, tuple)):
            context["cty.collection_length"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            value,
            _get_type_name_from_original(original_exception, "List"),
            path,
            **kwargs,
        )
    def xǁCtyListValidationErrorǁ__init____mutmut_25(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add list-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "list"

        if isinstance(value, (list, tuple)):
            context["cty.collection_length"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            _get_type_name_from_original(original_exception, "List"),
            path,
            **kwargs,
        )
    def xǁCtyListValidationErrorǁ__init____mutmut_26(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add list-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "list"

        if isinstance(value, (list, tuple)):
            context["cty.collection_length"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            path,
            **kwargs,
        )
    def xǁCtyListValidationErrorǁ__init____mutmut_27(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add list-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "list"

        if isinstance(value, (list, tuple)):
            context["cty.collection_length"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "List"),
            **kwargs,
        )
    def xǁCtyListValidationErrorǁ__init____mutmut_28(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add list-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "list"

        if isinstance(value, (list, tuple)):
            context["cty.collection_length"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "List"),
            path,
            )
    def xǁCtyListValidationErrorǁ__init____mutmut_29(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add list-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "list"

        if isinstance(value, (list, tuple)):
            context["cty.collection_length"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(None, "List"),
            path,
            **kwargs,
        )
    def xǁCtyListValidationErrorǁ__init____mutmut_30(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add list-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "list"

        if isinstance(value, (list, tuple)):
            context["cty.collection_length"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, None),
            path,
            **kwargs,
        )
    def xǁCtyListValidationErrorǁ__init____mutmut_31(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add list-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "list"

        if isinstance(value, (list, tuple)):
            context["cty.collection_length"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original("List"),
            path,
            **kwargs,
        )
    def xǁCtyListValidationErrorǁ__init____mutmut_32(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add list-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "list"

        if isinstance(value, (list, tuple)):
            context["cty.collection_length"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, ),
            path,
            **kwargs,
        )
    def xǁCtyListValidationErrorǁ__init____mutmut_33(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add list-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "list"

        if isinstance(value, (list, tuple)):
            context["cty.collection_length"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "XXListXX"),
            path,
            **kwargs,
        )
    def xǁCtyListValidationErrorǁ__init____mutmut_34(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add list-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "list"

        if isinstance(value, (list, tuple)):
            context["cty.collection_length"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "list"),
            path,
            **kwargs,
        )
    def xǁCtyListValidationErrorǁ__init____mutmut_35(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add list-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "list"

        if isinstance(value, (list, tuple)):
            context["cty.collection_length"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "LIST"),
            path,
            **kwargs,
        )
    
    xǁCtyListValidationErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCtyListValidationErrorǁ__init____mutmut_1': xǁCtyListValidationErrorǁ__init____mutmut_1, 
        'xǁCtyListValidationErrorǁ__init____mutmut_2': xǁCtyListValidationErrorǁ__init____mutmut_2, 
        'xǁCtyListValidationErrorǁ__init____mutmut_3': xǁCtyListValidationErrorǁ__init____mutmut_3, 
        'xǁCtyListValidationErrorǁ__init____mutmut_4': xǁCtyListValidationErrorǁ__init____mutmut_4, 
        'xǁCtyListValidationErrorǁ__init____mutmut_5': xǁCtyListValidationErrorǁ__init____mutmut_5, 
        'xǁCtyListValidationErrorǁ__init____mutmut_6': xǁCtyListValidationErrorǁ__init____mutmut_6, 
        'xǁCtyListValidationErrorǁ__init____mutmut_7': xǁCtyListValidationErrorǁ__init____mutmut_7, 
        'xǁCtyListValidationErrorǁ__init____mutmut_8': xǁCtyListValidationErrorǁ__init____mutmut_8, 
        'xǁCtyListValidationErrorǁ__init____mutmut_9': xǁCtyListValidationErrorǁ__init____mutmut_9, 
        'xǁCtyListValidationErrorǁ__init____mutmut_10': xǁCtyListValidationErrorǁ__init____mutmut_10, 
        'xǁCtyListValidationErrorǁ__init____mutmut_11': xǁCtyListValidationErrorǁ__init____mutmut_11, 
        'xǁCtyListValidationErrorǁ__init____mutmut_12': xǁCtyListValidationErrorǁ__init____mutmut_12, 
        'xǁCtyListValidationErrorǁ__init____mutmut_13': xǁCtyListValidationErrorǁ__init____mutmut_13, 
        'xǁCtyListValidationErrorǁ__init____mutmut_14': xǁCtyListValidationErrorǁ__init____mutmut_14, 
        'xǁCtyListValidationErrorǁ__init____mutmut_15': xǁCtyListValidationErrorǁ__init____mutmut_15, 
        'xǁCtyListValidationErrorǁ__init____mutmut_16': xǁCtyListValidationErrorǁ__init____mutmut_16, 
        'xǁCtyListValidationErrorǁ__init____mutmut_17': xǁCtyListValidationErrorǁ__init____mutmut_17, 
        'xǁCtyListValidationErrorǁ__init____mutmut_18': xǁCtyListValidationErrorǁ__init____mutmut_18, 
        'xǁCtyListValidationErrorǁ__init____mutmut_19': xǁCtyListValidationErrorǁ__init____mutmut_19, 
        'xǁCtyListValidationErrorǁ__init____mutmut_20': xǁCtyListValidationErrorǁ__init____mutmut_20, 
        'xǁCtyListValidationErrorǁ__init____mutmut_21': xǁCtyListValidationErrorǁ__init____mutmut_21, 
        'xǁCtyListValidationErrorǁ__init____mutmut_22': xǁCtyListValidationErrorǁ__init____mutmut_22, 
        'xǁCtyListValidationErrorǁ__init____mutmut_23': xǁCtyListValidationErrorǁ__init____mutmut_23, 
        'xǁCtyListValidationErrorǁ__init____mutmut_24': xǁCtyListValidationErrorǁ__init____mutmut_24, 
        'xǁCtyListValidationErrorǁ__init____mutmut_25': xǁCtyListValidationErrorǁ__init____mutmut_25, 
        'xǁCtyListValidationErrorǁ__init____mutmut_26': xǁCtyListValidationErrorǁ__init____mutmut_26, 
        'xǁCtyListValidationErrorǁ__init____mutmut_27': xǁCtyListValidationErrorǁ__init____mutmut_27, 
        'xǁCtyListValidationErrorǁ__init____mutmut_28': xǁCtyListValidationErrorǁ__init____mutmut_28, 
        'xǁCtyListValidationErrorǁ__init____mutmut_29': xǁCtyListValidationErrorǁ__init____mutmut_29, 
        'xǁCtyListValidationErrorǁ__init____mutmut_30': xǁCtyListValidationErrorǁ__init____mutmut_30, 
        'xǁCtyListValidationErrorǁ__init____mutmut_31': xǁCtyListValidationErrorǁ__init____mutmut_31, 
        'xǁCtyListValidationErrorǁ__init____mutmut_32': xǁCtyListValidationErrorǁ__init____mutmut_32, 
        'xǁCtyListValidationErrorǁ__init____mutmut_33': xǁCtyListValidationErrorǁ__init____mutmut_33, 
        'xǁCtyListValidationErrorǁ__init____mutmut_34': xǁCtyListValidationErrorǁ__init____mutmut_34, 
        'xǁCtyListValidationErrorǁ__init____mutmut_35': xǁCtyListValidationErrorǁ__init____mutmut_35
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCtyListValidationErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁCtyListValidationErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁCtyListValidationErrorǁ__init____mutmut_orig)
    xǁCtyListValidationErrorǁ__init____mutmut_orig.__name__ = 'xǁCtyListValidationErrorǁ__init__'


class CtyMapValidationError(CtyCollectionValidationError):
    def xǁCtyMapValidationErrorǁ__init____mutmut_orig(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add map-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "map"

        if isinstance(value, dict):
            context["cty.collection_size"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Map"),
            path,
            **kwargs,
        )
    def xǁCtyMapValidationErrorǁ__init____mutmut_1(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add map-specific context
        context = None
        context["cty.collection_type"] = "map"

        if isinstance(value, dict):
            context["cty.collection_size"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Map"),
            path,
            **kwargs,
        )
    def xǁCtyMapValidationErrorǁ__init____mutmut_2(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add map-specific context
        context = kwargs.setdefault(None, {})
        context["cty.collection_type"] = "map"

        if isinstance(value, dict):
            context["cty.collection_size"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Map"),
            path,
            **kwargs,
        )
    def xǁCtyMapValidationErrorǁ__init____mutmut_3(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add map-specific context
        context = kwargs.setdefault("context", None)
        context["cty.collection_type"] = "map"

        if isinstance(value, dict):
            context["cty.collection_size"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Map"),
            path,
            **kwargs,
        )
    def xǁCtyMapValidationErrorǁ__init____mutmut_4(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add map-specific context
        context = kwargs.setdefault({})
        context["cty.collection_type"] = "map"

        if isinstance(value, dict):
            context["cty.collection_size"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Map"),
            path,
            **kwargs,
        )
    def xǁCtyMapValidationErrorǁ__init____mutmut_5(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add map-specific context
        context = kwargs.setdefault("context", )
        context["cty.collection_type"] = "map"

        if isinstance(value, dict):
            context["cty.collection_size"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Map"),
            path,
            **kwargs,
        )
    def xǁCtyMapValidationErrorǁ__init____mutmut_6(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add map-specific context
        context = kwargs.setdefault("XXcontextXX", {})
        context["cty.collection_type"] = "map"

        if isinstance(value, dict):
            context["cty.collection_size"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Map"),
            path,
            **kwargs,
        )
    def xǁCtyMapValidationErrorǁ__init____mutmut_7(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add map-specific context
        context = kwargs.setdefault("CONTEXT", {})
        context["cty.collection_type"] = "map"

        if isinstance(value, dict):
            context["cty.collection_size"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Map"),
            path,
            **kwargs,
        )
    def xǁCtyMapValidationErrorǁ__init____mutmut_8(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add map-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = None

        if isinstance(value, dict):
            context["cty.collection_size"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Map"),
            path,
            **kwargs,
        )
    def xǁCtyMapValidationErrorǁ__init____mutmut_9(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add map-specific context
        context = kwargs.setdefault("context", {})
        context["XXcty.collection_typeXX"] = "map"

        if isinstance(value, dict):
            context["cty.collection_size"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Map"),
            path,
            **kwargs,
        )
    def xǁCtyMapValidationErrorǁ__init____mutmut_10(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add map-specific context
        context = kwargs.setdefault("context", {})
        context["CTY.COLLECTION_TYPE"] = "map"

        if isinstance(value, dict):
            context["cty.collection_size"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Map"),
            path,
            **kwargs,
        )
    def xǁCtyMapValidationErrorǁ__init____mutmut_11(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add map-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "XXmapXX"

        if isinstance(value, dict):
            context["cty.collection_size"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Map"),
            path,
            **kwargs,
        )
    def xǁCtyMapValidationErrorǁ__init____mutmut_12(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add map-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "MAP"

        if isinstance(value, dict):
            context["cty.collection_size"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Map"),
            path,
            **kwargs,
        )
    def xǁCtyMapValidationErrorǁ__init____mutmut_13(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add map-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "map"

        if isinstance(value, dict):
            context["cty.collection_size"] = None

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Map"),
            path,
            **kwargs,
        )
    def xǁCtyMapValidationErrorǁ__init____mutmut_14(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add map-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "map"

        if isinstance(value, dict):
            context["XXcty.collection_sizeXX"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Map"),
            path,
            **kwargs,
        )
    def xǁCtyMapValidationErrorǁ__init____mutmut_15(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add map-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "map"

        if isinstance(value, dict):
            context["CTY.COLLECTION_SIZE"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Map"),
            path,
            **kwargs,
        )
    def xǁCtyMapValidationErrorǁ__init____mutmut_16(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add map-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "map"

        if isinstance(value, dict):
            context["cty.collection_size"] = len(value)

        if original_exception:
            context["cty.nested_error"] = None

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Map"),
            path,
            **kwargs,
        )
    def xǁCtyMapValidationErrorǁ__init____mutmut_17(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add map-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "map"

        if isinstance(value, dict):
            context["cty.collection_size"] = len(value)

        if original_exception:
            context["XXcty.nested_errorXX"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Map"),
            path,
            **kwargs,
        )
    def xǁCtyMapValidationErrorǁ__init____mutmut_18(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add map-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "map"

        if isinstance(value, dict):
            context["cty.collection_size"] = len(value)

        if original_exception:
            context["CTY.NESTED_ERROR"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Map"),
            path,
            **kwargs,
        )
    def xǁCtyMapValidationErrorǁ__init____mutmut_19(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add map-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "map"

        if isinstance(value, dict):
            context["cty.collection_size"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(None).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Map"),
            path,
            **kwargs,
        )
    def xǁCtyMapValidationErrorǁ__init____mutmut_20(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add map-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "map"

        if isinstance(value, dict):
            context["cty.collection_size"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            None,
            value,
            _get_type_name_from_original(original_exception, "Map"),
            path,
            **kwargs,
        )
    def xǁCtyMapValidationErrorǁ__init____mutmut_21(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add map-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "map"

        if isinstance(value, dict):
            context["cty.collection_size"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            None,
            _get_type_name_from_original(original_exception, "Map"),
            path,
            **kwargs,
        )
    def xǁCtyMapValidationErrorǁ__init____mutmut_22(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add map-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "map"

        if isinstance(value, dict):
            context["cty.collection_size"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            None,
            path,
            **kwargs,
        )
    def xǁCtyMapValidationErrorǁ__init____mutmut_23(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add map-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "map"

        if isinstance(value, dict):
            context["cty.collection_size"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Map"),
            None,
            **kwargs,
        )
    def xǁCtyMapValidationErrorǁ__init____mutmut_24(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add map-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "map"

        if isinstance(value, dict):
            context["cty.collection_size"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            value,
            _get_type_name_from_original(original_exception, "Map"),
            path,
            **kwargs,
        )
    def xǁCtyMapValidationErrorǁ__init____mutmut_25(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add map-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "map"

        if isinstance(value, dict):
            context["cty.collection_size"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            _get_type_name_from_original(original_exception, "Map"),
            path,
            **kwargs,
        )
    def xǁCtyMapValidationErrorǁ__init____mutmut_26(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add map-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "map"

        if isinstance(value, dict):
            context["cty.collection_size"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            path,
            **kwargs,
        )
    def xǁCtyMapValidationErrorǁ__init____mutmut_27(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add map-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "map"

        if isinstance(value, dict):
            context["cty.collection_size"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Map"),
            **kwargs,
        )
    def xǁCtyMapValidationErrorǁ__init____mutmut_28(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add map-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "map"

        if isinstance(value, dict):
            context["cty.collection_size"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Map"),
            path,
            )
    def xǁCtyMapValidationErrorǁ__init____mutmut_29(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add map-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "map"

        if isinstance(value, dict):
            context["cty.collection_size"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(None, "Map"),
            path,
            **kwargs,
        )
    def xǁCtyMapValidationErrorǁ__init____mutmut_30(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add map-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "map"

        if isinstance(value, dict):
            context["cty.collection_size"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, None),
            path,
            **kwargs,
        )
    def xǁCtyMapValidationErrorǁ__init____mutmut_31(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add map-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "map"

        if isinstance(value, dict):
            context["cty.collection_size"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original("Map"),
            path,
            **kwargs,
        )
    def xǁCtyMapValidationErrorǁ__init____mutmut_32(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add map-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "map"

        if isinstance(value, dict):
            context["cty.collection_size"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, ),
            path,
            **kwargs,
        )
    def xǁCtyMapValidationErrorǁ__init____mutmut_33(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add map-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "map"

        if isinstance(value, dict):
            context["cty.collection_size"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "XXMapXX"),
            path,
            **kwargs,
        )
    def xǁCtyMapValidationErrorǁ__init____mutmut_34(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add map-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "map"

        if isinstance(value, dict):
            context["cty.collection_size"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "map"),
            path,
            **kwargs,
        )
    def xǁCtyMapValidationErrorǁ__init____mutmut_35(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add map-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "map"

        if isinstance(value, dict):
            context["cty.collection_size"] = len(value)

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "MAP"),
            path,
            **kwargs,
        )
    
    xǁCtyMapValidationErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCtyMapValidationErrorǁ__init____mutmut_1': xǁCtyMapValidationErrorǁ__init____mutmut_1, 
        'xǁCtyMapValidationErrorǁ__init____mutmut_2': xǁCtyMapValidationErrorǁ__init____mutmut_2, 
        'xǁCtyMapValidationErrorǁ__init____mutmut_3': xǁCtyMapValidationErrorǁ__init____mutmut_3, 
        'xǁCtyMapValidationErrorǁ__init____mutmut_4': xǁCtyMapValidationErrorǁ__init____mutmut_4, 
        'xǁCtyMapValidationErrorǁ__init____mutmut_5': xǁCtyMapValidationErrorǁ__init____mutmut_5, 
        'xǁCtyMapValidationErrorǁ__init____mutmut_6': xǁCtyMapValidationErrorǁ__init____mutmut_6, 
        'xǁCtyMapValidationErrorǁ__init____mutmut_7': xǁCtyMapValidationErrorǁ__init____mutmut_7, 
        'xǁCtyMapValidationErrorǁ__init____mutmut_8': xǁCtyMapValidationErrorǁ__init____mutmut_8, 
        'xǁCtyMapValidationErrorǁ__init____mutmut_9': xǁCtyMapValidationErrorǁ__init____mutmut_9, 
        'xǁCtyMapValidationErrorǁ__init____mutmut_10': xǁCtyMapValidationErrorǁ__init____mutmut_10, 
        'xǁCtyMapValidationErrorǁ__init____mutmut_11': xǁCtyMapValidationErrorǁ__init____mutmut_11, 
        'xǁCtyMapValidationErrorǁ__init____mutmut_12': xǁCtyMapValidationErrorǁ__init____mutmut_12, 
        'xǁCtyMapValidationErrorǁ__init____mutmut_13': xǁCtyMapValidationErrorǁ__init____mutmut_13, 
        'xǁCtyMapValidationErrorǁ__init____mutmut_14': xǁCtyMapValidationErrorǁ__init____mutmut_14, 
        'xǁCtyMapValidationErrorǁ__init____mutmut_15': xǁCtyMapValidationErrorǁ__init____mutmut_15, 
        'xǁCtyMapValidationErrorǁ__init____mutmut_16': xǁCtyMapValidationErrorǁ__init____mutmut_16, 
        'xǁCtyMapValidationErrorǁ__init____mutmut_17': xǁCtyMapValidationErrorǁ__init____mutmut_17, 
        'xǁCtyMapValidationErrorǁ__init____mutmut_18': xǁCtyMapValidationErrorǁ__init____mutmut_18, 
        'xǁCtyMapValidationErrorǁ__init____mutmut_19': xǁCtyMapValidationErrorǁ__init____mutmut_19, 
        'xǁCtyMapValidationErrorǁ__init____mutmut_20': xǁCtyMapValidationErrorǁ__init____mutmut_20, 
        'xǁCtyMapValidationErrorǁ__init____mutmut_21': xǁCtyMapValidationErrorǁ__init____mutmut_21, 
        'xǁCtyMapValidationErrorǁ__init____mutmut_22': xǁCtyMapValidationErrorǁ__init____mutmut_22, 
        'xǁCtyMapValidationErrorǁ__init____mutmut_23': xǁCtyMapValidationErrorǁ__init____mutmut_23, 
        'xǁCtyMapValidationErrorǁ__init____mutmut_24': xǁCtyMapValidationErrorǁ__init____mutmut_24, 
        'xǁCtyMapValidationErrorǁ__init____mutmut_25': xǁCtyMapValidationErrorǁ__init____mutmut_25, 
        'xǁCtyMapValidationErrorǁ__init____mutmut_26': xǁCtyMapValidationErrorǁ__init____mutmut_26, 
        'xǁCtyMapValidationErrorǁ__init____mutmut_27': xǁCtyMapValidationErrorǁ__init____mutmut_27, 
        'xǁCtyMapValidationErrorǁ__init____mutmut_28': xǁCtyMapValidationErrorǁ__init____mutmut_28, 
        'xǁCtyMapValidationErrorǁ__init____mutmut_29': xǁCtyMapValidationErrorǁ__init____mutmut_29, 
        'xǁCtyMapValidationErrorǁ__init____mutmut_30': xǁCtyMapValidationErrorǁ__init____mutmut_30, 
        'xǁCtyMapValidationErrorǁ__init____mutmut_31': xǁCtyMapValidationErrorǁ__init____mutmut_31, 
        'xǁCtyMapValidationErrorǁ__init____mutmut_32': xǁCtyMapValidationErrorǁ__init____mutmut_32, 
        'xǁCtyMapValidationErrorǁ__init____mutmut_33': xǁCtyMapValidationErrorǁ__init____mutmut_33, 
        'xǁCtyMapValidationErrorǁ__init____mutmut_34': xǁCtyMapValidationErrorǁ__init____mutmut_34, 
        'xǁCtyMapValidationErrorǁ__init____mutmut_35': xǁCtyMapValidationErrorǁ__init____mutmut_35
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCtyMapValidationErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁCtyMapValidationErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁCtyMapValidationErrorǁ__init____mutmut_orig)
    xǁCtyMapValidationErrorǁ__init____mutmut_orig.__name__ = 'xǁCtyMapValidationErrorǁ__init__'


class CtySetValidationError(CtyCollectionValidationError):
    def xǁCtySetValidationErrorǁ__init____mutmut_orig(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add set-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "set"

        if isinstance(value, (set, frozenset)):
            context["cty.collection_size"] = len(value)
            context["cty.set_type"] = type(value).__name__

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Set"),
            path,
            **kwargs,
        )
    def xǁCtySetValidationErrorǁ__init____mutmut_1(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add set-specific context
        context = None
        context["cty.collection_type"] = "set"

        if isinstance(value, (set, frozenset)):
            context["cty.collection_size"] = len(value)
            context["cty.set_type"] = type(value).__name__

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Set"),
            path,
            **kwargs,
        )
    def xǁCtySetValidationErrorǁ__init____mutmut_2(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add set-specific context
        context = kwargs.setdefault(None, {})
        context["cty.collection_type"] = "set"

        if isinstance(value, (set, frozenset)):
            context["cty.collection_size"] = len(value)
            context["cty.set_type"] = type(value).__name__

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Set"),
            path,
            **kwargs,
        )
    def xǁCtySetValidationErrorǁ__init____mutmut_3(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add set-specific context
        context = kwargs.setdefault("context", None)
        context["cty.collection_type"] = "set"

        if isinstance(value, (set, frozenset)):
            context["cty.collection_size"] = len(value)
            context["cty.set_type"] = type(value).__name__

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Set"),
            path,
            **kwargs,
        )
    def xǁCtySetValidationErrorǁ__init____mutmut_4(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add set-specific context
        context = kwargs.setdefault({})
        context["cty.collection_type"] = "set"

        if isinstance(value, (set, frozenset)):
            context["cty.collection_size"] = len(value)
            context["cty.set_type"] = type(value).__name__

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Set"),
            path,
            **kwargs,
        )
    def xǁCtySetValidationErrorǁ__init____mutmut_5(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add set-specific context
        context = kwargs.setdefault("context", )
        context["cty.collection_type"] = "set"

        if isinstance(value, (set, frozenset)):
            context["cty.collection_size"] = len(value)
            context["cty.set_type"] = type(value).__name__

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Set"),
            path,
            **kwargs,
        )
    def xǁCtySetValidationErrorǁ__init____mutmut_6(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add set-specific context
        context = kwargs.setdefault("XXcontextXX", {})
        context["cty.collection_type"] = "set"

        if isinstance(value, (set, frozenset)):
            context["cty.collection_size"] = len(value)
            context["cty.set_type"] = type(value).__name__

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Set"),
            path,
            **kwargs,
        )
    def xǁCtySetValidationErrorǁ__init____mutmut_7(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add set-specific context
        context = kwargs.setdefault("CONTEXT", {})
        context["cty.collection_type"] = "set"

        if isinstance(value, (set, frozenset)):
            context["cty.collection_size"] = len(value)
            context["cty.set_type"] = type(value).__name__

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Set"),
            path,
            **kwargs,
        )
    def xǁCtySetValidationErrorǁ__init____mutmut_8(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add set-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = None

        if isinstance(value, (set, frozenset)):
            context["cty.collection_size"] = len(value)
            context["cty.set_type"] = type(value).__name__

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Set"),
            path,
            **kwargs,
        )
    def xǁCtySetValidationErrorǁ__init____mutmut_9(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add set-specific context
        context = kwargs.setdefault("context", {})
        context["XXcty.collection_typeXX"] = "set"

        if isinstance(value, (set, frozenset)):
            context["cty.collection_size"] = len(value)
            context["cty.set_type"] = type(value).__name__

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Set"),
            path,
            **kwargs,
        )
    def xǁCtySetValidationErrorǁ__init____mutmut_10(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add set-specific context
        context = kwargs.setdefault("context", {})
        context["CTY.COLLECTION_TYPE"] = "set"

        if isinstance(value, (set, frozenset)):
            context["cty.collection_size"] = len(value)
            context["cty.set_type"] = type(value).__name__

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Set"),
            path,
            **kwargs,
        )
    def xǁCtySetValidationErrorǁ__init____mutmut_11(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add set-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "XXsetXX"

        if isinstance(value, (set, frozenset)):
            context["cty.collection_size"] = len(value)
            context["cty.set_type"] = type(value).__name__

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Set"),
            path,
            **kwargs,
        )
    def xǁCtySetValidationErrorǁ__init____mutmut_12(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add set-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "SET"

        if isinstance(value, (set, frozenset)):
            context["cty.collection_size"] = len(value)
            context["cty.set_type"] = type(value).__name__

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Set"),
            path,
            **kwargs,
        )
    def xǁCtySetValidationErrorǁ__init____mutmut_13(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add set-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "set"

        if isinstance(value, (set, frozenset)):
            context["cty.collection_size"] = None
            context["cty.set_type"] = type(value).__name__

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Set"),
            path,
            **kwargs,
        )
    def xǁCtySetValidationErrorǁ__init____mutmut_14(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add set-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "set"

        if isinstance(value, (set, frozenset)):
            context["XXcty.collection_sizeXX"] = len(value)
            context["cty.set_type"] = type(value).__name__

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Set"),
            path,
            **kwargs,
        )
    def xǁCtySetValidationErrorǁ__init____mutmut_15(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add set-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "set"

        if isinstance(value, (set, frozenset)):
            context["CTY.COLLECTION_SIZE"] = len(value)
            context["cty.set_type"] = type(value).__name__

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Set"),
            path,
            **kwargs,
        )
    def xǁCtySetValidationErrorǁ__init____mutmut_16(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add set-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "set"

        if isinstance(value, (set, frozenset)):
            context["cty.collection_size"] = len(value)
            context["cty.set_type"] = None

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Set"),
            path,
            **kwargs,
        )
    def xǁCtySetValidationErrorǁ__init____mutmut_17(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add set-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "set"

        if isinstance(value, (set, frozenset)):
            context["cty.collection_size"] = len(value)
            context["XXcty.set_typeXX"] = type(value).__name__

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Set"),
            path,
            **kwargs,
        )
    def xǁCtySetValidationErrorǁ__init____mutmut_18(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add set-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "set"

        if isinstance(value, (set, frozenset)):
            context["cty.collection_size"] = len(value)
            context["CTY.SET_TYPE"] = type(value).__name__

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Set"),
            path,
            **kwargs,
        )
    def xǁCtySetValidationErrorǁ__init____mutmut_19(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add set-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "set"

        if isinstance(value, (set, frozenset)):
            context["cty.collection_size"] = len(value)
            context["cty.set_type"] = type(None).__name__

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Set"),
            path,
            **kwargs,
        )
    def xǁCtySetValidationErrorǁ__init____mutmut_20(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add set-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "set"

        if isinstance(value, (set, frozenset)):
            context["cty.collection_size"] = len(value)
            context["cty.set_type"] = type(value).__name__

        if original_exception:
            context["cty.nested_error"] = None

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Set"),
            path,
            **kwargs,
        )
    def xǁCtySetValidationErrorǁ__init____mutmut_21(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add set-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "set"

        if isinstance(value, (set, frozenset)):
            context["cty.collection_size"] = len(value)
            context["cty.set_type"] = type(value).__name__

        if original_exception:
            context["XXcty.nested_errorXX"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Set"),
            path,
            **kwargs,
        )
    def xǁCtySetValidationErrorǁ__init____mutmut_22(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add set-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "set"

        if isinstance(value, (set, frozenset)):
            context["cty.collection_size"] = len(value)
            context["cty.set_type"] = type(value).__name__

        if original_exception:
            context["CTY.NESTED_ERROR"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Set"),
            path,
            **kwargs,
        )
    def xǁCtySetValidationErrorǁ__init____mutmut_23(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add set-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "set"

        if isinstance(value, (set, frozenset)):
            context["cty.collection_size"] = len(value)
            context["cty.set_type"] = type(value).__name__

        if original_exception:
            context["cty.nested_error"] = type(None).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Set"),
            path,
            **kwargs,
        )
    def xǁCtySetValidationErrorǁ__init____mutmut_24(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add set-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "set"

        if isinstance(value, (set, frozenset)):
            context["cty.collection_size"] = len(value)
            context["cty.set_type"] = type(value).__name__

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            None,
            value,
            _get_type_name_from_original(original_exception, "Set"),
            path,
            **kwargs,
        )
    def xǁCtySetValidationErrorǁ__init____mutmut_25(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add set-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "set"

        if isinstance(value, (set, frozenset)):
            context["cty.collection_size"] = len(value)
            context["cty.set_type"] = type(value).__name__

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            None,
            _get_type_name_from_original(original_exception, "Set"),
            path,
            **kwargs,
        )
    def xǁCtySetValidationErrorǁ__init____mutmut_26(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add set-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "set"

        if isinstance(value, (set, frozenset)):
            context["cty.collection_size"] = len(value)
            context["cty.set_type"] = type(value).__name__

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            None,
            path,
            **kwargs,
        )
    def xǁCtySetValidationErrorǁ__init____mutmut_27(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add set-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "set"

        if isinstance(value, (set, frozenset)):
            context["cty.collection_size"] = len(value)
            context["cty.set_type"] = type(value).__name__

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Set"),
            None,
            **kwargs,
        )
    def xǁCtySetValidationErrorǁ__init____mutmut_28(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add set-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "set"

        if isinstance(value, (set, frozenset)):
            context["cty.collection_size"] = len(value)
            context["cty.set_type"] = type(value).__name__

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            value,
            _get_type_name_from_original(original_exception, "Set"),
            path,
            **kwargs,
        )
    def xǁCtySetValidationErrorǁ__init____mutmut_29(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add set-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "set"

        if isinstance(value, (set, frozenset)):
            context["cty.collection_size"] = len(value)
            context["cty.set_type"] = type(value).__name__

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            _get_type_name_from_original(original_exception, "Set"),
            path,
            **kwargs,
        )
    def xǁCtySetValidationErrorǁ__init____mutmut_30(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add set-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "set"

        if isinstance(value, (set, frozenset)):
            context["cty.collection_size"] = len(value)
            context["cty.set_type"] = type(value).__name__

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            path,
            **kwargs,
        )
    def xǁCtySetValidationErrorǁ__init____mutmut_31(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add set-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "set"

        if isinstance(value, (set, frozenset)):
            context["cty.collection_size"] = len(value)
            context["cty.set_type"] = type(value).__name__

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Set"),
            **kwargs,
        )
    def xǁCtySetValidationErrorǁ__init____mutmut_32(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add set-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "set"

        if isinstance(value, (set, frozenset)):
            context["cty.collection_size"] = len(value)
            context["cty.set_type"] = type(value).__name__

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Set"),
            path,
            )
    def xǁCtySetValidationErrorǁ__init____mutmut_33(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add set-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "set"

        if isinstance(value, (set, frozenset)):
            context["cty.collection_size"] = len(value)
            context["cty.set_type"] = type(value).__name__

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(None, "Set"),
            path,
            **kwargs,
        )
    def xǁCtySetValidationErrorǁ__init____mutmut_34(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add set-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "set"

        if isinstance(value, (set, frozenset)):
            context["cty.collection_size"] = len(value)
            context["cty.set_type"] = type(value).__name__

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, None),
            path,
            **kwargs,
        )
    def xǁCtySetValidationErrorǁ__init____mutmut_35(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add set-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "set"

        if isinstance(value, (set, frozenset)):
            context["cty.collection_size"] = len(value)
            context["cty.set_type"] = type(value).__name__

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original("Set"),
            path,
            **kwargs,
        )
    def xǁCtySetValidationErrorǁ__init____mutmut_36(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add set-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "set"

        if isinstance(value, (set, frozenset)):
            context["cty.collection_size"] = len(value)
            context["cty.set_type"] = type(value).__name__

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, ),
            path,
            **kwargs,
        )
    def xǁCtySetValidationErrorǁ__init____mutmut_37(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add set-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "set"

        if isinstance(value, (set, frozenset)):
            context["cty.collection_size"] = len(value)
            context["cty.set_type"] = type(value).__name__

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "XXSetXX"),
            path,
            **kwargs,
        )
    def xǁCtySetValidationErrorǁ__init____mutmut_38(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add set-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "set"

        if isinstance(value, (set, frozenset)):
            context["cty.collection_size"] = len(value)
            context["cty.set_type"] = type(value).__name__

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "set"),
            path,
            **kwargs,
        )
    def xǁCtySetValidationErrorǁ__init____mutmut_39(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add set-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "set"

        if isinstance(value, (set, frozenset)):
            context["cty.collection_size"] = len(value)
            context["cty.set_type"] = type(value).__name__

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "SET"),
            path,
            **kwargs,
        )
    
    xǁCtySetValidationErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCtySetValidationErrorǁ__init____mutmut_1': xǁCtySetValidationErrorǁ__init____mutmut_1, 
        'xǁCtySetValidationErrorǁ__init____mutmut_2': xǁCtySetValidationErrorǁ__init____mutmut_2, 
        'xǁCtySetValidationErrorǁ__init____mutmut_3': xǁCtySetValidationErrorǁ__init____mutmut_3, 
        'xǁCtySetValidationErrorǁ__init____mutmut_4': xǁCtySetValidationErrorǁ__init____mutmut_4, 
        'xǁCtySetValidationErrorǁ__init____mutmut_5': xǁCtySetValidationErrorǁ__init____mutmut_5, 
        'xǁCtySetValidationErrorǁ__init____mutmut_6': xǁCtySetValidationErrorǁ__init____mutmut_6, 
        'xǁCtySetValidationErrorǁ__init____mutmut_7': xǁCtySetValidationErrorǁ__init____mutmut_7, 
        'xǁCtySetValidationErrorǁ__init____mutmut_8': xǁCtySetValidationErrorǁ__init____mutmut_8, 
        'xǁCtySetValidationErrorǁ__init____mutmut_9': xǁCtySetValidationErrorǁ__init____mutmut_9, 
        'xǁCtySetValidationErrorǁ__init____mutmut_10': xǁCtySetValidationErrorǁ__init____mutmut_10, 
        'xǁCtySetValidationErrorǁ__init____mutmut_11': xǁCtySetValidationErrorǁ__init____mutmut_11, 
        'xǁCtySetValidationErrorǁ__init____mutmut_12': xǁCtySetValidationErrorǁ__init____mutmut_12, 
        'xǁCtySetValidationErrorǁ__init____mutmut_13': xǁCtySetValidationErrorǁ__init____mutmut_13, 
        'xǁCtySetValidationErrorǁ__init____mutmut_14': xǁCtySetValidationErrorǁ__init____mutmut_14, 
        'xǁCtySetValidationErrorǁ__init____mutmut_15': xǁCtySetValidationErrorǁ__init____mutmut_15, 
        'xǁCtySetValidationErrorǁ__init____mutmut_16': xǁCtySetValidationErrorǁ__init____mutmut_16, 
        'xǁCtySetValidationErrorǁ__init____mutmut_17': xǁCtySetValidationErrorǁ__init____mutmut_17, 
        'xǁCtySetValidationErrorǁ__init____mutmut_18': xǁCtySetValidationErrorǁ__init____mutmut_18, 
        'xǁCtySetValidationErrorǁ__init____mutmut_19': xǁCtySetValidationErrorǁ__init____mutmut_19, 
        'xǁCtySetValidationErrorǁ__init____mutmut_20': xǁCtySetValidationErrorǁ__init____mutmut_20, 
        'xǁCtySetValidationErrorǁ__init____mutmut_21': xǁCtySetValidationErrorǁ__init____mutmut_21, 
        'xǁCtySetValidationErrorǁ__init____mutmut_22': xǁCtySetValidationErrorǁ__init____mutmut_22, 
        'xǁCtySetValidationErrorǁ__init____mutmut_23': xǁCtySetValidationErrorǁ__init____mutmut_23, 
        'xǁCtySetValidationErrorǁ__init____mutmut_24': xǁCtySetValidationErrorǁ__init____mutmut_24, 
        'xǁCtySetValidationErrorǁ__init____mutmut_25': xǁCtySetValidationErrorǁ__init____mutmut_25, 
        'xǁCtySetValidationErrorǁ__init____mutmut_26': xǁCtySetValidationErrorǁ__init____mutmut_26, 
        'xǁCtySetValidationErrorǁ__init____mutmut_27': xǁCtySetValidationErrorǁ__init____mutmut_27, 
        'xǁCtySetValidationErrorǁ__init____mutmut_28': xǁCtySetValidationErrorǁ__init____mutmut_28, 
        'xǁCtySetValidationErrorǁ__init____mutmut_29': xǁCtySetValidationErrorǁ__init____mutmut_29, 
        'xǁCtySetValidationErrorǁ__init____mutmut_30': xǁCtySetValidationErrorǁ__init____mutmut_30, 
        'xǁCtySetValidationErrorǁ__init____mutmut_31': xǁCtySetValidationErrorǁ__init____mutmut_31, 
        'xǁCtySetValidationErrorǁ__init____mutmut_32': xǁCtySetValidationErrorǁ__init____mutmut_32, 
        'xǁCtySetValidationErrorǁ__init____mutmut_33': xǁCtySetValidationErrorǁ__init____mutmut_33, 
        'xǁCtySetValidationErrorǁ__init____mutmut_34': xǁCtySetValidationErrorǁ__init____mutmut_34, 
        'xǁCtySetValidationErrorǁ__init____mutmut_35': xǁCtySetValidationErrorǁ__init____mutmut_35, 
        'xǁCtySetValidationErrorǁ__init____mutmut_36': xǁCtySetValidationErrorǁ__init____mutmut_36, 
        'xǁCtySetValidationErrorǁ__init____mutmut_37': xǁCtySetValidationErrorǁ__init____mutmut_37, 
        'xǁCtySetValidationErrorǁ__init____mutmut_38': xǁCtySetValidationErrorǁ__init____mutmut_38, 
        'xǁCtySetValidationErrorǁ__init____mutmut_39': xǁCtySetValidationErrorǁ__init____mutmut_39
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCtySetValidationErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁCtySetValidationErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁCtySetValidationErrorǁ__init____mutmut_orig)
    xǁCtySetValidationErrorǁ__init____mutmut_orig.__name__ = 'xǁCtySetValidationErrorǁ__init__'


class CtyTupleValidationError(CtyCollectionValidationError):
    def xǁCtyTupleValidationErrorǁ__init____mutmut_orig(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add tuple-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "tuple"

        if isinstance(value, tuple):
            context["cty.collection_length"] = len(value)
            context["cty.tuple_element_types"] = [type(item).__name__ for item in value]

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Tuple"),
            path,
            **kwargs,
        )
    def xǁCtyTupleValidationErrorǁ__init____mutmut_1(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add tuple-specific context
        context = None
        context["cty.collection_type"] = "tuple"

        if isinstance(value, tuple):
            context["cty.collection_length"] = len(value)
            context["cty.tuple_element_types"] = [type(item).__name__ for item in value]

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Tuple"),
            path,
            **kwargs,
        )
    def xǁCtyTupleValidationErrorǁ__init____mutmut_2(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add tuple-specific context
        context = kwargs.setdefault(None, {})
        context["cty.collection_type"] = "tuple"

        if isinstance(value, tuple):
            context["cty.collection_length"] = len(value)
            context["cty.tuple_element_types"] = [type(item).__name__ for item in value]

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Tuple"),
            path,
            **kwargs,
        )
    def xǁCtyTupleValidationErrorǁ__init____mutmut_3(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add tuple-specific context
        context = kwargs.setdefault("context", None)
        context["cty.collection_type"] = "tuple"

        if isinstance(value, tuple):
            context["cty.collection_length"] = len(value)
            context["cty.tuple_element_types"] = [type(item).__name__ for item in value]

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Tuple"),
            path,
            **kwargs,
        )
    def xǁCtyTupleValidationErrorǁ__init____mutmut_4(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add tuple-specific context
        context = kwargs.setdefault({})
        context["cty.collection_type"] = "tuple"

        if isinstance(value, tuple):
            context["cty.collection_length"] = len(value)
            context["cty.tuple_element_types"] = [type(item).__name__ for item in value]

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Tuple"),
            path,
            **kwargs,
        )
    def xǁCtyTupleValidationErrorǁ__init____mutmut_5(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add tuple-specific context
        context = kwargs.setdefault("context", )
        context["cty.collection_type"] = "tuple"

        if isinstance(value, tuple):
            context["cty.collection_length"] = len(value)
            context["cty.tuple_element_types"] = [type(item).__name__ for item in value]

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Tuple"),
            path,
            **kwargs,
        )
    def xǁCtyTupleValidationErrorǁ__init____mutmut_6(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add tuple-specific context
        context = kwargs.setdefault("XXcontextXX", {})
        context["cty.collection_type"] = "tuple"

        if isinstance(value, tuple):
            context["cty.collection_length"] = len(value)
            context["cty.tuple_element_types"] = [type(item).__name__ for item in value]

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Tuple"),
            path,
            **kwargs,
        )
    def xǁCtyTupleValidationErrorǁ__init____mutmut_7(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add tuple-specific context
        context = kwargs.setdefault("CONTEXT", {})
        context["cty.collection_type"] = "tuple"

        if isinstance(value, tuple):
            context["cty.collection_length"] = len(value)
            context["cty.tuple_element_types"] = [type(item).__name__ for item in value]

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Tuple"),
            path,
            **kwargs,
        )
    def xǁCtyTupleValidationErrorǁ__init____mutmut_8(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add tuple-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = None

        if isinstance(value, tuple):
            context["cty.collection_length"] = len(value)
            context["cty.tuple_element_types"] = [type(item).__name__ for item in value]

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Tuple"),
            path,
            **kwargs,
        )
    def xǁCtyTupleValidationErrorǁ__init____mutmut_9(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add tuple-specific context
        context = kwargs.setdefault("context", {})
        context["XXcty.collection_typeXX"] = "tuple"

        if isinstance(value, tuple):
            context["cty.collection_length"] = len(value)
            context["cty.tuple_element_types"] = [type(item).__name__ for item in value]

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Tuple"),
            path,
            **kwargs,
        )
    def xǁCtyTupleValidationErrorǁ__init____mutmut_10(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add tuple-specific context
        context = kwargs.setdefault("context", {})
        context["CTY.COLLECTION_TYPE"] = "tuple"

        if isinstance(value, tuple):
            context["cty.collection_length"] = len(value)
            context["cty.tuple_element_types"] = [type(item).__name__ for item in value]

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Tuple"),
            path,
            **kwargs,
        )
    def xǁCtyTupleValidationErrorǁ__init____mutmut_11(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add tuple-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "XXtupleXX"

        if isinstance(value, tuple):
            context["cty.collection_length"] = len(value)
            context["cty.tuple_element_types"] = [type(item).__name__ for item in value]

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Tuple"),
            path,
            **kwargs,
        )
    def xǁCtyTupleValidationErrorǁ__init____mutmut_12(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add tuple-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "TUPLE"

        if isinstance(value, tuple):
            context["cty.collection_length"] = len(value)
            context["cty.tuple_element_types"] = [type(item).__name__ for item in value]

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Tuple"),
            path,
            **kwargs,
        )
    def xǁCtyTupleValidationErrorǁ__init____mutmut_13(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add tuple-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "tuple"

        if isinstance(value, tuple):
            context["cty.collection_length"] = None
            context["cty.tuple_element_types"] = [type(item).__name__ for item in value]

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Tuple"),
            path,
            **kwargs,
        )
    def xǁCtyTupleValidationErrorǁ__init____mutmut_14(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add tuple-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "tuple"

        if isinstance(value, tuple):
            context["XXcty.collection_lengthXX"] = len(value)
            context["cty.tuple_element_types"] = [type(item).__name__ for item in value]

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Tuple"),
            path,
            **kwargs,
        )
    def xǁCtyTupleValidationErrorǁ__init____mutmut_15(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add tuple-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "tuple"

        if isinstance(value, tuple):
            context["CTY.COLLECTION_LENGTH"] = len(value)
            context["cty.tuple_element_types"] = [type(item).__name__ for item in value]

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Tuple"),
            path,
            **kwargs,
        )
    def xǁCtyTupleValidationErrorǁ__init____mutmut_16(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add tuple-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "tuple"

        if isinstance(value, tuple):
            context["cty.collection_length"] = len(value)
            context["cty.tuple_element_types"] = None

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Tuple"),
            path,
            **kwargs,
        )
    def xǁCtyTupleValidationErrorǁ__init____mutmut_17(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add tuple-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "tuple"

        if isinstance(value, tuple):
            context["cty.collection_length"] = len(value)
            context["XXcty.tuple_element_typesXX"] = [type(item).__name__ for item in value]

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Tuple"),
            path,
            **kwargs,
        )
    def xǁCtyTupleValidationErrorǁ__init____mutmut_18(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add tuple-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "tuple"

        if isinstance(value, tuple):
            context["cty.collection_length"] = len(value)
            context["CTY.TUPLE_ELEMENT_TYPES"] = [type(item).__name__ for item in value]

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Tuple"),
            path,
            **kwargs,
        )
    def xǁCtyTupleValidationErrorǁ__init____mutmut_19(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add tuple-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "tuple"

        if isinstance(value, tuple):
            context["cty.collection_length"] = len(value)
            context["cty.tuple_element_types"] = [type(None).__name__ for item in value]

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Tuple"),
            path,
            **kwargs,
        )
    def xǁCtyTupleValidationErrorǁ__init____mutmut_20(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add tuple-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "tuple"

        if isinstance(value, tuple):
            context["cty.collection_length"] = len(value)
            context["cty.tuple_element_types"] = [type(item).__name__ for item in value]

        if original_exception:
            context["cty.nested_error"] = None

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Tuple"),
            path,
            **kwargs,
        )
    def xǁCtyTupleValidationErrorǁ__init____mutmut_21(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add tuple-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "tuple"

        if isinstance(value, tuple):
            context["cty.collection_length"] = len(value)
            context["cty.tuple_element_types"] = [type(item).__name__ for item in value]

        if original_exception:
            context["XXcty.nested_errorXX"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Tuple"),
            path,
            **kwargs,
        )
    def xǁCtyTupleValidationErrorǁ__init____mutmut_22(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add tuple-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "tuple"

        if isinstance(value, tuple):
            context["cty.collection_length"] = len(value)
            context["cty.tuple_element_types"] = [type(item).__name__ for item in value]

        if original_exception:
            context["CTY.NESTED_ERROR"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Tuple"),
            path,
            **kwargs,
        )
    def xǁCtyTupleValidationErrorǁ__init____mutmut_23(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add tuple-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "tuple"

        if isinstance(value, tuple):
            context["cty.collection_length"] = len(value)
            context["cty.tuple_element_types"] = [type(item).__name__ for item in value]

        if original_exception:
            context["cty.nested_error"] = type(None).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Tuple"),
            path,
            **kwargs,
        )
    def xǁCtyTupleValidationErrorǁ__init____mutmut_24(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add tuple-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "tuple"

        if isinstance(value, tuple):
            context["cty.collection_length"] = len(value)
            context["cty.tuple_element_types"] = [type(item).__name__ for item in value]

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            None,
            value,
            _get_type_name_from_original(original_exception, "Tuple"),
            path,
            **kwargs,
        )
    def xǁCtyTupleValidationErrorǁ__init____mutmut_25(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add tuple-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "tuple"

        if isinstance(value, tuple):
            context["cty.collection_length"] = len(value)
            context["cty.tuple_element_types"] = [type(item).__name__ for item in value]

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            None,
            _get_type_name_from_original(original_exception, "Tuple"),
            path,
            **kwargs,
        )
    def xǁCtyTupleValidationErrorǁ__init____mutmut_26(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add tuple-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "tuple"

        if isinstance(value, tuple):
            context["cty.collection_length"] = len(value)
            context["cty.tuple_element_types"] = [type(item).__name__ for item in value]

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            None,
            path,
            **kwargs,
        )
    def xǁCtyTupleValidationErrorǁ__init____mutmut_27(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add tuple-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "tuple"

        if isinstance(value, tuple):
            context["cty.collection_length"] = len(value)
            context["cty.tuple_element_types"] = [type(item).__name__ for item in value]

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Tuple"),
            None,
            **kwargs,
        )
    def xǁCtyTupleValidationErrorǁ__init____mutmut_28(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add tuple-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "tuple"

        if isinstance(value, tuple):
            context["cty.collection_length"] = len(value)
            context["cty.tuple_element_types"] = [type(item).__name__ for item in value]

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            value,
            _get_type_name_from_original(original_exception, "Tuple"),
            path,
            **kwargs,
        )
    def xǁCtyTupleValidationErrorǁ__init____mutmut_29(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add tuple-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "tuple"

        if isinstance(value, tuple):
            context["cty.collection_length"] = len(value)
            context["cty.tuple_element_types"] = [type(item).__name__ for item in value]

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            _get_type_name_from_original(original_exception, "Tuple"),
            path,
            **kwargs,
        )
    def xǁCtyTupleValidationErrorǁ__init____mutmut_30(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add tuple-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "tuple"

        if isinstance(value, tuple):
            context["cty.collection_length"] = len(value)
            context["cty.tuple_element_types"] = [type(item).__name__ for item in value]

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            path,
            **kwargs,
        )
    def xǁCtyTupleValidationErrorǁ__init____mutmut_31(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add tuple-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "tuple"

        if isinstance(value, tuple):
            context["cty.collection_length"] = len(value)
            context["cty.tuple_element_types"] = [type(item).__name__ for item in value]

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Tuple"),
            **kwargs,
        )
    def xǁCtyTupleValidationErrorǁ__init____mutmut_32(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add tuple-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "tuple"

        if isinstance(value, tuple):
            context["cty.collection_length"] = len(value)
            context["cty.tuple_element_types"] = [type(item).__name__ for item in value]

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Tuple"),
            path,
            )
    def xǁCtyTupleValidationErrorǁ__init____mutmut_33(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add tuple-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "tuple"

        if isinstance(value, tuple):
            context["cty.collection_length"] = len(value)
            context["cty.tuple_element_types"] = [type(item).__name__ for item in value]

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(None, "Tuple"),
            path,
            **kwargs,
        )
    def xǁCtyTupleValidationErrorǁ__init____mutmut_34(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add tuple-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "tuple"

        if isinstance(value, tuple):
            context["cty.collection_length"] = len(value)
            context["cty.tuple_element_types"] = [type(item).__name__ for item in value]

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, None),
            path,
            **kwargs,
        )
    def xǁCtyTupleValidationErrorǁ__init____mutmut_35(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add tuple-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "tuple"

        if isinstance(value, tuple):
            context["cty.collection_length"] = len(value)
            context["cty.tuple_element_types"] = [type(item).__name__ for item in value]

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original("Tuple"),
            path,
            **kwargs,
        )
    def xǁCtyTupleValidationErrorǁ__init____mutmut_36(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add tuple-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "tuple"

        if isinstance(value, tuple):
            context["cty.collection_length"] = len(value)
            context["cty.tuple_element_types"] = [type(item).__name__ for item in value]

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, ),
            path,
            **kwargs,
        )
    def xǁCtyTupleValidationErrorǁ__init____mutmut_37(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add tuple-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "tuple"

        if isinstance(value, tuple):
            context["cty.collection_length"] = len(value)
            context["cty.tuple_element_types"] = [type(item).__name__ for item in value]

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "XXTupleXX"),
            path,
            **kwargs,
        )
    def xǁCtyTupleValidationErrorǁ__init____mutmut_38(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add tuple-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "tuple"

        if isinstance(value, tuple):
            context["cty.collection_length"] = len(value)
            context["cty.tuple_element_types"] = [type(item).__name__ for item in value]

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "tuple"),
            path,
            **kwargs,
        )
    def xǁCtyTupleValidationErrorǁ__init____mutmut_39(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add tuple-specific context
        context = kwargs.setdefault("context", {})
        context["cty.collection_type"] = "tuple"

        if isinstance(value, tuple):
            context["cty.collection_length"] = len(value)
            context["cty.tuple_element_types"] = [type(item).__name__ for item in value]

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "TUPLE"),
            path,
            **kwargs,
        )
    
    xǁCtyTupleValidationErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCtyTupleValidationErrorǁ__init____mutmut_1': xǁCtyTupleValidationErrorǁ__init____mutmut_1, 
        'xǁCtyTupleValidationErrorǁ__init____mutmut_2': xǁCtyTupleValidationErrorǁ__init____mutmut_2, 
        'xǁCtyTupleValidationErrorǁ__init____mutmut_3': xǁCtyTupleValidationErrorǁ__init____mutmut_3, 
        'xǁCtyTupleValidationErrorǁ__init____mutmut_4': xǁCtyTupleValidationErrorǁ__init____mutmut_4, 
        'xǁCtyTupleValidationErrorǁ__init____mutmut_5': xǁCtyTupleValidationErrorǁ__init____mutmut_5, 
        'xǁCtyTupleValidationErrorǁ__init____mutmut_6': xǁCtyTupleValidationErrorǁ__init____mutmut_6, 
        'xǁCtyTupleValidationErrorǁ__init____mutmut_7': xǁCtyTupleValidationErrorǁ__init____mutmut_7, 
        'xǁCtyTupleValidationErrorǁ__init____mutmut_8': xǁCtyTupleValidationErrorǁ__init____mutmut_8, 
        'xǁCtyTupleValidationErrorǁ__init____mutmut_9': xǁCtyTupleValidationErrorǁ__init____mutmut_9, 
        'xǁCtyTupleValidationErrorǁ__init____mutmut_10': xǁCtyTupleValidationErrorǁ__init____mutmut_10, 
        'xǁCtyTupleValidationErrorǁ__init____mutmut_11': xǁCtyTupleValidationErrorǁ__init____mutmut_11, 
        'xǁCtyTupleValidationErrorǁ__init____mutmut_12': xǁCtyTupleValidationErrorǁ__init____mutmut_12, 
        'xǁCtyTupleValidationErrorǁ__init____mutmut_13': xǁCtyTupleValidationErrorǁ__init____mutmut_13, 
        'xǁCtyTupleValidationErrorǁ__init____mutmut_14': xǁCtyTupleValidationErrorǁ__init____mutmut_14, 
        'xǁCtyTupleValidationErrorǁ__init____mutmut_15': xǁCtyTupleValidationErrorǁ__init____mutmut_15, 
        'xǁCtyTupleValidationErrorǁ__init____mutmut_16': xǁCtyTupleValidationErrorǁ__init____mutmut_16, 
        'xǁCtyTupleValidationErrorǁ__init____mutmut_17': xǁCtyTupleValidationErrorǁ__init____mutmut_17, 
        'xǁCtyTupleValidationErrorǁ__init____mutmut_18': xǁCtyTupleValidationErrorǁ__init____mutmut_18, 
        'xǁCtyTupleValidationErrorǁ__init____mutmut_19': xǁCtyTupleValidationErrorǁ__init____mutmut_19, 
        'xǁCtyTupleValidationErrorǁ__init____mutmut_20': xǁCtyTupleValidationErrorǁ__init____mutmut_20, 
        'xǁCtyTupleValidationErrorǁ__init____mutmut_21': xǁCtyTupleValidationErrorǁ__init____mutmut_21, 
        'xǁCtyTupleValidationErrorǁ__init____mutmut_22': xǁCtyTupleValidationErrorǁ__init____mutmut_22, 
        'xǁCtyTupleValidationErrorǁ__init____mutmut_23': xǁCtyTupleValidationErrorǁ__init____mutmut_23, 
        'xǁCtyTupleValidationErrorǁ__init____mutmut_24': xǁCtyTupleValidationErrorǁ__init____mutmut_24, 
        'xǁCtyTupleValidationErrorǁ__init____mutmut_25': xǁCtyTupleValidationErrorǁ__init____mutmut_25, 
        'xǁCtyTupleValidationErrorǁ__init____mutmut_26': xǁCtyTupleValidationErrorǁ__init____mutmut_26, 
        'xǁCtyTupleValidationErrorǁ__init____mutmut_27': xǁCtyTupleValidationErrorǁ__init____mutmut_27, 
        'xǁCtyTupleValidationErrorǁ__init____mutmut_28': xǁCtyTupleValidationErrorǁ__init____mutmut_28, 
        'xǁCtyTupleValidationErrorǁ__init____mutmut_29': xǁCtyTupleValidationErrorǁ__init____mutmut_29, 
        'xǁCtyTupleValidationErrorǁ__init____mutmut_30': xǁCtyTupleValidationErrorǁ__init____mutmut_30, 
        'xǁCtyTupleValidationErrorǁ__init____mutmut_31': xǁCtyTupleValidationErrorǁ__init____mutmut_31, 
        'xǁCtyTupleValidationErrorǁ__init____mutmut_32': xǁCtyTupleValidationErrorǁ__init____mutmut_32, 
        'xǁCtyTupleValidationErrorǁ__init____mutmut_33': xǁCtyTupleValidationErrorǁ__init____mutmut_33, 
        'xǁCtyTupleValidationErrorǁ__init____mutmut_34': xǁCtyTupleValidationErrorǁ__init____mutmut_34, 
        'xǁCtyTupleValidationErrorǁ__init____mutmut_35': xǁCtyTupleValidationErrorǁ__init____mutmut_35, 
        'xǁCtyTupleValidationErrorǁ__init____mutmut_36': xǁCtyTupleValidationErrorǁ__init____mutmut_36, 
        'xǁCtyTupleValidationErrorǁ__init____mutmut_37': xǁCtyTupleValidationErrorǁ__init____mutmut_37, 
        'xǁCtyTupleValidationErrorǁ__init____mutmut_38': xǁCtyTupleValidationErrorǁ__init____mutmut_38, 
        'xǁCtyTupleValidationErrorǁ__init____mutmut_39': xǁCtyTupleValidationErrorǁ__init____mutmut_39
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCtyTupleValidationErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁCtyTupleValidationErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁCtyTupleValidationErrorǁ__init____mutmut_orig)
    xǁCtyTupleValidationErrorǁ__init____mutmut_orig.__name__ = 'xǁCtyTupleValidationErrorǁ__init__'


# --- Structural and Type Definition Errors ---
class CtyAttributeValidationError(CtyValidationError):
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_orig(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("context", {})
        context["cty.validation_type"] = "object_attribute"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(first_step, "attribute_name"):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Object"),
            path,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_1(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = None
        context["cty.validation_type"] = "object_attribute"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(first_step, "attribute_name"):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Object"),
            path,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_2(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault(None, {})
        context["cty.validation_type"] = "object_attribute"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(first_step, "attribute_name"):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Object"),
            path,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_3(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("context", None)
        context["cty.validation_type"] = "object_attribute"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(first_step, "attribute_name"):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Object"),
            path,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_4(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault({})
        context["cty.validation_type"] = "object_attribute"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(first_step, "attribute_name"):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Object"),
            path,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_5(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("context", )
        context["cty.validation_type"] = "object_attribute"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(first_step, "attribute_name"):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Object"),
            path,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_6(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("XXcontextXX", {})
        context["cty.validation_type"] = "object_attribute"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(first_step, "attribute_name"):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Object"),
            path,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_7(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("CONTEXT", {})
        context["cty.validation_type"] = "object_attribute"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(first_step, "attribute_name"):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Object"),
            path,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_8(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("context", {})
        context["cty.validation_type"] = None

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(first_step, "attribute_name"):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Object"),
            path,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_9(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("context", {})
        context["XXcty.validation_typeXX"] = "object_attribute"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(first_step, "attribute_name"):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Object"),
            path,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_10(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("context", {})
        context["CTY.VALIDATION_TYPE"] = "object_attribute"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(first_step, "attribute_name"):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Object"),
            path,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_11(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("context", {})
        context["cty.validation_type"] = "XXobject_attributeXX"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(first_step, "attribute_name"):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Object"),
            path,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_12(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("context", {})
        context["cty.validation_type"] = "OBJECT_ATTRIBUTE"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(first_step, "attribute_name"):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Object"),
            path,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_13(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("context", {})
        context["cty.validation_type"] = "object_attribute"

        if path or path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(first_step, "attribute_name"):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Object"),
            path,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_14(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("context", {})
        context["cty.validation_type"] = "object_attribute"

        if path and path.steps:
            # Extract attribute name from path
            first_step = None
            if hasattr(first_step, "attribute_name"):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Object"),
            path,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_15(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("context", {})
        context["cty.validation_type"] = "object_attribute"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[1]
            if hasattr(first_step, "attribute_name"):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Object"),
            path,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_16(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("context", {})
        context["cty.validation_type"] = "object_attribute"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(None, "attribute_name"):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Object"),
            path,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_17(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("context", {})
        context["cty.validation_type"] = "object_attribute"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(first_step, None):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Object"),
            path,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_18(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("context", {})
        context["cty.validation_type"] = "object_attribute"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr("attribute_name"):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Object"),
            path,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_19(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("context", {})
        context["cty.validation_type"] = "object_attribute"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(first_step, ):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Object"),
            path,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_20(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("context", {})
        context["cty.validation_type"] = "object_attribute"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(first_step, "XXattribute_nameXX"):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Object"),
            path,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_21(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("context", {})
        context["cty.validation_type"] = "object_attribute"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(first_step, "ATTRIBUTE_NAME"):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Object"),
            path,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_22(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("context", {})
        context["cty.validation_type"] = "object_attribute"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(first_step, "attribute_name"):
                context["cty.attribute_name"] = None

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Object"),
            path,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_23(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("context", {})
        context["cty.validation_type"] = "object_attribute"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(first_step, "attribute_name"):
                context["XXcty.attribute_nameXX"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Object"),
            path,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_24(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("context", {})
        context["cty.validation_type"] = "object_attribute"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(first_step, "attribute_name"):
                context["CTY.ATTRIBUTE_NAME"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Object"),
            path,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_25(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("context", {})
        context["cty.validation_type"] = "object_attribute"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(first_step, "attribute_name"):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = None

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Object"),
            path,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_26(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("context", {})
        context["cty.validation_type"] = "object_attribute"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(first_step, "attribute_name"):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["XXcty.nested_errorXX"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Object"),
            path,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_27(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("context", {})
        context["cty.validation_type"] = "object_attribute"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(first_step, "attribute_name"):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["CTY.NESTED_ERROR"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Object"),
            path,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_28(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("context", {})
        context["cty.validation_type"] = "object_attribute"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(first_step, "attribute_name"):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = type(None).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Object"),
            path,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_29(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("context", {})
        context["cty.validation_type"] = "object_attribute"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(first_step, "attribute_name"):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            None,
            value,
            _get_type_name_from_original(original_exception, "Object"),
            path,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_30(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("context", {})
        context["cty.validation_type"] = "object_attribute"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(first_step, "attribute_name"):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            None,
            _get_type_name_from_original(original_exception, "Object"),
            path,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_31(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("context", {})
        context["cty.validation_type"] = "object_attribute"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(first_step, "attribute_name"):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            None,
            path,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_32(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("context", {})
        context["cty.validation_type"] = "object_attribute"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(first_step, "attribute_name"):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Object"),
            None,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_33(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("context", {})
        context["cty.validation_type"] = "object_attribute"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(first_step, "attribute_name"):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            value,
            _get_type_name_from_original(original_exception, "Object"),
            path,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_34(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("context", {})
        context["cty.validation_type"] = "object_attribute"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(first_step, "attribute_name"):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            _get_type_name_from_original(original_exception, "Object"),
            path,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_35(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("context", {})
        context["cty.validation_type"] = "object_attribute"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(first_step, "attribute_name"):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            path,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_36(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("context", {})
        context["cty.validation_type"] = "object_attribute"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(first_step, "attribute_name"):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Object"),
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_37(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("context", {})
        context["cty.validation_type"] = "object_attribute"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(first_step, "attribute_name"):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "Object"),
            path,
            )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_38(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("context", {})
        context["cty.validation_type"] = "object_attribute"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(first_step, "attribute_name"):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(None, "Object"),
            path,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_39(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("context", {})
        context["cty.validation_type"] = "object_attribute"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(first_step, "attribute_name"):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, None),
            path,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_40(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("context", {})
        context["cty.validation_type"] = "object_attribute"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(first_step, "attribute_name"):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original("Object"),
            path,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_41(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("context", {})
        context["cty.validation_type"] = "object_attribute"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(first_step, "attribute_name"):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, ),
            path,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_42(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("context", {})
        context["cty.validation_type"] = "object_attribute"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(first_step, "attribute_name"):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "XXObjectXX"),
            path,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_43(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("context", {})
        context["cty.validation_type"] = "object_attribute"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(first_step, "attribute_name"):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "object"),
            path,
            **kwargs,
        )
    def xǁCtyAttributeValidationErrorǁ__init____mutmut_44(
        self,
        message: str,
        value: object = None,
        path: CtyPath | None = None,
        *,
        original_exception: CtyValidationError | None = None,
        **kwargs: Any,
    ) -> None:
        # Add object-specific context
        context = kwargs.setdefault("context", {})
        context["cty.validation_type"] = "object_attribute"

        if path and path.steps:
            # Extract attribute name from path
            first_step = path.steps[0]
            if hasattr(first_step, "attribute_name"):
                context["cty.attribute_name"] = first_step.attribute_name

        if original_exception:
            context["cty.nested_error"] = type(original_exception).__name__

        super().__init__(
            message,
            value,
            _get_type_name_from_original(original_exception, "OBJECT"),
            path,
            **kwargs,
        )
    
    xǁCtyAttributeValidationErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCtyAttributeValidationErrorǁ__init____mutmut_1': xǁCtyAttributeValidationErrorǁ__init____mutmut_1, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_2': xǁCtyAttributeValidationErrorǁ__init____mutmut_2, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_3': xǁCtyAttributeValidationErrorǁ__init____mutmut_3, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_4': xǁCtyAttributeValidationErrorǁ__init____mutmut_4, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_5': xǁCtyAttributeValidationErrorǁ__init____mutmut_5, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_6': xǁCtyAttributeValidationErrorǁ__init____mutmut_6, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_7': xǁCtyAttributeValidationErrorǁ__init____mutmut_7, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_8': xǁCtyAttributeValidationErrorǁ__init____mutmut_8, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_9': xǁCtyAttributeValidationErrorǁ__init____mutmut_9, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_10': xǁCtyAttributeValidationErrorǁ__init____mutmut_10, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_11': xǁCtyAttributeValidationErrorǁ__init____mutmut_11, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_12': xǁCtyAttributeValidationErrorǁ__init____mutmut_12, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_13': xǁCtyAttributeValidationErrorǁ__init____mutmut_13, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_14': xǁCtyAttributeValidationErrorǁ__init____mutmut_14, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_15': xǁCtyAttributeValidationErrorǁ__init____mutmut_15, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_16': xǁCtyAttributeValidationErrorǁ__init____mutmut_16, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_17': xǁCtyAttributeValidationErrorǁ__init____mutmut_17, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_18': xǁCtyAttributeValidationErrorǁ__init____mutmut_18, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_19': xǁCtyAttributeValidationErrorǁ__init____mutmut_19, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_20': xǁCtyAttributeValidationErrorǁ__init____mutmut_20, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_21': xǁCtyAttributeValidationErrorǁ__init____mutmut_21, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_22': xǁCtyAttributeValidationErrorǁ__init____mutmut_22, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_23': xǁCtyAttributeValidationErrorǁ__init____mutmut_23, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_24': xǁCtyAttributeValidationErrorǁ__init____mutmut_24, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_25': xǁCtyAttributeValidationErrorǁ__init____mutmut_25, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_26': xǁCtyAttributeValidationErrorǁ__init____mutmut_26, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_27': xǁCtyAttributeValidationErrorǁ__init____mutmut_27, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_28': xǁCtyAttributeValidationErrorǁ__init____mutmut_28, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_29': xǁCtyAttributeValidationErrorǁ__init____mutmut_29, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_30': xǁCtyAttributeValidationErrorǁ__init____mutmut_30, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_31': xǁCtyAttributeValidationErrorǁ__init____mutmut_31, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_32': xǁCtyAttributeValidationErrorǁ__init____mutmut_32, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_33': xǁCtyAttributeValidationErrorǁ__init____mutmut_33, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_34': xǁCtyAttributeValidationErrorǁ__init____mutmut_34, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_35': xǁCtyAttributeValidationErrorǁ__init____mutmut_35, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_36': xǁCtyAttributeValidationErrorǁ__init____mutmut_36, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_37': xǁCtyAttributeValidationErrorǁ__init____mutmut_37, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_38': xǁCtyAttributeValidationErrorǁ__init____mutmut_38, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_39': xǁCtyAttributeValidationErrorǁ__init____mutmut_39, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_40': xǁCtyAttributeValidationErrorǁ__init____mutmut_40, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_41': xǁCtyAttributeValidationErrorǁ__init____mutmut_41, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_42': xǁCtyAttributeValidationErrorǁ__init____mutmut_42, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_43': xǁCtyAttributeValidationErrorǁ__init____mutmut_43, 
        'xǁCtyAttributeValidationErrorǁ__init____mutmut_44': xǁCtyAttributeValidationErrorǁ__init____mutmut_44
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCtyAttributeValidationErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁCtyAttributeValidationErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁCtyAttributeValidationErrorǁ__init____mutmut_orig)
    xǁCtyAttributeValidationErrorǁ__init____mutmut_orig.__name__ = 'xǁCtyAttributeValidationErrorǁ__init__'


class CtyTypeValidationError(CtyValidationError):
    def xǁCtyTypeValidationErrorǁ__init____mutmut_orig(
        self,
        message: str,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add type definition context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "type_definition"
        context["cty.type_category"] = "meta"

        super().__init__(message, type_name=type_name or "TypeDefinition", path=path, **kwargs)
    def xǁCtyTypeValidationErrorǁ__init____mutmut_1(
        self,
        message: str,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add type definition context
        context = None
        context["cty.validation_stage"] = "type_definition"
        context["cty.type_category"] = "meta"

        super().__init__(message, type_name=type_name or "TypeDefinition", path=path, **kwargs)
    def xǁCtyTypeValidationErrorǁ__init____mutmut_2(
        self,
        message: str,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add type definition context
        context = kwargs.setdefault(None, {})
        context["cty.validation_stage"] = "type_definition"
        context["cty.type_category"] = "meta"

        super().__init__(message, type_name=type_name or "TypeDefinition", path=path, **kwargs)
    def xǁCtyTypeValidationErrorǁ__init____mutmut_3(
        self,
        message: str,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add type definition context
        context = kwargs.setdefault("context", None)
        context["cty.validation_stage"] = "type_definition"
        context["cty.type_category"] = "meta"

        super().__init__(message, type_name=type_name or "TypeDefinition", path=path, **kwargs)
    def xǁCtyTypeValidationErrorǁ__init____mutmut_4(
        self,
        message: str,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add type definition context
        context = kwargs.setdefault({})
        context["cty.validation_stage"] = "type_definition"
        context["cty.type_category"] = "meta"

        super().__init__(message, type_name=type_name or "TypeDefinition", path=path, **kwargs)
    def xǁCtyTypeValidationErrorǁ__init____mutmut_5(
        self,
        message: str,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add type definition context
        context = kwargs.setdefault("context", )
        context["cty.validation_stage"] = "type_definition"
        context["cty.type_category"] = "meta"

        super().__init__(message, type_name=type_name or "TypeDefinition", path=path, **kwargs)
    def xǁCtyTypeValidationErrorǁ__init____mutmut_6(
        self,
        message: str,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add type definition context
        context = kwargs.setdefault("XXcontextXX", {})
        context["cty.validation_stage"] = "type_definition"
        context["cty.type_category"] = "meta"

        super().__init__(message, type_name=type_name or "TypeDefinition", path=path, **kwargs)
    def xǁCtyTypeValidationErrorǁ__init____mutmut_7(
        self,
        message: str,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add type definition context
        context = kwargs.setdefault("CONTEXT", {})
        context["cty.validation_stage"] = "type_definition"
        context["cty.type_category"] = "meta"

        super().__init__(message, type_name=type_name or "TypeDefinition", path=path, **kwargs)
    def xǁCtyTypeValidationErrorǁ__init____mutmut_8(
        self,
        message: str,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add type definition context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = None
        context["cty.type_category"] = "meta"

        super().__init__(message, type_name=type_name or "TypeDefinition", path=path, **kwargs)
    def xǁCtyTypeValidationErrorǁ__init____mutmut_9(
        self,
        message: str,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add type definition context
        context = kwargs.setdefault("context", {})
        context["XXcty.validation_stageXX"] = "type_definition"
        context["cty.type_category"] = "meta"

        super().__init__(message, type_name=type_name or "TypeDefinition", path=path, **kwargs)
    def xǁCtyTypeValidationErrorǁ__init____mutmut_10(
        self,
        message: str,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add type definition context
        context = kwargs.setdefault("context", {})
        context["CTY.VALIDATION_STAGE"] = "type_definition"
        context["cty.type_category"] = "meta"

        super().__init__(message, type_name=type_name or "TypeDefinition", path=path, **kwargs)
    def xǁCtyTypeValidationErrorǁ__init____mutmut_11(
        self,
        message: str,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add type definition context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "XXtype_definitionXX"
        context["cty.type_category"] = "meta"

        super().__init__(message, type_name=type_name or "TypeDefinition", path=path, **kwargs)
    def xǁCtyTypeValidationErrorǁ__init____mutmut_12(
        self,
        message: str,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add type definition context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "TYPE_DEFINITION"
        context["cty.type_category"] = "meta"

        super().__init__(message, type_name=type_name or "TypeDefinition", path=path, **kwargs)
    def xǁCtyTypeValidationErrorǁ__init____mutmut_13(
        self,
        message: str,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add type definition context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "type_definition"
        context["cty.type_category"] = None

        super().__init__(message, type_name=type_name or "TypeDefinition", path=path, **kwargs)
    def xǁCtyTypeValidationErrorǁ__init____mutmut_14(
        self,
        message: str,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add type definition context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "type_definition"
        context["XXcty.type_categoryXX"] = "meta"

        super().__init__(message, type_name=type_name or "TypeDefinition", path=path, **kwargs)
    def xǁCtyTypeValidationErrorǁ__init____mutmut_15(
        self,
        message: str,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add type definition context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "type_definition"
        context["CTY.TYPE_CATEGORY"] = "meta"

        super().__init__(message, type_name=type_name or "TypeDefinition", path=path, **kwargs)
    def xǁCtyTypeValidationErrorǁ__init____mutmut_16(
        self,
        message: str,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add type definition context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "type_definition"
        context["cty.type_category"] = "XXmetaXX"

        super().__init__(message, type_name=type_name or "TypeDefinition", path=path, **kwargs)
    def xǁCtyTypeValidationErrorǁ__init____mutmut_17(
        self,
        message: str,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add type definition context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "type_definition"
        context["cty.type_category"] = "META"

        super().__init__(message, type_name=type_name or "TypeDefinition", path=path, **kwargs)
    def xǁCtyTypeValidationErrorǁ__init____mutmut_18(
        self,
        message: str,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add type definition context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "type_definition"
        context["cty.type_category"] = "meta"

        super().__init__(None, type_name=type_name or "TypeDefinition", path=path, **kwargs)
    def xǁCtyTypeValidationErrorǁ__init____mutmut_19(
        self,
        message: str,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add type definition context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "type_definition"
        context["cty.type_category"] = "meta"

        super().__init__(message, type_name=None, path=path, **kwargs)
    def xǁCtyTypeValidationErrorǁ__init____mutmut_20(
        self,
        message: str,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add type definition context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "type_definition"
        context["cty.type_category"] = "meta"

        super().__init__(message, type_name=type_name or "TypeDefinition", path=None, **kwargs)
    def xǁCtyTypeValidationErrorǁ__init____mutmut_21(
        self,
        message: str,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add type definition context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "type_definition"
        context["cty.type_category"] = "meta"

        super().__init__(type_name=type_name or "TypeDefinition", path=path, **kwargs)
    def xǁCtyTypeValidationErrorǁ__init____mutmut_22(
        self,
        message: str,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add type definition context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "type_definition"
        context["cty.type_category"] = "meta"

        super().__init__(message, path=path, **kwargs)
    def xǁCtyTypeValidationErrorǁ__init____mutmut_23(
        self,
        message: str,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add type definition context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "type_definition"
        context["cty.type_category"] = "meta"

        super().__init__(message, type_name=type_name or "TypeDefinition", **kwargs)
    def xǁCtyTypeValidationErrorǁ__init____mutmut_24(
        self,
        message: str,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add type definition context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "type_definition"
        context["cty.type_category"] = "meta"

        super().__init__(message, type_name=type_name or "TypeDefinition", path=path, )
    def xǁCtyTypeValidationErrorǁ__init____mutmut_25(
        self,
        message: str,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add type definition context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "type_definition"
        context["cty.type_category"] = "meta"

        super().__init__(message, type_name=type_name and "TypeDefinition", path=path, **kwargs)
    def xǁCtyTypeValidationErrorǁ__init____mutmut_26(
        self,
        message: str,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add type definition context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "type_definition"
        context["cty.type_category"] = "meta"

        super().__init__(message, type_name=type_name or "XXTypeDefinitionXX", path=path, **kwargs)
    def xǁCtyTypeValidationErrorǁ__init____mutmut_27(
        self,
        message: str,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add type definition context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "type_definition"
        context["cty.type_category"] = "meta"

        super().__init__(message, type_name=type_name or "typedefinition", path=path, **kwargs)
    def xǁCtyTypeValidationErrorǁ__init____mutmut_28(
        self,
        message: str,
        type_name: str | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        # Add type definition context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "type_definition"
        context["cty.type_category"] = "meta"

        super().__init__(message, type_name=type_name or "TYPEDEFINITION", path=path, **kwargs)
    
    xǁCtyTypeValidationErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCtyTypeValidationErrorǁ__init____mutmut_1': xǁCtyTypeValidationErrorǁ__init____mutmut_1, 
        'xǁCtyTypeValidationErrorǁ__init____mutmut_2': xǁCtyTypeValidationErrorǁ__init____mutmut_2, 
        'xǁCtyTypeValidationErrorǁ__init____mutmut_3': xǁCtyTypeValidationErrorǁ__init____mutmut_3, 
        'xǁCtyTypeValidationErrorǁ__init____mutmut_4': xǁCtyTypeValidationErrorǁ__init____mutmut_4, 
        'xǁCtyTypeValidationErrorǁ__init____mutmut_5': xǁCtyTypeValidationErrorǁ__init____mutmut_5, 
        'xǁCtyTypeValidationErrorǁ__init____mutmut_6': xǁCtyTypeValidationErrorǁ__init____mutmut_6, 
        'xǁCtyTypeValidationErrorǁ__init____mutmut_7': xǁCtyTypeValidationErrorǁ__init____mutmut_7, 
        'xǁCtyTypeValidationErrorǁ__init____mutmut_8': xǁCtyTypeValidationErrorǁ__init____mutmut_8, 
        'xǁCtyTypeValidationErrorǁ__init____mutmut_9': xǁCtyTypeValidationErrorǁ__init____mutmut_9, 
        'xǁCtyTypeValidationErrorǁ__init____mutmut_10': xǁCtyTypeValidationErrorǁ__init____mutmut_10, 
        'xǁCtyTypeValidationErrorǁ__init____mutmut_11': xǁCtyTypeValidationErrorǁ__init____mutmut_11, 
        'xǁCtyTypeValidationErrorǁ__init____mutmut_12': xǁCtyTypeValidationErrorǁ__init____mutmut_12, 
        'xǁCtyTypeValidationErrorǁ__init____mutmut_13': xǁCtyTypeValidationErrorǁ__init____mutmut_13, 
        'xǁCtyTypeValidationErrorǁ__init____mutmut_14': xǁCtyTypeValidationErrorǁ__init____mutmut_14, 
        'xǁCtyTypeValidationErrorǁ__init____mutmut_15': xǁCtyTypeValidationErrorǁ__init____mutmut_15, 
        'xǁCtyTypeValidationErrorǁ__init____mutmut_16': xǁCtyTypeValidationErrorǁ__init____mutmut_16, 
        'xǁCtyTypeValidationErrorǁ__init____mutmut_17': xǁCtyTypeValidationErrorǁ__init____mutmut_17, 
        'xǁCtyTypeValidationErrorǁ__init____mutmut_18': xǁCtyTypeValidationErrorǁ__init____mutmut_18, 
        'xǁCtyTypeValidationErrorǁ__init____mutmut_19': xǁCtyTypeValidationErrorǁ__init____mutmut_19, 
        'xǁCtyTypeValidationErrorǁ__init____mutmut_20': xǁCtyTypeValidationErrorǁ__init____mutmut_20, 
        'xǁCtyTypeValidationErrorǁ__init____mutmut_21': xǁCtyTypeValidationErrorǁ__init____mutmut_21, 
        'xǁCtyTypeValidationErrorǁ__init____mutmut_22': xǁCtyTypeValidationErrorǁ__init____mutmut_22, 
        'xǁCtyTypeValidationErrorǁ__init____mutmut_23': xǁCtyTypeValidationErrorǁ__init____mutmut_23, 
        'xǁCtyTypeValidationErrorǁ__init____mutmut_24': xǁCtyTypeValidationErrorǁ__init____mutmut_24, 
        'xǁCtyTypeValidationErrorǁ__init____mutmut_25': xǁCtyTypeValidationErrorǁ__init____mutmut_25, 
        'xǁCtyTypeValidationErrorǁ__init____mutmut_26': xǁCtyTypeValidationErrorǁ__init____mutmut_26, 
        'xǁCtyTypeValidationErrorǁ__init____mutmut_27': xǁCtyTypeValidationErrorǁ__init____mutmut_27, 
        'xǁCtyTypeValidationErrorǁ__init____mutmut_28': xǁCtyTypeValidationErrorǁ__init____mutmut_28
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCtyTypeValidationErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁCtyTypeValidationErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁCtyTypeValidationErrorǁ__init____mutmut_orig)
    xǁCtyTypeValidationErrorǁ__init____mutmut_orig.__name__ = 'xǁCtyTypeValidationErrorǁ__init__'


class CtyTypeMismatchError(CtyValidationError):
    def xǁCtyTypeMismatchErrorǁ__init____mutmut_orig(
        self,
        message: str,
        actual_type: CtyType[Any] | None = None,
        expected_type: CtyType[Any] | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.actual_type = actual_type
        self.expected_type = expected_type

        # Add type mismatch context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "type_mismatch"
        context["cty.error_category"] = "type_compatibility"

        if actual_type:
            context["cty.actual_type"] = str(actual_type)
        if expected_type:
            context["cty.expected_type"] = str(expected_type)

        type_info = f"Expected {expected_type}, got {actual_type}"
        full_message = f"{message} ({type_info})"
        super().__init__(full_message, path=path, **kwargs)
    def xǁCtyTypeMismatchErrorǁ__init____mutmut_1(
        self,
        message: str,
        actual_type: CtyType[Any] | None = None,
        expected_type: CtyType[Any] | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.actual_type = None
        self.expected_type = expected_type

        # Add type mismatch context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "type_mismatch"
        context["cty.error_category"] = "type_compatibility"

        if actual_type:
            context["cty.actual_type"] = str(actual_type)
        if expected_type:
            context["cty.expected_type"] = str(expected_type)

        type_info = f"Expected {expected_type}, got {actual_type}"
        full_message = f"{message} ({type_info})"
        super().__init__(full_message, path=path, **kwargs)
    def xǁCtyTypeMismatchErrorǁ__init____mutmut_2(
        self,
        message: str,
        actual_type: CtyType[Any] | None = None,
        expected_type: CtyType[Any] | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.actual_type = actual_type
        self.expected_type = None

        # Add type mismatch context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "type_mismatch"
        context["cty.error_category"] = "type_compatibility"

        if actual_type:
            context["cty.actual_type"] = str(actual_type)
        if expected_type:
            context["cty.expected_type"] = str(expected_type)

        type_info = f"Expected {expected_type}, got {actual_type}"
        full_message = f"{message} ({type_info})"
        super().__init__(full_message, path=path, **kwargs)
    def xǁCtyTypeMismatchErrorǁ__init____mutmut_3(
        self,
        message: str,
        actual_type: CtyType[Any] | None = None,
        expected_type: CtyType[Any] | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.actual_type = actual_type
        self.expected_type = expected_type

        # Add type mismatch context
        context = None
        context["cty.validation_stage"] = "type_mismatch"
        context["cty.error_category"] = "type_compatibility"

        if actual_type:
            context["cty.actual_type"] = str(actual_type)
        if expected_type:
            context["cty.expected_type"] = str(expected_type)

        type_info = f"Expected {expected_type}, got {actual_type}"
        full_message = f"{message} ({type_info})"
        super().__init__(full_message, path=path, **kwargs)
    def xǁCtyTypeMismatchErrorǁ__init____mutmut_4(
        self,
        message: str,
        actual_type: CtyType[Any] | None = None,
        expected_type: CtyType[Any] | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.actual_type = actual_type
        self.expected_type = expected_type

        # Add type mismatch context
        context = kwargs.setdefault(None, {})
        context["cty.validation_stage"] = "type_mismatch"
        context["cty.error_category"] = "type_compatibility"

        if actual_type:
            context["cty.actual_type"] = str(actual_type)
        if expected_type:
            context["cty.expected_type"] = str(expected_type)

        type_info = f"Expected {expected_type}, got {actual_type}"
        full_message = f"{message} ({type_info})"
        super().__init__(full_message, path=path, **kwargs)
    def xǁCtyTypeMismatchErrorǁ__init____mutmut_5(
        self,
        message: str,
        actual_type: CtyType[Any] | None = None,
        expected_type: CtyType[Any] | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.actual_type = actual_type
        self.expected_type = expected_type

        # Add type mismatch context
        context = kwargs.setdefault("context", None)
        context["cty.validation_stage"] = "type_mismatch"
        context["cty.error_category"] = "type_compatibility"

        if actual_type:
            context["cty.actual_type"] = str(actual_type)
        if expected_type:
            context["cty.expected_type"] = str(expected_type)

        type_info = f"Expected {expected_type}, got {actual_type}"
        full_message = f"{message} ({type_info})"
        super().__init__(full_message, path=path, **kwargs)
    def xǁCtyTypeMismatchErrorǁ__init____mutmut_6(
        self,
        message: str,
        actual_type: CtyType[Any] | None = None,
        expected_type: CtyType[Any] | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.actual_type = actual_type
        self.expected_type = expected_type

        # Add type mismatch context
        context = kwargs.setdefault({})
        context["cty.validation_stage"] = "type_mismatch"
        context["cty.error_category"] = "type_compatibility"

        if actual_type:
            context["cty.actual_type"] = str(actual_type)
        if expected_type:
            context["cty.expected_type"] = str(expected_type)

        type_info = f"Expected {expected_type}, got {actual_type}"
        full_message = f"{message} ({type_info})"
        super().__init__(full_message, path=path, **kwargs)
    def xǁCtyTypeMismatchErrorǁ__init____mutmut_7(
        self,
        message: str,
        actual_type: CtyType[Any] | None = None,
        expected_type: CtyType[Any] | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.actual_type = actual_type
        self.expected_type = expected_type

        # Add type mismatch context
        context = kwargs.setdefault("context", )
        context["cty.validation_stage"] = "type_mismatch"
        context["cty.error_category"] = "type_compatibility"

        if actual_type:
            context["cty.actual_type"] = str(actual_type)
        if expected_type:
            context["cty.expected_type"] = str(expected_type)

        type_info = f"Expected {expected_type}, got {actual_type}"
        full_message = f"{message} ({type_info})"
        super().__init__(full_message, path=path, **kwargs)
    def xǁCtyTypeMismatchErrorǁ__init____mutmut_8(
        self,
        message: str,
        actual_type: CtyType[Any] | None = None,
        expected_type: CtyType[Any] | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.actual_type = actual_type
        self.expected_type = expected_type

        # Add type mismatch context
        context = kwargs.setdefault("XXcontextXX", {})
        context["cty.validation_stage"] = "type_mismatch"
        context["cty.error_category"] = "type_compatibility"

        if actual_type:
            context["cty.actual_type"] = str(actual_type)
        if expected_type:
            context["cty.expected_type"] = str(expected_type)

        type_info = f"Expected {expected_type}, got {actual_type}"
        full_message = f"{message} ({type_info})"
        super().__init__(full_message, path=path, **kwargs)
    def xǁCtyTypeMismatchErrorǁ__init____mutmut_9(
        self,
        message: str,
        actual_type: CtyType[Any] | None = None,
        expected_type: CtyType[Any] | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.actual_type = actual_type
        self.expected_type = expected_type

        # Add type mismatch context
        context = kwargs.setdefault("CONTEXT", {})
        context["cty.validation_stage"] = "type_mismatch"
        context["cty.error_category"] = "type_compatibility"

        if actual_type:
            context["cty.actual_type"] = str(actual_type)
        if expected_type:
            context["cty.expected_type"] = str(expected_type)

        type_info = f"Expected {expected_type}, got {actual_type}"
        full_message = f"{message} ({type_info})"
        super().__init__(full_message, path=path, **kwargs)
    def xǁCtyTypeMismatchErrorǁ__init____mutmut_10(
        self,
        message: str,
        actual_type: CtyType[Any] | None = None,
        expected_type: CtyType[Any] | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.actual_type = actual_type
        self.expected_type = expected_type

        # Add type mismatch context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = None
        context["cty.error_category"] = "type_compatibility"

        if actual_type:
            context["cty.actual_type"] = str(actual_type)
        if expected_type:
            context["cty.expected_type"] = str(expected_type)

        type_info = f"Expected {expected_type}, got {actual_type}"
        full_message = f"{message} ({type_info})"
        super().__init__(full_message, path=path, **kwargs)
    def xǁCtyTypeMismatchErrorǁ__init____mutmut_11(
        self,
        message: str,
        actual_type: CtyType[Any] | None = None,
        expected_type: CtyType[Any] | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.actual_type = actual_type
        self.expected_type = expected_type

        # Add type mismatch context
        context = kwargs.setdefault("context", {})
        context["XXcty.validation_stageXX"] = "type_mismatch"
        context["cty.error_category"] = "type_compatibility"

        if actual_type:
            context["cty.actual_type"] = str(actual_type)
        if expected_type:
            context["cty.expected_type"] = str(expected_type)

        type_info = f"Expected {expected_type}, got {actual_type}"
        full_message = f"{message} ({type_info})"
        super().__init__(full_message, path=path, **kwargs)
    def xǁCtyTypeMismatchErrorǁ__init____mutmut_12(
        self,
        message: str,
        actual_type: CtyType[Any] | None = None,
        expected_type: CtyType[Any] | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.actual_type = actual_type
        self.expected_type = expected_type

        # Add type mismatch context
        context = kwargs.setdefault("context", {})
        context["CTY.VALIDATION_STAGE"] = "type_mismatch"
        context["cty.error_category"] = "type_compatibility"

        if actual_type:
            context["cty.actual_type"] = str(actual_type)
        if expected_type:
            context["cty.expected_type"] = str(expected_type)

        type_info = f"Expected {expected_type}, got {actual_type}"
        full_message = f"{message} ({type_info})"
        super().__init__(full_message, path=path, **kwargs)
    def xǁCtyTypeMismatchErrorǁ__init____mutmut_13(
        self,
        message: str,
        actual_type: CtyType[Any] | None = None,
        expected_type: CtyType[Any] | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.actual_type = actual_type
        self.expected_type = expected_type

        # Add type mismatch context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "XXtype_mismatchXX"
        context["cty.error_category"] = "type_compatibility"

        if actual_type:
            context["cty.actual_type"] = str(actual_type)
        if expected_type:
            context["cty.expected_type"] = str(expected_type)

        type_info = f"Expected {expected_type}, got {actual_type}"
        full_message = f"{message} ({type_info})"
        super().__init__(full_message, path=path, **kwargs)
    def xǁCtyTypeMismatchErrorǁ__init____mutmut_14(
        self,
        message: str,
        actual_type: CtyType[Any] | None = None,
        expected_type: CtyType[Any] | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.actual_type = actual_type
        self.expected_type = expected_type

        # Add type mismatch context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "TYPE_MISMATCH"
        context["cty.error_category"] = "type_compatibility"

        if actual_type:
            context["cty.actual_type"] = str(actual_type)
        if expected_type:
            context["cty.expected_type"] = str(expected_type)

        type_info = f"Expected {expected_type}, got {actual_type}"
        full_message = f"{message} ({type_info})"
        super().__init__(full_message, path=path, **kwargs)
    def xǁCtyTypeMismatchErrorǁ__init____mutmut_15(
        self,
        message: str,
        actual_type: CtyType[Any] | None = None,
        expected_type: CtyType[Any] | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.actual_type = actual_type
        self.expected_type = expected_type

        # Add type mismatch context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "type_mismatch"
        context["cty.error_category"] = None

        if actual_type:
            context["cty.actual_type"] = str(actual_type)
        if expected_type:
            context["cty.expected_type"] = str(expected_type)

        type_info = f"Expected {expected_type}, got {actual_type}"
        full_message = f"{message} ({type_info})"
        super().__init__(full_message, path=path, **kwargs)
    def xǁCtyTypeMismatchErrorǁ__init____mutmut_16(
        self,
        message: str,
        actual_type: CtyType[Any] | None = None,
        expected_type: CtyType[Any] | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.actual_type = actual_type
        self.expected_type = expected_type

        # Add type mismatch context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "type_mismatch"
        context["XXcty.error_categoryXX"] = "type_compatibility"

        if actual_type:
            context["cty.actual_type"] = str(actual_type)
        if expected_type:
            context["cty.expected_type"] = str(expected_type)

        type_info = f"Expected {expected_type}, got {actual_type}"
        full_message = f"{message} ({type_info})"
        super().__init__(full_message, path=path, **kwargs)
    def xǁCtyTypeMismatchErrorǁ__init____mutmut_17(
        self,
        message: str,
        actual_type: CtyType[Any] | None = None,
        expected_type: CtyType[Any] | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.actual_type = actual_type
        self.expected_type = expected_type

        # Add type mismatch context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "type_mismatch"
        context["CTY.ERROR_CATEGORY"] = "type_compatibility"

        if actual_type:
            context["cty.actual_type"] = str(actual_type)
        if expected_type:
            context["cty.expected_type"] = str(expected_type)

        type_info = f"Expected {expected_type}, got {actual_type}"
        full_message = f"{message} ({type_info})"
        super().__init__(full_message, path=path, **kwargs)
    def xǁCtyTypeMismatchErrorǁ__init____mutmut_18(
        self,
        message: str,
        actual_type: CtyType[Any] | None = None,
        expected_type: CtyType[Any] | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.actual_type = actual_type
        self.expected_type = expected_type

        # Add type mismatch context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "type_mismatch"
        context["cty.error_category"] = "XXtype_compatibilityXX"

        if actual_type:
            context["cty.actual_type"] = str(actual_type)
        if expected_type:
            context["cty.expected_type"] = str(expected_type)

        type_info = f"Expected {expected_type}, got {actual_type}"
        full_message = f"{message} ({type_info})"
        super().__init__(full_message, path=path, **kwargs)
    def xǁCtyTypeMismatchErrorǁ__init____mutmut_19(
        self,
        message: str,
        actual_type: CtyType[Any] | None = None,
        expected_type: CtyType[Any] | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.actual_type = actual_type
        self.expected_type = expected_type

        # Add type mismatch context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "type_mismatch"
        context["cty.error_category"] = "TYPE_COMPATIBILITY"

        if actual_type:
            context["cty.actual_type"] = str(actual_type)
        if expected_type:
            context["cty.expected_type"] = str(expected_type)

        type_info = f"Expected {expected_type}, got {actual_type}"
        full_message = f"{message} ({type_info})"
        super().__init__(full_message, path=path, **kwargs)
    def xǁCtyTypeMismatchErrorǁ__init____mutmut_20(
        self,
        message: str,
        actual_type: CtyType[Any] | None = None,
        expected_type: CtyType[Any] | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.actual_type = actual_type
        self.expected_type = expected_type

        # Add type mismatch context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "type_mismatch"
        context["cty.error_category"] = "type_compatibility"

        if actual_type:
            context["cty.actual_type"] = None
        if expected_type:
            context["cty.expected_type"] = str(expected_type)

        type_info = f"Expected {expected_type}, got {actual_type}"
        full_message = f"{message} ({type_info})"
        super().__init__(full_message, path=path, **kwargs)
    def xǁCtyTypeMismatchErrorǁ__init____mutmut_21(
        self,
        message: str,
        actual_type: CtyType[Any] | None = None,
        expected_type: CtyType[Any] | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.actual_type = actual_type
        self.expected_type = expected_type

        # Add type mismatch context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "type_mismatch"
        context["cty.error_category"] = "type_compatibility"

        if actual_type:
            context["XXcty.actual_typeXX"] = str(actual_type)
        if expected_type:
            context["cty.expected_type"] = str(expected_type)

        type_info = f"Expected {expected_type}, got {actual_type}"
        full_message = f"{message} ({type_info})"
        super().__init__(full_message, path=path, **kwargs)
    def xǁCtyTypeMismatchErrorǁ__init____mutmut_22(
        self,
        message: str,
        actual_type: CtyType[Any] | None = None,
        expected_type: CtyType[Any] | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.actual_type = actual_type
        self.expected_type = expected_type

        # Add type mismatch context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "type_mismatch"
        context["cty.error_category"] = "type_compatibility"

        if actual_type:
            context["CTY.ACTUAL_TYPE"] = str(actual_type)
        if expected_type:
            context["cty.expected_type"] = str(expected_type)

        type_info = f"Expected {expected_type}, got {actual_type}"
        full_message = f"{message} ({type_info})"
        super().__init__(full_message, path=path, **kwargs)
    def xǁCtyTypeMismatchErrorǁ__init____mutmut_23(
        self,
        message: str,
        actual_type: CtyType[Any] | None = None,
        expected_type: CtyType[Any] | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.actual_type = actual_type
        self.expected_type = expected_type

        # Add type mismatch context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "type_mismatch"
        context["cty.error_category"] = "type_compatibility"

        if actual_type:
            context["cty.actual_type"] = str(None)
        if expected_type:
            context["cty.expected_type"] = str(expected_type)

        type_info = f"Expected {expected_type}, got {actual_type}"
        full_message = f"{message} ({type_info})"
        super().__init__(full_message, path=path, **kwargs)
    def xǁCtyTypeMismatchErrorǁ__init____mutmut_24(
        self,
        message: str,
        actual_type: CtyType[Any] | None = None,
        expected_type: CtyType[Any] | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.actual_type = actual_type
        self.expected_type = expected_type

        # Add type mismatch context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "type_mismatch"
        context["cty.error_category"] = "type_compatibility"

        if actual_type:
            context["cty.actual_type"] = str(actual_type)
        if expected_type:
            context["cty.expected_type"] = None

        type_info = f"Expected {expected_type}, got {actual_type}"
        full_message = f"{message} ({type_info})"
        super().__init__(full_message, path=path, **kwargs)
    def xǁCtyTypeMismatchErrorǁ__init____mutmut_25(
        self,
        message: str,
        actual_type: CtyType[Any] | None = None,
        expected_type: CtyType[Any] | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.actual_type = actual_type
        self.expected_type = expected_type

        # Add type mismatch context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "type_mismatch"
        context["cty.error_category"] = "type_compatibility"

        if actual_type:
            context["cty.actual_type"] = str(actual_type)
        if expected_type:
            context["XXcty.expected_typeXX"] = str(expected_type)

        type_info = f"Expected {expected_type}, got {actual_type}"
        full_message = f"{message} ({type_info})"
        super().__init__(full_message, path=path, **kwargs)
    def xǁCtyTypeMismatchErrorǁ__init____mutmut_26(
        self,
        message: str,
        actual_type: CtyType[Any] | None = None,
        expected_type: CtyType[Any] | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.actual_type = actual_type
        self.expected_type = expected_type

        # Add type mismatch context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "type_mismatch"
        context["cty.error_category"] = "type_compatibility"

        if actual_type:
            context["cty.actual_type"] = str(actual_type)
        if expected_type:
            context["CTY.EXPECTED_TYPE"] = str(expected_type)

        type_info = f"Expected {expected_type}, got {actual_type}"
        full_message = f"{message} ({type_info})"
        super().__init__(full_message, path=path, **kwargs)
    def xǁCtyTypeMismatchErrorǁ__init____mutmut_27(
        self,
        message: str,
        actual_type: CtyType[Any] | None = None,
        expected_type: CtyType[Any] | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.actual_type = actual_type
        self.expected_type = expected_type

        # Add type mismatch context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "type_mismatch"
        context["cty.error_category"] = "type_compatibility"

        if actual_type:
            context["cty.actual_type"] = str(actual_type)
        if expected_type:
            context["cty.expected_type"] = str(None)

        type_info = f"Expected {expected_type}, got {actual_type}"
        full_message = f"{message} ({type_info})"
        super().__init__(full_message, path=path, **kwargs)
    def xǁCtyTypeMismatchErrorǁ__init____mutmut_28(
        self,
        message: str,
        actual_type: CtyType[Any] | None = None,
        expected_type: CtyType[Any] | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.actual_type = actual_type
        self.expected_type = expected_type

        # Add type mismatch context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "type_mismatch"
        context["cty.error_category"] = "type_compatibility"

        if actual_type:
            context["cty.actual_type"] = str(actual_type)
        if expected_type:
            context["cty.expected_type"] = str(expected_type)

        type_info = None
        full_message = f"{message} ({type_info})"
        super().__init__(full_message, path=path, **kwargs)
    def xǁCtyTypeMismatchErrorǁ__init____mutmut_29(
        self,
        message: str,
        actual_type: CtyType[Any] | None = None,
        expected_type: CtyType[Any] | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.actual_type = actual_type
        self.expected_type = expected_type

        # Add type mismatch context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "type_mismatch"
        context["cty.error_category"] = "type_compatibility"

        if actual_type:
            context["cty.actual_type"] = str(actual_type)
        if expected_type:
            context["cty.expected_type"] = str(expected_type)

        type_info = f"Expected {expected_type}, got {actual_type}"
        full_message = None
        super().__init__(full_message, path=path, **kwargs)
    def xǁCtyTypeMismatchErrorǁ__init____mutmut_30(
        self,
        message: str,
        actual_type: CtyType[Any] | None = None,
        expected_type: CtyType[Any] | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.actual_type = actual_type
        self.expected_type = expected_type

        # Add type mismatch context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "type_mismatch"
        context["cty.error_category"] = "type_compatibility"

        if actual_type:
            context["cty.actual_type"] = str(actual_type)
        if expected_type:
            context["cty.expected_type"] = str(expected_type)

        type_info = f"Expected {expected_type}, got {actual_type}"
        full_message = f"{message} ({type_info})"
        super().__init__(None, path=path, **kwargs)
    def xǁCtyTypeMismatchErrorǁ__init____mutmut_31(
        self,
        message: str,
        actual_type: CtyType[Any] | None = None,
        expected_type: CtyType[Any] | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.actual_type = actual_type
        self.expected_type = expected_type

        # Add type mismatch context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "type_mismatch"
        context["cty.error_category"] = "type_compatibility"

        if actual_type:
            context["cty.actual_type"] = str(actual_type)
        if expected_type:
            context["cty.expected_type"] = str(expected_type)

        type_info = f"Expected {expected_type}, got {actual_type}"
        full_message = f"{message} ({type_info})"
        super().__init__(full_message, path=None, **kwargs)
    def xǁCtyTypeMismatchErrorǁ__init____mutmut_32(
        self,
        message: str,
        actual_type: CtyType[Any] | None = None,
        expected_type: CtyType[Any] | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.actual_type = actual_type
        self.expected_type = expected_type

        # Add type mismatch context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "type_mismatch"
        context["cty.error_category"] = "type_compatibility"

        if actual_type:
            context["cty.actual_type"] = str(actual_type)
        if expected_type:
            context["cty.expected_type"] = str(expected_type)

        type_info = f"Expected {expected_type}, got {actual_type}"
        full_message = f"{message} ({type_info})"
        super().__init__(path=path, **kwargs)
    def xǁCtyTypeMismatchErrorǁ__init____mutmut_33(
        self,
        message: str,
        actual_type: CtyType[Any] | None = None,
        expected_type: CtyType[Any] | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.actual_type = actual_type
        self.expected_type = expected_type

        # Add type mismatch context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "type_mismatch"
        context["cty.error_category"] = "type_compatibility"

        if actual_type:
            context["cty.actual_type"] = str(actual_type)
        if expected_type:
            context["cty.expected_type"] = str(expected_type)

        type_info = f"Expected {expected_type}, got {actual_type}"
        full_message = f"{message} ({type_info})"
        super().__init__(full_message, **kwargs)
    def xǁCtyTypeMismatchErrorǁ__init____mutmut_34(
        self,
        message: str,
        actual_type: CtyType[Any] | None = None,
        expected_type: CtyType[Any] | None = None,
        path: CtyPath | None = None,
        **kwargs: Any,
    ) -> None:
        self.actual_type = actual_type
        self.expected_type = expected_type

        # Add type mismatch context
        context = kwargs.setdefault("context", {})
        context["cty.validation_stage"] = "type_mismatch"
        context["cty.error_category"] = "type_compatibility"

        if actual_type:
            context["cty.actual_type"] = str(actual_type)
        if expected_type:
            context["cty.expected_type"] = str(expected_type)

        type_info = f"Expected {expected_type}, got {actual_type}"
        full_message = f"{message} ({type_info})"
        super().__init__(full_message, path=path, )
    
    xǁCtyTypeMismatchErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCtyTypeMismatchErrorǁ__init____mutmut_1': xǁCtyTypeMismatchErrorǁ__init____mutmut_1, 
        'xǁCtyTypeMismatchErrorǁ__init____mutmut_2': xǁCtyTypeMismatchErrorǁ__init____mutmut_2, 
        'xǁCtyTypeMismatchErrorǁ__init____mutmut_3': xǁCtyTypeMismatchErrorǁ__init____mutmut_3, 
        'xǁCtyTypeMismatchErrorǁ__init____mutmut_4': xǁCtyTypeMismatchErrorǁ__init____mutmut_4, 
        'xǁCtyTypeMismatchErrorǁ__init____mutmut_5': xǁCtyTypeMismatchErrorǁ__init____mutmut_5, 
        'xǁCtyTypeMismatchErrorǁ__init____mutmut_6': xǁCtyTypeMismatchErrorǁ__init____mutmut_6, 
        'xǁCtyTypeMismatchErrorǁ__init____mutmut_7': xǁCtyTypeMismatchErrorǁ__init____mutmut_7, 
        'xǁCtyTypeMismatchErrorǁ__init____mutmut_8': xǁCtyTypeMismatchErrorǁ__init____mutmut_8, 
        'xǁCtyTypeMismatchErrorǁ__init____mutmut_9': xǁCtyTypeMismatchErrorǁ__init____mutmut_9, 
        'xǁCtyTypeMismatchErrorǁ__init____mutmut_10': xǁCtyTypeMismatchErrorǁ__init____mutmut_10, 
        'xǁCtyTypeMismatchErrorǁ__init____mutmut_11': xǁCtyTypeMismatchErrorǁ__init____mutmut_11, 
        'xǁCtyTypeMismatchErrorǁ__init____mutmut_12': xǁCtyTypeMismatchErrorǁ__init____mutmut_12, 
        'xǁCtyTypeMismatchErrorǁ__init____mutmut_13': xǁCtyTypeMismatchErrorǁ__init____mutmut_13, 
        'xǁCtyTypeMismatchErrorǁ__init____mutmut_14': xǁCtyTypeMismatchErrorǁ__init____mutmut_14, 
        'xǁCtyTypeMismatchErrorǁ__init____mutmut_15': xǁCtyTypeMismatchErrorǁ__init____mutmut_15, 
        'xǁCtyTypeMismatchErrorǁ__init____mutmut_16': xǁCtyTypeMismatchErrorǁ__init____mutmut_16, 
        'xǁCtyTypeMismatchErrorǁ__init____mutmut_17': xǁCtyTypeMismatchErrorǁ__init____mutmut_17, 
        'xǁCtyTypeMismatchErrorǁ__init____mutmut_18': xǁCtyTypeMismatchErrorǁ__init____mutmut_18, 
        'xǁCtyTypeMismatchErrorǁ__init____mutmut_19': xǁCtyTypeMismatchErrorǁ__init____mutmut_19, 
        'xǁCtyTypeMismatchErrorǁ__init____mutmut_20': xǁCtyTypeMismatchErrorǁ__init____mutmut_20, 
        'xǁCtyTypeMismatchErrorǁ__init____mutmut_21': xǁCtyTypeMismatchErrorǁ__init____mutmut_21, 
        'xǁCtyTypeMismatchErrorǁ__init____mutmut_22': xǁCtyTypeMismatchErrorǁ__init____mutmut_22, 
        'xǁCtyTypeMismatchErrorǁ__init____mutmut_23': xǁCtyTypeMismatchErrorǁ__init____mutmut_23, 
        'xǁCtyTypeMismatchErrorǁ__init____mutmut_24': xǁCtyTypeMismatchErrorǁ__init____mutmut_24, 
        'xǁCtyTypeMismatchErrorǁ__init____mutmut_25': xǁCtyTypeMismatchErrorǁ__init____mutmut_25, 
        'xǁCtyTypeMismatchErrorǁ__init____mutmut_26': xǁCtyTypeMismatchErrorǁ__init____mutmut_26, 
        'xǁCtyTypeMismatchErrorǁ__init____mutmut_27': xǁCtyTypeMismatchErrorǁ__init____mutmut_27, 
        'xǁCtyTypeMismatchErrorǁ__init____mutmut_28': xǁCtyTypeMismatchErrorǁ__init____mutmut_28, 
        'xǁCtyTypeMismatchErrorǁ__init____mutmut_29': xǁCtyTypeMismatchErrorǁ__init____mutmut_29, 
        'xǁCtyTypeMismatchErrorǁ__init____mutmut_30': xǁCtyTypeMismatchErrorǁ__init____mutmut_30, 
        'xǁCtyTypeMismatchErrorǁ__init____mutmut_31': xǁCtyTypeMismatchErrorǁ__init____mutmut_31, 
        'xǁCtyTypeMismatchErrorǁ__init____mutmut_32': xǁCtyTypeMismatchErrorǁ__init____mutmut_32, 
        'xǁCtyTypeMismatchErrorǁ__init____mutmut_33': xǁCtyTypeMismatchErrorǁ__init____mutmut_33, 
        'xǁCtyTypeMismatchErrorǁ__init____mutmut_34': xǁCtyTypeMismatchErrorǁ__init____mutmut_34
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCtyTypeMismatchErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁCtyTypeMismatchErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁCtyTypeMismatchErrorǁ__init____mutmut_orig)
    xǁCtyTypeMismatchErrorǁ__init____mutmut_orig.__name__ = 'xǁCtyTypeMismatchErrorǁ__init__'


# 🌊🪢🐛🪄
