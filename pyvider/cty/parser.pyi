from .exceptions import CtyValidationError as CtyValidationError
from .types import CtyBool as CtyBool, CtyDynamic as CtyDynamic, CtyList as CtyList, CtyMap as CtyMap, CtyNumber as CtyNumber, CtyObject as CtyObject, CtySet as CtySet, CtyString as CtyString, CtyTuple as CtyTuple, CtyType as CtyType
from typing import Any

def parse_tf_type_to_ctytype(tf_type: Any) -> CtyType[Any]: ...
parse_type_string_to_ctytype = parse_tf_type_to_ctytype
