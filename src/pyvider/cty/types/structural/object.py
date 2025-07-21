from typing import Any, ClassVar

from attrs import define, field

from pyvider.cty.exceptions import (
    CtyAttributeValidationError,
    CtyTypeMismatchError,
    CtyValidationError,
    InvalidTypeError,
)
from pyvider.cty.path import CtyPath, GetAttrStep
from pyvider.cty.types.base import CtyType
from pyvider.cty.values import CtyValue


def _attrs_to_dict_safe(inst: Any) -> dict[str, Any]:
    res = {}
    for a in getattr(type(inst), "__attrs_attrs__", []):
        res[a.name] = getattr(inst, a.name)
    return res


@define(frozen=True, slots=True)
class CtyObject(CtyType[dict[str, object]]):
    ctype: ClassVar[str] = "object"
    attribute_types: dict[str, "CtyType[Any]"] = field(factory=dict)
    optional_attributes: frozenset[str] = field(
        factory=frozenset, converter=frozenset
    )

    def __attrs_post_init__(self) -> None:
        for name, attr_type in self.attribute_types.items():
            if not isinstance(attr_type, CtyType):
                raise InvalidTypeError(
                    f"Attribute '{name}' must be a CtyType, but got {type(attr_type).__name__}"
                )

    def __hash__(self) -> int:
        return hash(
            (
                self.ctype,
                frozenset(self.attribute_types.items()),
                self.optional_attributes,
            )
        )

    def validate(self, value: object) -> "CtyValue[dict[str, Any]]":  # noqa: C901
        if value is None:
            return CtyValue.null(self)
        from pyvider.cty.types.structural.dynamic import CtyDynamic

        unknown_optionals = self.optional_attributes - set(self.attribute_types.keys())
        if unknown_optionals:
            raise CtyAttributeValidationError(
                f"Unknown optional attributes: {', '.join(sorted(list(unknown_optionals)))}"
            )

        if isinstance(value, CtyValue):
            if value.is_unknown:
                return CtyValue.unknown(self)
            if value.is_null:
                return CtyValue.null(self)
            value = value.value

        if hasattr(type(value), "__attrs_attrs__"):
            value = _attrs_to_dict_safe(value)
        if not isinstance(value, dict):
            raise CtyAttributeValidationError(
                f"Expected a dictionary for CtyObject, got {type(value).__name__}"
            )

        validated_attrs: dict[str, CtyValue[Any]] = {}
        all_expected_attrs = set(self.attribute_types.keys())
        unknown = set(value.keys()) - all_expected_attrs
        if unknown:
            raise CtyAttributeValidationError(
                f"Unknown attributes: {', '.join(sorted(list(unknown)))}"
            )

        for name, attr_type in self.attribute_types.items():
            path = CtyPath(steps=[GetAttrStep(name)])
            if name not in value:
                if name in self.optional_attributes:
                    validated_attrs[name] = CtyValue.null(attr_type)
                    continue
                raise CtyAttributeValidationError(
                    "Missing required attribute", value=None, path=path
                )

            raw_attr_value = value.get(name)
            try:
                existing_marks: frozenset[Any] = frozenset()
                if isinstance(raw_attr_value, CtyValue):
                    existing_marks = raw_attr_value.marks

                validated_attr = attr_type.validate(raw_attr_value)

                if existing_marks:
                    validated_attr = validated_attr.with_marks(existing_marks)  # type: ignore

            except CtyValidationError as e:
                new_path = CtyPath(
                    steps=[GetAttrStep(name)] + (e.path.steps if e.path else [])
                )
                raise CtyAttributeValidationError(
                    e.message, value=raw_attr_value, path=new_path, original_exception=e
                ) from e

            if (
                name not in self.optional_attributes
                and validated_attr.is_null
                and not isinstance(attr_type, CtyDynamic)
            ):
                raise CtyAttributeValidationError(
                    "Attribute cannot be null", value=None, path=path
                )

            validated_attrs[name] = validated_attr

        return CtyValue(vtype=self, value=validated_attrs)

    def get_attribute(self, obj_value: "CtyValue[Any]", name: str) -> "CtyValue[Any]":
        if not isinstance(obj_value, CtyValue):
            raise CtyTypeMismatchError("get_attribute requires a CtyValue object")
        if not self.has_attribute(name):
            raise CtyAttributeValidationError(
                f"Object has no attribute '{name}'", path=CtyPath.get_attr(name)
            )
        if obj_value.is_unknown:
            return CtyValue.unknown(self.attribute_types[name])
        if obj_value.is_null:
            return CtyValue.null(self.attribute_types[name])
        if isinstance(obj_value.value, dict):
            return obj_value.value.get(name, CtyValue.null(self.attribute_types[name]))  # type: ignore
        raise CtyTypeMismatchError("CtyObject value is not a dict")

    def has_attribute(self, name: str) -> bool:
        return name in self.attribute_types

    def equal(self, other: CtyType[Any]) -> bool:
        if not isinstance(other, CtyObject):
            return False
        if self.optional_attributes != other.optional_attributes:
            return False
        if self.attribute_types.keys() != other.attribute_types.keys():
            return False
        for key in self.attribute_types:
            if not self.attribute_types[key].equal(other.attribute_types[key]):
                return False
        return True

    def usable_as(self, other: CtyType[Any]) -> bool:
        from pyvider.cty.types.structural import CtyDynamic

        if isinstance(other, CtyDynamic):
            return True
        if not isinstance(other, CtyObject):
            return False
        other_attrs = set(other.attribute_types.keys())
        self_attrs = set(self.attribute_types.keys())
        if not other_attrs.issubset(self_attrs):
            return False
        self_required = self_attrs - self.optional_attributes
        other_required = other_attrs - other.optional_attributes
        if not other_required.issubset(self_required):
            return False
        return all(
            self.attribute_types[name].usable_as(other_type)
            for name, other_type in other.attribute_types.items()
        )

    def _to_wire_json(self) -> Any:
        attrs_json = {
            name: attr_type._to_wire_json()
            for name, attr_type in self.attribute_types.items()
        }
        return [self.ctype, attrs_json]

    def is_primitive_type(self) -> bool:
        return False
