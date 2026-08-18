#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""CtyError has to be what its own docstring says it is.

It describes itself as "the root exception for all errors that occur within the
cty type system" and as usable "to catch any cty-related error". Callers write
`except CtyError` on the strength of that. The validation branch descended only
from foundation's ValidationError, so twelve of twenty-eight classes escaped
it -- including every type-validation failure, which is the one a caller is
most likely to meet.

This test enumerates the package rather than naming classes, so a new exception
added outside the branch fails here rather than in a provider's error handler.
"""

import importlib
import inspect
import pkgutil

import pytest

import pyvider.cty.exceptions as exceptions_package
from pyvider.cty.exceptions import CtyError


def _all_exception_classes() -> dict[type, str]:
    modules = [exceptions_package] + [
        importlib.import_module(f"pyvider.cty.exceptions.{module.name}")
        for module in pkgutil.iter_modules(exceptions_package.__path__)
    ]
    found: dict[type, str] = {}
    for module in modules:
        for name, obj in vars(module).items():
            if (
                inspect.isclass(obj)
                and issubclass(obj, BaseException)
                and obj.__module__.startswith("pyvider")
            ):
                found[obj] = name
    return found


def test_every_exception_in_the_package_is_a_cty_error() -> None:
    escaped = sorted(name for cls, name in _all_exception_classes().items() if not issubclass(cls, CtyError))

    assert not escaped, f"these escape `except CtyError`: {escaped}"


@pytest.mark.parametrize(
    "module_name, class_name",
    [
        ("validation", "CtyValidationError"),
        ("validation", "CtyListValidationError"),
        ("validation", "CtyTypeMismatchError"),
    ],
)
def test_validation_errors_keep_their_foundation_behaviour(module_name: str, class_name: str) -> None:
    """Joining the roots must not cost the diagnostics that motivated the other."""
    from provide.foundation.errors import ValidationError as FoundationValidationError

    cls = getattr(importlib.import_module(f"pyvider.cty.exceptions.{module_name}"), class_name)

    assert issubclass(cls, CtyError)
    assert issubclass(cls, FoundationValidationError)
