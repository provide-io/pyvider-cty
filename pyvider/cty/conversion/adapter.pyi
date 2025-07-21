from pyvider.cty.types import CtyDynamic as CtyDynamic, CtyList as CtyList, CtyMap as CtyMap, CtyObject as CtyObject, CtySet as CtySet, CtyTuple as CtyTuple
from pyvider.cty.values import CtyValue as CtyValue
from typing import Any

def cty_to_native(value: Any) -> Any: ...
