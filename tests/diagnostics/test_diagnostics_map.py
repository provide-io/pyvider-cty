#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TODO: Add module docstring."""

import pytest

from pyvider.cty import CtyMap, CtyMapValidationError, CtyNumber

from ._helpers import assert_diagnostic


class TestMapDiagnostics:
    def test_wrong_value_type_for_key(self) -> None:
        """
        Tests that a map with a value of the wrong type produces a
        correctly formatted diagnostic.
        """
        schema = CtyMap(element_type=CtyNumber())
        config = {"retries": 5, "timeout": "long"}

        assert_diagnostic(
            schema_type=schema,
            invalid_config=config,
            expected_error_type=CtyMapValidationError,
            expected_error_message="At ['timeout']: Number validation error: Cannot represent str value 'long' as Decimal",
        )

    def test_non_string_key_raises_error(self) -> None:
        """
        Ensures that a map with non-string keys raises a specific error.
        This test remains as-is because it checks the message with a regex match,
        not an exact string equality.
        """
        schema = CtyMap(element_type=CtyNumber())
        config = {123: 456}
        with pytest.raises(
            CtyMapValidationError,
            match="Map keys must be strings, but got key of type int",
        ):
            schema.validate(config)


# 🌊🪢🔚
