#!/usr/bin/env python3
from examples.example_utils import configure_for_example
from pyvider.cty.context import OperationContext, operation_context
from pyvider.cty.context.validation_context import deeper_validation, get_validation_depth

configure_for_example()

print(f"Initial validation depth: {get_validation_depth()}")

with deeper_validation():
    print(f"Validation depth inside 'deeper_validation': {get_validation_depth()}")

print(f"Validation depth after 'deeper_validation': {get_validation_depth()}")

with operation_context(OperationContext.CONFIG):
    print(f"Inside 'operation_context(OperationContext.CONFIG)': {operation_context(OperationContext.CONFIG)}")
