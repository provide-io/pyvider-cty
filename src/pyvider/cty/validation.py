
# pyvider/schema/validation.py

from typing import Any

import attrs

from .base import Schema


@attrs.define
class ValidationContext:
    """Context for schema validation"""
    path: list[str] = attrs.field(factory=list)
    errors: list[str] = attrs.field(factory=list)

def validate_schema(schema: Schema, data: dict[str, Any]) -> list[str]:
    """Validate data against schema"""
    ctx = ValidationContext()

    for name, field in schema._fields.items():
        value = data.get(name)

        if field.required and value is None:
            ctx.errors.append(f"Missing required field: {name}")
            continue

        if value is not None:
            try:
                field.validate(value)
            except Exception as e:
                ctx.errors.append(f"Validation failed for {name}: {e!s}")

    return ctx.errors
