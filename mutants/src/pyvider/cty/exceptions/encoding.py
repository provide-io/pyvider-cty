# pyvider/cty/exceptions/encoding.py
#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Any, cast

from pyvider.cty.exceptions.base import CtyError

#
# pyvider/cty/exceptions/encoding.py
#
"""
Defines exceptions related to CTY schema transformations, path errors,
and general encoding/serialization processes.
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

################################################################################
# Transformation and Path Errors
################################################################################


class TransformationError(CtyError):
    """
    Raised when a schema transformation fails.

    This exception occurs when a schema cannot be transformed from one
    representation to another, such as during conversion between different
    schema formats or when applying schema transformations.

    Attributes:
        message: A human-readable error description
        schema: The schema that failed transformation
        target_type: The intended target type of a transformation, if applicable
    """

    def xǁTransformationErrorǁ__init____mutmut_orig(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_1(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = None
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_2(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = None

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_3(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = None  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_4(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault(None, {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_5(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", None)  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_6(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault({})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_7(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", )  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_8(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("XXcontextXX", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_9(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("CONTEXT", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_10(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = None
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_11(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["XXcty.operationXX"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_12(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["CTY.OPERATION"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_13(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "XXschema_transformationXX"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_14(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "SCHEMA_TRANSFORMATION"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_15(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = None

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_16(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["XXcty.error_categoryXX"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_17(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["CTY.ERROR_CATEGORY"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_18(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "XXtransformationXX"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_19(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "TRANSFORMATION"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_20(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_21(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = None
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_22(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["XXtransformation.schema_typeXX"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_23(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["TRANSFORMATION.SCHEMA_TYPE"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_24(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(None).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_25(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = None

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_26(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["XXcty.source_schema_typeXX"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_27(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["CTY.SOURCE_SCHEMA_TYPE"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_28(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(None).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_29(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_30(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = None
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_31(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(None, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_32(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, None, str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_33(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", None)
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_34(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr("__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_35(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_36(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", )
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_37(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "XX__name__XX", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_38(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__NAME__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_39(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(None))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_40(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = None
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_41(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["XXtransformation.target_typeXX"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_42(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["TRANSFORMATION.TARGET_TYPE"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_43(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = None

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_44(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["XXcty.target_typeXX"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_45(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["CTY.TARGET_TYPE"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_46(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = None
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_47(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_48(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(None)
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_49(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(None).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_50(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_51(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = None
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_52(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(None, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_53(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, None, str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_54(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", None)
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_55(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr("__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_56(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_57(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", )
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_58(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "XX__name__XX", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_59(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__NAME__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_60(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(None))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_61(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(None)

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_62(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = None

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_63(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(None)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_64(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({'XX, XX'.join(context_parts)})"

        super().__init__(message, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_65(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(None, **kwargs)

    def xǁTransformationErrorǁ__init____mutmut_66(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(**kwargs)

    def xǁTransformationErrorǁ__init____mutmut_67(
        self,
        message: str,
        schema: object = None,
        target_type: object = None,
        **kwargs: object,
    ) -> None:
        """
        Initializes the TransformationError.

        Args:
            message: The base error message.
            schema: The schema object that was being transformed.
            target_type: The intended target type of the transformation.
            **kwargs: Additional keyword arguments for foundation error context.
        """
        self.schema = schema
        self.target_type = target_type

        # Add rich transformation context
        # kwargs.setdefault returns object, but we know it's dict[str, Any]
        context: dict[str, Any] = kwargs.setdefault("context", {})  # type: ignore[assignment]
        context["cty.operation"] = "schema_transformation"
        context["cty.error_category"] = "transformation"

        if schema is not None:
            context["transformation.schema_type"] = type(schema).__name__
            context["cty.source_schema_type"] = type(schema).__name__

        if target_type is not None:
            target_name = getattr(target_type, "__name__", str(target_type))
            context["transformation.target_type"] = target_name
            context["cty.target_type"] = target_name

        context_parts = []
        if schema is not None:
            context_parts.append(f"schema_type={type(schema).__name__}")
        if target_type is not None:
            target_type_name = getattr(target_type, "__name__", str(target_type))
            context_parts.append(f"target_type={target_type_name}")

        if context_parts:
            message = f"{message} ({', '.join(context_parts)})"

        super().__init__(message, )
    
    xǁTransformationErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁTransformationErrorǁ__init____mutmut_1': xǁTransformationErrorǁ__init____mutmut_1, 
        'xǁTransformationErrorǁ__init____mutmut_2': xǁTransformationErrorǁ__init____mutmut_2, 
        'xǁTransformationErrorǁ__init____mutmut_3': xǁTransformationErrorǁ__init____mutmut_3, 
        'xǁTransformationErrorǁ__init____mutmut_4': xǁTransformationErrorǁ__init____mutmut_4, 
        'xǁTransformationErrorǁ__init____mutmut_5': xǁTransformationErrorǁ__init____mutmut_5, 
        'xǁTransformationErrorǁ__init____mutmut_6': xǁTransformationErrorǁ__init____mutmut_6, 
        'xǁTransformationErrorǁ__init____mutmut_7': xǁTransformationErrorǁ__init____mutmut_7, 
        'xǁTransformationErrorǁ__init____mutmut_8': xǁTransformationErrorǁ__init____mutmut_8, 
        'xǁTransformationErrorǁ__init____mutmut_9': xǁTransformationErrorǁ__init____mutmut_9, 
        'xǁTransformationErrorǁ__init____mutmut_10': xǁTransformationErrorǁ__init____mutmut_10, 
        'xǁTransformationErrorǁ__init____mutmut_11': xǁTransformationErrorǁ__init____mutmut_11, 
        'xǁTransformationErrorǁ__init____mutmut_12': xǁTransformationErrorǁ__init____mutmut_12, 
        'xǁTransformationErrorǁ__init____mutmut_13': xǁTransformationErrorǁ__init____mutmut_13, 
        'xǁTransformationErrorǁ__init____mutmut_14': xǁTransformationErrorǁ__init____mutmut_14, 
        'xǁTransformationErrorǁ__init____mutmut_15': xǁTransformationErrorǁ__init____mutmut_15, 
        'xǁTransformationErrorǁ__init____mutmut_16': xǁTransformationErrorǁ__init____mutmut_16, 
        'xǁTransformationErrorǁ__init____mutmut_17': xǁTransformationErrorǁ__init____mutmut_17, 
        'xǁTransformationErrorǁ__init____mutmut_18': xǁTransformationErrorǁ__init____mutmut_18, 
        'xǁTransformationErrorǁ__init____mutmut_19': xǁTransformationErrorǁ__init____mutmut_19, 
        'xǁTransformationErrorǁ__init____mutmut_20': xǁTransformationErrorǁ__init____mutmut_20, 
        'xǁTransformationErrorǁ__init____mutmut_21': xǁTransformationErrorǁ__init____mutmut_21, 
        'xǁTransformationErrorǁ__init____mutmut_22': xǁTransformationErrorǁ__init____mutmut_22, 
        'xǁTransformationErrorǁ__init____mutmut_23': xǁTransformationErrorǁ__init____mutmut_23, 
        'xǁTransformationErrorǁ__init____mutmut_24': xǁTransformationErrorǁ__init____mutmut_24, 
        'xǁTransformationErrorǁ__init____mutmut_25': xǁTransformationErrorǁ__init____mutmut_25, 
        'xǁTransformationErrorǁ__init____mutmut_26': xǁTransformationErrorǁ__init____mutmut_26, 
        'xǁTransformationErrorǁ__init____mutmut_27': xǁTransformationErrorǁ__init____mutmut_27, 
        'xǁTransformationErrorǁ__init____mutmut_28': xǁTransformationErrorǁ__init____mutmut_28, 
        'xǁTransformationErrorǁ__init____mutmut_29': xǁTransformationErrorǁ__init____mutmut_29, 
        'xǁTransformationErrorǁ__init____mutmut_30': xǁTransformationErrorǁ__init____mutmut_30, 
        'xǁTransformationErrorǁ__init____mutmut_31': xǁTransformationErrorǁ__init____mutmut_31, 
        'xǁTransformationErrorǁ__init____mutmut_32': xǁTransformationErrorǁ__init____mutmut_32, 
        'xǁTransformationErrorǁ__init____mutmut_33': xǁTransformationErrorǁ__init____mutmut_33, 
        'xǁTransformationErrorǁ__init____mutmut_34': xǁTransformationErrorǁ__init____mutmut_34, 
        'xǁTransformationErrorǁ__init____mutmut_35': xǁTransformationErrorǁ__init____mutmut_35, 
        'xǁTransformationErrorǁ__init____mutmut_36': xǁTransformationErrorǁ__init____mutmut_36, 
        'xǁTransformationErrorǁ__init____mutmut_37': xǁTransformationErrorǁ__init____mutmut_37, 
        'xǁTransformationErrorǁ__init____mutmut_38': xǁTransformationErrorǁ__init____mutmut_38, 
        'xǁTransformationErrorǁ__init____mutmut_39': xǁTransformationErrorǁ__init____mutmut_39, 
        'xǁTransformationErrorǁ__init____mutmut_40': xǁTransformationErrorǁ__init____mutmut_40, 
        'xǁTransformationErrorǁ__init____mutmut_41': xǁTransformationErrorǁ__init____mutmut_41, 
        'xǁTransformationErrorǁ__init____mutmut_42': xǁTransformationErrorǁ__init____mutmut_42, 
        'xǁTransformationErrorǁ__init____mutmut_43': xǁTransformationErrorǁ__init____mutmut_43, 
        'xǁTransformationErrorǁ__init____mutmut_44': xǁTransformationErrorǁ__init____mutmut_44, 
        'xǁTransformationErrorǁ__init____mutmut_45': xǁTransformationErrorǁ__init____mutmut_45, 
        'xǁTransformationErrorǁ__init____mutmut_46': xǁTransformationErrorǁ__init____mutmut_46, 
        'xǁTransformationErrorǁ__init____mutmut_47': xǁTransformationErrorǁ__init____mutmut_47, 
        'xǁTransformationErrorǁ__init____mutmut_48': xǁTransformationErrorǁ__init____mutmut_48, 
        'xǁTransformationErrorǁ__init____mutmut_49': xǁTransformationErrorǁ__init____mutmut_49, 
        'xǁTransformationErrorǁ__init____mutmut_50': xǁTransformationErrorǁ__init____mutmut_50, 
        'xǁTransformationErrorǁ__init____mutmut_51': xǁTransformationErrorǁ__init____mutmut_51, 
        'xǁTransformationErrorǁ__init____mutmut_52': xǁTransformationErrorǁ__init____mutmut_52, 
        'xǁTransformationErrorǁ__init____mutmut_53': xǁTransformationErrorǁ__init____mutmut_53, 
        'xǁTransformationErrorǁ__init____mutmut_54': xǁTransformationErrorǁ__init____mutmut_54, 
        'xǁTransformationErrorǁ__init____mutmut_55': xǁTransformationErrorǁ__init____mutmut_55, 
        'xǁTransformationErrorǁ__init____mutmut_56': xǁTransformationErrorǁ__init____mutmut_56, 
        'xǁTransformationErrorǁ__init____mutmut_57': xǁTransformationErrorǁ__init____mutmut_57, 
        'xǁTransformationErrorǁ__init____mutmut_58': xǁTransformationErrorǁ__init____mutmut_58, 
        'xǁTransformationErrorǁ__init____mutmut_59': xǁTransformationErrorǁ__init____mutmut_59, 
        'xǁTransformationErrorǁ__init____mutmut_60': xǁTransformationErrorǁ__init____mutmut_60, 
        'xǁTransformationErrorǁ__init____mutmut_61': xǁTransformationErrorǁ__init____mutmut_61, 
        'xǁTransformationErrorǁ__init____mutmut_62': xǁTransformationErrorǁ__init____mutmut_62, 
        'xǁTransformationErrorǁ__init____mutmut_63': xǁTransformationErrorǁ__init____mutmut_63, 
        'xǁTransformationErrorǁ__init____mutmut_64': xǁTransformationErrorǁ__init____mutmut_64, 
        'xǁTransformationErrorǁ__init____mutmut_65': xǁTransformationErrorǁ__init____mutmut_65, 
        'xǁTransformationErrorǁ__init____mutmut_66': xǁTransformationErrorǁ__init____mutmut_66, 
        'xǁTransformationErrorǁ__init____mutmut_67': xǁTransformationErrorǁ__init____mutmut_67
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁTransformationErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁTransformationErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁTransformationErrorǁ__init____mutmut_orig)
    xǁTransformationErrorǁ__init____mutmut_orig.__name__ = 'xǁTransformationErrorǁ__init__'


class InvalidTypeError(CtyError):
    """
    Raised when an invalid type is used in a type definition.

    This exception occurs when attempting to create a type with invalid
    parameters or constraints, such as using a non-CtyType instance when
    a CtyType is required.

    Attributes:
        message: A human-readable error description
        invalid_type: The invalid type that caused the error
    """

    def xǁInvalidTypeErrorǁ__init____mutmut_orig(self, message: str, invalid_type: object = None, **kwargs: Any) -> None:
        """
        Initializes the InvalidTypeError.

        Args:
            message: The base error message.
            invalid_type: The type object that was found to be invalid.
        """
        self.invalid_type = invalid_type

        # Add type validation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "invalid_type"
        context["cty.validation_stage"] = "type_definition"

        if invalid_type is not None:
            context["cty.invalid_type"] = type(invalid_type).__name__
            context["cty.invalid_type_str"] = str(invalid_type)[:100]  # Truncated for safety

        super().__init__(message, **kwargs)

    def xǁInvalidTypeErrorǁ__init____mutmut_1(self, message: str, invalid_type: object = None, **kwargs: Any) -> None:
        """
        Initializes the InvalidTypeError.

        Args:
            message: The base error message.
            invalid_type: The type object that was found to be invalid.
        """
        self.invalid_type = None

        # Add type validation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "invalid_type"
        context["cty.validation_stage"] = "type_definition"

        if invalid_type is not None:
            context["cty.invalid_type"] = type(invalid_type).__name__
            context["cty.invalid_type_str"] = str(invalid_type)[:100]  # Truncated for safety

        super().__init__(message, **kwargs)

    def xǁInvalidTypeErrorǁ__init____mutmut_2(self, message: str, invalid_type: object = None, **kwargs: Any) -> None:
        """
        Initializes the InvalidTypeError.

        Args:
            message: The base error message.
            invalid_type: The type object that was found to be invalid.
        """
        self.invalid_type = invalid_type

        # Add type validation context
        context: dict[str, Any] = None
        context["cty.error_category"] = "invalid_type"
        context["cty.validation_stage"] = "type_definition"

        if invalid_type is not None:
            context["cty.invalid_type"] = type(invalid_type).__name__
            context["cty.invalid_type_str"] = str(invalid_type)[:100]  # Truncated for safety

        super().__init__(message, **kwargs)

    def xǁInvalidTypeErrorǁ__init____mutmut_3(self, message: str, invalid_type: object = None, **kwargs: Any) -> None:
        """
        Initializes the InvalidTypeError.

        Args:
            message: The base error message.
            invalid_type: The type object that was found to be invalid.
        """
        self.invalid_type = invalid_type

        # Add type validation context
        context: dict[str, Any] = kwargs.setdefault(None, {})
        context["cty.error_category"] = "invalid_type"
        context["cty.validation_stage"] = "type_definition"

        if invalid_type is not None:
            context["cty.invalid_type"] = type(invalid_type).__name__
            context["cty.invalid_type_str"] = str(invalid_type)[:100]  # Truncated for safety

        super().__init__(message, **kwargs)

    def xǁInvalidTypeErrorǁ__init____mutmut_4(self, message: str, invalid_type: object = None, **kwargs: Any) -> None:
        """
        Initializes the InvalidTypeError.

        Args:
            message: The base error message.
            invalid_type: The type object that was found to be invalid.
        """
        self.invalid_type = invalid_type

        # Add type validation context
        context: dict[str, Any] = kwargs.setdefault("context", None)
        context["cty.error_category"] = "invalid_type"
        context["cty.validation_stage"] = "type_definition"

        if invalid_type is not None:
            context["cty.invalid_type"] = type(invalid_type).__name__
            context["cty.invalid_type_str"] = str(invalid_type)[:100]  # Truncated for safety

        super().__init__(message, **kwargs)

    def xǁInvalidTypeErrorǁ__init____mutmut_5(self, message: str, invalid_type: object = None, **kwargs: Any) -> None:
        """
        Initializes the InvalidTypeError.

        Args:
            message: The base error message.
            invalid_type: The type object that was found to be invalid.
        """
        self.invalid_type = invalid_type

        # Add type validation context
        context: dict[str, Any] = kwargs.setdefault({})
        context["cty.error_category"] = "invalid_type"
        context["cty.validation_stage"] = "type_definition"

        if invalid_type is not None:
            context["cty.invalid_type"] = type(invalid_type).__name__
            context["cty.invalid_type_str"] = str(invalid_type)[:100]  # Truncated for safety

        super().__init__(message, **kwargs)

    def xǁInvalidTypeErrorǁ__init____mutmut_6(self, message: str, invalid_type: object = None, **kwargs: Any) -> None:
        """
        Initializes the InvalidTypeError.

        Args:
            message: The base error message.
            invalid_type: The type object that was found to be invalid.
        """
        self.invalid_type = invalid_type

        # Add type validation context
        context: dict[str, Any] = kwargs.setdefault("context", )
        context["cty.error_category"] = "invalid_type"
        context["cty.validation_stage"] = "type_definition"

        if invalid_type is not None:
            context["cty.invalid_type"] = type(invalid_type).__name__
            context["cty.invalid_type_str"] = str(invalid_type)[:100]  # Truncated for safety

        super().__init__(message, **kwargs)

    def xǁInvalidTypeErrorǁ__init____mutmut_7(self, message: str, invalid_type: object = None, **kwargs: Any) -> None:
        """
        Initializes the InvalidTypeError.

        Args:
            message: The base error message.
            invalid_type: The type object that was found to be invalid.
        """
        self.invalid_type = invalid_type

        # Add type validation context
        context: dict[str, Any] = kwargs.setdefault("XXcontextXX", {})
        context["cty.error_category"] = "invalid_type"
        context["cty.validation_stage"] = "type_definition"

        if invalid_type is not None:
            context["cty.invalid_type"] = type(invalid_type).__name__
            context["cty.invalid_type_str"] = str(invalid_type)[:100]  # Truncated for safety

        super().__init__(message, **kwargs)

    def xǁInvalidTypeErrorǁ__init____mutmut_8(self, message: str, invalid_type: object = None, **kwargs: Any) -> None:
        """
        Initializes the InvalidTypeError.

        Args:
            message: The base error message.
            invalid_type: The type object that was found to be invalid.
        """
        self.invalid_type = invalid_type

        # Add type validation context
        context: dict[str, Any] = kwargs.setdefault("CONTEXT", {})
        context["cty.error_category"] = "invalid_type"
        context["cty.validation_stage"] = "type_definition"

        if invalid_type is not None:
            context["cty.invalid_type"] = type(invalid_type).__name__
            context["cty.invalid_type_str"] = str(invalid_type)[:100]  # Truncated for safety

        super().__init__(message, **kwargs)

    def xǁInvalidTypeErrorǁ__init____mutmut_9(self, message: str, invalid_type: object = None, **kwargs: Any) -> None:
        """
        Initializes the InvalidTypeError.

        Args:
            message: The base error message.
            invalid_type: The type object that was found to be invalid.
        """
        self.invalid_type = invalid_type

        # Add type validation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = None
        context["cty.validation_stage"] = "type_definition"

        if invalid_type is not None:
            context["cty.invalid_type"] = type(invalid_type).__name__
            context["cty.invalid_type_str"] = str(invalid_type)[:100]  # Truncated for safety

        super().__init__(message, **kwargs)

    def xǁInvalidTypeErrorǁ__init____mutmut_10(self, message: str, invalid_type: object = None, **kwargs: Any) -> None:
        """
        Initializes the InvalidTypeError.

        Args:
            message: The base error message.
            invalid_type: The type object that was found to be invalid.
        """
        self.invalid_type = invalid_type

        # Add type validation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["XXcty.error_categoryXX"] = "invalid_type"
        context["cty.validation_stage"] = "type_definition"

        if invalid_type is not None:
            context["cty.invalid_type"] = type(invalid_type).__name__
            context["cty.invalid_type_str"] = str(invalid_type)[:100]  # Truncated for safety

        super().__init__(message, **kwargs)

    def xǁInvalidTypeErrorǁ__init____mutmut_11(self, message: str, invalid_type: object = None, **kwargs: Any) -> None:
        """
        Initializes the InvalidTypeError.

        Args:
            message: The base error message.
            invalid_type: The type object that was found to be invalid.
        """
        self.invalid_type = invalid_type

        # Add type validation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["CTY.ERROR_CATEGORY"] = "invalid_type"
        context["cty.validation_stage"] = "type_definition"

        if invalid_type is not None:
            context["cty.invalid_type"] = type(invalid_type).__name__
            context["cty.invalid_type_str"] = str(invalid_type)[:100]  # Truncated for safety

        super().__init__(message, **kwargs)

    def xǁInvalidTypeErrorǁ__init____mutmut_12(self, message: str, invalid_type: object = None, **kwargs: Any) -> None:
        """
        Initializes the InvalidTypeError.

        Args:
            message: The base error message.
            invalid_type: The type object that was found to be invalid.
        """
        self.invalid_type = invalid_type

        # Add type validation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "XXinvalid_typeXX"
        context["cty.validation_stage"] = "type_definition"

        if invalid_type is not None:
            context["cty.invalid_type"] = type(invalid_type).__name__
            context["cty.invalid_type_str"] = str(invalid_type)[:100]  # Truncated for safety

        super().__init__(message, **kwargs)

    def xǁInvalidTypeErrorǁ__init____mutmut_13(self, message: str, invalid_type: object = None, **kwargs: Any) -> None:
        """
        Initializes the InvalidTypeError.

        Args:
            message: The base error message.
            invalid_type: The type object that was found to be invalid.
        """
        self.invalid_type = invalid_type

        # Add type validation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "INVALID_TYPE"
        context["cty.validation_stage"] = "type_definition"

        if invalid_type is not None:
            context["cty.invalid_type"] = type(invalid_type).__name__
            context["cty.invalid_type_str"] = str(invalid_type)[:100]  # Truncated for safety

        super().__init__(message, **kwargs)

    def xǁInvalidTypeErrorǁ__init____mutmut_14(self, message: str, invalid_type: object = None, **kwargs: Any) -> None:
        """
        Initializes the InvalidTypeError.

        Args:
            message: The base error message.
            invalid_type: The type object that was found to be invalid.
        """
        self.invalid_type = invalid_type

        # Add type validation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "invalid_type"
        context["cty.validation_stage"] = None

        if invalid_type is not None:
            context["cty.invalid_type"] = type(invalid_type).__name__
            context["cty.invalid_type_str"] = str(invalid_type)[:100]  # Truncated for safety

        super().__init__(message, **kwargs)

    def xǁInvalidTypeErrorǁ__init____mutmut_15(self, message: str, invalid_type: object = None, **kwargs: Any) -> None:
        """
        Initializes the InvalidTypeError.

        Args:
            message: The base error message.
            invalid_type: The type object that was found to be invalid.
        """
        self.invalid_type = invalid_type

        # Add type validation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "invalid_type"
        context["XXcty.validation_stageXX"] = "type_definition"

        if invalid_type is not None:
            context["cty.invalid_type"] = type(invalid_type).__name__
            context["cty.invalid_type_str"] = str(invalid_type)[:100]  # Truncated for safety

        super().__init__(message, **kwargs)

    def xǁInvalidTypeErrorǁ__init____mutmut_16(self, message: str, invalid_type: object = None, **kwargs: Any) -> None:
        """
        Initializes the InvalidTypeError.

        Args:
            message: The base error message.
            invalid_type: The type object that was found to be invalid.
        """
        self.invalid_type = invalid_type

        # Add type validation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "invalid_type"
        context["CTY.VALIDATION_STAGE"] = "type_definition"

        if invalid_type is not None:
            context["cty.invalid_type"] = type(invalid_type).__name__
            context["cty.invalid_type_str"] = str(invalid_type)[:100]  # Truncated for safety

        super().__init__(message, **kwargs)

    def xǁInvalidTypeErrorǁ__init____mutmut_17(self, message: str, invalid_type: object = None, **kwargs: Any) -> None:
        """
        Initializes the InvalidTypeError.

        Args:
            message: The base error message.
            invalid_type: The type object that was found to be invalid.
        """
        self.invalid_type = invalid_type

        # Add type validation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "invalid_type"
        context["cty.validation_stage"] = "XXtype_definitionXX"

        if invalid_type is not None:
            context["cty.invalid_type"] = type(invalid_type).__name__
            context["cty.invalid_type_str"] = str(invalid_type)[:100]  # Truncated for safety

        super().__init__(message, **kwargs)

    def xǁInvalidTypeErrorǁ__init____mutmut_18(self, message: str, invalid_type: object = None, **kwargs: Any) -> None:
        """
        Initializes the InvalidTypeError.

        Args:
            message: The base error message.
            invalid_type: The type object that was found to be invalid.
        """
        self.invalid_type = invalid_type

        # Add type validation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "invalid_type"
        context["cty.validation_stage"] = "TYPE_DEFINITION"

        if invalid_type is not None:
            context["cty.invalid_type"] = type(invalid_type).__name__
            context["cty.invalid_type_str"] = str(invalid_type)[:100]  # Truncated for safety

        super().__init__(message, **kwargs)

    def xǁInvalidTypeErrorǁ__init____mutmut_19(self, message: str, invalid_type: object = None, **kwargs: Any) -> None:
        """
        Initializes the InvalidTypeError.

        Args:
            message: The base error message.
            invalid_type: The type object that was found to be invalid.
        """
        self.invalid_type = invalid_type

        # Add type validation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "invalid_type"
        context["cty.validation_stage"] = "type_definition"

        if invalid_type is None:
            context["cty.invalid_type"] = type(invalid_type).__name__
            context["cty.invalid_type_str"] = str(invalid_type)[:100]  # Truncated for safety

        super().__init__(message, **kwargs)

    def xǁInvalidTypeErrorǁ__init____mutmut_20(self, message: str, invalid_type: object = None, **kwargs: Any) -> None:
        """
        Initializes the InvalidTypeError.

        Args:
            message: The base error message.
            invalid_type: The type object that was found to be invalid.
        """
        self.invalid_type = invalid_type

        # Add type validation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "invalid_type"
        context["cty.validation_stage"] = "type_definition"

        if invalid_type is not None:
            context["cty.invalid_type"] = None
            context["cty.invalid_type_str"] = str(invalid_type)[:100]  # Truncated for safety

        super().__init__(message, **kwargs)

    def xǁInvalidTypeErrorǁ__init____mutmut_21(self, message: str, invalid_type: object = None, **kwargs: Any) -> None:
        """
        Initializes the InvalidTypeError.

        Args:
            message: The base error message.
            invalid_type: The type object that was found to be invalid.
        """
        self.invalid_type = invalid_type

        # Add type validation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "invalid_type"
        context["cty.validation_stage"] = "type_definition"

        if invalid_type is not None:
            context["XXcty.invalid_typeXX"] = type(invalid_type).__name__
            context["cty.invalid_type_str"] = str(invalid_type)[:100]  # Truncated for safety

        super().__init__(message, **kwargs)

    def xǁInvalidTypeErrorǁ__init____mutmut_22(self, message: str, invalid_type: object = None, **kwargs: Any) -> None:
        """
        Initializes the InvalidTypeError.

        Args:
            message: The base error message.
            invalid_type: The type object that was found to be invalid.
        """
        self.invalid_type = invalid_type

        # Add type validation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "invalid_type"
        context["cty.validation_stage"] = "type_definition"

        if invalid_type is not None:
            context["CTY.INVALID_TYPE"] = type(invalid_type).__name__
            context["cty.invalid_type_str"] = str(invalid_type)[:100]  # Truncated for safety

        super().__init__(message, **kwargs)

    def xǁInvalidTypeErrorǁ__init____mutmut_23(self, message: str, invalid_type: object = None, **kwargs: Any) -> None:
        """
        Initializes the InvalidTypeError.

        Args:
            message: The base error message.
            invalid_type: The type object that was found to be invalid.
        """
        self.invalid_type = invalid_type

        # Add type validation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "invalid_type"
        context["cty.validation_stage"] = "type_definition"

        if invalid_type is not None:
            context["cty.invalid_type"] = type(None).__name__
            context["cty.invalid_type_str"] = str(invalid_type)[:100]  # Truncated for safety

        super().__init__(message, **kwargs)

    def xǁInvalidTypeErrorǁ__init____mutmut_24(self, message: str, invalid_type: object = None, **kwargs: Any) -> None:
        """
        Initializes the InvalidTypeError.

        Args:
            message: The base error message.
            invalid_type: The type object that was found to be invalid.
        """
        self.invalid_type = invalid_type

        # Add type validation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "invalid_type"
        context["cty.validation_stage"] = "type_definition"

        if invalid_type is not None:
            context["cty.invalid_type"] = type(invalid_type).__name__
            context["cty.invalid_type_str"] = None  # Truncated for safety

        super().__init__(message, **kwargs)

    def xǁInvalidTypeErrorǁ__init____mutmut_25(self, message: str, invalid_type: object = None, **kwargs: Any) -> None:
        """
        Initializes the InvalidTypeError.

        Args:
            message: The base error message.
            invalid_type: The type object that was found to be invalid.
        """
        self.invalid_type = invalid_type

        # Add type validation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "invalid_type"
        context["cty.validation_stage"] = "type_definition"

        if invalid_type is not None:
            context["cty.invalid_type"] = type(invalid_type).__name__
            context["XXcty.invalid_type_strXX"] = str(invalid_type)[:100]  # Truncated for safety

        super().__init__(message, **kwargs)

    def xǁInvalidTypeErrorǁ__init____mutmut_26(self, message: str, invalid_type: object = None, **kwargs: Any) -> None:
        """
        Initializes the InvalidTypeError.

        Args:
            message: The base error message.
            invalid_type: The type object that was found to be invalid.
        """
        self.invalid_type = invalid_type

        # Add type validation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "invalid_type"
        context["cty.validation_stage"] = "type_definition"

        if invalid_type is not None:
            context["cty.invalid_type"] = type(invalid_type).__name__
            context["CTY.INVALID_TYPE_STR"] = str(invalid_type)[:100]  # Truncated for safety

        super().__init__(message, **kwargs)

    def xǁInvalidTypeErrorǁ__init____mutmut_27(self, message: str, invalid_type: object = None, **kwargs: Any) -> None:
        """
        Initializes the InvalidTypeError.

        Args:
            message: The base error message.
            invalid_type: The type object that was found to be invalid.
        """
        self.invalid_type = invalid_type

        # Add type validation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "invalid_type"
        context["cty.validation_stage"] = "type_definition"

        if invalid_type is not None:
            context["cty.invalid_type"] = type(invalid_type).__name__
            context["cty.invalid_type_str"] = str(None)[:100]  # Truncated for safety

        super().__init__(message, **kwargs)

    def xǁInvalidTypeErrorǁ__init____mutmut_28(self, message: str, invalid_type: object = None, **kwargs: Any) -> None:
        """
        Initializes the InvalidTypeError.

        Args:
            message: The base error message.
            invalid_type: The type object that was found to be invalid.
        """
        self.invalid_type = invalid_type

        # Add type validation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "invalid_type"
        context["cty.validation_stage"] = "type_definition"

        if invalid_type is not None:
            context["cty.invalid_type"] = type(invalid_type).__name__
            context["cty.invalid_type_str"] = str(invalid_type)[:101]  # Truncated for safety

        super().__init__(message, **kwargs)

    def xǁInvalidTypeErrorǁ__init____mutmut_29(self, message: str, invalid_type: object = None, **kwargs: Any) -> None:
        """
        Initializes the InvalidTypeError.

        Args:
            message: The base error message.
            invalid_type: The type object that was found to be invalid.
        """
        self.invalid_type = invalid_type

        # Add type validation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "invalid_type"
        context["cty.validation_stage"] = "type_definition"

        if invalid_type is not None:
            context["cty.invalid_type"] = type(invalid_type).__name__
            context["cty.invalid_type_str"] = str(invalid_type)[:100]  # Truncated for safety

        super().__init__(None, **kwargs)

    def xǁInvalidTypeErrorǁ__init____mutmut_30(self, message: str, invalid_type: object = None, **kwargs: Any) -> None:
        """
        Initializes the InvalidTypeError.

        Args:
            message: The base error message.
            invalid_type: The type object that was found to be invalid.
        """
        self.invalid_type = invalid_type

        # Add type validation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "invalid_type"
        context["cty.validation_stage"] = "type_definition"

        if invalid_type is not None:
            context["cty.invalid_type"] = type(invalid_type).__name__
            context["cty.invalid_type_str"] = str(invalid_type)[:100]  # Truncated for safety

        super().__init__(**kwargs)

    def xǁInvalidTypeErrorǁ__init____mutmut_31(self, message: str, invalid_type: object = None, **kwargs: Any) -> None:
        """
        Initializes the InvalidTypeError.

        Args:
            message: The base error message.
            invalid_type: The type object that was found to be invalid.
        """
        self.invalid_type = invalid_type

        # Add type validation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "invalid_type"
        context["cty.validation_stage"] = "type_definition"

        if invalid_type is not None:
            context["cty.invalid_type"] = type(invalid_type).__name__
            context["cty.invalid_type_str"] = str(invalid_type)[:100]  # Truncated for safety

        super().__init__(message, )
    
    xǁInvalidTypeErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁInvalidTypeErrorǁ__init____mutmut_1': xǁInvalidTypeErrorǁ__init____mutmut_1, 
        'xǁInvalidTypeErrorǁ__init____mutmut_2': xǁInvalidTypeErrorǁ__init____mutmut_2, 
        'xǁInvalidTypeErrorǁ__init____mutmut_3': xǁInvalidTypeErrorǁ__init____mutmut_3, 
        'xǁInvalidTypeErrorǁ__init____mutmut_4': xǁInvalidTypeErrorǁ__init____mutmut_4, 
        'xǁInvalidTypeErrorǁ__init____mutmut_5': xǁInvalidTypeErrorǁ__init____mutmut_5, 
        'xǁInvalidTypeErrorǁ__init____mutmut_6': xǁInvalidTypeErrorǁ__init____mutmut_6, 
        'xǁInvalidTypeErrorǁ__init____mutmut_7': xǁInvalidTypeErrorǁ__init____mutmut_7, 
        'xǁInvalidTypeErrorǁ__init____mutmut_8': xǁInvalidTypeErrorǁ__init____mutmut_8, 
        'xǁInvalidTypeErrorǁ__init____mutmut_9': xǁInvalidTypeErrorǁ__init____mutmut_9, 
        'xǁInvalidTypeErrorǁ__init____mutmut_10': xǁInvalidTypeErrorǁ__init____mutmut_10, 
        'xǁInvalidTypeErrorǁ__init____mutmut_11': xǁInvalidTypeErrorǁ__init____mutmut_11, 
        'xǁInvalidTypeErrorǁ__init____mutmut_12': xǁInvalidTypeErrorǁ__init____mutmut_12, 
        'xǁInvalidTypeErrorǁ__init____mutmut_13': xǁInvalidTypeErrorǁ__init____mutmut_13, 
        'xǁInvalidTypeErrorǁ__init____mutmut_14': xǁInvalidTypeErrorǁ__init____mutmut_14, 
        'xǁInvalidTypeErrorǁ__init____mutmut_15': xǁInvalidTypeErrorǁ__init____mutmut_15, 
        'xǁInvalidTypeErrorǁ__init____mutmut_16': xǁInvalidTypeErrorǁ__init____mutmut_16, 
        'xǁInvalidTypeErrorǁ__init____mutmut_17': xǁInvalidTypeErrorǁ__init____mutmut_17, 
        'xǁInvalidTypeErrorǁ__init____mutmut_18': xǁInvalidTypeErrorǁ__init____mutmut_18, 
        'xǁInvalidTypeErrorǁ__init____mutmut_19': xǁInvalidTypeErrorǁ__init____mutmut_19, 
        'xǁInvalidTypeErrorǁ__init____mutmut_20': xǁInvalidTypeErrorǁ__init____mutmut_20, 
        'xǁInvalidTypeErrorǁ__init____mutmut_21': xǁInvalidTypeErrorǁ__init____mutmut_21, 
        'xǁInvalidTypeErrorǁ__init____mutmut_22': xǁInvalidTypeErrorǁ__init____mutmut_22, 
        'xǁInvalidTypeErrorǁ__init____mutmut_23': xǁInvalidTypeErrorǁ__init____mutmut_23, 
        'xǁInvalidTypeErrorǁ__init____mutmut_24': xǁInvalidTypeErrorǁ__init____mutmut_24, 
        'xǁInvalidTypeErrorǁ__init____mutmut_25': xǁInvalidTypeErrorǁ__init____mutmut_25, 
        'xǁInvalidTypeErrorǁ__init____mutmut_26': xǁInvalidTypeErrorǁ__init____mutmut_26, 
        'xǁInvalidTypeErrorǁ__init____mutmut_27': xǁInvalidTypeErrorǁ__init____mutmut_27, 
        'xǁInvalidTypeErrorǁ__init____mutmut_28': xǁInvalidTypeErrorǁ__init____mutmut_28, 
        'xǁInvalidTypeErrorǁ__init____mutmut_29': xǁInvalidTypeErrorǁ__init____mutmut_29, 
        'xǁInvalidTypeErrorǁ__init____mutmut_30': xǁInvalidTypeErrorǁ__init____mutmut_30, 
        'xǁInvalidTypeErrorǁ__init____mutmut_31': xǁInvalidTypeErrorǁ__init____mutmut_31
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁInvalidTypeErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁInvalidTypeErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁInvalidTypeErrorǁ__init____mutmut_orig)
    xǁInvalidTypeErrorǁ__init____mutmut_orig.__name__ = 'xǁInvalidTypeErrorǁ__init__'


class AttributePathError(CtyError):
    """
    Raised when there's an error with an attribute path.

    This exception occurs when a path operation fails, such as:
    - When a path cannot be applied to a value
    - When a path step refers to a non-existent attribute or index
    - When a path operation is applied to an incompatible value type

    Attributes:
        message: A human-readable error description
        path: The path that caused the error
        value: The value the path was being applied to
    """

    def xǁAttributePathErrorǁ__init____mutmut_orig(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_1(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = None
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_2(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = None

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_3(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = None
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_4(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault(None, {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_5(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", None)
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_6(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault({})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_7(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", )
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_8(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("XXcontextXX", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_9(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("CONTEXT", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_10(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = None
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_11(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["XXcty.error_categoryXX"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_12(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["CTY.ERROR_CATEGORY"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_13(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "XXpath_operationXX"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_14(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "PATH_OPERATION"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_15(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = None

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_16(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["XXcty.operationXX"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_17(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["CTY.OPERATION"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_18(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "XXattribute_path_accessXX"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_19(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "ATTRIBUTE_PATH_ACCESS"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_20(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_21(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = None
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_22(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["XXcty.pathXX"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_23(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["CTY.PATH"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_24(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(None)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_25(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(None, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_26(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, None):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_27(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr("steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_28(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, ):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_29(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "XXstepsXX"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_30(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "STEPS"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_31(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = None
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_32(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(None, path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_33(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], None)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_34(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_35(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], )
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_36(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = None

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_37(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["XXcty.path_depthXX"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_38(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["CTY.PATH_DEPTH"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_39(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_40(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = None
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_41(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["XXcty.value_typeXX"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_42(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["CTY.VALUE_TYPE"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_43(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(None).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_44(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(None, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_45(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, None):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_46(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr("type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_47(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, ):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_48(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "XXtypeXX"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_49(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "TYPE"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_50(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = None

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_51(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["XXcty.cty_typeXX"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_52(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["CTY.CTY_TYPE"] = str(value.type)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_53(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(None)

        super().__init__(message, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_54(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(None, **kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_55(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(**kwargs)

    def xǁAttributePathErrorǁ__init____mutmut_56(self, message: str, path: object = None, value: object = None, **kwargs: Any) -> None:
        """
        Initializes the AttributePathError.

        Args:
            message: The base error message.
            path: The CtyPath or path representation that caused the error.
            value: The CtyValue to which the path was being applied.
        """
        self.path = path
        self.value = value

        # Add path operation context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "path_operation"
        context["cty.operation"] = "attribute_path_access"

        if path is not None:
            context["cty.path"] = str(path)
            if hasattr(path, "steps"):
                steps = cast(list[Any], path.steps)
                context["cty.path_depth"] = len(steps)

        if value is not None:
            context["cty.value_type"] = type(value).__name__
            if hasattr(value, "type"):
                context["cty.cty_type"] = str(value.type)

        super().__init__(message, )
    
    xǁAttributePathErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAttributePathErrorǁ__init____mutmut_1': xǁAttributePathErrorǁ__init____mutmut_1, 
        'xǁAttributePathErrorǁ__init____mutmut_2': xǁAttributePathErrorǁ__init____mutmut_2, 
        'xǁAttributePathErrorǁ__init____mutmut_3': xǁAttributePathErrorǁ__init____mutmut_3, 
        'xǁAttributePathErrorǁ__init____mutmut_4': xǁAttributePathErrorǁ__init____mutmut_4, 
        'xǁAttributePathErrorǁ__init____mutmut_5': xǁAttributePathErrorǁ__init____mutmut_5, 
        'xǁAttributePathErrorǁ__init____mutmut_6': xǁAttributePathErrorǁ__init____mutmut_6, 
        'xǁAttributePathErrorǁ__init____mutmut_7': xǁAttributePathErrorǁ__init____mutmut_7, 
        'xǁAttributePathErrorǁ__init____mutmut_8': xǁAttributePathErrorǁ__init____mutmut_8, 
        'xǁAttributePathErrorǁ__init____mutmut_9': xǁAttributePathErrorǁ__init____mutmut_9, 
        'xǁAttributePathErrorǁ__init____mutmut_10': xǁAttributePathErrorǁ__init____mutmut_10, 
        'xǁAttributePathErrorǁ__init____mutmut_11': xǁAttributePathErrorǁ__init____mutmut_11, 
        'xǁAttributePathErrorǁ__init____mutmut_12': xǁAttributePathErrorǁ__init____mutmut_12, 
        'xǁAttributePathErrorǁ__init____mutmut_13': xǁAttributePathErrorǁ__init____mutmut_13, 
        'xǁAttributePathErrorǁ__init____mutmut_14': xǁAttributePathErrorǁ__init____mutmut_14, 
        'xǁAttributePathErrorǁ__init____mutmut_15': xǁAttributePathErrorǁ__init____mutmut_15, 
        'xǁAttributePathErrorǁ__init____mutmut_16': xǁAttributePathErrorǁ__init____mutmut_16, 
        'xǁAttributePathErrorǁ__init____mutmut_17': xǁAttributePathErrorǁ__init____mutmut_17, 
        'xǁAttributePathErrorǁ__init____mutmut_18': xǁAttributePathErrorǁ__init____mutmut_18, 
        'xǁAttributePathErrorǁ__init____mutmut_19': xǁAttributePathErrorǁ__init____mutmut_19, 
        'xǁAttributePathErrorǁ__init____mutmut_20': xǁAttributePathErrorǁ__init____mutmut_20, 
        'xǁAttributePathErrorǁ__init____mutmut_21': xǁAttributePathErrorǁ__init____mutmut_21, 
        'xǁAttributePathErrorǁ__init____mutmut_22': xǁAttributePathErrorǁ__init____mutmut_22, 
        'xǁAttributePathErrorǁ__init____mutmut_23': xǁAttributePathErrorǁ__init____mutmut_23, 
        'xǁAttributePathErrorǁ__init____mutmut_24': xǁAttributePathErrorǁ__init____mutmut_24, 
        'xǁAttributePathErrorǁ__init____mutmut_25': xǁAttributePathErrorǁ__init____mutmut_25, 
        'xǁAttributePathErrorǁ__init____mutmut_26': xǁAttributePathErrorǁ__init____mutmut_26, 
        'xǁAttributePathErrorǁ__init____mutmut_27': xǁAttributePathErrorǁ__init____mutmut_27, 
        'xǁAttributePathErrorǁ__init____mutmut_28': xǁAttributePathErrorǁ__init____mutmut_28, 
        'xǁAttributePathErrorǁ__init____mutmut_29': xǁAttributePathErrorǁ__init____mutmut_29, 
        'xǁAttributePathErrorǁ__init____mutmut_30': xǁAttributePathErrorǁ__init____mutmut_30, 
        'xǁAttributePathErrorǁ__init____mutmut_31': xǁAttributePathErrorǁ__init____mutmut_31, 
        'xǁAttributePathErrorǁ__init____mutmut_32': xǁAttributePathErrorǁ__init____mutmut_32, 
        'xǁAttributePathErrorǁ__init____mutmut_33': xǁAttributePathErrorǁ__init____mutmut_33, 
        'xǁAttributePathErrorǁ__init____mutmut_34': xǁAttributePathErrorǁ__init____mutmut_34, 
        'xǁAttributePathErrorǁ__init____mutmut_35': xǁAttributePathErrorǁ__init____mutmut_35, 
        'xǁAttributePathErrorǁ__init____mutmut_36': xǁAttributePathErrorǁ__init____mutmut_36, 
        'xǁAttributePathErrorǁ__init____mutmut_37': xǁAttributePathErrorǁ__init____mutmut_37, 
        'xǁAttributePathErrorǁ__init____mutmut_38': xǁAttributePathErrorǁ__init____mutmut_38, 
        'xǁAttributePathErrorǁ__init____mutmut_39': xǁAttributePathErrorǁ__init____mutmut_39, 
        'xǁAttributePathErrorǁ__init____mutmut_40': xǁAttributePathErrorǁ__init____mutmut_40, 
        'xǁAttributePathErrorǁ__init____mutmut_41': xǁAttributePathErrorǁ__init____mutmut_41, 
        'xǁAttributePathErrorǁ__init____mutmut_42': xǁAttributePathErrorǁ__init____mutmut_42, 
        'xǁAttributePathErrorǁ__init____mutmut_43': xǁAttributePathErrorǁ__init____mutmut_43, 
        'xǁAttributePathErrorǁ__init____mutmut_44': xǁAttributePathErrorǁ__init____mutmut_44, 
        'xǁAttributePathErrorǁ__init____mutmut_45': xǁAttributePathErrorǁ__init____mutmut_45, 
        'xǁAttributePathErrorǁ__init____mutmut_46': xǁAttributePathErrorǁ__init____mutmut_46, 
        'xǁAttributePathErrorǁ__init____mutmut_47': xǁAttributePathErrorǁ__init____mutmut_47, 
        'xǁAttributePathErrorǁ__init____mutmut_48': xǁAttributePathErrorǁ__init____mutmut_48, 
        'xǁAttributePathErrorǁ__init____mutmut_49': xǁAttributePathErrorǁ__init____mutmut_49, 
        'xǁAttributePathErrorǁ__init____mutmut_50': xǁAttributePathErrorǁ__init____mutmut_50, 
        'xǁAttributePathErrorǁ__init____mutmut_51': xǁAttributePathErrorǁ__init____mutmut_51, 
        'xǁAttributePathErrorǁ__init____mutmut_52': xǁAttributePathErrorǁ__init____mutmut_52, 
        'xǁAttributePathErrorǁ__init____mutmut_53': xǁAttributePathErrorǁ__init____mutmut_53, 
        'xǁAttributePathErrorǁ__init____mutmut_54': xǁAttributePathErrorǁ__init____mutmut_54, 
        'xǁAttributePathErrorǁ__init____mutmut_55': xǁAttributePathErrorǁ__init____mutmut_55, 
        'xǁAttributePathErrorǁ__init____mutmut_56': xǁAttributePathErrorǁ__init____mutmut_56
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAttributePathErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁAttributePathErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁAttributePathErrorǁ__init____mutmut_orig)
    xǁAttributePathErrorǁ__init____mutmut_orig.__name__ = 'xǁAttributePathErrorǁ__init__'


################################################################################
# Encoding Errors
################################################################################


class EncodingError(CtyError):
    """
    Base exception for all encoding/serialization errors.

    This exception serves as the parent class for more specific errors
    related to serialization and deserialization of Cty values.

    Attributes:
        message: A human-readable error description
        data: The data that caused the encoding error
        encoding: The name of the encoding format that was being used
    """

    def xǁEncodingErrorǁ__init____mutmut_orig(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_1(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = None
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_2(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = None
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_3(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = None

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_4(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = None
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_5(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault(None, {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_6(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", None)
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_7(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault({})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_8(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", )
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_9(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("XXcontextXX", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_10(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("CONTEXT", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_11(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = None
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_12(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["XXcty.error_categoryXX"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_13(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["CTY.ERROR_CATEGORY"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_14(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "XXencodingXX"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_15(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "ENCODING"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_16(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = None

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_17(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["XXcty.operationXX"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_18(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["CTY.OPERATION"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_19(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "XXserializationXX"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_20(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "SERIALIZATION"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_21(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = None
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_22(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["XXcty.encoding_formatXX"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_23(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["CTY.ENCODING_FORMAT"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_24(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = None

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_25(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["XXencoding.formatXX"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_26(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["ENCODING.FORMAT"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_27(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_28(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = None
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_29(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["XXcty.data_typeXX"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_30(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["CTY.DATA_TYPE"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_31(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(None).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_32(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = None
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_33(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(None)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_34(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = None
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_35(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["XXencoding.data_previewXX"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_36(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["ENCODING.DATA_PREVIEW"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_37(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] - "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_38(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:101] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_39(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "XX...XX" if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_40(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) >= 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_41(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 101 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_42(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = None

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_43(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["XXencoding.data_previewXX"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_44(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["ENCODING.DATA_PREVIEW"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_45(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(None).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_46(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None or not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_47(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_48(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_49(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(None):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_50(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.lower()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_51(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = None

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_52(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.lower()} encoding error: {message}"

        super().__init__(message, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_53(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(None, **kwargs)

    def xǁEncodingErrorǁ__init____mutmut_54(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(**kwargs)

    def xǁEncodingErrorǁ__init____mutmut_55(
        self,
        message: str,
        data: object = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EncodingError.

        Args:
            message: The base error message.
            data: The data that was being encoded/decoded when the error occurred.
            encoding: The name of the encoding format (e.g., "json", "msgpack").
        """
        self.data = data
        self.encoding = encoding
        # Store original message if subclasses want to modify it AFTER super call
        self._original_message = message

        # Add encoding context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.error_category"] = "encoding"
        context["cty.operation"] = "serialization"

        if encoding:
            context["cty.encoding_format"] = encoding
            context["encoding.format"] = encoding

        if data is not None:
            context["cty.data_type"] = type(data).__name__
            # Safe data representation for debugging
            try:
                data_repr = repr(data)
                context["encoding.data_preview"] = (
                    data_repr[:100] + "..." if len(data_repr) > 100 else data_repr
                )
            except Exception:
                context["encoding.data_preview"] = f"<repr failed for {type(data).__name__}>"

        # Add format information to the message if available
        if encoding is not None and not message.strip().startswith(encoding.upper()):
            # Avoid double-prefixing if subclass already added it
            message = f"{encoding.upper()} encoding error: {message}"

        super().__init__(message, )
    
    xǁEncodingErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁEncodingErrorǁ__init____mutmut_1': xǁEncodingErrorǁ__init____mutmut_1, 
        'xǁEncodingErrorǁ__init____mutmut_2': xǁEncodingErrorǁ__init____mutmut_2, 
        'xǁEncodingErrorǁ__init____mutmut_3': xǁEncodingErrorǁ__init____mutmut_3, 
        'xǁEncodingErrorǁ__init____mutmut_4': xǁEncodingErrorǁ__init____mutmut_4, 
        'xǁEncodingErrorǁ__init____mutmut_5': xǁEncodingErrorǁ__init____mutmut_5, 
        'xǁEncodingErrorǁ__init____mutmut_6': xǁEncodingErrorǁ__init____mutmut_6, 
        'xǁEncodingErrorǁ__init____mutmut_7': xǁEncodingErrorǁ__init____mutmut_7, 
        'xǁEncodingErrorǁ__init____mutmut_8': xǁEncodingErrorǁ__init____mutmut_8, 
        'xǁEncodingErrorǁ__init____mutmut_9': xǁEncodingErrorǁ__init____mutmut_9, 
        'xǁEncodingErrorǁ__init____mutmut_10': xǁEncodingErrorǁ__init____mutmut_10, 
        'xǁEncodingErrorǁ__init____mutmut_11': xǁEncodingErrorǁ__init____mutmut_11, 
        'xǁEncodingErrorǁ__init____mutmut_12': xǁEncodingErrorǁ__init____mutmut_12, 
        'xǁEncodingErrorǁ__init____mutmut_13': xǁEncodingErrorǁ__init____mutmut_13, 
        'xǁEncodingErrorǁ__init____mutmut_14': xǁEncodingErrorǁ__init____mutmut_14, 
        'xǁEncodingErrorǁ__init____mutmut_15': xǁEncodingErrorǁ__init____mutmut_15, 
        'xǁEncodingErrorǁ__init____mutmut_16': xǁEncodingErrorǁ__init____mutmut_16, 
        'xǁEncodingErrorǁ__init____mutmut_17': xǁEncodingErrorǁ__init____mutmut_17, 
        'xǁEncodingErrorǁ__init____mutmut_18': xǁEncodingErrorǁ__init____mutmut_18, 
        'xǁEncodingErrorǁ__init____mutmut_19': xǁEncodingErrorǁ__init____mutmut_19, 
        'xǁEncodingErrorǁ__init____mutmut_20': xǁEncodingErrorǁ__init____mutmut_20, 
        'xǁEncodingErrorǁ__init____mutmut_21': xǁEncodingErrorǁ__init____mutmut_21, 
        'xǁEncodingErrorǁ__init____mutmut_22': xǁEncodingErrorǁ__init____mutmut_22, 
        'xǁEncodingErrorǁ__init____mutmut_23': xǁEncodingErrorǁ__init____mutmut_23, 
        'xǁEncodingErrorǁ__init____mutmut_24': xǁEncodingErrorǁ__init____mutmut_24, 
        'xǁEncodingErrorǁ__init____mutmut_25': xǁEncodingErrorǁ__init____mutmut_25, 
        'xǁEncodingErrorǁ__init____mutmut_26': xǁEncodingErrorǁ__init____mutmut_26, 
        'xǁEncodingErrorǁ__init____mutmut_27': xǁEncodingErrorǁ__init____mutmut_27, 
        'xǁEncodingErrorǁ__init____mutmut_28': xǁEncodingErrorǁ__init____mutmut_28, 
        'xǁEncodingErrorǁ__init____mutmut_29': xǁEncodingErrorǁ__init____mutmut_29, 
        'xǁEncodingErrorǁ__init____mutmut_30': xǁEncodingErrorǁ__init____mutmut_30, 
        'xǁEncodingErrorǁ__init____mutmut_31': xǁEncodingErrorǁ__init____mutmut_31, 
        'xǁEncodingErrorǁ__init____mutmut_32': xǁEncodingErrorǁ__init____mutmut_32, 
        'xǁEncodingErrorǁ__init____mutmut_33': xǁEncodingErrorǁ__init____mutmut_33, 
        'xǁEncodingErrorǁ__init____mutmut_34': xǁEncodingErrorǁ__init____mutmut_34, 
        'xǁEncodingErrorǁ__init____mutmut_35': xǁEncodingErrorǁ__init____mutmut_35, 
        'xǁEncodingErrorǁ__init____mutmut_36': xǁEncodingErrorǁ__init____mutmut_36, 
        'xǁEncodingErrorǁ__init____mutmut_37': xǁEncodingErrorǁ__init____mutmut_37, 
        'xǁEncodingErrorǁ__init____mutmut_38': xǁEncodingErrorǁ__init____mutmut_38, 
        'xǁEncodingErrorǁ__init____mutmut_39': xǁEncodingErrorǁ__init____mutmut_39, 
        'xǁEncodingErrorǁ__init____mutmut_40': xǁEncodingErrorǁ__init____mutmut_40, 
        'xǁEncodingErrorǁ__init____mutmut_41': xǁEncodingErrorǁ__init____mutmut_41, 
        'xǁEncodingErrorǁ__init____mutmut_42': xǁEncodingErrorǁ__init____mutmut_42, 
        'xǁEncodingErrorǁ__init____mutmut_43': xǁEncodingErrorǁ__init____mutmut_43, 
        'xǁEncodingErrorǁ__init____mutmut_44': xǁEncodingErrorǁ__init____mutmut_44, 
        'xǁEncodingErrorǁ__init____mutmut_45': xǁEncodingErrorǁ__init____mutmut_45, 
        'xǁEncodingErrorǁ__init____mutmut_46': xǁEncodingErrorǁ__init____mutmut_46, 
        'xǁEncodingErrorǁ__init____mutmut_47': xǁEncodingErrorǁ__init____mutmut_47, 
        'xǁEncodingErrorǁ__init____mutmut_48': xǁEncodingErrorǁ__init____mutmut_48, 
        'xǁEncodingErrorǁ__init____mutmut_49': xǁEncodingErrorǁ__init____mutmut_49, 
        'xǁEncodingErrorǁ__init____mutmut_50': xǁEncodingErrorǁ__init____mutmut_50, 
        'xǁEncodingErrorǁ__init____mutmut_51': xǁEncodingErrorǁ__init____mutmut_51, 
        'xǁEncodingErrorǁ__init____mutmut_52': xǁEncodingErrorǁ__init____mutmut_52, 
        'xǁEncodingErrorǁ__init____mutmut_53': xǁEncodingErrorǁ__init____mutmut_53, 
        'xǁEncodingErrorǁ__init____mutmut_54': xǁEncodingErrorǁ__init____mutmut_54, 
        'xǁEncodingErrorǁ__init____mutmut_55': xǁEncodingErrorǁ__init____mutmut_55
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁEncodingErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁEncodingErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁEncodingErrorǁ__init____mutmut_orig)
    xǁEncodingErrorǁ__init____mutmut_orig.__name__ = 'xǁEncodingErrorǁ__init__'


class SerializationError(EncodingError):
    """
    Raised when serialization of a value fails.

    This exception occurs when a Cty value cannot be serialized to a
    particular format, such as when a value contains types that aren't
    supported by the serialization format.

    Attributes:
        message: A human-readable error description
        value: The value that failed to serialize
        format_name: The name of the format that was being used
    """

    def xǁSerializationErrorǁ__init____mutmut_orig(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = value

        # Add serialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "serialize"

        if value is not None and hasattr(value, "type"):
            context["cty.serialized_cty_type"] = str(value.type)
            if hasattr(value, "is_null"):
                context["cty.serialized_is_null"] = value.is_null

        super().__init__(message, value, format_name, **kwargs)

    def xǁSerializationErrorǁ__init____mutmut_1(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = None

        # Add serialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "serialize"

        if value is not None and hasattr(value, "type"):
            context["cty.serialized_cty_type"] = str(value.type)
            if hasattr(value, "is_null"):
                context["cty.serialized_is_null"] = value.is_null

        super().__init__(message, value, format_name, **kwargs)

    def xǁSerializationErrorǁ__init____mutmut_2(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = value

        # Add serialization-specific context
        context: dict[str, Any] = None
        context["cty.serialization_direction"] = "serialize"

        if value is not None and hasattr(value, "type"):
            context["cty.serialized_cty_type"] = str(value.type)
            if hasattr(value, "is_null"):
                context["cty.serialized_is_null"] = value.is_null

        super().__init__(message, value, format_name, **kwargs)

    def xǁSerializationErrorǁ__init____mutmut_3(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = value

        # Add serialization-specific context
        context: dict[str, Any] = kwargs.setdefault(None, {})
        context["cty.serialization_direction"] = "serialize"

        if value is not None and hasattr(value, "type"):
            context["cty.serialized_cty_type"] = str(value.type)
            if hasattr(value, "is_null"):
                context["cty.serialized_is_null"] = value.is_null

        super().__init__(message, value, format_name, **kwargs)

    def xǁSerializationErrorǁ__init____mutmut_4(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = value

        # Add serialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", None)
        context["cty.serialization_direction"] = "serialize"

        if value is not None and hasattr(value, "type"):
            context["cty.serialized_cty_type"] = str(value.type)
            if hasattr(value, "is_null"):
                context["cty.serialized_is_null"] = value.is_null

        super().__init__(message, value, format_name, **kwargs)

    def xǁSerializationErrorǁ__init____mutmut_5(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = value

        # Add serialization-specific context
        context: dict[str, Any] = kwargs.setdefault({})
        context["cty.serialization_direction"] = "serialize"

        if value is not None and hasattr(value, "type"):
            context["cty.serialized_cty_type"] = str(value.type)
            if hasattr(value, "is_null"):
                context["cty.serialized_is_null"] = value.is_null

        super().__init__(message, value, format_name, **kwargs)

    def xǁSerializationErrorǁ__init____mutmut_6(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = value

        # Add serialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", )
        context["cty.serialization_direction"] = "serialize"

        if value is not None and hasattr(value, "type"):
            context["cty.serialized_cty_type"] = str(value.type)
            if hasattr(value, "is_null"):
                context["cty.serialized_is_null"] = value.is_null

        super().__init__(message, value, format_name, **kwargs)

    def xǁSerializationErrorǁ__init____mutmut_7(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = value

        # Add serialization-specific context
        context: dict[str, Any] = kwargs.setdefault("XXcontextXX", {})
        context["cty.serialization_direction"] = "serialize"

        if value is not None and hasattr(value, "type"):
            context["cty.serialized_cty_type"] = str(value.type)
            if hasattr(value, "is_null"):
                context["cty.serialized_is_null"] = value.is_null

        super().__init__(message, value, format_name, **kwargs)

    def xǁSerializationErrorǁ__init____mutmut_8(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = value

        # Add serialization-specific context
        context: dict[str, Any] = kwargs.setdefault("CONTEXT", {})
        context["cty.serialization_direction"] = "serialize"

        if value is not None and hasattr(value, "type"):
            context["cty.serialized_cty_type"] = str(value.type)
            if hasattr(value, "is_null"):
                context["cty.serialized_is_null"] = value.is_null

        super().__init__(message, value, format_name, **kwargs)

    def xǁSerializationErrorǁ__init____mutmut_9(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = value

        # Add serialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = None

        if value is not None and hasattr(value, "type"):
            context["cty.serialized_cty_type"] = str(value.type)
            if hasattr(value, "is_null"):
                context["cty.serialized_is_null"] = value.is_null

        super().__init__(message, value, format_name, **kwargs)

    def xǁSerializationErrorǁ__init____mutmut_10(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = value

        # Add serialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["XXcty.serialization_directionXX"] = "serialize"

        if value is not None and hasattr(value, "type"):
            context["cty.serialized_cty_type"] = str(value.type)
            if hasattr(value, "is_null"):
                context["cty.serialized_is_null"] = value.is_null

        super().__init__(message, value, format_name, **kwargs)

    def xǁSerializationErrorǁ__init____mutmut_11(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = value

        # Add serialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["CTY.SERIALIZATION_DIRECTION"] = "serialize"

        if value is not None and hasattr(value, "type"):
            context["cty.serialized_cty_type"] = str(value.type)
            if hasattr(value, "is_null"):
                context["cty.serialized_is_null"] = value.is_null

        super().__init__(message, value, format_name, **kwargs)

    def xǁSerializationErrorǁ__init____mutmut_12(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = value

        # Add serialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "XXserializeXX"

        if value is not None and hasattr(value, "type"):
            context["cty.serialized_cty_type"] = str(value.type)
            if hasattr(value, "is_null"):
                context["cty.serialized_is_null"] = value.is_null

        super().__init__(message, value, format_name, **kwargs)

    def xǁSerializationErrorǁ__init____mutmut_13(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = value

        # Add serialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "SERIALIZE"

        if value is not None and hasattr(value, "type"):
            context["cty.serialized_cty_type"] = str(value.type)
            if hasattr(value, "is_null"):
                context["cty.serialized_is_null"] = value.is_null

        super().__init__(message, value, format_name, **kwargs)

    def xǁSerializationErrorǁ__init____mutmut_14(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = value

        # Add serialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "serialize"

        if value is not None or hasattr(value, "type"):
            context["cty.serialized_cty_type"] = str(value.type)
            if hasattr(value, "is_null"):
                context["cty.serialized_is_null"] = value.is_null

        super().__init__(message, value, format_name, **kwargs)

    def xǁSerializationErrorǁ__init____mutmut_15(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = value

        # Add serialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "serialize"

        if value is None and hasattr(value, "type"):
            context["cty.serialized_cty_type"] = str(value.type)
            if hasattr(value, "is_null"):
                context["cty.serialized_is_null"] = value.is_null

        super().__init__(message, value, format_name, **kwargs)

    def xǁSerializationErrorǁ__init____mutmut_16(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = value

        # Add serialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "serialize"

        if value is not None and hasattr(None, "type"):
            context["cty.serialized_cty_type"] = str(value.type)
            if hasattr(value, "is_null"):
                context["cty.serialized_is_null"] = value.is_null

        super().__init__(message, value, format_name, **kwargs)

    def xǁSerializationErrorǁ__init____mutmut_17(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = value

        # Add serialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "serialize"

        if value is not None and hasattr(value, None):
            context["cty.serialized_cty_type"] = str(value.type)
            if hasattr(value, "is_null"):
                context["cty.serialized_is_null"] = value.is_null

        super().__init__(message, value, format_name, **kwargs)

    def xǁSerializationErrorǁ__init____mutmut_18(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = value

        # Add serialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "serialize"

        if value is not None and hasattr("type"):
            context["cty.serialized_cty_type"] = str(value.type)
            if hasattr(value, "is_null"):
                context["cty.serialized_is_null"] = value.is_null

        super().__init__(message, value, format_name, **kwargs)

    def xǁSerializationErrorǁ__init____mutmut_19(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = value

        # Add serialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "serialize"

        if value is not None and hasattr(value, ):
            context["cty.serialized_cty_type"] = str(value.type)
            if hasattr(value, "is_null"):
                context["cty.serialized_is_null"] = value.is_null

        super().__init__(message, value, format_name, **kwargs)

    def xǁSerializationErrorǁ__init____mutmut_20(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = value

        # Add serialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "serialize"

        if value is not None and hasattr(value, "XXtypeXX"):
            context["cty.serialized_cty_type"] = str(value.type)
            if hasattr(value, "is_null"):
                context["cty.serialized_is_null"] = value.is_null

        super().__init__(message, value, format_name, **kwargs)

    def xǁSerializationErrorǁ__init____mutmut_21(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = value

        # Add serialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "serialize"

        if value is not None and hasattr(value, "TYPE"):
            context["cty.serialized_cty_type"] = str(value.type)
            if hasattr(value, "is_null"):
                context["cty.serialized_is_null"] = value.is_null

        super().__init__(message, value, format_name, **kwargs)

    def xǁSerializationErrorǁ__init____mutmut_22(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = value

        # Add serialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "serialize"

        if value is not None and hasattr(value, "type"):
            context["cty.serialized_cty_type"] = None
            if hasattr(value, "is_null"):
                context["cty.serialized_is_null"] = value.is_null

        super().__init__(message, value, format_name, **kwargs)

    def xǁSerializationErrorǁ__init____mutmut_23(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = value

        # Add serialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "serialize"

        if value is not None and hasattr(value, "type"):
            context["XXcty.serialized_cty_typeXX"] = str(value.type)
            if hasattr(value, "is_null"):
                context["cty.serialized_is_null"] = value.is_null

        super().__init__(message, value, format_name, **kwargs)

    def xǁSerializationErrorǁ__init____mutmut_24(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = value

        # Add serialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "serialize"

        if value is not None and hasattr(value, "type"):
            context["CTY.SERIALIZED_CTY_TYPE"] = str(value.type)
            if hasattr(value, "is_null"):
                context["cty.serialized_is_null"] = value.is_null

        super().__init__(message, value, format_name, **kwargs)

    def xǁSerializationErrorǁ__init____mutmut_25(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = value

        # Add serialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "serialize"

        if value is not None and hasattr(value, "type"):
            context["cty.serialized_cty_type"] = str(None)
            if hasattr(value, "is_null"):
                context["cty.serialized_is_null"] = value.is_null

        super().__init__(message, value, format_name, **kwargs)

    def xǁSerializationErrorǁ__init____mutmut_26(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = value

        # Add serialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "serialize"

        if value is not None and hasattr(value, "type"):
            context["cty.serialized_cty_type"] = str(value.type)
            if hasattr(None, "is_null"):
                context["cty.serialized_is_null"] = value.is_null

        super().__init__(message, value, format_name, **kwargs)

    def xǁSerializationErrorǁ__init____mutmut_27(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = value

        # Add serialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "serialize"

        if value is not None and hasattr(value, "type"):
            context["cty.serialized_cty_type"] = str(value.type)
            if hasattr(value, None):
                context["cty.serialized_is_null"] = value.is_null

        super().__init__(message, value, format_name, **kwargs)

    def xǁSerializationErrorǁ__init____mutmut_28(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = value

        # Add serialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "serialize"

        if value is not None and hasattr(value, "type"):
            context["cty.serialized_cty_type"] = str(value.type)
            if hasattr("is_null"):
                context["cty.serialized_is_null"] = value.is_null

        super().__init__(message, value, format_name, **kwargs)

    def xǁSerializationErrorǁ__init____mutmut_29(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = value

        # Add serialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "serialize"

        if value is not None and hasattr(value, "type"):
            context["cty.serialized_cty_type"] = str(value.type)
            if hasattr(value, ):
                context["cty.serialized_is_null"] = value.is_null

        super().__init__(message, value, format_name, **kwargs)

    def xǁSerializationErrorǁ__init____mutmut_30(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = value

        # Add serialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "serialize"

        if value is not None and hasattr(value, "type"):
            context["cty.serialized_cty_type"] = str(value.type)
            if hasattr(value, "XXis_nullXX"):
                context["cty.serialized_is_null"] = value.is_null

        super().__init__(message, value, format_name, **kwargs)

    def xǁSerializationErrorǁ__init____mutmut_31(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = value

        # Add serialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "serialize"

        if value is not None and hasattr(value, "type"):
            context["cty.serialized_cty_type"] = str(value.type)
            if hasattr(value, "IS_NULL"):
                context["cty.serialized_is_null"] = value.is_null

        super().__init__(message, value, format_name, **kwargs)

    def xǁSerializationErrorǁ__init____mutmut_32(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = value

        # Add serialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "serialize"

        if value is not None and hasattr(value, "type"):
            context["cty.serialized_cty_type"] = str(value.type)
            if hasattr(value, "is_null"):
                context["cty.serialized_is_null"] = None

        super().__init__(message, value, format_name, **kwargs)

    def xǁSerializationErrorǁ__init____mutmut_33(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = value

        # Add serialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "serialize"

        if value is not None and hasattr(value, "type"):
            context["cty.serialized_cty_type"] = str(value.type)
            if hasattr(value, "is_null"):
                context["XXcty.serialized_is_nullXX"] = value.is_null

        super().__init__(message, value, format_name, **kwargs)

    def xǁSerializationErrorǁ__init____mutmut_34(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = value

        # Add serialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "serialize"

        if value is not None and hasattr(value, "type"):
            context["cty.serialized_cty_type"] = str(value.type)
            if hasattr(value, "is_null"):
                context["CTY.SERIALIZED_IS_NULL"] = value.is_null

        super().__init__(message, value, format_name, **kwargs)

    def xǁSerializationErrorǁ__init____mutmut_35(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = value

        # Add serialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "serialize"

        if value is not None and hasattr(value, "type"):
            context["cty.serialized_cty_type"] = str(value.type)
            if hasattr(value, "is_null"):
                context["cty.serialized_is_null"] = value.is_null

        super().__init__(None, value, format_name, **kwargs)

    def xǁSerializationErrorǁ__init____mutmut_36(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = value

        # Add serialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "serialize"

        if value is not None and hasattr(value, "type"):
            context["cty.serialized_cty_type"] = str(value.type)
            if hasattr(value, "is_null"):
                context["cty.serialized_is_null"] = value.is_null

        super().__init__(message, None, format_name, **kwargs)

    def xǁSerializationErrorǁ__init____mutmut_37(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = value

        # Add serialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "serialize"

        if value is not None and hasattr(value, "type"):
            context["cty.serialized_cty_type"] = str(value.type)
            if hasattr(value, "is_null"):
                context["cty.serialized_is_null"] = value.is_null

        super().__init__(message, value, None, **kwargs)

    def xǁSerializationErrorǁ__init____mutmut_38(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = value

        # Add serialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "serialize"

        if value is not None and hasattr(value, "type"):
            context["cty.serialized_cty_type"] = str(value.type)
            if hasattr(value, "is_null"):
                context["cty.serialized_is_null"] = value.is_null

        super().__init__(value, format_name, **kwargs)

    def xǁSerializationErrorǁ__init____mutmut_39(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = value

        # Add serialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "serialize"

        if value is not None and hasattr(value, "type"):
            context["cty.serialized_cty_type"] = str(value.type)
            if hasattr(value, "is_null"):
                context["cty.serialized_is_null"] = value.is_null

        super().__init__(message, format_name, **kwargs)

    def xǁSerializationErrorǁ__init____mutmut_40(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = value

        # Add serialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "serialize"

        if value is not None and hasattr(value, "type"):
            context["cty.serialized_cty_type"] = str(value.type)
            if hasattr(value, "is_null"):
                context["cty.serialized_is_null"] = value.is_null

        super().__init__(message, value, **kwargs)

    def xǁSerializationErrorǁ__init____mutmut_41(
        self,
        message: str,
        value: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the SerializationError.

        Args:
            message: The base error message.
            value: The value that failed to serialize.
            format_name: The name of the serialization format.
        """
        self.value = value

        # Add serialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "serialize"

        if value is not None and hasattr(value, "type"):
            context["cty.serialized_cty_type"] = str(value.type)
            if hasattr(value, "is_null"):
                context["cty.serialized_is_null"] = value.is_null

        super().__init__(message, value, format_name, )
    
    xǁSerializationErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSerializationErrorǁ__init____mutmut_1': xǁSerializationErrorǁ__init____mutmut_1, 
        'xǁSerializationErrorǁ__init____mutmut_2': xǁSerializationErrorǁ__init____mutmut_2, 
        'xǁSerializationErrorǁ__init____mutmut_3': xǁSerializationErrorǁ__init____mutmut_3, 
        'xǁSerializationErrorǁ__init____mutmut_4': xǁSerializationErrorǁ__init____mutmut_4, 
        'xǁSerializationErrorǁ__init____mutmut_5': xǁSerializationErrorǁ__init____mutmut_5, 
        'xǁSerializationErrorǁ__init____mutmut_6': xǁSerializationErrorǁ__init____mutmut_6, 
        'xǁSerializationErrorǁ__init____mutmut_7': xǁSerializationErrorǁ__init____mutmut_7, 
        'xǁSerializationErrorǁ__init____mutmut_8': xǁSerializationErrorǁ__init____mutmut_8, 
        'xǁSerializationErrorǁ__init____mutmut_9': xǁSerializationErrorǁ__init____mutmut_9, 
        'xǁSerializationErrorǁ__init____mutmut_10': xǁSerializationErrorǁ__init____mutmut_10, 
        'xǁSerializationErrorǁ__init____mutmut_11': xǁSerializationErrorǁ__init____mutmut_11, 
        'xǁSerializationErrorǁ__init____mutmut_12': xǁSerializationErrorǁ__init____mutmut_12, 
        'xǁSerializationErrorǁ__init____mutmut_13': xǁSerializationErrorǁ__init____mutmut_13, 
        'xǁSerializationErrorǁ__init____mutmut_14': xǁSerializationErrorǁ__init____mutmut_14, 
        'xǁSerializationErrorǁ__init____mutmut_15': xǁSerializationErrorǁ__init____mutmut_15, 
        'xǁSerializationErrorǁ__init____mutmut_16': xǁSerializationErrorǁ__init____mutmut_16, 
        'xǁSerializationErrorǁ__init____mutmut_17': xǁSerializationErrorǁ__init____mutmut_17, 
        'xǁSerializationErrorǁ__init____mutmut_18': xǁSerializationErrorǁ__init____mutmut_18, 
        'xǁSerializationErrorǁ__init____mutmut_19': xǁSerializationErrorǁ__init____mutmut_19, 
        'xǁSerializationErrorǁ__init____mutmut_20': xǁSerializationErrorǁ__init____mutmut_20, 
        'xǁSerializationErrorǁ__init____mutmut_21': xǁSerializationErrorǁ__init____mutmut_21, 
        'xǁSerializationErrorǁ__init____mutmut_22': xǁSerializationErrorǁ__init____mutmut_22, 
        'xǁSerializationErrorǁ__init____mutmut_23': xǁSerializationErrorǁ__init____mutmut_23, 
        'xǁSerializationErrorǁ__init____mutmut_24': xǁSerializationErrorǁ__init____mutmut_24, 
        'xǁSerializationErrorǁ__init____mutmut_25': xǁSerializationErrorǁ__init____mutmut_25, 
        'xǁSerializationErrorǁ__init____mutmut_26': xǁSerializationErrorǁ__init____mutmut_26, 
        'xǁSerializationErrorǁ__init____mutmut_27': xǁSerializationErrorǁ__init____mutmut_27, 
        'xǁSerializationErrorǁ__init____mutmut_28': xǁSerializationErrorǁ__init____mutmut_28, 
        'xǁSerializationErrorǁ__init____mutmut_29': xǁSerializationErrorǁ__init____mutmut_29, 
        'xǁSerializationErrorǁ__init____mutmut_30': xǁSerializationErrorǁ__init____mutmut_30, 
        'xǁSerializationErrorǁ__init____mutmut_31': xǁSerializationErrorǁ__init____mutmut_31, 
        'xǁSerializationErrorǁ__init____mutmut_32': xǁSerializationErrorǁ__init____mutmut_32, 
        'xǁSerializationErrorǁ__init____mutmut_33': xǁSerializationErrorǁ__init____mutmut_33, 
        'xǁSerializationErrorǁ__init____mutmut_34': xǁSerializationErrorǁ__init____mutmut_34, 
        'xǁSerializationErrorǁ__init____mutmut_35': xǁSerializationErrorǁ__init____mutmut_35, 
        'xǁSerializationErrorǁ__init____mutmut_36': xǁSerializationErrorǁ__init____mutmut_36, 
        'xǁSerializationErrorǁ__init____mutmut_37': xǁSerializationErrorǁ__init____mutmut_37, 
        'xǁSerializationErrorǁ__init____mutmut_38': xǁSerializationErrorǁ__init____mutmut_38, 
        'xǁSerializationErrorǁ__init____mutmut_39': xǁSerializationErrorǁ__init____mutmut_39, 
        'xǁSerializationErrorǁ__init____mutmut_40': xǁSerializationErrorǁ__init____mutmut_40, 
        'xǁSerializationErrorǁ__init____mutmut_41': xǁSerializationErrorǁ__init____mutmut_41
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSerializationErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁSerializationErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁSerializationErrorǁ__init____mutmut_orig)
    xǁSerializationErrorǁ__init____mutmut_orig.__name__ = 'xǁSerializationErrorǁ__init__'


class DeserializationError(EncodingError):
    """
    Raised when deserialization of data fails.

    This exception occurs when serialized data cannot be converted back into
    a Cty value, such as when the data is corrupt or in an incompatible format.

    Attributes:
        message: A human-readable error description
        data: The data that failed to deserialize
        format_name: The name of the format that was being used
    """

    def xǁDeserializationErrorǁ__init____mutmut_orig(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "deserialize"

        if data is not None:
            if hasattr(data, "__len__"):
                data_with_len = cast(list[Any] | dict[Any, Any] | str | bytes, data)
                context["cty.deserialized_data_size"] = len(data_with_len)
            else:
                context["cty.deserialized_data_size"] = "unknown"

        super().__init__(message, data, format_name, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_1(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = None
        context["cty.serialization_direction"] = "deserialize"

        if data is not None:
            if hasattr(data, "__len__"):
                data_with_len = cast(list[Any] | dict[Any, Any] | str | bytes, data)
                context["cty.deserialized_data_size"] = len(data_with_len)
            else:
                context["cty.deserialized_data_size"] = "unknown"

        super().__init__(message, data, format_name, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_2(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault(None, {})
        context["cty.serialization_direction"] = "deserialize"

        if data is not None:
            if hasattr(data, "__len__"):
                data_with_len = cast(list[Any] | dict[Any, Any] | str | bytes, data)
                context["cty.deserialized_data_size"] = len(data_with_len)
            else:
                context["cty.deserialized_data_size"] = "unknown"

        super().__init__(message, data, format_name, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_3(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", None)
        context["cty.serialization_direction"] = "deserialize"

        if data is not None:
            if hasattr(data, "__len__"):
                data_with_len = cast(list[Any] | dict[Any, Any] | str | bytes, data)
                context["cty.deserialized_data_size"] = len(data_with_len)
            else:
                context["cty.deserialized_data_size"] = "unknown"

        super().__init__(message, data, format_name, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_4(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault({})
        context["cty.serialization_direction"] = "deserialize"

        if data is not None:
            if hasattr(data, "__len__"):
                data_with_len = cast(list[Any] | dict[Any, Any] | str | bytes, data)
                context["cty.deserialized_data_size"] = len(data_with_len)
            else:
                context["cty.deserialized_data_size"] = "unknown"

        super().__init__(message, data, format_name, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_5(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", )
        context["cty.serialization_direction"] = "deserialize"

        if data is not None:
            if hasattr(data, "__len__"):
                data_with_len = cast(list[Any] | dict[Any, Any] | str | bytes, data)
                context["cty.deserialized_data_size"] = len(data_with_len)
            else:
                context["cty.deserialized_data_size"] = "unknown"

        super().__init__(message, data, format_name, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_6(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault("XXcontextXX", {})
        context["cty.serialization_direction"] = "deserialize"

        if data is not None:
            if hasattr(data, "__len__"):
                data_with_len = cast(list[Any] | dict[Any, Any] | str | bytes, data)
                context["cty.deserialized_data_size"] = len(data_with_len)
            else:
                context["cty.deserialized_data_size"] = "unknown"

        super().__init__(message, data, format_name, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_7(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault("CONTEXT", {})
        context["cty.serialization_direction"] = "deserialize"

        if data is not None:
            if hasattr(data, "__len__"):
                data_with_len = cast(list[Any] | dict[Any, Any] | str | bytes, data)
                context["cty.deserialized_data_size"] = len(data_with_len)
            else:
                context["cty.deserialized_data_size"] = "unknown"

        super().__init__(message, data, format_name, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_8(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = None

        if data is not None:
            if hasattr(data, "__len__"):
                data_with_len = cast(list[Any] | dict[Any, Any] | str | bytes, data)
                context["cty.deserialized_data_size"] = len(data_with_len)
            else:
                context["cty.deserialized_data_size"] = "unknown"

        super().__init__(message, data, format_name, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_9(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["XXcty.serialization_directionXX"] = "deserialize"

        if data is not None:
            if hasattr(data, "__len__"):
                data_with_len = cast(list[Any] | dict[Any, Any] | str | bytes, data)
                context["cty.deserialized_data_size"] = len(data_with_len)
            else:
                context["cty.deserialized_data_size"] = "unknown"

        super().__init__(message, data, format_name, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_10(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["CTY.SERIALIZATION_DIRECTION"] = "deserialize"

        if data is not None:
            if hasattr(data, "__len__"):
                data_with_len = cast(list[Any] | dict[Any, Any] | str | bytes, data)
                context["cty.deserialized_data_size"] = len(data_with_len)
            else:
                context["cty.deserialized_data_size"] = "unknown"

        super().__init__(message, data, format_name, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_11(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "XXdeserializeXX"

        if data is not None:
            if hasattr(data, "__len__"):
                data_with_len = cast(list[Any] | dict[Any, Any] | str | bytes, data)
                context["cty.deserialized_data_size"] = len(data_with_len)
            else:
                context["cty.deserialized_data_size"] = "unknown"

        super().__init__(message, data, format_name, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_12(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "DESERIALIZE"

        if data is not None:
            if hasattr(data, "__len__"):
                data_with_len = cast(list[Any] | dict[Any, Any] | str | bytes, data)
                context["cty.deserialized_data_size"] = len(data_with_len)
            else:
                context["cty.deserialized_data_size"] = "unknown"

        super().__init__(message, data, format_name, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_13(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "deserialize"

        if data is None:
            if hasattr(data, "__len__"):
                data_with_len = cast(list[Any] | dict[Any, Any] | str | bytes, data)
                context["cty.deserialized_data_size"] = len(data_with_len)
            else:
                context["cty.deserialized_data_size"] = "unknown"

        super().__init__(message, data, format_name, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_14(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "deserialize"

        if data is not None:
            if hasattr(None, "__len__"):
                data_with_len = cast(list[Any] | dict[Any, Any] | str | bytes, data)
                context["cty.deserialized_data_size"] = len(data_with_len)
            else:
                context["cty.deserialized_data_size"] = "unknown"

        super().__init__(message, data, format_name, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_15(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "deserialize"

        if data is not None:
            if hasattr(data, None):
                data_with_len = cast(list[Any] | dict[Any, Any] | str | bytes, data)
                context["cty.deserialized_data_size"] = len(data_with_len)
            else:
                context["cty.deserialized_data_size"] = "unknown"

        super().__init__(message, data, format_name, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_16(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "deserialize"

        if data is not None:
            if hasattr("__len__"):
                data_with_len = cast(list[Any] | dict[Any, Any] | str | bytes, data)
                context["cty.deserialized_data_size"] = len(data_with_len)
            else:
                context["cty.deserialized_data_size"] = "unknown"

        super().__init__(message, data, format_name, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_17(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "deserialize"

        if data is not None:
            if hasattr(data, ):
                data_with_len = cast(list[Any] | dict[Any, Any] | str | bytes, data)
                context["cty.deserialized_data_size"] = len(data_with_len)
            else:
                context["cty.deserialized_data_size"] = "unknown"

        super().__init__(message, data, format_name, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_18(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "deserialize"

        if data is not None:
            if hasattr(data, "XX__len__XX"):
                data_with_len = cast(list[Any] | dict[Any, Any] | str | bytes, data)
                context["cty.deserialized_data_size"] = len(data_with_len)
            else:
                context["cty.deserialized_data_size"] = "unknown"

        super().__init__(message, data, format_name, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_19(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "deserialize"

        if data is not None:
            if hasattr(data, "__LEN__"):
                data_with_len = cast(list[Any] | dict[Any, Any] | str | bytes, data)
                context["cty.deserialized_data_size"] = len(data_with_len)
            else:
                context["cty.deserialized_data_size"] = "unknown"

        super().__init__(message, data, format_name, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_20(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "deserialize"

        if data is not None:
            if hasattr(data, "__len__"):
                data_with_len = None
                context["cty.deserialized_data_size"] = len(data_with_len)
            else:
                context["cty.deserialized_data_size"] = "unknown"

        super().__init__(message, data, format_name, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_21(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "deserialize"

        if data is not None:
            if hasattr(data, "__len__"):
                data_with_len = cast(None, data)
                context["cty.deserialized_data_size"] = len(data_with_len)
            else:
                context["cty.deserialized_data_size"] = "unknown"

        super().__init__(message, data, format_name, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_22(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "deserialize"

        if data is not None:
            if hasattr(data, "__len__"):
                data_with_len = cast(list[Any] | dict[Any, Any] | str | bytes, None)
                context["cty.deserialized_data_size"] = len(data_with_len)
            else:
                context["cty.deserialized_data_size"] = "unknown"

        super().__init__(message, data, format_name, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_23(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "deserialize"

        if data is not None:
            if hasattr(data, "__len__"):
                data_with_len = cast(data)
                context["cty.deserialized_data_size"] = len(data_with_len)
            else:
                context["cty.deserialized_data_size"] = "unknown"

        super().__init__(message, data, format_name, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_24(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "deserialize"

        if data is not None:
            if hasattr(data, "__len__"):
                data_with_len = cast(list[Any] | dict[Any, Any] | str | bytes, )
                context["cty.deserialized_data_size"] = len(data_with_len)
            else:
                context["cty.deserialized_data_size"] = "unknown"

        super().__init__(message, data, format_name, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_25(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "deserialize"

        if data is not None:
            if hasattr(data, "__len__"):
                data_with_len = cast(list[Any] | dict[Any, Any] | str & bytes, data)
                context["cty.deserialized_data_size"] = len(data_with_len)
            else:
                context["cty.deserialized_data_size"] = "unknown"

        super().__init__(message, data, format_name, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_26(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "deserialize"

        if data is not None:
            if hasattr(data, "__len__"):
                data_with_len = cast(list[Any] | dict[Any, Any] & str | bytes, data)
                context["cty.deserialized_data_size"] = len(data_with_len)
            else:
                context["cty.deserialized_data_size"] = "unknown"

        super().__init__(message, data, format_name, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_27(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "deserialize"

        if data is not None:
            if hasattr(data, "__len__"):
                data_with_len = cast(list[Any] & dict[Any, Any] | str | bytes, data)
                context["cty.deserialized_data_size"] = len(data_with_len)
            else:
                context["cty.deserialized_data_size"] = "unknown"

        super().__init__(message, data, format_name, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_28(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "deserialize"

        if data is not None:
            if hasattr(data, "__len__"):
                data_with_len = cast(list[Any] | dict[Any, Any] | str | bytes, data)
                context["cty.deserialized_data_size"] = None
            else:
                context["cty.deserialized_data_size"] = "unknown"

        super().__init__(message, data, format_name, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_29(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "deserialize"

        if data is not None:
            if hasattr(data, "__len__"):
                data_with_len = cast(list[Any] | dict[Any, Any] | str | bytes, data)
                context["XXcty.deserialized_data_sizeXX"] = len(data_with_len)
            else:
                context["cty.deserialized_data_size"] = "unknown"

        super().__init__(message, data, format_name, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_30(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "deserialize"

        if data is not None:
            if hasattr(data, "__len__"):
                data_with_len = cast(list[Any] | dict[Any, Any] | str | bytes, data)
                context["CTY.DESERIALIZED_DATA_SIZE"] = len(data_with_len)
            else:
                context["cty.deserialized_data_size"] = "unknown"

        super().__init__(message, data, format_name, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_31(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "deserialize"

        if data is not None:
            if hasattr(data, "__len__"):
                data_with_len = cast(list[Any] | dict[Any, Any] | str | bytes, data)
                context["cty.deserialized_data_size"] = len(data_with_len)
            else:
                context["cty.deserialized_data_size"] = None

        super().__init__(message, data, format_name, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_32(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "deserialize"

        if data is not None:
            if hasattr(data, "__len__"):
                data_with_len = cast(list[Any] | dict[Any, Any] | str | bytes, data)
                context["cty.deserialized_data_size"] = len(data_with_len)
            else:
                context["XXcty.deserialized_data_sizeXX"] = "unknown"

        super().__init__(message, data, format_name, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_33(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "deserialize"

        if data is not None:
            if hasattr(data, "__len__"):
                data_with_len = cast(list[Any] | dict[Any, Any] | str | bytes, data)
                context["cty.deserialized_data_size"] = len(data_with_len)
            else:
                context["CTY.DESERIALIZED_DATA_SIZE"] = "unknown"

        super().__init__(message, data, format_name, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_34(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "deserialize"

        if data is not None:
            if hasattr(data, "__len__"):
                data_with_len = cast(list[Any] | dict[Any, Any] | str | bytes, data)
                context["cty.deserialized_data_size"] = len(data_with_len)
            else:
                context["cty.deserialized_data_size"] = "XXunknownXX"

        super().__init__(message, data, format_name, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_35(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "deserialize"

        if data is not None:
            if hasattr(data, "__len__"):
                data_with_len = cast(list[Any] | dict[Any, Any] | str | bytes, data)
                context["cty.deserialized_data_size"] = len(data_with_len)
            else:
                context["cty.deserialized_data_size"] = "UNKNOWN"

        super().__init__(message, data, format_name, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_36(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "deserialize"

        if data is not None:
            if hasattr(data, "__len__"):
                data_with_len = cast(list[Any] | dict[Any, Any] | str | bytes, data)
                context["cty.deserialized_data_size"] = len(data_with_len)
            else:
                context["cty.deserialized_data_size"] = "unknown"

        super().__init__(None, data, format_name, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_37(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "deserialize"

        if data is not None:
            if hasattr(data, "__len__"):
                data_with_len = cast(list[Any] | dict[Any, Any] | str | bytes, data)
                context["cty.deserialized_data_size"] = len(data_with_len)
            else:
                context["cty.deserialized_data_size"] = "unknown"

        super().__init__(message, None, format_name, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_38(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "deserialize"

        if data is not None:
            if hasattr(data, "__len__"):
                data_with_len = cast(list[Any] | dict[Any, Any] | str | bytes, data)
                context["cty.deserialized_data_size"] = len(data_with_len)
            else:
                context["cty.deserialized_data_size"] = "unknown"

        super().__init__(message, data, None, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_39(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "deserialize"

        if data is not None:
            if hasattr(data, "__len__"):
                data_with_len = cast(list[Any] | dict[Any, Any] | str | bytes, data)
                context["cty.deserialized_data_size"] = len(data_with_len)
            else:
                context["cty.deserialized_data_size"] = "unknown"

        super().__init__(data, format_name, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_40(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "deserialize"

        if data is not None:
            if hasattr(data, "__len__"):
                data_with_len = cast(list[Any] | dict[Any, Any] | str | bytes, data)
                context["cty.deserialized_data_size"] = len(data_with_len)
            else:
                context["cty.deserialized_data_size"] = "unknown"

        super().__init__(message, format_name, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_41(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "deserialize"

        if data is not None:
            if hasattr(data, "__len__"):
                data_with_len = cast(list[Any] | dict[Any, Any] | str | bytes, data)
                context["cty.deserialized_data_size"] = len(data_with_len)
            else:
                context["cty.deserialized_data_size"] = "unknown"

        super().__init__(message, data, **kwargs)

    def xǁDeserializationErrorǁ__init____mutmut_42(
        self,
        message: str,
        data: object = None,
        format_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the DeserializationError.

        Args:
            message: The base error message.
            data: The data that failed to deserialize.
            format_name: The name of the deserialization format.
        """
        # Add deserialization-specific context
        context: dict[str, Any] = kwargs.setdefault("context", {})
        context["cty.serialization_direction"] = "deserialize"

        if data is not None:
            if hasattr(data, "__len__"):
                data_with_len = cast(list[Any] | dict[Any, Any] | str | bytes, data)
                context["cty.deserialized_data_size"] = len(data_with_len)
            else:
                context["cty.deserialized_data_size"] = "unknown"

        super().__init__(message, data, format_name, )
    
    xǁDeserializationErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDeserializationErrorǁ__init____mutmut_1': xǁDeserializationErrorǁ__init____mutmut_1, 
        'xǁDeserializationErrorǁ__init____mutmut_2': xǁDeserializationErrorǁ__init____mutmut_2, 
        'xǁDeserializationErrorǁ__init____mutmut_3': xǁDeserializationErrorǁ__init____mutmut_3, 
        'xǁDeserializationErrorǁ__init____mutmut_4': xǁDeserializationErrorǁ__init____mutmut_4, 
        'xǁDeserializationErrorǁ__init____mutmut_5': xǁDeserializationErrorǁ__init____mutmut_5, 
        'xǁDeserializationErrorǁ__init____mutmut_6': xǁDeserializationErrorǁ__init____mutmut_6, 
        'xǁDeserializationErrorǁ__init____mutmut_7': xǁDeserializationErrorǁ__init____mutmut_7, 
        'xǁDeserializationErrorǁ__init____mutmut_8': xǁDeserializationErrorǁ__init____mutmut_8, 
        'xǁDeserializationErrorǁ__init____mutmut_9': xǁDeserializationErrorǁ__init____mutmut_9, 
        'xǁDeserializationErrorǁ__init____mutmut_10': xǁDeserializationErrorǁ__init____mutmut_10, 
        'xǁDeserializationErrorǁ__init____mutmut_11': xǁDeserializationErrorǁ__init____mutmut_11, 
        'xǁDeserializationErrorǁ__init____mutmut_12': xǁDeserializationErrorǁ__init____mutmut_12, 
        'xǁDeserializationErrorǁ__init____mutmut_13': xǁDeserializationErrorǁ__init____mutmut_13, 
        'xǁDeserializationErrorǁ__init____mutmut_14': xǁDeserializationErrorǁ__init____mutmut_14, 
        'xǁDeserializationErrorǁ__init____mutmut_15': xǁDeserializationErrorǁ__init____mutmut_15, 
        'xǁDeserializationErrorǁ__init____mutmut_16': xǁDeserializationErrorǁ__init____mutmut_16, 
        'xǁDeserializationErrorǁ__init____mutmut_17': xǁDeserializationErrorǁ__init____mutmut_17, 
        'xǁDeserializationErrorǁ__init____mutmut_18': xǁDeserializationErrorǁ__init____mutmut_18, 
        'xǁDeserializationErrorǁ__init____mutmut_19': xǁDeserializationErrorǁ__init____mutmut_19, 
        'xǁDeserializationErrorǁ__init____mutmut_20': xǁDeserializationErrorǁ__init____mutmut_20, 
        'xǁDeserializationErrorǁ__init____mutmut_21': xǁDeserializationErrorǁ__init____mutmut_21, 
        'xǁDeserializationErrorǁ__init____mutmut_22': xǁDeserializationErrorǁ__init____mutmut_22, 
        'xǁDeserializationErrorǁ__init____mutmut_23': xǁDeserializationErrorǁ__init____mutmut_23, 
        'xǁDeserializationErrorǁ__init____mutmut_24': xǁDeserializationErrorǁ__init____mutmut_24, 
        'xǁDeserializationErrorǁ__init____mutmut_25': xǁDeserializationErrorǁ__init____mutmut_25, 
        'xǁDeserializationErrorǁ__init____mutmut_26': xǁDeserializationErrorǁ__init____mutmut_26, 
        'xǁDeserializationErrorǁ__init____mutmut_27': xǁDeserializationErrorǁ__init____mutmut_27, 
        'xǁDeserializationErrorǁ__init____mutmut_28': xǁDeserializationErrorǁ__init____mutmut_28, 
        'xǁDeserializationErrorǁ__init____mutmut_29': xǁDeserializationErrorǁ__init____mutmut_29, 
        'xǁDeserializationErrorǁ__init____mutmut_30': xǁDeserializationErrorǁ__init____mutmut_30, 
        'xǁDeserializationErrorǁ__init____mutmut_31': xǁDeserializationErrorǁ__init____mutmut_31, 
        'xǁDeserializationErrorǁ__init____mutmut_32': xǁDeserializationErrorǁ__init____mutmut_32, 
        'xǁDeserializationErrorǁ__init____mutmut_33': xǁDeserializationErrorǁ__init____mutmut_33, 
        'xǁDeserializationErrorǁ__init____mutmut_34': xǁDeserializationErrorǁ__init____mutmut_34, 
        'xǁDeserializationErrorǁ__init____mutmut_35': xǁDeserializationErrorǁ__init____mutmut_35, 
        'xǁDeserializationErrorǁ__init____mutmut_36': xǁDeserializationErrorǁ__init____mutmut_36, 
        'xǁDeserializationErrorǁ__init____mutmut_37': xǁDeserializationErrorǁ__init____mutmut_37, 
        'xǁDeserializationErrorǁ__init____mutmut_38': xǁDeserializationErrorǁ__init____mutmut_38, 
        'xǁDeserializationErrorǁ__init____mutmut_39': xǁDeserializationErrorǁ__init____mutmut_39, 
        'xǁDeserializationErrorǁ__init____mutmut_40': xǁDeserializationErrorǁ__init____mutmut_40, 
        'xǁDeserializationErrorǁ__init____mutmut_41': xǁDeserializationErrorǁ__init____mutmut_41, 
        'xǁDeserializationErrorǁ__init____mutmut_42': xǁDeserializationErrorǁ__init____mutmut_42
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDeserializationErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁDeserializationErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁDeserializationErrorǁ__init____mutmut_orig)
    xǁDeserializationErrorǁ__init____mutmut_orig.__name__ = 'xǁDeserializationErrorǁ__init__'


class DynamicValueError(SerializationError):
    """
    Raised when there's an error encoding or decoding a DynamicValue.

    This exception is specific to the handling of dynamic values in
    serialization contexts, where type information might be unknown
    or ambiguous.

    Attributes:
        message: A human-readable error description
        value: The dynamic value that caused the error
    """

    def xǁDynamicValueErrorǁ__init____mutmut_orig(self, message: str, value: object = None) -> None:
        """
        Initializes the DynamicValueError.

        Args:
            message: The base error message.
            value: The dynamic value that caused the error.
        """
        super().__init__(message, value, "DynamicValue")

    def xǁDynamicValueErrorǁ__init____mutmut_1(self, message: str, value: object = None) -> None:
        """
        Initializes the DynamicValueError.

        Args:
            message: The base error message.
            value: The dynamic value that caused the error.
        """
        super().__init__(None, value, "DynamicValue")

    def xǁDynamicValueErrorǁ__init____mutmut_2(self, message: str, value: object = None) -> None:
        """
        Initializes the DynamicValueError.

        Args:
            message: The base error message.
            value: The dynamic value that caused the error.
        """
        super().__init__(message, None, "DynamicValue")

    def xǁDynamicValueErrorǁ__init____mutmut_3(self, message: str, value: object = None) -> None:
        """
        Initializes the DynamicValueError.

        Args:
            message: The base error message.
            value: The dynamic value that caused the error.
        """
        super().__init__(message, value, None)

    def xǁDynamicValueErrorǁ__init____mutmut_4(self, message: str, value: object = None) -> None:
        """
        Initializes the DynamicValueError.

        Args:
            message: The base error message.
            value: The dynamic value that caused the error.
        """
        super().__init__(value, "DynamicValue")

    def xǁDynamicValueErrorǁ__init____mutmut_5(self, message: str, value: object = None) -> None:
        """
        Initializes the DynamicValueError.

        Args:
            message: The base error message.
            value: The dynamic value that caused the error.
        """
        super().__init__(message, "DynamicValue")

    def xǁDynamicValueErrorǁ__init____mutmut_6(self, message: str, value: object = None) -> None:
        """
        Initializes the DynamicValueError.

        Args:
            message: The base error message.
            value: The dynamic value that caused the error.
        """
        super().__init__(message, value, )

    def xǁDynamicValueErrorǁ__init____mutmut_7(self, message: str, value: object = None) -> None:
        """
        Initializes the DynamicValueError.

        Args:
            message: The base error message.
            value: The dynamic value that caused the error.
        """
        super().__init__(message, value, "XXDynamicValueXX")

    def xǁDynamicValueErrorǁ__init____mutmut_8(self, message: str, value: object = None) -> None:
        """
        Initializes the DynamicValueError.

        Args:
            message: The base error message.
            value: The dynamic value that caused the error.
        """
        super().__init__(message, value, "dynamicvalue")

    def xǁDynamicValueErrorǁ__init____mutmut_9(self, message: str, value: object = None) -> None:
        """
        Initializes the DynamicValueError.

        Args:
            message: The base error message.
            value: The dynamic value that caused the error.
        """
        super().__init__(message, value, "DYNAMICVALUE")
    
    xǁDynamicValueErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDynamicValueErrorǁ__init____mutmut_1': xǁDynamicValueErrorǁ__init____mutmut_1, 
        'xǁDynamicValueErrorǁ__init____mutmut_2': xǁDynamicValueErrorǁ__init____mutmut_2, 
        'xǁDynamicValueErrorǁ__init____mutmut_3': xǁDynamicValueErrorǁ__init____mutmut_3, 
        'xǁDynamicValueErrorǁ__init____mutmut_4': xǁDynamicValueErrorǁ__init____mutmut_4, 
        'xǁDynamicValueErrorǁ__init____mutmut_5': xǁDynamicValueErrorǁ__init____mutmut_5, 
        'xǁDynamicValueErrorǁ__init____mutmut_6': xǁDynamicValueErrorǁ__init____mutmut_6, 
        'xǁDynamicValueErrorǁ__init____mutmut_7': xǁDynamicValueErrorǁ__init____mutmut_7, 
        'xǁDynamicValueErrorǁ__init____mutmut_8': xǁDynamicValueErrorǁ__init____mutmut_8, 
        'xǁDynamicValueErrorǁ__init____mutmut_9': xǁDynamicValueErrorǁ__init____mutmut_9
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDynamicValueErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁDynamicValueErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁDynamicValueErrorǁ__init____mutmut_orig)
    xǁDynamicValueErrorǁ__init____mutmut_orig.__name__ = 'xǁDynamicValueErrorǁ__init__'


class JsonEncodingError(EncodingError):
    """
    Raised when JSON encoding or decoding fails.

    This exception provides specific context for JSON serialization errors,
    including details about the specific JSON operation that failed.

    Attributes:
        message: A human-readable error description
        data: The data that caused the encoding error
        operation: The operation that failed (encode/decode)
    """

    def xǁJsonEncodingErrorǁ__init____mutmut_orig(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the JsonEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the JSON operation.
            operation: The JSON operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        # Pass original message, data, and "json" as encoding to EncodingError
        super().__init__(message, data, "json")
        # Now, self.args[0] is "JSON encoding error: {message}"
        # Prepend operation part if it exists
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            # Remove the "JSON encoding error: " part, add op, then re-add prefix
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁJsonEncodingErrorǁ__init____mutmut_1(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the JsonEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the JSON operation.
            operation: The JSON operation that failed (e.g., "encode", "decode").
        """
        self.operation = None
        # Pass original message, data, and "json" as encoding to EncodingError
        super().__init__(message, data, "json")
        # Now, self.args[0] is "JSON encoding error: {message}"
        # Prepend operation part if it exists
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            # Remove the "JSON encoding error: " part, add op, then re-add prefix
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁJsonEncodingErrorǁ__init____mutmut_2(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the JsonEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the JSON operation.
            operation: The JSON operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        # Pass original message, data, and "json" as encoding to EncodingError
        super().__init__(None, data, "json")
        # Now, self.args[0] is "JSON encoding error: {message}"
        # Prepend operation part if it exists
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            # Remove the "JSON encoding error: " part, add op, then re-add prefix
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁJsonEncodingErrorǁ__init____mutmut_3(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the JsonEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the JSON operation.
            operation: The JSON operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        # Pass original message, data, and "json" as encoding to EncodingError
        super().__init__(message, None, "json")
        # Now, self.args[0] is "JSON encoding error: {message}"
        # Prepend operation part if it exists
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            # Remove the "JSON encoding error: " part, add op, then re-add prefix
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁJsonEncodingErrorǁ__init____mutmut_4(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the JsonEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the JSON operation.
            operation: The JSON operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        # Pass original message, data, and "json" as encoding to EncodingError
        super().__init__(message, data, None)
        # Now, self.args[0] is "JSON encoding error: {message}"
        # Prepend operation part if it exists
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            # Remove the "JSON encoding error: " part, add op, then re-add prefix
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁJsonEncodingErrorǁ__init____mutmut_5(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the JsonEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the JSON operation.
            operation: The JSON operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        # Pass original message, data, and "json" as encoding to EncodingError
        super().__init__(data, "json")
        # Now, self.args[0] is "JSON encoding error: {message}"
        # Prepend operation part if it exists
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            # Remove the "JSON encoding error: " part, add op, then re-add prefix
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁJsonEncodingErrorǁ__init____mutmut_6(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the JsonEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the JSON operation.
            operation: The JSON operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        # Pass original message, data, and "json" as encoding to EncodingError
        super().__init__(message, "json")
        # Now, self.args[0] is "JSON encoding error: {message}"
        # Prepend operation part if it exists
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            # Remove the "JSON encoding error: " part, add op, then re-add prefix
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁJsonEncodingErrorǁ__init____mutmut_7(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the JsonEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the JSON operation.
            operation: The JSON operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        # Pass original message, data, and "json" as encoding to EncodingError
        super().__init__(message, data, )
        # Now, self.args[0] is "JSON encoding error: {message}"
        # Prepend operation part if it exists
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            # Remove the "JSON encoding error: " part, add op, then re-add prefix
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁJsonEncodingErrorǁ__init____mutmut_8(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the JsonEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the JSON operation.
            operation: The JSON operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        # Pass original message, data, and "json" as encoding to EncodingError
        super().__init__(message, data, "XXjsonXX")
        # Now, self.args[0] is "JSON encoding error: {message}"
        # Prepend operation part if it exists
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            # Remove the "JSON encoding error: " part, add op, then re-add prefix
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁJsonEncodingErrorǁ__init____mutmut_9(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the JsonEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the JSON operation.
            operation: The JSON operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        # Pass original message, data, and "json" as encoding to EncodingError
        super().__init__(message, data, "JSON")
        # Now, self.args[0] is "JSON encoding error: {message}"
        # Prepend operation part if it exists
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            # Remove the "JSON encoding error: " part, add op, then re-add prefix
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁJsonEncodingErrorǁ__init____mutmut_10(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the JsonEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the JSON operation.
            operation: The JSON operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        # Pass original message, data, and "json" as encoding to EncodingError
        super().__init__(message, data, "json")
        # Now, self.args[0] is "JSON encoding error: {message}"
        # Prepend operation part if it exists
        if operation or self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            # Remove the "JSON encoding error: " part, add op, then re-add prefix
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁJsonEncodingErrorǁ__init____mutmut_11(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the JsonEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the JSON operation.
            operation: The JSON operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        # Pass original message, data, and "json" as encoding to EncodingError
        super().__init__(message, data, "json")
        # Now, self.args[0] is "JSON encoding error: {message}"
        # Prepend operation part if it exists
        if operation and self.encoding:
            current_message = None
            # Remove the "JSON encoding error: " part, add op, then re-add prefix
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁJsonEncodingErrorǁ__init____mutmut_12(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the JsonEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the JSON operation.
            operation: The JSON operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        # Pass original message, data, and "json" as encoding to EncodingError
        super().__init__(message, data, "json")
        # Now, self.args[0] is "JSON encoding error: {message}"
        # Prepend operation part if it exists
        if operation and self.encoding:
            current_message = str(None) if self.args else ""
            # Remove the "JSON encoding error: " part, add op, then re-add prefix
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁJsonEncodingErrorǁ__init____mutmut_13(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the JsonEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the JSON operation.
            operation: The JSON operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        # Pass original message, data, and "json" as encoding to EncodingError
        super().__init__(message, data, "json")
        # Now, self.args[0] is "JSON encoding error: {message}"
        # Prepend operation part if it exists
        if operation and self.encoding:
            current_message = str(self.args[1]) if self.args else ""
            # Remove the "JSON encoding error: " part, add op, then re-add prefix
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁJsonEncodingErrorǁ__init____mutmut_14(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the JsonEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the JSON operation.
            operation: The JSON operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        # Pass original message, data, and "json" as encoding to EncodingError
        super().__init__(message, data, "json")
        # Now, self.args[0] is "JSON encoding error: {message}"
        # Prepend operation part if it exists
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else "XXXX"
            # Remove the "JSON encoding error: " part, add op, then re-add prefix
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁJsonEncodingErrorǁ__init____mutmut_15(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the JsonEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the JSON operation.
            operation: The JSON operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        # Pass original message, data, and "json" as encoding to EncodingError
        super().__init__(message, data, "json")
        # Now, self.args[0] is "JSON encoding error: {message}"
        # Prepend operation part if it exists
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            # Remove the "JSON encoding error: " part, add op, then re-add prefix
            base_message = None
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁJsonEncodingErrorǁ__init____mutmut_16(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the JsonEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the JSON operation.
            operation: The JSON operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        # Pass original message, data, and "json" as encoding to EncodingError
        super().__init__(message, data, "json")
        # Now, self.args[0] is "JSON encoding error: {message}"
        # Prepend operation part if it exists
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            # Remove the "JSON encoding error: " part, add op, then re-add prefix
            base_message = current_message.replace(None, "", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁJsonEncodingErrorǁ__init____mutmut_17(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the JsonEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the JSON operation.
            operation: The JSON operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        # Pass original message, data, and "json" as encoding to EncodingError
        super().__init__(message, data, "json")
        # Now, self.args[0] is "JSON encoding error: {message}"
        # Prepend operation part if it exists
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            # Remove the "JSON encoding error: " part, add op, then re-add prefix
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", None, 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁJsonEncodingErrorǁ__init____mutmut_18(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the JsonEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the JSON operation.
            operation: The JSON operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        # Pass original message, data, and "json" as encoding to EncodingError
        super().__init__(message, data, "json")
        # Now, self.args[0] is "JSON encoding error: {message}"
        # Prepend operation part if it exists
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            # Remove the "JSON encoding error: " part, add op, then re-add prefix
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", None)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁJsonEncodingErrorǁ__init____mutmut_19(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the JsonEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the JSON operation.
            operation: The JSON operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        # Pass original message, data, and "json" as encoding to EncodingError
        super().__init__(message, data, "json")
        # Now, self.args[0] is "JSON encoding error: {message}"
        # Prepend operation part if it exists
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            # Remove the "JSON encoding error: " part, add op, then re-add prefix
            base_message = current_message.replace("", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁJsonEncodingErrorǁ__init____mutmut_20(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the JsonEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the JSON operation.
            operation: The JSON operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        # Pass original message, data, and "json" as encoding to EncodingError
        super().__init__(message, data, "json")
        # Now, self.args[0] is "JSON encoding error: {message}"
        # Prepend operation part if it exists
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            # Remove the "JSON encoding error: " part, add op, then re-add prefix
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁJsonEncodingErrorǁ__init____mutmut_21(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the JsonEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the JSON operation.
            operation: The JSON operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        # Pass original message, data, and "json" as encoding to EncodingError
        super().__init__(message, data, "json")
        # Now, self.args[0] is "JSON encoding error: {message}"
        # Prepend operation part if it exists
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            # Remove the "JSON encoding error: " part, add op, then re-add prefix
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", )
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁJsonEncodingErrorǁ__init____mutmut_22(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the JsonEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the JSON operation.
            operation: The JSON operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        # Pass original message, data, and "json" as encoding to EncodingError
        super().__init__(message, data, "json")
        # Now, self.args[0] is "JSON encoding error: {message}"
        # Prepend operation part if it exists
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            # Remove the "JSON encoding error: " part, add op, then re-add prefix
            base_message = current_message.replace(f"{self.encoding.lower()} encoding error: ", "", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁJsonEncodingErrorǁ__init____mutmut_23(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the JsonEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the JSON operation.
            operation: The JSON operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        # Pass original message, data, and "json" as encoding to EncodingError
        super().__init__(message, data, "json")
        # Now, self.args[0] is "JSON encoding error: {message}"
        # Prepend operation part if it exists
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            # Remove the "JSON encoding error: " part, add op, then re-add prefix
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "XXXX", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁJsonEncodingErrorǁ__init____mutmut_24(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the JsonEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the JSON operation.
            operation: The JSON operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        # Pass original message, data, and "json" as encoding to EncodingError
        super().__init__(message, data, "json")
        # Now, self.args[0] is "JSON encoding error: {message}"
        # Prepend operation part if it exists
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            # Remove the "JSON encoding error: " part, add op, then re-add prefix
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", 2)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁJsonEncodingErrorǁ__init____mutmut_25(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the JsonEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the JSON operation.
            operation: The JSON operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        # Pass original message, data, and "json" as encoding to EncodingError
        super().__init__(message, data, "json")
        # Now, self.args[0] is "JSON encoding error: {message}"
        # Prepend operation part if it exists
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            # Remove the "JSON encoding error: " part, add op, then re-add prefix
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", 1)
            formatted_message = None
            self.args = (formatted_message, *self.args[1:])

    def xǁJsonEncodingErrorǁ__init____mutmut_26(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the JsonEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the JSON operation.
            operation: The JSON operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        # Pass original message, data, and "json" as encoding to EncodingError
        super().__init__(message, data, "json")
        # Now, self.args[0] is "JSON encoding error: {message}"
        # Prepend operation part if it exists
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            # Remove the "JSON encoding error: " part, add op, then re-add prefix
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", 1)
            formatted_message = f"{self.encoding.lower()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁJsonEncodingErrorǁ__init____mutmut_27(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the JsonEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the JSON operation.
            operation: The JSON operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        # Pass original message, data, and "json" as encoding to EncodingError
        super().__init__(message, data, "json")
        # Now, self.args[0] is "JSON encoding error: {message}"
        # Prepend operation part if it exists
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            # Remove the "JSON encoding error: " part, add op, then re-add prefix
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = None

    def xǁJsonEncodingErrorǁ__init____mutmut_28(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the JsonEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the JSON operation.
            operation: The JSON operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        # Pass original message, data, and "json" as encoding to EncodingError
        super().__init__(message, data, "json")
        # Now, self.args[0] is "JSON encoding error: {message}"
        # Prepend operation part if it exists
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            # Remove the "JSON encoding error: " part, add op, then re-add prefix
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[2:])
    
    xǁJsonEncodingErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁJsonEncodingErrorǁ__init____mutmut_1': xǁJsonEncodingErrorǁ__init____mutmut_1, 
        'xǁJsonEncodingErrorǁ__init____mutmut_2': xǁJsonEncodingErrorǁ__init____mutmut_2, 
        'xǁJsonEncodingErrorǁ__init____mutmut_3': xǁJsonEncodingErrorǁ__init____mutmut_3, 
        'xǁJsonEncodingErrorǁ__init____mutmut_4': xǁJsonEncodingErrorǁ__init____mutmut_4, 
        'xǁJsonEncodingErrorǁ__init____mutmut_5': xǁJsonEncodingErrorǁ__init____mutmut_5, 
        'xǁJsonEncodingErrorǁ__init____mutmut_6': xǁJsonEncodingErrorǁ__init____mutmut_6, 
        'xǁJsonEncodingErrorǁ__init____mutmut_7': xǁJsonEncodingErrorǁ__init____mutmut_7, 
        'xǁJsonEncodingErrorǁ__init____mutmut_8': xǁJsonEncodingErrorǁ__init____mutmut_8, 
        'xǁJsonEncodingErrorǁ__init____mutmut_9': xǁJsonEncodingErrorǁ__init____mutmut_9, 
        'xǁJsonEncodingErrorǁ__init____mutmut_10': xǁJsonEncodingErrorǁ__init____mutmut_10, 
        'xǁJsonEncodingErrorǁ__init____mutmut_11': xǁJsonEncodingErrorǁ__init____mutmut_11, 
        'xǁJsonEncodingErrorǁ__init____mutmut_12': xǁJsonEncodingErrorǁ__init____mutmut_12, 
        'xǁJsonEncodingErrorǁ__init____mutmut_13': xǁJsonEncodingErrorǁ__init____mutmut_13, 
        'xǁJsonEncodingErrorǁ__init____mutmut_14': xǁJsonEncodingErrorǁ__init____mutmut_14, 
        'xǁJsonEncodingErrorǁ__init____mutmut_15': xǁJsonEncodingErrorǁ__init____mutmut_15, 
        'xǁJsonEncodingErrorǁ__init____mutmut_16': xǁJsonEncodingErrorǁ__init____mutmut_16, 
        'xǁJsonEncodingErrorǁ__init____mutmut_17': xǁJsonEncodingErrorǁ__init____mutmut_17, 
        'xǁJsonEncodingErrorǁ__init____mutmut_18': xǁJsonEncodingErrorǁ__init____mutmut_18, 
        'xǁJsonEncodingErrorǁ__init____mutmut_19': xǁJsonEncodingErrorǁ__init____mutmut_19, 
        'xǁJsonEncodingErrorǁ__init____mutmut_20': xǁJsonEncodingErrorǁ__init____mutmut_20, 
        'xǁJsonEncodingErrorǁ__init____mutmut_21': xǁJsonEncodingErrorǁ__init____mutmut_21, 
        'xǁJsonEncodingErrorǁ__init____mutmut_22': xǁJsonEncodingErrorǁ__init____mutmut_22, 
        'xǁJsonEncodingErrorǁ__init____mutmut_23': xǁJsonEncodingErrorǁ__init____mutmut_23, 
        'xǁJsonEncodingErrorǁ__init____mutmut_24': xǁJsonEncodingErrorǁ__init____mutmut_24, 
        'xǁJsonEncodingErrorǁ__init____mutmut_25': xǁJsonEncodingErrorǁ__init____mutmut_25, 
        'xǁJsonEncodingErrorǁ__init____mutmut_26': xǁJsonEncodingErrorǁ__init____mutmut_26, 
        'xǁJsonEncodingErrorǁ__init____mutmut_27': xǁJsonEncodingErrorǁ__init____mutmut_27, 
        'xǁJsonEncodingErrorǁ__init____mutmut_28': xǁJsonEncodingErrorǁ__init____mutmut_28
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁJsonEncodingErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁJsonEncodingErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁJsonEncodingErrorǁ__init____mutmut_orig)
    xǁJsonEncodingErrorǁ__init____mutmut_orig.__name__ = 'xǁJsonEncodingErrorǁ__init__'


class MsgPackEncodingError(EncodingError):
    """
    Raised when MessagePack encoding or decoding fails.

    This exception provides specific context for MessagePack serialization errors,
    including details about the specific MessagePack operation that failed.

    Attributes:
        message: A human-readable error description
        data: The data that caused the encoding error
        operation: The operation that failed (encode/decode)
    """

    def xǁMsgPackEncodingErrorǁ__init____mutmut_orig(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the MsgPackEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the MessagePack operation.
            operation: The MessagePack operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        super().__init__(message, data, "msgpack")
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁMsgPackEncodingErrorǁ__init____mutmut_1(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the MsgPackEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the MessagePack operation.
            operation: The MessagePack operation that failed (e.g., "encode", "decode").
        """
        self.operation = None
        super().__init__(message, data, "msgpack")
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁMsgPackEncodingErrorǁ__init____mutmut_2(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the MsgPackEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the MessagePack operation.
            operation: The MessagePack operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        super().__init__(None, data, "msgpack")
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁMsgPackEncodingErrorǁ__init____mutmut_3(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the MsgPackEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the MessagePack operation.
            operation: The MessagePack operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        super().__init__(message, None, "msgpack")
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁMsgPackEncodingErrorǁ__init____mutmut_4(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the MsgPackEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the MessagePack operation.
            operation: The MessagePack operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        super().__init__(message, data, None)
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁMsgPackEncodingErrorǁ__init____mutmut_5(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the MsgPackEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the MessagePack operation.
            operation: The MessagePack operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        super().__init__(data, "msgpack")
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁMsgPackEncodingErrorǁ__init____mutmut_6(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the MsgPackEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the MessagePack operation.
            operation: The MessagePack operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        super().__init__(message, "msgpack")
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁMsgPackEncodingErrorǁ__init____mutmut_7(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the MsgPackEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the MessagePack operation.
            operation: The MessagePack operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        super().__init__(message, data, )
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁMsgPackEncodingErrorǁ__init____mutmut_8(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the MsgPackEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the MessagePack operation.
            operation: The MessagePack operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        super().__init__(message, data, "XXmsgpackXX")
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁMsgPackEncodingErrorǁ__init____mutmut_9(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the MsgPackEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the MessagePack operation.
            operation: The MessagePack operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        super().__init__(message, data, "MSGPACK")
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁMsgPackEncodingErrorǁ__init____mutmut_10(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the MsgPackEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the MessagePack operation.
            operation: The MessagePack operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        super().__init__(message, data, "msgpack")
        if operation or self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁMsgPackEncodingErrorǁ__init____mutmut_11(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the MsgPackEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the MessagePack operation.
            operation: The MessagePack operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        super().__init__(message, data, "msgpack")
        if operation and self.encoding:
            current_message = None
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁMsgPackEncodingErrorǁ__init____mutmut_12(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the MsgPackEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the MessagePack operation.
            operation: The MessagePack operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        super().__init__(message, data, "msgpack")
        if operation and self.encoding:
            current_message = str(None) if self.args else ""
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁMsgPackEncodingErrorǁ__init____mutmut_13(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the MsgPackEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the MessagePack operation.
            operation: The MessagePack operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        super().__init__(message, data, "msgpack")
        if operation and self.encoding:
            current_message = str(self.args[1]) if self.args else ""
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁMsgPackEncodingErrorǁ__init____mutmut_14(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the MsgPackEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the MessagePack operation.
            operation: The MessagePack operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        super().__init__(message, data, "msgpack")
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else "XXXX"
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁMsgPackEncodingErrorǁ__init____mutmut_15(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the MsgPackEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the MessagePack operation.
            operation: The MessagePack operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        super().__init__(message, data, "msgpack")
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            base_message = None
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁMsgPackEncodingErrorǁ__init____mutmut_16(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the MsgPackEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the MessagePack operation.
            operation: The MessagePack operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        super().__init__(message, data, "msgpack")
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            base_message = current_message.replace(None, "", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁMsgPackEncodingErrorǁ__init____mutmut_17(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the MsgPackEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the MessagePack operation.
            operation: The MessagePack operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        super().__init__(message, data, "msgpack")
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", None, 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁMsgPackEncodingErrorǁ__init____mutmut_18(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the MsgPackEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the MessagePack operation.
            operation: The MessagePack operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        super().__init__(message, data, "msgpack")
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", None)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁMsgPackEncodingErrorǁ__init____mutmut_19(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the MsgPackEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the MessagePack operation.
            operation: The MessagePack operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        super().__init__(message, data, "msgpack")
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            base_message = current_message.replace("", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁMsgPackEncodingErrorǁ__init____mutmut_20(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the MsgPackEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the MessagePack operation.
            operation: The MessagePack operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        super().__init__(message, data, "msgpack")
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁMsgPackEncodingErrorǁ__init____mutmut_21(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the MsgPackEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the MessagePack operation.
            operation: The MessagePack operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        super().__init__(message, data, "msgpack")
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", )
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁMsgPackEncodingErrorǁ__init____mutmut_22(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the MsgPackEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the MessagePack operation.
            operation: The MessagePack operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        super().__init__(message, data, "msgpack")
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            base_message = current_message.replace(f"{self.encoding.lower()} encoding error: ", "", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁMsgPackEncodingErrorǁ__init____mutmut_23(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the MsgPackEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the MessagePack operation.
            operation: The MessagePack operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        super().__init__(message, data, "msgpack")
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "XXXX", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁMsgPackEncodingErrorǁ__init____mutmut_24(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the MsgPackEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the MessagePack operation.
            operation: The MessagePack operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        super().__init__(message, data, "msgpack")
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", 2)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁMsgPackEncodingErrorǁ__init____mutmut_25(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the MsgPackEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the MessagePack operation.
            operation: The MessagePack operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        super().__init__(message, data, "msgpack")
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", 1)
            formatted_message = None
            self.args = (formatted_message, *self.args[1:])

    def xǁMsgPackEncodingErrorǁ__init____mutmut_26(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the MsgPackEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the MessagePack operation.
            operation: The MessagePack operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        super().__init__(message, data, "msgpack")
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", 1)
            formatted_message = f"{self.encoding.lower()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[1:])

    def xǁMsgPackEncodingErrorǁ__init____mutmut_27(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the MsgPackEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the MessagePack operation.
            operation: The MessagePack operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        super().__init__(message, data, "msgpack")
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = None

    def xǁMsgPackEncodingErrorǁ__init____mutmut_28(self, message: str, data: object = None, operation: str | None = None) -> None:
        """
        Initializes the MsgPackEncodingError.

        Args:
            message: The base error message.
            data: The data involved in the MessagePack operation.
            operation: The MessagePack operation that failed (e.g., "encode", "decode").
        """
        self.operation = operation
        super().__init__(message, data, "msgpack")
        if operation and self.encoding:
            current_message = str(self.args[0]) if self.args else ""
            base_message = current_message.replace(f"{self.encoding.upper()} encoding error: ", "", 1)
            formatted_message = f"{self.encoding.upper()} {operation} error: {base_message}"
            self.args = (formatted_message, *self.args[2:])
    
    xǁMsgPackEncodingErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMsgPackEncodingErrorǁ__init____mutmut_1': xǁMsgPackEncodingErrorǁ__init____mutmut_1, 
        'xǁMsgPackEncodingErrorǁ__init____mutmut_2': xǁMsgPackEncodingErrorǁ__init____mutmut_2, 
        'xǁMsgPackEncodingErrorǁ__init____mutmut_3': xǁMsgPackEncodingErrorǁ__init____mutmut_3, 
        'xǁMsgPackEncodingErrorǁ__init____mutmut_4': xǁMsgPackEncodingErrorǁ__init____mutmut_4, 
        'xǁMsgPackEncodingErrorǁ__init____mutmut_5': xǁMsgPackEncodingErrorǁ__init____mutmut_5, 
        'xǁMsgPackEncodingErrorǁ__init____mutmut_6': xǁMsgPackEncodingErrorǁ__init____mutmut_6, 
        'xǁMsgPackEncodingErrorǁ__init____mutmut_7': xǁMsgPackEncodingErrorǁ__init____mutmut_7, 
        'xǁMsgPackEncodingErrorǁ__init____mutmut_8': xǁMsgPackEncodingErrorǁ__init____mutmut_8, 
        'xǁMsgPackEncodingErrorǁ__init____mutmut_9': xǁMsgPackEncodingErrorǁ__init____mutmut_9, 
        'xǁMsgPackEncodingErrorǁ__init____mutmut_10': xǁMsgPackEncodingErrorǁ__init____mutmut_10, 
        'xǁMsgPackEncodingErrorǁ__init____mutmut_11': xǁMsgPackEncodingErrorǁ__init____mutmut_11, 
        'xǁMsgPackEncodingErrorǁ__init____mutmut_12': xǁMsgPackEncodingErrorǁ__init____mutmut_12, 
        'xǁMsgPackEncodingErrorǁ__init____mutmut_13': xǁMsgPackEncodingErrorǁ__init____mutmut_13, 
        'xǁMsgPackEncodingErrorǁ__init____mutmut_14': xǁMsgPackEncodingErrorǁ__init____mutmut_14, 
        'xǁMsgPackEncodingErrorǁ__init____mutmut_15': xǁMsgPackEncodingErrorǁ__init____mutmut_15, 
        'xǁMsgPackEncodingErrorǁ__init____mutmut_16': xǁMsgPackEncodingErrorǁ__init____mutmut_16, 
        'xǁMsgPackEncodingErrorǁ__init____mutmut_17': xǁMsgPackEncodingErrorǁ__init____mutmut_17, 
        'xǁMsgPackEncodingErrorǁ__init____mutmut_18': xǁMsgPackEncodingErrorǁ__init____mutmut_18, 
        'xǁMsgPackEncodingErrorǁ__init____mutmut_19': xǁMsgPackEncodingErrorǁ__init____mutmut_19, 
        'xǁMsgPackEncodingErrorǁ__init____mutmut_20': xǁMsgPackEncodingErrorǁ__init____mutmut_20, 
        'xǁMsgPackEncodingErrorǁ__init____mutmut_21': xǁMsgPackEncodingErrorǁ__init____mutmut_21, 
        'xǁMsgPackEncodingErrorǁ__init____mutmut_22': xǁMsgPackEncodingErrorǁ__init____mutmut_22, 
        'xǁMsgPackEncodingErrorǁ__init____mutmut_23': xǁMsgPackEncodingErrorǁ__init____mutmut_23, 
        'xǁMsgPackEncodingErrorǁ__init____mutmut_24': xǁMsgPackEncodingErrorǁ__init____mutmut_24, 
        'xǁMsgPackEncodingErrorǁ__init____mutmut_25': xǁMsgPackEncodingErrorǁ__init____mutmut_25, 
        'xǁMsgPackEncodingErrorǁ__init____mutmut_26': xǁMsgPackEncodingErrorǁ__init____mutmut_26, 
        'xǁMsgPackEncodingErrorǁ__init____mutmut_27': xǁMsgPackEncodingErrorǁ__init____mutmut_27, 
        'xǁMsgPackEncodingErrorǁ__init____mutmut_28': xǁMsgPackEncodingErrorǁ__init____mutmut_28
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMsgPackEncodingErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁMsgPackEncodingErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁMsgPackEncodingErrorǁ__init____mutmut_orig)
    xǁMsgPackEncodingErrorǁ__init____mutmut_orig.__name__ = 'xǁMsgPackEncodingErrorǁ__init__'


class WireFormatError(TransformationError):
    """
    Raised when wire format encoding or decoding fails.

    This exception is specific to the wire format system and provides
    additional context about the operation that failed.

    Attributes:
        message: A human-readable error description
        format_type: The wire format type that encountered an error
        operation: The operation that failed (marshal/unmarshal)
    """

    def xǁWireFormatErrorǁ__init____mutmut_orig(
        self,
        message: str,
        *,
        format_type: object = None,
        operation: str | None = None,
        **kwargs: object,  # Catches schema, target_type for TransformationError
    ) -> None:
        """
        Initializes the WireFormatError.

        Args:
            message: The base error message.
            format_type: The wire format type that encountered the error.
            operation: The wire format operation that failed (e.g., "marshal", "unmarshal").
            **kwargs: Additional arguments for the parent TransformationError.
        """
        self.format_type = format_type
        self.operation = operation

        # Initialize TransformationError with the original message and its specific args
        super().__init__(message, schema=kwargs.get("schema"), target_type=kwargs.get("target_type"))

        # self.args[0] now contains message possibly formatted by TransformationError
        # Append WireFormatError specific details to it
        current_message = str(self.args[0]) if self.args else ""

        if format_type is not None:
            format_info = f" using {format_type}"
            if operation:
                format_info = f" during {operation}{format_info}"
            current_message = f"{current_message}{format_info}"
        elif operation:  # Only operation is present, no format_type
            current_message = f"{current_message} during {operation}"

        self.args = (current_message, *self.args[1:])

    def xǁWireFormatErrorǁ__init____mutmut_1(
        self,
        message: str,
        *,
        format_type: object = None,
        operation: str | None = None,
        **kwargs: object,  # Catches schema, target_type for TransformationError
    ) -> None:
        """
        Initializes the WireFormatError.

        Args:
            message: The base error message.
            format_type: The wire format type that encountered the error.
            operation: The wire format operation that failed (e.g., "marshal", "unmarshal").
            **kwargs: Additional arguments for the parent TransformationError.
        """
        self.format_type = None
        self.operation = operation

        # Initialize TransformationError with the original message and its specific args
        super().__init__(message, schema=kwargs.get("schema"), target_type=kwargs.get("target_type"))

        # self.args[0] now contains message possibly formatted by TransformationError
        # Append WireFormatError specific details to it
        current_message = str(self.args[0]) if self.args else ""

        if format_type is not None:
            format_info = f" using {format_type}"
            if operation:
                format_info = f" during {operation}{format_info}"
            current_message = f"{current_message}{format_info}"
        elif operation:  # Only operation is present, no format_type
            current_message = f"{current_message} during {operation}"

        self.args = (current_message, *self.args[1:])

    def xǁWireFormatErrorǁ__init____mutmut_2(
        self,
        message: str,
        *,
        format_type: object = None,
        operation: str | None = None,
        **kwargs: object,  # Catches schema, target_type for TransformationError
    ) -> None:
        """
        Initializes the WireFormatError.

        Args:
            message: The base error message.
            format_type: The wire format type that encountered the error.
            operation: The wire format operation that failed (e.g., "marshal", "unmarshal").
            **kwargs: Additional arguments for the parent TransformationError.
        """
        self.format_type = format_type
        self.operation = None

        # Initialize TransformationError with the original message and its specific args
        super().__init__(message, schema=kwargs.get("schema"), target_type=kwargs.get("target_type"))

        # self.args[0] now contains message possibly formatted by TransformationError
        # Append WireFormatError specific details to it
        current_message = str(self.args[0]) if self.args else ""

        if format_type is not None:
            format_info = f" using {format_type}"
            if operation:
                format_info = f" during {operation}{format_info}"
            current_message = f"{current_message}{format_info}"
        elif operation:  # Only operation is present, no format_type
            current_message = f"{current_message} during {operation}"

        self.args = (current_message, *self.args[1:])

    def xǁWireFormatErrorǁ__init____mutmut_3(
        self,
        message: str,
        *,
        format_type: object = None,
        operation: str | None = None,
        **kwargs: object,  # Catches schema, target_type for TransformationError
    ) -> None:
        """
        Initializes the WireFormatError.

        Args:
            message: The base error message.
            format_type: The wire format type that encountered the error.
            operation: The wire format operation that failed (e.g., "marshal", "unmarshal").
            **kwargs: Additional arguments for the parent TransformationError.
        """
        self.format_type = format_type
        self.operation = operation

        # Initialize TransformationError with the original message and its specific args
        super().__init__(None, schema=kwargs.get("schema"), target_type=kwargs.get("target_type"))

        # self.args[0] now contains message possibly formatted by TransformationError
        # Append WireFormatError specific details to it
        current_message = str(self.args[0]) if self.args else ""

        if format_type is not None:
            format_info = f" using {format_type}"
            if operation:
                format_info = f" during {operation}{format_info}"
            current_message = f"{current_message}{format_info}"
        elif operation:  # Only operation is present, no format_type
            current_message = f"{current_message} during {operation}"

        self.args = (current_message, *self.args[1:])

    def xǁWireFormatErrorǁ__init____mutmut_4(
        self,
        message: str,
        *,
        format_type: object = None,
        operation: str | None = None,
        **kwargs: object,  # Catches schema, target_type for TransformationError
    ) -> None:
        """
        Initializes the WireFormatError.

        Args:
            message: The base error message.
            format_type: The wire format type that encountered the error.
            operation: The wire format operation that failed (e.g., "marshal", "unmarshal").
            **kwargs: Additional arguments for the parent TransformationError.
        """
        self.format_type = format_type
        self.operation = operation

        # Initialize TransformationError with the original message and its specific args
        super().__init__(message, schema=None, target_type=kwargs.get("target_type"))

        # self.args[0] now contains message possibly formatted by TransformationError
        # Append WireFormatError specific details to it
        current_message = str(self.args[0]) if self.args else ""

        if format_type is not None:
            format_info = f" using {format_type}"
            if operation:
                format_info = f" during {operation}{format_info}"
            current_message = f"{current_message}{format_info}"
        elif operation:  # Only operation is present, no format_type
            current_message = f"{current_message} during {operation}"

        self.args = (current_message, *self.args[1:])

    def xǁWireFormatErrorǁ__init____mutmut_5(
        self,
        message: str,
        *,
        format_type: object = None,
        operation: str | None = None,
        **kwargs: object,  # Catches schema, target_type for TransformationError
    ) -> None:
        """
        Initializes the WireFormatError.

        Args:
            message: The base error message.
            format_type: The wire format type that encountered the error.
            operation: The wire format operation that failed (e.g., "marshal", "unmarshal").
            **kwargs: Additional arguments for the parent TransformationError.
        """
        self.format_type = format_type
        self.operation = operation

        # Initialize TransformationError with the original message and its specific args
        super().__init__(message, schema=kwargs.get("schema"), target_type=None)

        # self.args[0] now contains message possibly formatted by TransformationError
        # Append WireFormatError specific details to it
        current_message = str(self.args[0]) if self.args else ""

        if format_type is not None:
            format_info = f" using {format_type}"
            if operation:
                format_info = f" during {operation}{format_info}"
            current_message = f"{current_message}{format_info}"
        elif operation:  # Only operation is present, no format_type
            current_message = f"{current_message} during {operation}"

        self.args = (current_message, *self.args[1:])

    def xǁWireFormatErrorǁ__init____mutmut_6(
        self,
        message: str,
        *,
        format_type: object = None,
        operation: str | None = None,
        **kwargs: object,  # Catches schema, target_type for TransformationError
    ) -> None:
        """
        Initializes the WireFormatError.

        Args:
            message: The base error message.
            format_type: The wire format type that encountered the error.
            operation: The wire format operation that failed (e.g., "marshal", "unmarshal").
            **kwargs: Additional arguments for the parent TransformationError.
        """
        self.format_type = format_type
        self.operation = operation

        # Initialize TransformationError with the original message and its specific args
        super().__init__(schema=kwargs.get("schema"), target_type=kwargs.get("target_type"))

        # self.args[0] now contains message possibly formatted by TransformationError
        # Append WireFormatError specific details to it
        current_message = str(self.args[0]) if self.args else ""

        if format_type is not None:
            format_info = f" using {format_type}"
            if operation:
                format_info = f" during {operation}{format_info}"
            current_message = f"{current_message}{format_info}"
        elif operation:  # Only operation is present, no format_type
            current_message = f"{current_message} during {operation}"

        self.args = (current_message, *self.args[1:])

    def xǁWireFormatErrorǁ__init____mutmut_7(
        self,
        message: str,
        *,
        format_type: object = None,
        operation: str | None = None,
        **kwargs: object,  # Catches schema, target_type for TransformationError
    ) -> None:
        """
        Initializes the WireFormatError.

        Args:
            message: The base error message.
            format_type: The wire format type that encountered the error.
            operation: The wire format operation that failed (e.g., "marshal", "unmarshal").
            **kwargs: Additional arguments for the parent TransformationError.
        """
        self.format_type = format_type
        self.operation = operation

        # Initialize TransformationError with the original message and its specific args
        super().__init__(message, target_type=kwargs.get("target_type"))

        # self.args[0] now contains message possibly formatted by TransformationError
        # Append WireFormatError specific details to it
        current_message = str(self.args[0]) if self.args else ""

        if format_type is not None:
            format_info = f" using {format_type}"
            if operation:
                format_info = f" during {operation}{format_info}"
            current_message = f"{current_message}{format_info}"
        elif operation:  # Only operation is present, no format_type
            current_message = f"{current_message} during {operation}"

        self.args = (current_message, *self.args[1:])

    def xǁWireFormatErrorǁ__init____mutmut_8(
        self,
        message: str,
        *,
        format_type: object = None,
        operation: str | None = None,
        **kwargs: object,  # Catches schema, target_type for TransformationError
    ) -> None:
        """
        Initializes the WireFormatError.

        Args:
            message: The base error message.
            format_type: The wire format type that encountered the error.
            operation: The wire format operation that failed (e.g., "marshal", "unmarshal").
            **kwargs: Additional arguments for the parent TransformationError.
        """
        self.format_type = format_type
        self.operation = operation

        # Initialize TransformationError with the original message and its specific args
        super().__init__(message, schema=kwargs.get("schema"), )

        # self.args[0] now contains message possibly formatted by TransformationError
        # Append WireFormatError specific details to it
        current_message = str(self.args[0]) if self.args else ""

        if format_type is not None:
            format_info = f" using {format_type}"
            if operation:
                format_info = f" during {operation}{format_info}"
            current_message = f"{current_message}{format_info}"
        elif operation:  # Only operation is present, no format_type
            current_message = f"{current_message} during {operation}"

        self.args = (current_message, *self.args[1:])

    def xǁWireFormatErrorǁ__init____mutmut_9(
        self,
        message: str,
        *,
        format_type: object = None,
        operation: str | None = None,
        **kwargs: object,  # Catches schema, target_type for TransformationError
    ) -> None:
        """
        Initializes the WireFormatError.

        Args:
            message: The base error message.
            format_type: The wire format type that encountered the error.
            operation: The wire format operation that failed (e.g., "marshal", "unmarshal").
            **kwargs: Additional arguments for the parent TransformationError.
        """
        self.format_type = format_type
        self.operation = operation

        # Initialize TransformationError with the original message and its specific args
        super().__init__(message, schema=kwargs.get(None), target_type=kwargs.get("target_type"))

        # self.args[0] now contains message possibly formatted by TransformationError
        # Append WireFormatError specific details to it
        current_message = str(self.args[0]) if self.args else ""

        if format_type is not None:
            format_info = f" using {format_type}"
            if operation:
                format_info = f" during {operation}{format_info}"
            current_message = f"{current_message}{format_info}"
        elif operation:  # Only operation is present, no format_type
            current_message = f"{current_message} during {operation}"

        self.args = (current_message, *self.args[1:])

    def xǁWireFormatErrorǁ__init____mutmut_10(
        self,
        message: str,
        *,
        format_type: object = None,
        operation: str | None = None,
        **kwargs: object,  # Catches schema, target_type for TransformationError
    ) -> None:
        """
        Initializes the WireFormatError.

        Args:
            message: The base error message.
            format_type: The wire format type that encountered the error.
            operation: The wire format operation that failed (e.g., "marshal", "unmarshal").
            **kwargs: Additional arguments for the parent TransformationError.
        """
        self.format_type = format_type
        self.operation = operation

        # Initialize TransformationError with the original message and its specific args
        super().__init__(message, schema=kwargs.get("XXschemaXX"), target_type=kwargs.get("target_type"))

        # self.args[0] now contains message possibly formatted by TransformationError
        # Append WireFormatError specific details to it
        current_message = str(self.args[0]) if self.args else ""

        if format_type is not None:
            format_info = f" using {format_type}"
            if operation:
                format_info = f" during {operation}{format_info}"
            current_message = f"{current_message}{format_info}"
        elif operation:  # Only operation is present, no format_type
            current_message = f"{current_message} during {operation}"

        self.args = (current_message, *self.args[1:])

    def xǁWireFormatErrorǁ__init____mutmut_11(
        self,
        message: str,
        *,
        format_type: object = None,
        operation: str | None = None,
        **kwargs: object,  # Catches schema, target_type for TransformationError
    ) -> None:
        """
        Initializes the WireFormatError.

        Args:
            message: The base error message.
            format_type: The wire format type that encountered the error.
            operation: The wire format operation that failed (e.g., "marshal", "unmarshal").
            **kwargs: Additional arguments for the parent TransformationError.
        """
        self.format_type = format_type
        self.operation = operation

        # Initialize TransformationError with the original message and its specific args
        super().__init__(message, schema=kwargs.get("SCHEMA"), target_type=kwargs.get("target_type"))

        # self.args[0] now contains message possibly formatted by TransformationError
        # Append WireFormatError specific details to it
        current_message = str(self.args[0]) if self.args else ""

        if format_type is not None:
            format_info = f" using {format_type}"
            if operation:
                format_info = f" during {operation}{format_info}"
            current_message = f"{current_message}{format_info}"
        elif operation:  # Only operation is present, no format_type
            current_message = f"{current_message} during {operation}"

        self.args = (current_message, *self.args[1:])

    def xǁWireFormatErrorǁ__init____mutmut_12(
        self,
        message: str,
        *,
        format_type: object = None,
        operation: str | None = None,
        **kwargs: object,  # Catches schema, target_type for TransformationError
    ) -> None:
        """
        Initializes the WireFormatError.

        Args:
            message: The base error message.
            format_type: The wire format type that encountered the error.
            operation: The wire format operation that failed (e.g., "marshal", "unmarshal").
            **kwargs: Additional arguments for the parent TransformationError.
        """
        self.format_type = format_type
        self.operation = operation

        # Initialize TransformationError with the original message and its specific args
        super().__init__(message, schema=kwargs.get("schema"), target_type=kwargs.get(None))

        # self.args[0] now contains message possibly formatted by TransformationError
        # Append WireFormatError specific details to it
        current_message = str(self.args[0]) if self.args else ""

        if format_type is not None:
            format_info = f" using {format_type}"
            if operation:
                format_info = f" during {operation}{format_info}"
            current_message = f"{current_message}{format_info}"
        elif operation:  # Only operation is present, no format_type
            current_message = f"{current_message} during {operation}"

        self.args = (current_message, *self.args[1:])

    def xǁWireFormatErrorǁ__init____mutmut_13(
        self,
        message: str,
        *,
        format_type: object = None,
        operation: str | None = None,
        **kwargs: object,  # Catches schema, target_type for TransformationError
    ) -> None:
        """
        Initializes the WireFormatError.

        Args:
            message: The base error message.
            format_type: The wire format type that encountered the error.
            operation: The wire format operation that failed (e.g., "marshal", "unmarshal").
            **kwargs: Additional arguments for the parent TransformationError.
        """
        self.format_type = format_type
        self.operation = operation

        # Initialize TransformationError with the original message and its specific args
        super().__init__(message, schema=kwargs.get("schema"), target_type=kwargs.get("XXtarget_typeXX"))

        # self.args[0] now contains message possibly formatted by TransformationError
        # Append WireFormatError specific details to it
        current_message = str(self.args[0]) if self.args else ""

        if format_type is not None:
            format_info = f" using {format_type}"
            if operation:
                format_info = f" during {operation}{format_info}"
            current_message = f"{current_message}{format_info}"
        elif operation:  # Only operation is present, no format_type
            current_message = f"{current_message} during {operation}"

        self.args = (current_message, *self.args[1:])

    def xǁWireFormatErrorǁ__init____mutmut_14(
        self,
        message: str,
        *,
        format_type: object = None,
        operation: str | None = None,
        **kwargs: object,  # Catches schema, target_type for TransformationError
    ) -> None:
        """
        Initializes the WireFormatError.

        Args:
            message: The base error message.
            format_type: The wire format type that encountered the error.
            operation: The wire format operation that failed (e.g., "marshal", "unmarshal").
            **kwargs: Additional arguments for the parent TransformationError.
        """
        self.format_type = format_type
        self.operation = operation

        # Initialize TransformationError with the original message and its specific args
        super().__init__(message, schema=kwargs.get("schema"), target_type=kwargs.get("TARGET_TYPE"))

        # self.args[0] now contains message possibly formatted by TransformationError
        # Append WireFormatError specific details to it
        current_message = str(self.args[0]) if self.args else ""

        if format_type is not None:
            format_info = f" using {format_type}"
            if operation:
                format_info = f" during {operation}{format_info}"
            current_message = f"{current_message}{format_info}"
        elif operation:  # Only operation is present, no format_type
            current_message = f"{current_message} during {operation}"

        self.args = (current_message, *self.args[1:])

    def xǁWireFormatErrorǁ__init____mutmut_15(
        self,
        message: str,
        *,
        format_type: object = None,
        operation: str | None = None,
        **kwargs: object,  # Catches schema, target_type for TransformationError
    ) -> None:
        """
        Initializes the WireFormatError.

        Args:
            message: The base error message.
            format_type: The wire format type that encountered the error.
            operation: The wire format operation that failed (e.g., "marshal", "unmarshal").
            **kwargs: Additional arguments for the parent TransformationError.
        """
        self.format_type = format_type
        self.operation = operation

        # Initialize TransformationError with the original message and its specific args
        super().__init__(message, schema=kwargs.get("schema"), target_type=kwargs.get("target_type"))

        # self.args[0] now contains message possibly formatted by TransformationError
        # Append WireFormatError specific details to it
        current_message = None

        if format_type is not None:
            format_info = f" using {format_type}"
            if operation:
                format_info = f" during {operation}{format_info}"
            current_message = f"{current_message}{format_info}"
        elif operation:  # Only operation is present, no format_type
            current_message = f"{current_message} during {operation}"

        self.args = (current_message, *self.args[1:])

    def xǁWireFormatErrorǁ__init____mutmut_16(
        self,
        message: str,
        *,
        format_type: object = None,
        operation: str | None = None,
        **kwargs: object,  # Catches schema, target_type for TransformationError
    ) -> None:
        """
        Initializes the WireFormatError.

        Args:
            message: The base error message.
            format_type: The wire format type that encountered the error.
            operation: The wire format operation that failed (e.g., "marshal", "unmarshal").
            **kwargs: Additional arguments for the parent TransformationError.
        """
        self.format_type = format_type
        self.operation = operation

        # Initialize TransformationError with the original message and its specific args
        super().__init__(message, schema=kwargs.get("schema"), target_type=kwargs.get("target_type"))

        # self.args[0] now contains message possibly formatted by TransformationError
        # Append WireFormatError specific details to it
        current_message = str(None) if self.args else ""

        if format_type is not None:
            format_info = f" using {format_type}"
            if operation:
                format_info = f" during {operation}{format_info}"
            current_message = f"{current_message}{format_info}"
        elif operation:  # Only operation is present, no format_type
            current_message = f"{current_message} during {operation}"

        self.args = (current_message, *self.args[1:])

    def xǁWireFormatErrorǁ__init____mutmut_17(
        self,
        message: str,
        *,
        format_type: object = None,
        operation: str | None = None,
        **kwargs: object,  # Catches schema, target_type for TransformationError
    ) -> None:
        """
        Initializes the WireFormatError.

        Args:
            message: The base error message.
            format_type: The wire format type that encountered the error.
            operation: The wire format operation that failed (e.g., "marshal", "unmarshal").
            **kwargs: Additional arguments for the parent TransformationError.
        """
        self.format_type = format_type
        self.operation = operation

        # Initialize TransformationError with the original message and its specific args
        super().__init__(message, schema=kwargs.get("schema"), target_type=kwargs.get("target_type"))

        # self.args[0] now contains message possibly formatted by TransformationError
        # Append WireFormatError specific details to it
        current_message = str(self.args[1]) if self.args else ""

        if format_type is not None:
            format_info = f" using {format_type}"
            if operation:
                format_info = f" during {operation}{format_info}"
            current_message = f"{current_message}{format_info}"
        elif operation:  # Only operation is present, no format_type
            current_message = f"{current_message} during {operation}"

        self.args = (current_message, *self.args[1:])

    def xǁWireFormatErrorǁ__init____mutmut_18(
        self,
        message: str,
        *,
        format_type: object = None,
        operation: str | None = None,
        **kwargs: object,  # Catches schema, target_type for TransformationError
    ) -> None:
        """
        Initializes the WireFormatError.

        Args:
            message: The base error message.
            format_type: The wire format type that encountered the error.
            operation: The wire format operation that failed (e.g., "marshal", "unmarshal").
            **kwargs: Additional arguments for the parent TransformationError.
        """
        self.format_type = format_type
        self.operation = operation

        # Initialize TransformationError with the original message and its specific args
        super().__init__(message, schema=kwargs.get("schema"), target_type=kwargs.get("target_type"))

        # self.args[0] now contains message possibly formatted by TransformationError
        # Append WireFormatError specific details to it
        current_message = str(self.args[0]) if self.args else "XXXX"

        if format_type is not None:
            format_info = f" using {format_type}"
            if operation:
                format_info = f" during {operation}{format_info}"
            current_message = f"{current_message}{format_info}"
        elif operation:  # Only operation is present, no format_type
            current_message = f"{current_message} during {operation}"

        self.args = (current_message, *self.args[1:])

    def xǁWireFormatErrorǁ__init____mutmut_19(
        self,
        message: str,
        *,
        format_type: object = None,
        operation: str | None = None,
        **kwargs: object,  # Catches schema, target_type for TransformationError
    ) -> None:
        """
        Initializes the WireFormatError.

        Args:
            message: The base error message.
            format_type: The wire format type that encountered the error.
            operation: The wire format operation that failed (e.g., "marshal", "unmarshal").
            **kwargs: Additional arguments for the parent TransformationError.
        """
        self.format_type = format_type
        self.operation = operation

        # Initialize TransformationError with the original message and its specific args
        super().__init__(message, schema=kwargs.get("schema"), target_type=kwargs.get("target_type"))

        # self.args[0] now contains message possibly formatted by TransformationError
        # Append WireFormatError specific details to it
        current_message = str(self.args[0]) if self.args else ""

        if format_type is None:
            format_info = f" using {format_type}"
            if operation:
                format_info = f" during {operation}{format_info}"
            current_message = f"{current_message}{format_info}"
        elif operation:  # Only operation is present, no format_type
            current_message = f"{current_message} during {operation}"

        self.args = (current_message, *self.args[1:])

    def xǁWireFormatErrorǁ__init____mutmut_20(
        self,
        message: str,
        *,
        format_type: object = None,
        operation: str | None = None,
        **kwargs: object,  # Catches schema, target_type for TransformationError
    ) -> None:
        """
        Initializes the WireFormatError.

        Args:
            message: The base error message.
            format_type: The wire format type that encountered the error.
            operation: The wire format operation that failed (e.g., "marshal", "unmarshal").
            **kwargs: Additional arguments for the parent TransformationError.
        """
        self.format_type = format_type
        self.operation = operation

        # Initialize TransformationError with the original message and its specific args
        super().__init__(message, schema=kwargs.get("schema"), target_type=kwargs.get("target_type"))

        # self.args[0] now contains message possibly formatted by TransformationError
        # Append WireFormatError specific details to it
        current_message = str(self.args[0]) if self.args else ""

        if format_type is not None:
            format_info = None
            if operation:
                format_info = f" during {operation}{format_info}"
            current_message = f"{current_message}{format_info}"
        elif operation:  # Only operation is present, no format_type
            current_message = f"{current_message} during {operation}"

        self.args = (current_message, *self.args[1:])

    def xǁWireFormatErrorǁ__init____mutmut_21(
        self,
        message: str,
        *,
        format_type: object = None,
        operation: str | None = None,
        **kwargs: object,  # Catches schema, target_type for TransformationError
    ) -> None:
        """
        Initializes the WireFormatError.

        Args:
            message: The base error message.
            format_type: The wire format type that encountered the error.
            operation: The wire format operation that failed (e.g., "marshal", "unmarshal").
            **kwargs: Additional arguments for the parent TransformationError.
        """
        self.format_type = format_type
        self.operation = operation

        # Initialize TransformationError with the original message and its specific args
        super().__init__(message, schema=kwargs.get("schema"), target_type=kwargs.get("target_type"))

        # self.args[0] now contains message possibly formatted by TransformationError
        # Append WireFormatError specific details to it
        current_message = str(self.args[0]) if self.args else ""

        if format_type is not None:
            format_info = f" using {format_type}"
            if operation:
                format_info = None
            current_message = f"{current_message}{format_info}"
        elif operation:  # Only operation is present, no format_type
            current_message = f"{current_message} during {operation}"

        self.args = (current_message, *self.args[1:])

    def xǁWireFormatErrorǁ__init____mutmut_22(
        self,
        message: str,
        *,
        format_type: object = None,
        operation: str | None = None,
        **kwargs: object,  # Catches schema, target_type for TransformationError
    ) -> None:
        """
        Initializes the WireFormatError.

        Args:
            message: The base error message.
            format_type: The wire format type that encountered the error.
            operation: The wire format operation that failed (e.g., "marshal", "unmarshal").
            **kwargs: Additional arguments for the parent TransformationError.
        """
        self.format_type = format_type
        self.operation = operation

        # Initialize TransformationError with the original message and its specific args
        super().__init__(message, schema=kwargs.get("schema"), target_type=kwargs.get("target_type"))

        # self.args[0] now contains message possibly formatted by TransformationError
        # Append WireFormatError specific details to it
        current_message = str(self.args[0]) if self.args else ""

        if format_type is not None:
            format_info = f" using {format_type}"
            if operation:
                format_info = f" during {operation}{format_info}"
            current_message = None
        elif operation:  # Only operation is present, no format_type
            current_message = f"{current_message} during {operation}"

        self.args = (current_message, *self.args[1:])

    def xǁWireFormatErrorǁ__init____mutmut_23(
        self,
        message: str,
        *,
        format_type: object = None,
        operation: str | None = None,
        **kwargs: object,  # Catches schema, target_type for TransformationError
    ) -> None:
        """
        Initializes the WireFormatError.

        Args:
            message: The base error message.
            format_type: The wire format type that encountered the error.
            operation: The wire format operation that failed (e.g., "marshal", "unmarshal").
            **kwargs: Additional arguments for the parent TransformationError.
        """
        self.format_type = format_type
        self.operation = operation

        # Initialize TransformationError with the original message and its specific args
        super().__init__(message, schema=kwargs.get("schema"), target_type=kwargs.get("target_type"))

        # self.args[0] now contains message possibly formatted by TransformationError
        # Append WireFormatError specific details to it
        current_message = str(self.args[0]) if self.args else ""

        if format_type is not None:
            format_info = f" using {format_type}"
            if operation:
                format_info = f" during {operation}{format_info}"
            current_message = f"{current_message}{format_info}"
        elif operation:  # Only operation is present, no format_type
            current_message = None

        self.args = (current_message, *self.args[1:])

    def xǁWireFormatErrorǁ__init____mutmut_24(
        self,
        message: str,
        *,
        format_type: object = None,
        operation: str | None = None,
        **kwargs: object,  # Catches schema, target_type for TransformationError
    ) -> None:
        """
        Initializes the WireFormatError.

        Args:
            message: The base error message.
            format_type: The wire format type that encountered the error.
            operation: The wire format operation that failed (e.g., "marshal", "unmarshal").
            **kwargs: Additional arguments for the parent TransformationError.
        """
        self.format_type = format_type
        self.operation = operation

        # Initialize TransformationError with the original message and its specific args
        super().__init__(message, schema=kwargs.get("schema"), target_type=kwargs.get("target_type"))

        # self.args[0] now contains message possibly formatted by TransformationError
        # Append WireFormatError specific details to it
        current_message = str(self.args[0]) if self.args else ""

        if format_type is not None:
            format_info = f" using {format_type}"
            if operation:
                format_info = f" during {operation}{format_info}"
            current_message = f"{current_message}{format_info}"
        elif operation:  # Only operation is present, no format_type
            current_message = f"{current_message} during {operation}"

        self.args = None

    def xǁWireFormatErrorǁ__init____mutmut_25(
        self,
        message: str,
        *,
        format_type: object = None,
        operation: str | None = None,
        **kwargs: object,  # Catches schema, target_type for TransformationError
    ) -> None:
        """
        Initializes the WireFormatError.

        Args:
            message: The base error message.
            format_type: The wire format type that encountered the error.
            operation: The wire format operation that failed (e.g., "marshal", "unmarshal").
            **kwargs: Additional arguments for the parent TransformationError.
        """
        self.format_type = format_type
        self.operation = operation

        # Initialize TransformationError with the original message and its specific args
        super().__init__(message, schema=kwargs.get("schema"), target_type=kwargs.get("target_type"))

        # self.args[0] now contains message possibly formatted by TransformationError
        # Append WireFormatError specific details to it
        current_message = str(self.args[0]) if self.args else ""

        if format_type is not None:
            format_info = f" using {format_type}"
            if operation:
                format_info = f" during {operation}{format_info}"
            current_message = f"{current_message}{format_info}"
        elif operation:  # Only operation is present, no format_type
            current_message = f"{current_message} during {operation}"

        self.args = (current_message, *self.args[2:])
    
    xǁWireFormatErrorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁWireFormatErrorǁ__init____mutmut_1': xǁWireFormatErrorǁ__init____mutmut_1, 
        'xǁWireFormatErrorǁ__init____mutmut_2': xǁWireFormatErrorǁ__init____mutmut_2, 
        'xǁWireFormatErrorǁ__init____mutmut_3': xǁWireFormatErrorǁ__init____mutmut_3, 
        'xǁWireFormatErrorǁ__init____mutmut_4': xǁWireFormatErrorǁ__init____mutmut_4, 
        'xǁWireFormatErrorǁ__init____mutmut_5': xǁWireFormatErrorǁ__init____mutmut_5, 
        'xǁWireFormatErrorǁ__init____mutmut_6': xǁWireFormatErrorǁ__init____mutmut_6, 
        'xǁWireFormatErrorǁ__init____mutmut_7': xǁWireFormatErrorǁ__init____mutmut_7, 
        'xǁWireFormatErrorǁ__init____mutmut_8': xǁWireFormatErrorǁ__init____mutmut_8, 
        'xǁWireFormatErrorǁ__init____mutmut_9': xǁWireFormatErrorǁ__init____mutmut_9, 
        'xǁWireFormatErrorǁ__init____mutmut_10': xǁWireFormatErrorǁ__init____mutmut_10, 
        'xǁWireFormatErrorǁ__init____mutmut_11': xǁWireFormatErrorǁ__init____mutmut_11, 
        'xǁWireFormatErrorǁ__init____mutmut_12': xǁWireFormatErrorǁ__init____mutmut_12, 
        'xǁWireFormatErrorǁ__init____mutmut_13': xǁWireFormatErrorǁ__init____mutmut_13, 
        'xǁWireFormatErrorǁ__init____mutmut_14': xǁWireFormatErrorǁ__init____mutmut_14, 
        'xǁWireFormatErrorǁ__init____mutmut_15': xǁWireFormatErrorǁ__init____mutmut_15, 
        'xǁWireFormatErrorǁ__init____mutmut_16': xǁWireFormatErrorǁ__init____mutmut_16, 
        'xǁWireFormatErrorǁ__init____mutmut_17': xǁWireFormatErrorǁ__init____mutmut_17, 
        'xǁWireFormatErrorǁ__init____mutmut_18': xǁWireFormatErrorǁ__init____mutmut_18, 
        'xǁWireFormatErrorǁ__init____mutmut_19': xǁWireFormatErrorǁ__init____mutmut_19, 
        'xǁWireFormatErrorǁ__init____mutmut_20': xǁWireFormatErrorǁ__init____mutmut_20, 
        'xǁWireFormatErrorǁ__init____mutmut_21': xǁWireFormatErrorǁ__init____mutmut_21, 
        'xǁWireFormatErrorǁ__init____mutmut_22': xǁWireFormatErrorǁ__init____mutmut_22, 
        'xǁWireFormatErrorǁ__init____mutmut_23': xǁWireFormatErrorǁ__init____mutmut_23, 
        'xǁWireFormatErrorǁ__init____mutmut_24': xǁWireFormatErrorǁ__init____mutmut_24, 
        'xǁWireFormatErrorǁ__init____mutmut_25': xǁWireFormatErrorǁ__init____mutmut_25
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁWireFormatErrorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁWireFormatErrorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁWireFormatErrorǁ__init____mutmut_orig)
    xǁWireFormatErrorǁ__init____mutmut_orig.__name__ = 'xǁWireFormatErrorǁ__init__'


# 🐍🏗️🐣
# 🌊🪢🐛🪄
