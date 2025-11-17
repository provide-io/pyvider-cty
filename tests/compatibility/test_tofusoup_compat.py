#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Cross-language compatibility tests using TofuSoup.

The Go compatibility infrastructure has been replaced by TofuSoup, which provides
comprehensive cross-language conformance testing for CTY implementations.

To run cross-language compatibility tests:

1. Install TofuSoup from the tofusoup repository
2. Run: `soup cty test`
3. Run: `soup cty benchmark` for performance validation

TofuSoup provides:
- Go harnesses for CTY serialization/deserialization
- Bidirectional testing (Go ↔ Python)
- Rich CLI tools for debugging and validation
- Performance benchmarking

For more information, see the TofuSoup repository and documentation."""

import pytest


@pytest.mark.compat
def test_tofusoup_compatibility_placeholder() -> None:
    """
    Placeholder test to maintain the @pytest.mark.compat marker.

    Actual cross-language compatibility testing should be done via TofuSoup:
    - soup cty test
    - soup cty benchmark
    """
    # This test validates that the Python fixtures can still be deserialized
    # from the existing Go-generated fixtures in compatibility/tests/fixtures/
    from pathlib import Path

    from pyvider.cty import CtyString
    from pyvider.cty.codec import cty_from_msgpack

    # Test with a simple fixture that should exist
    fixture_path = (
        Path(__file__).parent.parent.parent
        / "compatibility"
        / "tests"
        / "fixtures"
        / "go-cty"
        / "string_simple.msgpack"
    )

    if fixture_path.exists():
        packed_bytes = fixture_path.read_bytes()
        deserialized_val = cty_from_msgpack(packed_bytes, CtyString())
        assert deserialized_val.type.equal(CtyString())
        assert not deserialized_val.is_null
        assert not deserialized_val.is_unknown
    else:
        pytest.skip("Go-generated fixtures not available. Use TofuSoup for cross-language testing.")


# 🌊🪢🔚
