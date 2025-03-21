
# pyvider-cty/tests/path/test_cty_refinement.py


from decimal import Decimal

from pyvider.cty.values.refinement import (
    ValueRefinement, NotNullRefinement, StringPrefixRefinement,
    NumberRangeRefinement, ValueRefinementBuilder
)
from pyvider.cty import CtyString
from pyvider.cty import CtyValue

class TestRefinement:
    def test_not_null_refinement(self):
        """Test NotNullRefinement creation."""
        refinement = NotNullRefinement()
        assert isinstance(refinement, ValueRefinement)
    
    def test_string_prefix_refinement(self):
        """Test StringPrefixRefinement creation and properties."""
        prefix = "test_"
        refinement = StringPrefixRefinement(prefix=prefix)
        
        assert isinstance(refinement, ValueRefinement)
        assert refinement.prefix == prefix
    
    def test_number_range_refinement(self):
        """Test NumberRangeRefinement creation and properties."""
        min_val = Decimal("0")
        max_val = Decimal("100")
        
        refinement = NumberRangeRefinement(
            min_value=min_val,
            max_value=max_val,
            min_inclusive=True,
            max_inclusive=False
        )
        
        assert isinstance(refinement, ValueRefinement)
        assert refinement.min_value == min_val
        assert refinement.max_value == max_val
        assert refinement.min_inclusive is True
        assert refinement.max_inclusive is False
    
    def test_refinement_builder(self):
        """Test ValueRefinementBuilder initialization."""
        value = CtyValue(type_=CtyString(), value="test")
        builder = ValueRefinementBuilder(value)
        
        assert builder._value == value
        assert len(builder._refinements) == 0
    
    def test_not_null_builder(self):
        """Test adding NotNullRefinement through builder."""
        value = CtyValue(type_=CtyString(), value="test")
        builder = ValueRefinementBuilder(value)
        
        # Add not_null refinement
        result = builder.not_null()
        
        # Verify builder was returned (for chaining)
        assert result is builder
        
        # Verify refinement was added
        assert len(builder._refinements) == 1
        assert isinstance(builder._refinements[0], NotNullRefinement)
    
    # Add more tests for other refinements and new_value method