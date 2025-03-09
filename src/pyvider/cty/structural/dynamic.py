
from pyvider.exceptions import ValidationError
from pyvider.cty.base import TFType

class TFDynamic(TFType):
    """
    TFDynamic represents a dynamic Terraform type that can accept any value.
    This type acts as a catch-all during schema validation, allowing flexibility 
    for attributes whose structure or type cannot be determined at schema definition time.
    """

    def validate(self, value: object) -> None:
        """
        Validation for TFDynamic is a no-op since it accepts any value.

        Args:
            value (object): Any value to validate.

        Raises:
            ValidationError: If the value is explicitly set to an unsupported form.
        """
        if isinstance(value, (dict, list, int, float, bool, str, type(None))):
            return  # All standard types are acceptable

        raise ValidationError("Unsupported value for TFDynamic. Acceptable types are primitive types, dict, list, or None.")

    def equal(self, other: TFType) -> bool:
        """
        TFDynamic instances are considered equal to any other instance of TFDynamic.

        Args:
            other (TFType): Another TFType instance.

        Returns:
            bool: True if the types are compatible, otherwise False.
        """
        return isinstance(other, TFDynamic)

    def usable_as(self, other: TFType) -> bool:
        """
        TFDynamic can be used interchangeably with any other TFDynamic.

        Args:
            other (TFType): Target TFType to compare against.

        Returns:
            bool: True if usable as the target type.
        """
        return isinstance(other, TFDynamic)

    def __str__(self) -> str:
        return "TFDynamic"

    def __repr__(self) -> str:
        return "TFDynamic()"

# Factory function for schema definition

def tfdynamic(**kwargs) -> 'AttributeValue':
    """
    Factory method for creating a TFDynamic attribute in schema definitions.

    Returns:
        AttributeValue: An attribute containing TFDynamic as its type.
    """
    from pyvider.schema.attributes import AttributeMetadata, AttributeValue
    meta = AttributeMetadata(**kwargs)
    return AttributeValue(ctype=TFDynamic(), metadata=meta)
