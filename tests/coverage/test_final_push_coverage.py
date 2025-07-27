"""
This test suite targets the final remaining coverage gaps in the project,
particularly in capsule validation and value comparison error paths.
"""
import pytest

from pyvider.cty import CtyCapsule, CtyNumber, CtyString, CtyValue
from pyvider.cty.exceptions import CtyValidationError

class Opaque: pass
class OtherOpaque: pass

class TestFinalCoveragePush:
    """Targeted tests for remaining uncovered lines."""

    def test_capsule_validate_cty_value_wrong_inner_type(self) -> None:
        """Covers CtyCapsule.validate with a CtyValue of a different capsule type."""
        capsule_type = CtyCapsule("Opaque", Opaque)
        
        # A CtyValue whose .type is correct, but whose inner .value is not an instance of Opaque
        val = CtyValue(vtype=capsule_type, value=OtherOpaque())
        
        with pytest.raises(CtyValidationError, match="Value is not an instance of Opaque"):
            capsule_type.validate(val)

    def test_value_comparison_on_unsupported_type(self) -> None:
        """Covers the TypeError raised when comparing unorderable CtyValues."""
        val1 = CtyCapsule("T", Opaque).validate(Opaque())
        val2 = CtyCapsule("T", Opaque).validate(Opaque())

        with pytest.raises(TypeError, match=r"Value of type CtyCapsule\([^)]+\) is not comparable"):
            _ = val1 < val2
        with pytest.raises(TypeError, match=r"Value of type CtyCapsule\([^)]+\) is not comparable"):
            _ = val1 <= val2
        with pytest.raises(TypeError, match=r"Value of type CtyCapsule\([^)]+\) is not comparable"):
            _ = val1 > val2
        with pytest.raises(TypeError, match=r"Value of type CtyCapsule\([^)]+\) is not comparable"):
            _ = val1 >= val2
