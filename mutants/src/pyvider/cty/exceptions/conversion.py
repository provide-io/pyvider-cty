# pyvider/cty/exceptions/conversion.py
#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Any

from pyvider.cty.exceptions.base import CtyError

# pyvider/cty/exceptions/conversion.py
"""
Defines exceptions related to CTY type and value conversions.
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


class CtyConversionError(CtyError):
    """Base for CTY value or type conversion errors."""

    def xǁCtyConversionErrorǁ__init____mutmut_orig(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_1(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = None
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_2(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = None

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_3(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = None
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_4(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault(None, {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_5(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", None)
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_6(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault({})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_7(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", )
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_8(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("XXcontextXX", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_9(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("CONTEXT", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_10(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = None
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_11(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["XXcty.operationXX"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_12(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["CTY.OPERATION"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_13(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "XXconversionXX"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_14(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "CONVERSION"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_15(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = None

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_16(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["XXcty.error_categoryXX"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_17(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["CTY.ERROR_CATEGORY"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_18(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "XXtype_conversionXX"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_19(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "TYPE_CONVERSION"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_20(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = None
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_21(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_22(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(None)
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_23(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(None).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_24(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = None
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_25(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["XXconversion.source_typeXX"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_26(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["CONVERSION.SOURCE_TYPE"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_27(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(None).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_28(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = None

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_29(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["XXconversion.source_value_typeXX"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_30(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["CONVERSION.SOURCE_VALUE_TYPE"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_31(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(None).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_32(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") or hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_33(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(None, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_34(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, None) and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_35(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr("type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_36(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, ) and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_37(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "XXtypeXX") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_38(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "TYPE") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_39(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(None, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_40(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, None):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_41(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr("is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_42(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, ):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_43(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "XXis_nullXX"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_44(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "IS_NULL"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_45(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = None
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_46(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["XXconversion.source_cty_typeXX"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_47(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["CONVERSION.SOURCE_CTY_TYPE"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_48(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(None)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_49(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = None
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_50(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["XXconversion.source_is_nullXX"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_51(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["CONVERSION.SOURCE_IS_NULL"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_52(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(None, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_53(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, None):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_54(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr("is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_55(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, ):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_56(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "XXis_unknownXX"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_57(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "IS_UNKNOWN"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_58(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = None

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_59(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["XXconversion.source_is_unknownXX"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_60(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["CONVERSION.SOURCE_IS_UNKNOWN"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_61(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_62(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = None
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_63(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(None, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_64(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, None) else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_65(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr("__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_66(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, ) else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_67(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "XX__name__XX") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_68(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__NAME__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_69(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(None)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_70(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(None)
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_71(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = None
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_72(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["XXconversion.target_typeXX"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_73(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["CONVERSION.TARGET_TYPE"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_74(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = None

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_75(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["XXconversion.target_type_strXX"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_76(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["CONVERSION.TARGET_TYPE_STR"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_77(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(None)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_78(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = None

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_79(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(None)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_80(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({'XX, XX'.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_81(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(None, **kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_82(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(**kwargs)

    def xǁCtyConversionErrorǁ__init____mutmut_83(
        self,
        message: str,
        *,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyConversionError.

        Args:
            message: The base error message.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
            **kwargs: Additional foundation error context.
        """
        self.source_value = source_value
        self.target_type = target_type

        # Add rich conversion context
        context = kwargs.setdefault("context", {})
        context["cty.operation"] = "conversion"
        context["cty.error_category"] = "type_conversion"

        # Build message with old format for compatibility
        context_parts = []
        if source_value is not None:
            context_parts.append(f"source_type={type(source_value).__name__}")
            # Also add to foundation context
            context["conversion.source_type"] = type(source_value).__name__
            context["conversion.source_value_type"] = type(source_value).__name__

            # Add value analysis for better debugging
            if hasattr(source_value, "type") and hasattr(source_value, "is_null"):
                context["conversion.source_cty_type"] = str(source_value.type)
                context["conversion.source_is_null"] = source_value.is_null
                if hasattr(source_value, "is_unknown"):
                    context["conversion.source_is_unknown"] = source_value.is_unknown

        if target_type is not None:
            target_name = target_type.__name__ if hasattr(target_type, "__name__") else str(target_type)
            context_parts.append(f"target_type={target_name}")
            context["conversion.target_type"] = target_name
            context["conversion.target_type_str"] = str(target_type)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, )
    
    xǁCtyConversionErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCtyConversionErrorǁ__init____mutmut_1': xǁCtyConversionErrorǁ__init____mutmut_1, 
        'xǁCtyConversionErrorǁ__init____mutmut_2': xǁCtyConversionErrorǁ__init____mutmut_2, 
        'xǁCtyConversionErrorǁ__init____mutmut_3': xǁCtyConversionErrorǁ__init____mutmut_3, 
        'xǁCtyConversionErrorǁ__init____mutmut_4': xǁCtyConversionErrorǁ__init____mutmut_4, 
        'xǁCtyConversionErrorǁ__init____mutmut_5': xǁCtyConversionErrorǁ__init____mutmut_5, 
        'xǁCtyConversionErrorǁ__init____mutmut_6': xǁCtyConversionErrorǁ__init____mutmut_6, 
        'xǁCtyConversionErrorǁ__init____mutmut_7': xǁCtyConversionErrorǁ__init____mutmut_7, 
        'xǁCtyConversionErrorǁ__init____mutmut_8': xǁCtyConversionErrorǁ__init____mutmut_8, 
        'xǁCtyConversionErrorǁ__init____mutmut_9': xǁCtyConversionErrorǁ__init____mutmut_9, 
        'xǁCtyConversionErrorǁ__init____mutmut_10': xǁCtyConversionErrorǁ__init____mutmut_10, 
        'xǁCtyConversionErrorǁ__init____mutmut_11': xǁCtyConversionErrorǁ__init____mutmut_11, 
        'xǁCtyConversionErrorǁ__init____mutmut_12': xǁCtyConversionErrorǁ__init____mutmut_12, 
        'xǁCtyConversionErrorǁ__init____mutmut_13': xǁCtyConversionErrorǁ__init____mutmut_13, 
        'xǁCtyConversionErrorǁ__init____mutmut_14': xǁCtyConversionErrorǁ__init____mutmut_14, 
        'xǁCtyConversionErrorǁ__init____mutmut_15': xǁCtyConversionErrorǁ__init____mutmut_15, 
        'xǁCtyConversionErrorǁ__init____mutmut_16': xǁCtyConversionErrorǁ__init____mutmut_16, 
        'xǁCtyConversionErrorǁ__init____mutmut_17': xǁCtyConversionErrorǁ__init____mutmut_17, 
        'xǁCtyConversionErrorǁ__init____mutmut_18': xǁCtyConversionErrorǁ__init____mutmut_18, 
        'xǁCtyConversionErrorǁ__init____mutmut_19': xǁCtyConversionErrorǁ__init____mutmut_19, 
        'xǁCtyConversionErrorǁ__init____mutmut_20': xǁCtyConversionErrorǁ__init____mutmut_20, 
        'xǁCtyConversionErrorǁ__init____mutmut_21': xǁCtyConversionErrorǁ__init____mutmut_21, 
        'xǁCtyConversionErrorǁ__init____mutmut_22': xǁCtyConversionErrorǁ__init____mutmut_22, 
        'xǁCtyConversionErrorǁ__init____mutmut_23': xǁCtyConversionErrorǁ__init____mutmut_23, 
        'xǁCtyConversionErrorǁ__init____mutmut_24': xǁCtyConversionErrorǁ__init____mutmut_24, 
        'xǁCtyConversionErrorǁ__init____mutmut_25': xǁCtyConversionErrorǁ__init____mutmut_25, 
        'xǁCtyConversionErrorǁ__init____mutmut_26': xǁCtyConversionErrorǁ__init____mutmut_26, 
        'xǁCtyConversionErrorǁ__init____mutmut_27': xǁCtyConversionErrorǁ__init____mutmut_27, 
        'xǁCtyConversionErrorǁ__init____mutmut_28': xǁCtyConversionErrorǁ__init____mutmut_28, 
        'xǁCtyConversionErrorǁ__init____mutmut_29': xǁCtyConversionErrorǁ__init____mutmut_29, 
        'xǁCtyConversionErrorǁ__init____mutmut_30': xǁCtyConversionErrorǁ__init____mutmut_30, 
        'xǁCtyConversionErrorǁ__init____mutmut_31': xǁCtyConversionErrorǁ__init____mutmut_31, 
        'xǁCtyConversionErrorǁ__init____mutmut_32': xǁCtyConversionErrorǁ__init____mutmut_32, 
        'xǁCtyConversionErrorǁ__init____mutmut_33': xǁCtyConversionErrorǁ__init____mutmut_33, 
        'xǁCtyConversionErrorǁ__init____mutmut_34': xǁCtyConversionErrorǁ__init____mutmut_34, 
        'xǁCtyConversionErrorǁ__init____mutmut_35': xǁCtyConversionErrorǁ__init____mutmut_35, 
        'xǁCtyConversionErrorǁ__init____mutmut_36': xǁCtyConversionErrorǁ__init____mutmut_36, 
        'xǁCtyConversionErrorǁ__init____mutmut_37': xǁCtyConversionErrorǁ__init____mutmut_37, 
        'xǁCtyConversionErrorǁ__init____mutmut_38': xǁCtyConversionErrorǁ__init____mutmut_38, 
        'xǁCtyConversionErrorǁ__init____mutmut_39': xǁCtyConversionErrorǁ__init____mutmut_39, 
        'xǁCtyConversionErrorǁ__init____mutmut_40': xǁCtyConversionErrorǁ__init____mutmut_40, 
        'xǁCtyConversionErrorǁ__init____mutmut_41': xǁCtyConversionErrorǁ__init____mutmut_41, 
        'xǁCtyConversionErrorǁ__init____mutmut_42': xǁCtyConversionErrorǁ__init____mutmut_42, 
        'xǁCtyConversionErrorǁ__init____mutmut_43': xǁCtyConversionErrorǁ__init____mutmut_43, 
        'xǁCtyConversionErrorǁ__init____mutmut_44': xǁCtyConversionErrorǁ__init____mutmut_44, 
        'xǁCtyConversionErrorǁ__init____mutmut_45': xǁCtyConversionErrorǁ__init____mutmut_45, 
        'xǁCtyConversionErrorǁ__init____mutmut_46': xǁCtyConversionErrorǁ__init____mutmut_46, 
        'xǁCtyConversionErrorǁ__init____mutmut_47': xǁCtyConversionErrorǁ__init____mutmut_47, 
        'xǁCtyConversionErrorǁ__init____mutmut_48': xǁCtyConversionErrorǁ__init____mutmut_48, 
        'xǁCtyConversionErrorǁ__init____mutmut_49': xǁCtyConversionErrorǁ__init____mutmut_49, 
        'xǁCtyConversionErrorǁ__init____mutmut_50': xǁCtyConversionErrorǁ__init____mutmut_50, 
        'xǁCtyConversionErrorǁ__init____mutmut_51': xǁCtyConversionErrorǁ__init____mutmut_51, 
        'xǁCtyConversionErrorǁ__init____mutmut_52': xǁCtyConversionErrorǁ__init____mutmut_52, 
        'xǁCtyConversionErrorǁ__init____mutmut_53': xǁCtyConversionErrorǁ__init____mutmut_53, 
        'xǁCtyConversionErrorǁ__init____mutmut_54': xǁCtyConversionErrorǁ__init____mutmut_54, 
        'xǁCtyConversionErrorǁ__init____mutmut_55': xǁCtyConversionErrorǁ__init____mutmut_55, 
        'xǁCtyConversionErrorǁ__init____mutmut_56': xǁCtyConversionErrorǁ__init____mutmut_56, 
        'xǁCtyConversionErrorǁ__init____mutmut_57': xǁCtyConversionErrorǁ__init____mutmut_57, 
        'xǁCtyConversionErrorǁ__init____mutmut_58': xǁCtyConversionErrorǁ__init____mutmut_58, 
        'xǁCtyConversionErrorǁ__init____mutmut_59': xǁCtyConversionErrorǁ__init____mutmut_59, 
        'xǁCtyConversionErrorǁ__init____mutmut_60': xǁCtyConversionErrorǁ__init____mutmut_60, 
        'xǁCtyConversionErrorǁ__init____mutmut_61': xǁCtyConversionErrorǁ__init____mutmut_61, 
        'xǁCtyConversionErrorǁ__init____mutmut_62': xǁCtyConversionErrorǁ__init____mutmut_62, 
        'xǁCtyConversionErrorǁ__init____mutmut_63': xǁCtyConversionErrorǁ__init____mutmut_63, 
        'xǁCtyConversionErrorǁ__init____mutmut_64': xǁCtyConversionErrorǁ__init____mutmut_64, 
        'xǁCtyConversionErrorǁ__init____mutmut_65': xǁCtyConversionErrorǁ__init____mutmut_65, 
        'xǁCtyConversionErrorǁ__init____mutmut_66': xǁCtyConversionErrorǁ__init____mutmut_66, 
        'xǁCtyConversionErrorǁ__init____mutmut_67': xǁCtyConversionErrorǁ__init____mutmut_67, 
        'xǁCtyConversionErrorǁ__init____mutmut_68': xǁCtyConversionErrorǁ__init____mutmut_68, 
        'xǁCtyConversionErrorǁ__init____mutmut_69': xǁCtyConversionErrorǁ__init____mutmut_69, 
        'xǁCtyConversionErrorǁ__init____mutmut_70': xǁCtyConversionErrorǁ__init____mutmut_70, 
        'xǁCtyConversionErrorǁ__init____mutmut_71': xǁCtyConversionErrorǁ__init____mutmut_71, 
        'xǁCtyConversionErrorǁ__init____mutmut_72': xǁCtyConversionErrorǁ__init____mutmut_72, 
        'xǁCtyConversionErrorǁ__init____mutmut_73': xǁCtyConversionErrorǁ__init____mutmut_73, 
        'xǁCtyConversionErrorǁ__init____mutmut_74': xǁCtyConversionErrorǁ__init____mutmut_74, 
        'xǁCtyConversionErrorǁ__init____mutmut_75': xǁCtyConversionErrorǁ__init____mutmut_75, 
        'xǁCtyConversionErrorǁ__init____mutmut_76': xǁCtyConversionErrorǁ__init____mutmut_76, 
        'xǁCtyConversionErrorǁ__init____mutmut_77': xǁCtyConversionErrorǁ__init____mutmut_77, 
        'xǁCtyConversionErrorǁ__init____mutmut_78': xǁCtyConversionErrorǁ__init____mutmut_78, 
        'xǁCtyConversionErrorǁ__init____mutmut_79': xǁCtyConversionErrorǁ__init____mutmut_79, 
        'xǁCtyConversionErrorǁ__init____mutmut_80': xǁCtyConversionErrorǁ__init____mutmut_80, 
        'xǁCtyConversionErrorǁ__init____mutmut_81': xǁCtyConversionErrorǁ__init____mutmut_81, 
        'xǁCtyConversionErrorǁ__init____mutmut_82': xǁCtyConversionErrorǁ__init____mutmut_82, 
        'xǁCtyConversionErrorǁ__init____mutmut_83': xǁCtyConversionErrorǁ__init____mutmut_83
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCtyConversionErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁCtyConversionErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁCtyConversionErrorǁ__init____mutmut_orig)
    xǁCtyConversionErrorǁ__init____mutmut_orig.__name__ = 'xǁCtyConversionErrorǁ__init__'

    def xǁCtyConversionErrorǁ_default_code__mutmut_orig(self) -> str:
        return "CTY_CONVERSION_ERROR"

    def xǁCtyConversionErrorǁ_default_code__mutmut_1(self) -> str:
        return "XXCTY_CONVERSION_ERRORXX"

    def xǁCtyConversionErrorǁ_default_code__mutmut_2(self) -> str:
        return "cty_conversion_error"
    
    xǁCtyConversionErrorǁ_default_code__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCtyConversionErrorǁ_default_code__mutmut_1': xǁCtyConversionErrorǁ_default_code__mutmut_1, 
        'xǁCtyConversionErrorǁ_default_code__mutmut_2': xǁCtyConversionErrorǁ_default_code__mutmut_2
    }
    
    def _default_code(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCtyConversionErrorǁ_default_code__mutmut_orig"), object.__getattribute__(self, "xǁCtyConversionErrorǁ_default_code__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _default_code.__signature__ = _mutmut_signature(xǁCtyConversionErrorǁ_default_code__mutmut_orig)
    xǁCtyConversionErrorǁ_default_code__mutmut_orig.__name__ = 'xǁCtyConversionErrorǁ_default_code'


class CtyTypeConversionError(CtyConversionError):
    """CTY type representation conversion failure."""

    def xǁCtyTypeConversionErrorǁ__init____mutmut_orig(
        self,
        message: str,
        *,
        type_name: str | None = None,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyTypeConversionError.

        Args:
            message: The base error message.
            type_name: The name of the CTY type involved in the conversion failure.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
        """
        self.type_name = type_name

        # Add type-specific context
        context = kwargs.setdefault("context", {})
        context["cty.conversion_category"] = "type_representation"

        if type_name:
            context["cty.failing_type"] = type_name
            message = f'CTY Type "{type_name}" representation conversion failed: {message}'

        super().__init__(message, source_value=source_value, target_type=target_type, **kwargs)

    def xǁCtyTypeConversionErrorǁ__init____mutmut_1(
        self,
        message: str,
        *,
        type_name: str | None = None,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyTypeConversionError.

        Args:
            message: The base error message.
            type_name: The name of the CTY type involved in the conversion failure.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
        """
        self.type_name = None

        # Add type-specific context
        context = kwargs.setdefault("context", {})
        context["cty.conversion_category"] = "type_representation"

        if type_name:
            context["cty.failing_type"] = type_name
            message = f'CTY Type "{type_name}" representation conversion failed: {message}'

        super().__init__(message, source_value=source_value, target_type=target_type, **kwargs)

    def xǁCtyTypeConversionErrorǁ__init____mutmut_2(
        self,
        message: str,
        *,
        type_name: str | None = None,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyTypeConversionError.

        Args:
            message: The base error message.
            type_name: The name of the CTY type involved in the conversion failure.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
        """
        self.type_name = type_name

        # Add type-specific context
        context = None
        context["cty.conversion_category"] = "type_representation"

        if type_name:
            context["cty.failing_type"] = type_name
            message = f'CTY Type "{type_name}" representation conversion failed: {message}'

        super().__init__(message, source_value=source_value, target_type=target_type, **kwargs)

    def xǁCtyTypeConversionErrorǁ__init____mutmut_3(
        self,
        message: str,
        *,
        type_name: str | None = None,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyTypeConversionError.

        Args:
            message: The base error message.
            type_name: The name of the CTY type involved in the conversion failure.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
        """
        self.type_name = type_name

        # Add type-specific context
        context = kwargs.setdefault(None, {})
        context["cty.conversion_category"] = "type_representation"

        if type_name:
            context["cty.failing_type"] = type_name
            message = f'CTY Type "{type_name}" representation conversion failed: {message}'

        super().__init__(message, source_value=source_value, target_type=target_type, **kwargs)

    def xǁCtyTypeConversionErrorǁ__init____mutmut_4(
        self,
        message: str,
        *,
        type_name: str | None = None,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyTypeConversionError.

        Args:
            message: The base error message.
            type_name: The name of the CTY type involved in the conversion failure.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
        """
        self.type_name = type_name

        # Add type-specific context
        context = kwargs.setdefault("context", None)
        context["cty.conversion_category"] = "type_representation"

        if type_name:
            context["cty.failing_type"] = type_name
            message = f'CTY Type "{type_name}" representation conversion failed: {message}'

        super().__init__(message, source_value=source_value, target_type=target_type, **kwargs)

    def xǁCtyTypeConversionErrorǁ__init____mutmut_5(
        self,
        message: str,
        *,
        type_name: str | None = None,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyTypeConversionError.

        Args:
            message: The base error message.
            type_name: The name of the CTY type involved in the conversion failure.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
        """
        self.type_name = type_name

        # Add type-specific context
        context = kwargs.setdefault({})
        context["cty.conversion_category"] = "type_representation"

        if type_name:
            context["cty.failing_type"] = type_name
            message = f'CTY Type "{type_name}" representation conversion failed: {message}'

        super().__init__(message, source_value=source_value, target_type=target_type, **kwargs)

    def xǁCtyTypeConversionErrorǁ__init____mutmut_6(
        self,
        message: str,
        *,
        type_name: str | None = None,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyTypeConversionError.

        Args:
            message: The base error message.
            type_name: The name of the CTY type involved in the conversion failure.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
        """
        self.type_name = type_name

        # Add type-specific context
        context = kwargs.setdefault("context", )
        context["cty.conversion_category"] = "type_representation"

        if type_name:
            context["cty.failing_type"] = type_name
            message = f'CTY Type "{type_name}" representation conversion failed: {message}'

        super().__init__(message, source_value=source_value, target_type=target_type, **kwargs)

    def xǁCtyTypeConversionErrorǁ__init____mutmut_7(
        self,
        message: str,
        *,
        type_name: str | None = None,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyTypeConversionError.

        Args:
            message: The base error message.
            type_name: The name of the CTY type involved in the conversion failure.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
        """
        self.type_name = type_name

        # Add type-specific context
        context = kwargs.setdefault("XXcontextXX", {})
        context["cty.conversion_category"] = "type_representation"

        if type_name:
            context["cty.failing_type"] = type_name
            message = f'CTY Type "{type_name}" representation conversion failed: {message}'

        super().__init__(message, source_value=source_value, target_type=target_type, **kwargs)

    def xǁCtyTypeConversionErrorǁ__init____mutmut_8(
        self,
        message: str,
        *,
        type_name: str | None = None,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyTypeConversionError.

        Args:
            message: The base error message.
            type_name: The name of the CTY type involved in the conversion failure.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
        """
        self.type_name = type_name

        # Add type-specific context
        context = kwargs.setdefault("CONTEXT", {})
        context["cty.conversion_category"] = "type_representation"

        if type_name:
            context["cty.failing_type"] = type_name
            message = f'CTY Type "{type_name}" representation conversion failed: {message}'

        super().__init__(message, source_value=source_value, target_type=target_type, **kwargs)

    def xǁCtyTypeConversionErrorǁ__init____mutmut_9(
        self,
        message: str,
        *,
        type_name: str | None = None,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyTypeConversionError.

        Args:
            message: The base error message.
            type_name: The name of the CTY type involved in the conversion failure.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
        """
        self.type_name = type_name

        # Add type-specific context
        context = kwargs.setdefault("context", {})
        context["cty.conversion_category"] = None

        if type_name:
            context["cty.failing_type"] = type_name
            message = f'CTY Type "{type_name}" representation conversion failed: {message}'

        super().__init__(message, source_value=source_value, target_type=target_type, **kwargs)

    def xǁCtyTypeConversionErrorǁ__init____mutmut_10(
        self,
        message: str,
        *,
        type_name: str | None = None,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyTypeConversionError.

        Args:
            message: The base error message.
            type_name: The name of the CTY type involved in the conversion failure.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
        """
        self.type_name = type_name

        # Add type-specific context
        context = kwargs.setdefault("context", {})
        context["XXcty.conversion_categoryXX"] = "type_representation"

        if type_name:
            context["cty.failing_type"] = type_name
            message = f'CTY Type "{type_name}" representation conversion failed: {message}'

        super().__init__(message, source_value=source_value, target_type=target_type, **kwargs)

    def xǁCtyTypeConversionErrorǁ__init____mutmut_11(
        self,
        message: str,
        *,
        type_name: str | None = None,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyTypeConversionError.

        Args:
            message: The base error message.
            type_name: The name of the CTY type involved in the conversion failure.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
        """
        self.type_name = type_name

        # Add type-specific context
        context = kwargs.setdefault("context", {})
        context["CTY.CONVERSION_CATEGORY"] = "type_representation"

        if type_name:
            context["cty.failing_type"] = type_name
            message = f'CTY Type "{type_name}" representation conversion failed: {message}'

        super().__init__(message, source_value=source_value, target_type=target_type, **kwargs)

    def xǁCtyTypeConversionErrorǁ__init____mutmut_12(
        self,
        message: str,
        *,
        type_name: str | None = None,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyTypeConversionError.

        Args:
            message: The base error message.
            type_name: The name of the CTY type involved in the conversion failure.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
        """
        self.type_name = type_name

        # Add type-specific context
        context = kwargs.setdefault("context", {})
        context["cty.conversion_category"] = "XXtype_representationXX"

        if type_name:
            context["cty.failing_type"] = type_name
            message = f'CTY Type "{type_name}" representation conversion failed: {message}'

        super().__init__(message, source_value=source_value, target_type=target_type, **kwargs)

    def xǁCtyTypeConversionErrorǁ__init____mutmut_13(
        self,
        message: str,
        *,
        type_name: str | None = None,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyTypeConversionError.

        Args:
            message: The base error message.
            type_name: The name of the CTY type involved in the conversion failure.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
        """
        self.type_name = type_name

        # Add type-specific context
        context = kwargs.setdefault("context", {})
        context["cty.conversion_category"] = "TYPE_REPRESENTATION"

        if type_name:
            context["cty.failing_type"] = type_name
            message = f'CTY Type "{type_name}" representation conversion failed: {message}'

        super().__init__(message, source_value=source_value, target_type=target_type, **kwargs)

    def xǁCtyTypeConversionErrorǁ__init____mutmut_14(
        self,
        message: str,
        *,
        type_name: str | None = None,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyTypeConversionError.

        Args:
            message: The base error message.
            type_name: The name of the CTY type involved in the conversion failure.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
        """
        self.type_name = type_name

        # Add type-specific context
        context = kwargs.setdefault("context", {})
        context["cty.conversion_category"] = "type_representation"

        if type_name:
            context["cty.failing_type"] = None
            message = f'CTY Type "{type_name}" representation conversion failed: {message}'

        super().__init__(message, source_value=source_value, target_type=target_type, **kwargs)

    def xǁCtyTypeConversionErrorǁ__init____mutmut_15(
        self,
        message: str,
        *,
        type_name: str | None = None,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyTypeConversionError.

        Args:
            message: The base error message.
            type_name: The name of the CTY type involved in the conversion failure.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
        """
        self.type_name = type_name

        # Add type-specific context
        context = kwargs.setdefault("context", {})
        context["cty.conversion_category"] = "type_representation"

        if type_name:
            context["XXcty.failing_typeXX"] = type_name
            message = f'CTY Type "{type_name}" representation conversion failed: {message}'

        super().__init__(message, source_value=source_value, target_type=target_type, **kwargs)

    def xǁCtyTypeConversionErrorǁ__init____mutmut_16(
        self,
        message: str,
        *,
        type_name: str | None = None,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyTypeConversionError.

        Args:
            message: The base error message.
            type_name: The name of the CTY type involved in the conversion failure.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
        """
        self.type_name = type_name

        # Add type-specific context
        context = kwargs.setdefault("context", {})
        context["cty.conversion_category"] = "type_representation"

        if type_name:
            context["CTY.FAILING_TYPE"] = type_name
            message = f'CTY Type "{type_name}" representation conversion failed: {message}'

        super().__init__(message, source_value=source_value, target_type=target_type, **kwargs)

    def xǁCtyTypeConversionErrorǁ__init____mutmut_17(
        self,
        message: str,
        *,
        type_name: str | None = None,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyTypeConversionError.

        Args:
            message: The base error message.
            type_name: The name of the CTY type involved in the conversion failure.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
        """
        self.type_name = type_name

        # Add type-specific context
        context = kwargs.setdefault("context", {})
        context["cty.conversion_category"] = "type_representation"

        if type_name:
            context["cty.failing_type"] = type_name
            message = None

        super().__init__(message, source_value=source_value, target_type=target_type, **kwargs)

    def xǁCtyTypeConversionErrorǁ__init____mutmut_18(
        self,
        message: str,
        *,
        type_name: str | None = None,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyTypeConversionError.

        Args:
            message: The base error message.
            type_name: The name of the CTY type involved in the conversion failure.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
        """
        self.type_name = type_name

        # Add type-specific context
        context = kwargs.setdefault("context", {})
        context["cty.conversion_category"] = "type_representation"

        if type_name:
            context["cty.failing_type"] = type_name
            message = f'CTY Type "{type_name}" representation conversion failed: {message}'

        super().__init__(None, source_value=source_value, target_type=target_type, **kwargs)

    def xǁCtyTypeConversionErrorǁ__init____mutmut_19(
        self,
        message: str,
        *,
        type_name: str | None = None,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyTypeConversionError.

        Args:
            message: The base error message.
            type_name: The name of the CTY type involved in the conversion failure.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
        """
        self.type_name = type_name

        # Add type-specific context
        context = kwargs.setdefault("context", {})
        context["cty.conversion_category"] = "type_representation"

        if type_name:
            context["cty.failing_type"] = type_name
            message = f'CTY Type "{type_name}" representation conversion failed: {message}'

        super().__init__(message, source_value=None, target_type=target_type, **kwargs)

    def xǁCtyTypeConversionErrorǁ__init____mutmut_20(
        self,
        message: str,
        *,
        type_name: str | None = None,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyTypeConversionError.

        Args:
            message: The base error message.
            type_name: The name of the CTY type involved in the conversion failure.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
        """
        self.type_name = type_name

        # Add type-specific context
        context = kwargs.setdefault("context", {})
        context["cty.conversion_category"] = "type_representation"

        if type_name:
            context["cty.failing_type"] = type_name
            message = f'CTY Type "{type_name}" representation conversion failed: {message}'

        super().__init__(message, source_value=source_value, target_type=None, **kwargs)

    def xǁCtyTypeConversionErrorǁ__init____mutmut_21(
        self,
        message: str,
        *,
        type_name: str | None = None,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyTypeConversionError.

        Args:
            message: The base error message.
            type_name: The name of the CTY type involved in the conversion failure.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
        """
        self.type_name = type_name

        # Add type-specific context
        context = kwargs.setdefault("context", {})
        context["cty.conversion_category"] = "type_representation"

        if type_name:
            context["cty.failing_type"] = type_name
            message = f'CTY Type "{type_name}" representation conversion failed: {message}'

        super().__init__(source_value=source_value, target_type=target_type, **kwargs)

    def xǁCtyTypeConversionErrorǁ__init____mutmut_22(
        self,
        message: str,
        *,
        type_name: str | None = None,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyTypeConversionError.

        Args:
            message: The base error message.
            type_name: The name of the CTY type involved in the conversion failure.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
        """
        self.type_name = type_name

        # Add type-specific context
        context = kwargs.setdefault("context", {})
        context["cty.conversion_category"] = "type_representation"

        if type_name:
            context["cty.failing_type"] = type_name
            message = f'CTY Type "{type_name}" representation conversion failed: {message}'

        super().__init__(message, target_type=target_type, **kwargs)

    def xǁCtyTypeConversionErrorǁ__init____mutmut_23(
        self,
        message: str,
        *,
        type_name: str | None = None,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyTypeConversionError.

        Args:
            message: The base error message.
            type_name: The name of the CTY type involved in the conversion failure.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
        """
        self.type_name = type_name

        # Add type-specific context
        context = kwargs.setdefault("context", {})
        context["cty.conversion_category"] = "type_representation"

        if type_name:
            context["cty.failing_type"] = type_name
            message = f'CTY Type "{type_name}" representation conversion failed: {message}'

        super().__init__(message, source_value=source_value, **kwargs)

    def xǁCtyTypeConversionErrorǁ__init____mutmut_24(
        self,
        message: str,
        *,
        type_name: str | None = None,
        source_value: object | None = None,
        target_type: object | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the CtyTypeConversionError.

        Args:
            message: The base error message.
            type_name: The name of the CTY type involved in the conversion failure.
            source_value: The value that was being converted.
            target_type: The intended target type of the conversion.
        """
        self.type_name = type_name

        # Add type-specific context
        context = kwargs.setdefault("context", {})
        context["cty.conversion_category"] = "type_representation"

        if type_name:
            context["cty.failing_type"] = type_name
            message = f'CTY Type "{type_name}" representation conversion failed: {message}'

        super().__init__(message, source_value=source_value, target_type=target_type, )
    
    xǁCtyTypeConversionErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCtyTypeConversionErrorǁ__init____mutmut_1': xǁCtyTypeConversionErrorǁ__init____mutmut_1, 
        'xǁCtyTypeConversionErrorǁ__init____mutmut_2': xǁCtyTypeConversionErrorǁ__init____mutmut_2, 
        'xǁCtyTypeConversionErrorǁ__init____mutmut_3': xǁCtyTypeConversionErrorǁ__init____mutmut_3, 
        'xǁCtyTypeConversionErrorǁ__init____mutmut_4': xǁCtyTypeConversionErrorǁ__init____mutmut_4, 
        'xǁCtyTypeConversionErrorǁ__init____mutmut_5': xǁCtyTypeConversionErrorǁ__init____mutmut_5, 
        'xǁCtyTypeConversionErrorǁ__init____mutmut_6': xǁCtyTypeConversionErrorǁ__init____mutmut_6, 
        'xǁCtyTypeConversionErrorǁ__init____mutmut_7': xǁCtyTypeConversionErrorǁ__init____mutmut_7, 
        'xǁCtyTypeConversionErrorǁ__init____mutmut_8': xǁCtyTypeConversionErrorǁ__init____mutmut_8, 
        'xǁCtyTypeConversionErrorǁ__init____mutmut_9': xǁCtyTypeConversionErrorǁ__init____mutmut_9, 
        'xǁCtyTypeConversionErrorǁ__init____mutmut_10': xǁCtyTypeConversionErrorǁ__init____mutmut_10, 
        'xǁCtyTypeConversionErrorǁ__init____mutmut_11': xǁCtyTypeConversionErrorǁ__init____mutmut_11, 
        'xǁCtyTypeConversionErrorǁ__init____mutmut_12': xǁCtyTypeConversionErrorǁ__init____mutmut_12, 
        'xǁCtyTypeConversionErrorǁ__init____mutmut_13': xǁCtyTypeConversionErrorǁ__init____mutmut_13, 
        'xǁCtyTypeConversionErrorǁ__init____mutmut_14': xǁCtyTypeConversionErrorǁ__init____mutmut_14, 
        'xǁCtyTypeConversionErrorǁ__init____mutmut_15': xǁCtyTypeConversionErrorǁ__init____mutmut_15, 
        'xǁCtyTypeConversionErrorǁ__init____mutmut_16': xǁCtyTypeConversionErrorǁ__init____mutmut_16, 
        'xǁCtyTypeConversionErrorǁ__init____mutmut_17': xǁCtyTypeConversionErrorǁ__init____mutmut_17, 
        'xǁCtyTypeConversionErrorǁ__init____mutmut_18': xǁCtyTypeConversionErrorǁ__init____mutmut_18, 
        'xǁCtyTypeConversionErrorǁ__init____mutmut_19': xǁCtyTypeConversionErrorǁ__init____mutmut_19, 
        'xǁCtyTypeConversionErrorǁ__init____mutmut_20': xǁCtyTypeConversionErrorǁ__init____mutmut_20, 
        'xǁCtyTypeConversionErrorǁ__init____mutmut_21': xǁCtyTypeConversionErrorǁ__init____mutmut_21, 
        'xǁCtyTypeConversionErrorǁ__init____mutmut_22': xǁCtyTypeConversionErrorǁ__init____mutmut_22, 
        'xǁCtyTypeConversionErrorǁ__init____mutmut_23': xǁCtyTypeConversionErrorǁ__init____mutmut_23, 
        'xǁCtyTypeConversionErrorǁ__init____mutmut_24': xǁCtyTypeConversionErrorǁ__init____mutmut_24
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCtyTypeConversionErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁCtyTypeConversionErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁCtyTypeConversionErrorǁ__init____mutmut_orig)
    xǁCtyTypeConversionErrorǁ__init____mutmut_orig.__name__ = 'xǁCtyTypeConversionErrorǁ__init__'


class CtyTypeParseError(CtyConversionError):
    """Raised when a CTY type string cannot be parsed."""

    def xǁCtyTypeParseErrorǁ__init____mutmut_orig(self, message: str, type_string: str, **kwargs: Any) -> None:
        self.type_string = type_string

        # Add parsing context
        context = kwargs.setdefault("context", {})
        context["cty.conversion_category"] = "type_parsing"
        context["cty.parse_input"] = str(type_string)[:100]  # Truncate for safety
        context["cty.parse_input_type"] = type(type_string).__name__

        full_message = f"{message}: '{type_string}'"
        super().__init__(full_message, source_value=type_string, **kwargs)

    def xǁCtyTypeParseErrorǁ__init____mutmut_1(self, message: str, type_string: str, **kwargs: Any) -> None:
        self.type_string = None

        # Add parsing context
        context = kwargs.setdefault("context", {})
        context["cty.conversion_category"] = "type_parsing"
        context["cty.parse_input"] = str(type_string)[:100]  # Truncate for safety
        context["cty.parse_input_type"] = type(type_string).__name__

        full_message = f"{message}: '{type_string}'"
        super().__init__(full_message, source_value=type_string, **kwargs)

    def xǁCtyTypeParseErrorǁ__init____mutmut_2(self, message: str, type_string: str, **kwargs: Any) -> None:
        self.type_string = type_string

        # Add parsing context
        context = None
        context["cty.conversion_category"] = "type_parsing"
        context["cty.parse_input"] = str(type_string)[:100]  # Truncate for safety
        context["cty.parse_input_type"] = type(type_string).__name__

        full_message = f"{message}: '{type_string}'"
        super().__init__(full_message, source_value=type_string, **kwargs)

    def xǁCtyTypeParseErrorǁ__init____mutmut_3(self, message: str, type_string: str, **kwargs: Any) -> None:
        self.type_string = type_string

        # Add parsing context
        context = kwargs.setdefault(None, {})
        context["cty.conversion_category"] = "type_parsing"
        context["cty.parse_input"] = str(type_string)[:100]  # Truncate for safety
        context["cty.parse_input_type"] = type(type_string).__name__

        full_message = f"{message}: '{type_string}'"
        super().__init__(full_message, source_value=type_string, **kwargs)

    def xǁCtyTypeParseErrorǁ__init____mutmut_4(self, message: str, type_string: str, **kwargs: Any) -> None:
        self.type_string = type_string

        # Add parsing context
        context = kwargs.setdefault("context", None)
        context["cty.conversion_category"] = "type_parsing"
        context["cty.parse_input"] = str(type_string)[:100]  # Truncate for safety
        context["cty.parse_input_type"] = type(type_string).__name__

        full_message = f"{message}: '{type_string}'"
        super().__init__(full_message, source_value=type_string, **kwargs)

    def xǁCtyTypeParseErrorǁ__init____mutmut_5(self, message: str, type_string: str, **kwargs: Any) -> None:
        self.type_string = type_string

        # Add parsing context
        context = kwargs.setdefault({})
        context["cty.conversion_category"] = "type_parsing"
        context["cty.parse_input"] = str(type_string)[:100]  # Truncate for safety
        context["cty.parse_input_type"] = type(type_string).__name__

        full_message = f"{message}: '{type_string}'"
        super().__init__(full_message, source_value=type_string, **kwargs)

    def xǁCtyTypeParseErrorǁ__init____mutmut_6(self, message: str, type_string: str, **kwargs: Any) -> None:
        self.type_string = type_string

        # Add parsing context
        context = kwargs.setdefault("context", )
        context["cty.conversion_category"] = "type_parsing"
        context["cty.parse_input"] = str(type_string)[:100]  # Truncate for safety
        context["cty.parse_input_type"] = type(type_string).__name__

        full_message = f"{message}: '{type_string}'"
        super().__init__(full_message, source_value=type_string, **kwargs)

    def xǁCtyTypeParseErrorǁ__init____mutmut_7(self, message: str, type_string: str, **kwargs: Any) -> None:
        self.type_string = type_string

        # Add parsing context
        context = kwargs.setdefault("XXcontextXX", {})
        context["cty.conversion_category"] = "type_parsing"
        context["cty.parse_input"] = str(type_string)[:100]  # Truncate for safety
        context["cty.parse_input_type"] = type(type_string).__name__

        full_message = f"{message}: '{type_string}'"
        super().__init__(full_message, source_value=type_string, **kwargs)

    def xǁCtyTypeParseErrorǁ__init____mutmut_8(self, message: str, type_string: str, **kwargs: Any) -> None:
        self.type_string = type_string

        # Add parsing context
        context = kwargs.setdefault("CONTEXT", {})
        context["cty.conversion_category"] = "type_parsing"
        context["cty.parse_input"] = str(type_string)[:100]  # Truncate for safety
        context["cty.parse_input_type"] = type(type_string).__name__

        full_message = f"{message}: '{type_string}'"
        super().__init__(full_message, source_value=type_string, **kwargs)

    def xǁCtyTypeParseErrorǁ__init____mutmut_9(self, message: str, type_string: str, **kwargs: Any) -> None:
        self.type_string = type_string

        # Add parsing context
        context = kwargs.setdefault("context", {})
        context["cty.conversion_category"] = None
        context["cty.parse_input"] = str(type_string)[:100]  # Truncate for safety
        context["cty.parse_input_type"] = type(type_string).__name__

        full_message = f"{message}: '{type_string}'"
        super().__init__(full_message, source_value=type_string, **kwargs)

    def xǁCtyTypeParseErrorǁ__init____mutmut_10(self, message: str, type_string: str, **kwargs: Any) -> None:
        self.type_string = type_string

        # Add parsing context
        context = kwargs.setdefault("context", {})
        context["XXcty.conversion_categoryXX"] = "type_parsing"
        context["cty.parse_input"] = str(type_string)[:100]  # Truncate for safety
        context["cty.parse_input_type"] = type(type_string).__name__

        full_message = f"{message}: '{type_string}'"
        super().__init__(full_message, source_value=type_string, **kwargs)

    def xǁCtyTypeParseErrorǁ__init____mutmut_11(self, message: str, type_string: str, **kwargs: Any) -> None:
        self.type_string = type_string

        # Add parsing context
        context = kwargs.setdefault("context", {})
        context["CTY.CONVERSION_CATEGORY"] = "type_parsing"
        context["cty.parse_input"] = str(type_string)[:100]  # Truncate for safety
        context["cty.parse_input_type"] = type(type_string).__name__

        full_message = f"{message}: '{type_string}'"
        super().__init__(full_message, source_value=type_string, **kwargs)

    def xǁCtyTypeParseErrorǁ__init____mutmut_12(self, message: str, type_string: str, **kwargs: Any) -> None:
        self.type_string = type_string

        # Add parsing context
        context = kwargs.setdefault("context", {})
        context["cty.conversion_category"] = "XXtype_parsingXX"
        context["cty.parse_input"] = str(type_string)[:100]  # Truncate for safety
        context["cty.parse_input_type"] = type(type_string).__name__

        full_message = f"{message}: '{type_string}'"
        super().__init__(full_message, source_value=type_string, **kwargs)

    def xǁCtyTypeParseErrorǁ__init____mutmut_13(self, message: str, type_string: str, **kwargs: Any) -> None:
        self.type_string = type_string

        # Add parsing context
        context = kwargs.setdefault("context", {})
        context["cty.conversion_category"] = "TYPE_PARSING"
        context["cty.parse_input"] = str(type_string)[:100]  # Truncate for safety
        context["cty.parse_input_type"] = type(type_string).__name__

        full_message = f"{message}: '{type_string}'"
        super().__init__(full_message, source_value=type_string, **kwargs)

    def xǁCtyTypeParseErrorǁ__init____mutmut_14(self, message: str, type_string: str, **kwargs: Any) -> None:
        self.type_string = type_string

        # Add parsing context
        context = kwargs.setdefault("context", {})
        context["cty.conversion_category"] = "type_parsing"
        context["cty.parse_input"] = None  # Truncate for safety
        context["cty.parse_input_type"] = type(type_string).__name__

        full_message = f"{message}: '{type_string}'"
        super().__init__(full_message, source_value=type_string, **kwargs)

    def xǁCtyTypeParseErrorǁ__init____mutmut_15(self, message: str, type_string: str, **kwargs: Any) -> None:
        self.type_string = type_string

        # Add parsing context
        context = kwargs.setdefault("context", {})
        context["cty.conversion_category"] = "type_parsing"
        context["XXcty.parse_inputXX"] = str(type_string)[:100]  # Truncate for safety
        context["cty.parse_input_type"] = type(type_string).__name__

        full_message = f"{message}: '{type_string}'"
        super().__init__(full_message, source_value=type_string, **kwargs)

    def xǁCtyTypeParseErrorǁ__init____mutmut_16(self, message: str, type_string: str, **kwargs: Any) -> None:
        self.type_string = type_string

        # Add parsing context
        context = kwargs.setdefault("context", {})
        context["cty.conversion_category"] = "type_parsing"
        context["CTY.PARSE_INPUT"] = str(type_string)[:100]  # Truncate for safety
        context["cty.parse_input_type"] = type(type_string).__name__

        full_message = f"{message}: '{type_string}'"
        super().__init__(full_message, source_value=type_string, **kwargs)

    def xǁCtyTypeParseErrorǁ__init____mutmut_17(self, message: str, type_string: str, **kwargs: Any) -> None:
        self.type_string = type_string

        # Add parsing context
        context = kwargs.setdefault("context", {})
        context["cty.conversion_category"] = "type_parsing"
        context["cty.parse_input"] = str(None)[:100]  # Truncate for safety
        context["cty.parse_input_type"] = type(type_string).__name__

        full_message = f"{message}: '{type_string}'"
        super().__init__(full_message, source_value=type_string, **kwargs)

    def xǁCtyTypeParseErrorǁ__init____mutmut_18(self, message: str, type_string: str, **kwargs: Any) -> None:
        self.type_string = type_string

        # Add parsing context
        context = kwargs.setdefault("context", {})
        context["cty.conversion_category"] = "type_parsing"
        context["cty.parse_input"] = str(type_string)[:101]  # Truncate for safety
        context["cty.parse_input_type"] = type(type_string).__name__

        full_message = f"{message}: '{type_string}'"
        super().__init__(full_message, source_value=type_string, **kwargs)

    def xǁCtyTypeParseErrorǁ__init____mutmut_19(self, message: str, type_string: str, **kwargs: Any) -> None:
        self.type_string = type_string

        # Add parsing context
        context = kwargs.setdefault("context", {})
        context["cty.conversion_category"] = "type_parsing"
        context["cty.parse_input"] = str(type_string)[:100]  # Truncate for safety
        context["cty.parse_input_type"] = None

        full_message = f"{message}: '{type_string}'"
        super().__init__(full_message, source_value=type_string, **kwargs)

    def xǁCtyTypeParseErrorǁ__init____mutmut_20(self, message: str, type_string: str, **kwargs: Any) -> None:
        self.type_string = type_string

        # Add parsing context
        context = kwargs.setdefault("context", {})
        context["cty.conversion_category"] = "type_parsing"
        context["cty.parse_input"] = str(type_string)[:100]  # Truncate for safety
        context["XXcty.parse_input_typeXX"] = type(type_string).__name__

        full_message = f"{message}: '{type_string}'"
        super().__init__(full_message, source_value=type_string, **kwargs)

    def xǁCtyTypeParseErrorǁ__init____mutmut_21(self, message: str, type_string: str, **kwargs: Any) -> None:
        self.type_string = type_string

        # Add parsing context
        context = kwargs.setdefault("context", {})
        context["cty.conversion_category"] = "type_parsing"
        context["cty.parse_input"] = str(type_string)[:100]  # Truncate for safety
        context["CTY.PARSE_INPUT_TYPE"] = type(type_string).__name__

        full_message = f"{message}: '{type_string}'"
        super().__init__(full_message, source_value=type_string, **kwargs)

    def xǁCtyTypeParseErrorǁ__init____mutmut_22(self, message: str, type_string: str, **kwargs: Any) -> None:
        self.type_string = type_string

        # Add parsing context
        context = kwargs.setdefault("context", {})
        context["cty.conversion_category"] = "type_parsing"
        context["cty.parse_input"] = str(type_string)[:100]  # Truncate for safety
        context["cty.parse_input_type"] = type(None).__name__

        full_message = f"{message}: '{type_string}'"
        super().__init__(full_message, source_value=type_string, **kwargs)

    def xǁCtyTypeParseErrorǁ__init____mutmut_23(self, message: str, type_string: str, **kwargs: Any) -> None:
        self.type_string = type_string

        # Add parsing context
        context = kwargs.setdefault("context", {})
        context["cty.conversion_category"] = "type_parsing"
        context["cty.parse_input"] = str(type_string)[:100]  # Truncate for safety
        context["cty.parse_input_type"] = type(type_string).__name__

        full_message = None
        super().__init__(full_message, source_value=type_string, **kwargs)

    def xǁCtyTypeParseErrorǁ__init____mutmut_24(self, message: str, type_string: str, **kwargs: Any) -> None:
        self.type_string = type_string

        # Add parsing context
        context = kwargs.setdefault("context", {})
        context["cty.conversion_category"] = "type_parsing"
        context["cty.parse_input"] = str(type_string)[:100]  # Truncate for safety
        context["cty.parse_input_type"] = type(type_string).__name__

        full_message = f"{message}: '{type_string}'"
        super().__init__(None, source_value=type_string, **kwargs)

    def xǁCtyTypeParseErrorǁ__init____mutmut_25(self, message: str, type_string: str, **kwargs: Any) -> None:
        self.type_string = type_string

        # Add parsing context
        context = kwargs.setdefault("context", {})
        context["cty.conversion_category"] = "type_parsing"
        context["cty.parse_input"] = str(type_string)[:100]  # Truncate for safety
        context["cty.parse_input_type"] = type(type_string).__name__

        full_message = f"{message}: '{type_string}'"
        super().__init__(full_message, source_value=None, **kwargs)

    def xǁCtyTypeParseErrorǁ__init____mutmut_26(self, message: str, type_string: str, **kwargs: Any) -> None:
        self.type_string = type_string

        # Add parsing context
        context = kwargs.setdefault("context", {})
        context["cty.conversion_category"] = "type_parsing"
        context["cty.parse_input"] = str(type_string)[:100]  # Truncate for safety
        context["cty.parse_input_type"] = type(type_string).__name__

        full_message = f"{message}: '{type_string}'"
        super().__init__(source_value=type_string, **kwargs)

    def xǁCtyTypeParseErrorǁ__init____mutmut_27(self, message: str, type_string: str, **kwargs: Any) -> None:
        self.type_string = type_string

        # Add parsing context
        context = kwargs.setdefault("context", {})
        context["cty.conversion_category"] = "type_parsing"
        context["cty.parse_input"] = str(type_string)[:100]  # Truncate for safety
        context["cty.parse_input_type"] = type(type_string).__name__

        full_message = f"{message}: '{type_string}'"
        super().__init__(full_message, **kwargs)

    def xǁCtyTypeParseErrorǁ__init____mutmut_28(self, message: str, type_string: str, **kwargs: Any) -> None:
        self.type_string = type_string

        # Add parsing context
        context = kwargs.setdefault("context", {})
        context["cty.conversion_category"] = "type_parsing"
        context["cty.parse_input"] = str(type_string)[:100]  # Truncate for safety
        context["cty.parse_input_type"] = type(type_string).__name__

        full_message = f"{message}: '{type_string}'"
        super().__init__(full_message, source_value=type_string, )
    
    xǁCtyTypeParseErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCtyTypeParseErrorǁ__init____mutmut_1': xǁCtyTypeParseErrorǁ__init____mutmut_1, 
        'xǁCtyTypeParseErrorǁ__init____mutmut_2': xǁCtyTypeParseErrorǁ__init____mutmut_2, 
        'xǁCtyTypeParseErrorǁ__init____mutmut_3': xǁCtyTypeParseErrorǁ__init____mutmut_3, 
        'xǁCtyTypeParseErrorǁ__init____mutmut_4': xǁCtyTypeParseErrorǁ__init____mutmut_4, 
        'xǁCtyTypeParseErrorǁ__init____mutmut_5': xǁCtyTypeParseErrorǁ__init____mutmut_5, 
        'xǁCtyTypeParseErrorǁ__init____mutmut_6': xǁCtyTypeParseErrorǁ__init____mutmut_6, 
        'xǁCtyTypeParseErrorǁ__init____mutmut_7': xǁCtyTypeParseErrorǁ__init____mutmut_7, 
        'xǁCtyTypeParseErrorǁ__init____mutmut_8': xǁCtyTypeParseErrorǁ__init____mutmut_8, 
        'xǁCtyTypeParseErrorǁ__init____mutmut_9': xǁCtyTypeParseErrorǁ__init____mutmut_9, 
        'xǁCtyTypeParseErrorǁ__init____mutmut_10': xǁCtyTypeParseErrorǁ__init____mutmut_10, 
        'xǁCtyTypeParseErrorǁ__init____mutmut_11': xǁCtyTypeParseErrorǁ__init____mutmut_11, 
        'xǁCtyTypeParseErrorǁ__init____mutmut_12': xǁCtyTypeParseErrorǁ__init____mutmut_12, 
        'xǁCtyTypeParseErrorǁ__init____mutmut_13': xǁCtyTypeParseErrorǁ__init____mutmut_13, 
        'xǁCtyTypeParseErrorǁ__init____mutmut_14': xǁCtyTypeParseErrorǁ__init____mutmut_14, 
        'xǁCtyTypeParseErrorǁ__init____mutmut_15': xǁCtyTypeParseErrorǁ__init____mutmut_15, 
        'xǁCtyTypeParseErrorǁ__init____mutmut_16': xǁCtyTypeParseErrorǁ__init____mutmut_16, 
        'xǁCtyTypeParseErrorǁ__init____mutmut_17': xǁCtyTypeParseErrorǁ__init____mutmut_17, 
        'xǁCtyTypeParseErrorǁ__init____mutmut_18': xǁCtyTypeParseErrorǁ__init____mutmut_18, 
        'xǁCtyTypeParseErrorǁ__init____mutmut_19': xǁCtyTypeParseErrorǁ__init____mutmut_19, 
        'xǁCtyTypeParseErrorǁ__init____mutmut_20': xǁCtyTypeParseErrorǁ__init____mutmut_20, 
        'xǁCtyTypeParseErrorǁ__init____mutmut_21': xǁCtyTypeParseErrorǁ__init____mutmut_21, 
        'xǁCtyTypeParseErrorǁ__init____mutmut_22': xǁCtyTypeParseErrorǁ__init____mutmut_22, 
        'xǁCtyTypeParseErrorǁ__init____mutmut_23': xǁCtyTypeParseErrorǁ__init____mutmut_23, 
        'xǁCtyTypeParseErrorǁ__init____mutmut_24': xǁCtyTypeParseErrorǁ__init____mutmut_24, 
        'xǁCtyTypeParseErrorǁ__init____mutmut_25': xǁCtyTypeParseErrorǁ__init____mutmut_25, 
        'xǁCtyTypeParseErrorǁ__init____mutmut_26': xǁCtyTypeParseErrorǁ__init____mutmut_26, 
        'xǁCtyTypeParseErrorǁ__init____mutmut_27': xǁCtyTypeParseErrorǁ__init____mutmut_27, 
        'xǁCtyTypeParseErrorǁ__init____mutmut_28': xǁCtyTypeParseErrorǁ__init____mutmut_28
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCtyTypeParseErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁCtyTypeParseErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁCtyTypeParseErrorǁ__init____mutmut_orig)
    xǁCtyTypeParseErrorǁ__init____mutmut_orig.__name__ = 'xǁCtyTypeParseErrorǁ__init__'


__all__ = ["CtyConversionError", "CtyTypeConversionError", "CtyTypeParseError"]
# 🌊🪢🐛🪄
