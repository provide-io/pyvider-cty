#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


import pytest

from pyvider.cty import CtyNumber, CtyObject, CtyString
from pyvider.cty.exceptions import CtyAttributeValidationError, CtyTypeMismatchError


@pytest.mark.asyncio
async def test_attribute_access_error_handling() -> None:
    person_type = CtyObject(attribute_types={"name": CtyString(), "age": CtyNumber()})
    validated = person_type.validate({"name": "Alice", "age": 30})
    with pytest.raises(CtyAttributeValidationError):
        person_type.get_attribute(validated, "unknown")
    with pytest.raises(CtyTypeMismatchError):
        person_type.get_attribute("not a cty value", "name")


# 🌊🪢🔚
