
# pyvider/cty/function/base.py

"""
Core function infrastructure for the Cty type system.

This module provides the base classes and utilities for defining and executing
type-safe functions on Cty values. It implements:

1. Function signature and parameter definitions
2. Type checking and validation for function calls
3. Error handling for function execution
4. The framework for the function registry

The function system follows go-cty's design but with Pythonic idioms and
asynchronous execution.
"""

import asyncio
import inspect
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Generic, List, Optional, Sequence, Type, TypeVar, Union, cast

import attrs

from pyvider.cty.logger import logger
from pyvider.cty.types.base import CtyType
from pyvider.cty.types.primitives import CtyString, CtyNumber, CtyBool
from pyvider.cty.types.collections import CtyList, CtyMap, CtySet
from pyvider.cty.types.structural import CtyObject, CtyDynamic, CtyTuple
from pyvider.cty.exceptions import ValidationError
from pyvider.cty.values import CtyValue

T = TypeVar('T')

@attrs.define(frozen=True, eq=True)
class Parameter:
    """
    Definition of a function parameter.
    
    Parameters define the expected type, name, and validation rules for
    function arguments.
    """
    name: str = attrs.field()
    type: CtyType = attrs.field()
    allow_null: bool = attrs.field(default=False)
    allow_unknown: bool = attrs.field(default=False)
    allow_dynamic_type: bool = attrs.field(default=False)
    
    @name.validator
    def _validate_name(self, attribute, value):
        """Ensure parameter name is valid."""
        if not value:
            raise ValueError("Parameter name cannot be empty")
        if not value.isidentifier():
            raise ValueError(f"Invalid parameter name: {value}")
            
    async def validate(self, value: CtyValue) -> bool:
        """
        Validate a value against this parameter's rules.
        
        Args:
            value: The value to validate
            
        Returns:
            bool: True if valid, False otherwise
            
        Raises:
            ValidationError: If validation fails
        """
        # from pyvider.cty.values.base import Value
        
        logger.debug(f"🧰🔍🔄 Validating parameter {self.name} with value {value}")
        
        # Check for null
        if value.is_null and not self.allow_null:
            raise ValidationError(f"Parameter '{self.name}' cannot be null")
            
        # Check for unknown
        if value.is_unknown and not self.allow_unknown:
            raise ValidationError(f"Parameter '{self.name}' cannot be unknown")
            
        # Check type compatibility
        if not self.allow_dynamic_type and not isinstance(value.type, type(self.type)):
            # Special case: we might be able to convert the value
            from pyvider.cty.convert.convert import can_convert
            
            if await can_convert(value.type, self.type):
                logger.debug(f"🧰🔍🔄 CtyValue can be converted to required type {self.type.__class__.__name__}")
                return True
                
            raise ValidationError(
                f"Parameter '{self.name}' expected type {self.type.__class__.__name__}, "
                f"got {value.type.__class__.__name__}"
            )
            
        return True
        
    def __str__(self) -> str:
        return f"{self.name}: {self.type.__class__.__name__}"

@attrs.define(frozen=True, eq=True)
class VariadicParameter(Parameter):
    """
    A special parameter that can accept multiple values.
    
    This represents a "rest" parameter (e.g., *args in Python),
    which can collect any remaining arguments.
    """
    min_elements: int = attrs.field(default=0)
    max_elements: Optional[int] = attrs.field(default=None)
    
    @min_elements.validator
    def _validate_min_elements(self, attribute, value):
        if value < 0:
            raise ValueError("min_elements cannot be negative")
            
    @max_elements.validator
    def _validate_max_elements(self, attribute, value):
        if value is not None and value < self.min_elements:
            raise ValueError("max_elements cannot be less than min_elements")
            
    async def validate_all(self, values: List[CtyValue]) -> bool:
        """
        Validate a list of values against this parameter's rules.
        
        Args:
            values: The values to validate
            
        Returns:
            bool: True if valid, False otherwise
            
        Raises:
            ValidationError: If validation fails
        """
        logger.debug(f"🧰🔍🔄 Validating variadic parameter {self.name} with {len(values)} values")
        
        # Check number of elements
        if len(values) < self.min_elements:
            raise ValidationError(
                f"Variadic parameter '{self.name}' requires at least {self.min_elements} elements, "
                f"got {len(values)}"
            )
            
        if self.max_elements is not None and len(values) > self.max_elements:
            raise ValidationError(
                f"Variadic parameter '{self.name}' accepts at most {self.max_elements} elements, "
                f"got {len(values)}"
            )
            
        # Validate each value
        for i, value in enumerate(values):
            try:
                await self.validate(value)
            except ValidationError as e:
                raise ValidationError(f"Variadic parameter '{self.name}' element {i}: {e}")
                
        return True

@attrs.define
class FunctionSpec:
    # Required attributes must come first
    name: str = attrs.field()
    params: List[Parameter] = attrs.field()
    return_type_fn: Callable[[List[CtyValue]], CtyType] = attrs.field()
    implementation: Callable[[List[CtyValue], CtyType], CtyValue] = attrs.field()
    
    # Optional attributes with defaults come last
    variadic_param: Optional[VariadicParameter] = attrs.field(default=None)
    description: str = attrs.field(default="")
        
    @name.validator
    def _validate_name(self, attribute, value):
        if not value:
            raise ValueError("Function name cannot be empty")
        if not value.isidentifier():
            raise ValueError(f"Invalid function name: {value}")
            
    async def validate_args(self, args: List[CtyValue]) -> bool:
        """
        Validate function arguments against the parameter specifications.
        
        Args:
            args: The arguments to validate
            
        Returns:
            bool: True if valid, False otherwise
            
        Raises:
            ValidationError: If validation fails
        """
        logger.debug(f"🧰🔍🔄 Validating {len(args)} arguments for function {self.name}")
        
        # Check number of arguments
        min_args = len(self.params)
        max_args = min_args
        
        if self.variadic_param is not None:
            min_args = len(self.params) + self.variadic_param.min_elements
            
            if self.variadic_param.max_elements is not None:
                max_args = len(self.params) + self.variadic_param.max_elements
            else:
                max_args = None  # Unlimited
                
        if len(args) < min_args:
            raise ValidationError(
                f"Function '{self.name}' requires at least {min_args} arguments, "
                f"got {len(args)}"
            )
            
        if max_args is not None and len(args) > max_args:
            raise ValidationError(
                f"Function '{self.name}' accepts at most {max_args} arguments, "
                f"got {len(args)}"
            )
            
        # Validate positional parameters
        for i, param in enumerate(self.params):
            if i < len(args):
                try:
                    await param.validate(args[i])
                except ValidationError as e:
                    raise ValidationError(f"Argument {i+1} ({param.name}): {e}")
                    
        # Validate variadic parameter
        if self.variadic_param is not None and len(args) > len(self.params):
            variadic_args = args[len(self.params):]
            await self.variadic_param.validate_all(variadic_args)
            
        return True
    
    async def call(self, args: List[CtyValue]) -> CtyValue:
        """
        Call the function with the given arguments.
        
        Args:
            args: The arguments to pass to the function
            
        Returns:
            Value: The result of the function call
            
        Raises:
            ValidationError: If argument validation fails
            Exception: If the function implementation raises an exception
        """
        logger.debug(f"🧰🚀🔄 Calling function {self.name} with {len(args)} arguments")
        
        # Validate arguments
        await self.validate_args(args)
        
        # Determine return type
        return_type = self.return_type_fn(args)
        logger.debug(f"🧰🚀🔄 Determined return type: {return_type.__class__.__name__}")
        
        # Call implementation
        try:
            result = await asyncio.to_thread(self.implementation, args, return_type)
            logger.debug(f"🧰🚀✅ Function {self.name} returned result: {result}")
            return result
        except Exception as e:
            logger.error(f"🧰🚀❌ Error in function {self.name}: {e}")
            raise

class Function:
    """
    A callable Cty function.
    
    This class wraps a FunctionSpec to provide a callable interface and
    additional metadata.
    """
    
    def __init__(self, spec: FunctionSpec):
        """
        Initialize a function with its specification.
        
        Args:
            spec: The function specification
        """
        self.spec = spec
        
    async def __call__(self, *args: CtyValue) -> CtyValue:
        """
        Call the function with the given arguments.
        
        Args:
            *args: The arguments to pass to the function
            
        Returns:
            Value: The result of the function call
            
        Raises:
            ValidationError: If argument validation fails
            Exception: If the function implementation raises an exception
        """
        # Convert args to a list
        arg_list = list(args)
        
        # Call the function spec
        return await self.spec.call(arg_list)
        
    @property
    def name(self) -> str:
        """Get the function name."""
        return self.spec.name
        
    @property
    def description(self) -> str:
        """Get the function description."""
        return self.spec.description
        
    def __str__(self) -> str:
        """String representation of the function."""
        param_strs = [str(param) for param in self.spec.params]
        if self.spec.variadic_param is not None:
            param_strs.append(f"*{self.spec.variadic_param}")
        return f"{self.name}({', '.join(param_strs)})"

class FunctionRegistry:
    """
    Registry for Cty functions.
    
    This class manages a collection of functions and provides lookup by name.
    """
    
    def __init__(self):
        """Initialize an empty function registry."""
        self._functions: Dict[str, Function] = {}
        
    def register(self, function: Function) -> None:
        """
        Register a function with the registry.
        
        Args:
            function: The function to register
            
        Raises:
            ValueError: If a function with the same name is already registered
        """
        logger.debug(f"🧰📝✅ Registering function {function.name}")
        
        if function.name in self._functions:
            raise ValueError(f"Function '{function.name}' is already registered")
            
        self._functions[function.name] = function
        
    def get(self, name: str) -> Optional[Function]:
        """
        Get a function by name.
        
        Args:
            name: The name of the function to get
            
        Returns:
            Function: The function, or None if not found
        """
        return self._functions.get(name)
        
    def has(self, name: str) -> bool:
        """
        Check if a function is registered.
        
        Args:
            name: The name of the function to check
            
        Returns:
            bool: True if the function is registered, False otherwise
        """
        return name in self._functions
        
    def list(self) -> List[str]:
        """
        List all registered function names.
        
        Returns:
            List[str]: The names of all registered functions
        """
        return list(self._functions.keys())
        
    def __iter__(self):
        """Iterate over all registered functions."""
        return iter(self._functions.values())
        
    def __len__(self) -> int:
        """Get the number of registered functions."""
        return len(self._functions)

# Global function registry
registry = FunctionRegistry()
