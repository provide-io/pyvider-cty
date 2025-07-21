from .conversion import encode_cty_type_to_wire_json as encode_cty_type_to_wire_json
from .exceptions import DeserializationError as DeserializationError
from .types import CtyDynamic as CtyDynamic, CtyList as CtyList, CtyMap as CtyMap, CtyObject as CtyObject, CtySet as CtySet, CtyTuple as CtyTuple, CtyType as CtyType
from .values import CtyValue as CtyValue
from .values.markers import RefinedUnknownValue as RefinedUnknownValue, UNREFINED_UNKNOWN as UNREFINED_UNKNOWN, UnknownValue as UnknownValue
from typing import Any

def cty_to_msgpack(value: CtyValue[Any], schema: CtyType[Any]) -> bytes: ...
def cty_from_msgpack(data: bytes, cty_type: CtyType[Any]) -> CtyValue[Any]: ...
