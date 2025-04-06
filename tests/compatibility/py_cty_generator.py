#!/usr/bin/env python3

import json
import os
import sys
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple, Union, cast

# Assume pyvider.cty is importable and provides its own logger instance
try:
    from pyvider.telemetry import logger # Import the library's logger
    from pyvider.cty import (
        CtyValue, CtyType,
        CtyString, CtyNumber, CtyBool,
        CtyList, CtyMap, CtySet,
        CtyObject, CtyTuple, CtyDynamic,
    )
    from pyvider.cty.exceptions import CtyValidationError, CtyAttributeValidationError
except ImportError as e:
    print(f"ERROR: Could not import pyvider.cty or its logger. Make sure it's installed and accessible: {e}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"ERROR: An unexpected error occurred during import: {e}", file=sys.stderr)
    sys.exit(1)


# --- Emoji Definitions ---
# Define Emoji Mappings for pyvider.cty context
domTypeSystem = "🏗️ " # TypeSystem (Defining/Handling Cty Types)
domValue      = "🧱" # Value (Creating/Manipulating Cty Values)
domValidation = "🛡️" # Validation (Running validation logic)
domPath       = "🗺️" # Path (Path creation/navigation)
domEncoding   = "📦" # Encoding (Serialization/Deserialization)
domTooling    = "⚙️ " # Tooling (Script logic, file I/O, helpers)
domError      = "❗" # Error/Exception

actDefine   = "🔧" # Define/Create (Types, Values)
actValidate = "🔍" # Validate/Check (Values against Types)
actConvert  = "🔄" # Convert/Coerce (Go -> Cty, Type -> Description)
actAccess   = "🔩" # Access/Get (Attributes, Elements)
actNavigate = "➡️" # Navigate (Applying path steps)
actMarshal  = "✏️ " # Serialize/Marshal (Value -> JSON)
actWrite    = "📄" # Write/Output (File operations)
actInfo     = "ℹ️ " # Info/Log Step

statOK    = "✅" # Success / OK
statError = "❌" # Error / Fail (Problem occurred)
statWarn  = "⚠️" # Warning / Caveat
statStart = "⏳" # Pending / In Progress
statEmpty = "⭕" # Empty / Null / None

# --- Emoji Helper ---
# [e]moji [l]ogging [p]refix
def elp(domain: str, action: str, status: str) -> str:
    """Generates the 3-emoji prefix string."""
    return f"{domain}{action}{status}"

# --- Emoji Matrix Function ---
def print_emoji_matrix():
    # (Implementation remains the same as previous version)
    print("\n--- CTY Tool Emoji Matrix ---")
    print(" Structure: [Domain][Action][Status]")
    print("\n Domains (Component):")
    print(f"  {domTypeSystem} : TypeSystem (Types)")
    print(f"  {domValue} : Value (Values)")
    print(f"  {domValidation} : Validation")
    print(f"  {domPath} : Path")
    print(f"  {domEncoding} : Encoding")
    print(f"  {domTooling} : Tooling (Helpers, I/O)")
    print(f"  {domError} : Error/Exception")
    print("\n Actions (Operation):")
    print(f"  {actDefine} : Define/Create")
    print(f"  {actValidate} : Validate/Check")
    print(f"  {actConvert} : Convert/Coerce")
    print(f"  {actAccess} : Access/Get")
    print(f"  {actNavigate} : Navigate")
    print(f"  {actMarshal} : Serialize/Marshal")
    print(f"  {actWrite} : Write/Output")
    print(f"  {actInfo} : Info/Log Step")
    print("\n Status (Outcome):")
    print(f"  {statOK} : Success/OK")
    print(f"  {statError} : Error/Fail")
    print(f"  {statWarn} : Warning/Caveat")
    print(f"  {statStart} : Pending/Start")
    print(f"  {statEmpty} : Empty/Null/None")
    print("-----------------------------")

# --- Cty Value Creation Helper Functions ---

def python_to_cty_value(v: Any) -> CtyValue:
    """Converts basic Python types to *concrete* CtyValue instances."""
    pfx_start = elp(domValue, actConvert, statStart)
    logger.debug(f"{pfx_start} Converting Python value of type {type(v).__name__} to CtyValue")

    try:
        match v:
            case str():
                pfx = elp(domValue, actConvert, statOK)
                logger.debug(f"{pfx} Converted Python string")
                return CtyValue.string(v)
            case bool():
                pfx = elp(domValue, actConvert, statOK)
                logger.debug(f"{pfx} Converted Python bool")
                return CtyValue.bool(v)
            case int() | float():
                pfx = elp(domValue, actConvert, statOK)
                logger.debug(f"{pfx} Converted Python {type(v).__name__} to CtyNumber")
                return CtyValue.number(Decimal(str(v))) # Use Decimal
            case Decimal():
                pfx = elp(domValue, actConvert, statOK)
                logger.debug(f"{pfx} Converted Python Decimal to CtyNumber")
                return CtyValue.number(v)
            case dict():
                logger.debug(f"{pfx_start} Handling nested dict -> map_to_cty_object")
                return map_to_cty_object(v)
            case list() | tuple():
                logger.debug(f"{pfx_start} Handling nested list/tuple -> sequence_to_cty_list")
                return sequence_to_cty_list(v)
            case None:
                err_msg = "Cannot convert bare Python None to CtyValue without target type"
                pfx = elp(domValue, actConvert, statError)
                logger.error(f"{pfx} {err_msg}")
                raise ValueError(err_msg)
            case _:
                err_msg = f"Unhandled Python type in python_to_cty_value: {type(v).__name__}"
                pfx = elp(domValue, actConvert, statError)
                logger.error(f"{pfx} {err_msg}")
                raise TypeError(err_msg)
    except Exception as e:
        # Catch potential errors from CtyValue factories or Decimal conversion
        pfx = elp(domError, actConvert, statError)
        logger.error(f"{pfx} Error during Python to CtyValue conversion: {e}", exc_info=True)
        # Re-raise as ValueError or TypeError as appropriate
        if isinstance(e, (ValueError, TypeError)):
            raise
        else:
            raise ValueError(f"Failed conversion for {v}: {e}") from e


def map_to_cty_object(data: Dict[str, Any]) -> CtyValue:
    """Converts a Python dict to a CtyObject value."""
    pfx_start = elp(domValue, actConvert, statStart)
    logger.debug(f"{pfx_start} Converting dict with {len(data)} keys to CtyObject value")
    attrs: Dict[str, CtyValue] = {}
    attr_types: Dict[str, CtyType] = {}
    for k, v in data.items():
        if v is None:
            pfx = elp(domValue, actConvert, statWarn)
            logger.debug(f"{pfx} Skipping None value for key '{k}' in map_to_cty_object")
            continue
        try:
            val = python_to_cty_value(v)
            attrs[k] = val
            attr_types[k] = val.type
            pfx = elp(domValue, actConvert, statOK)
            logger.debug(f"{pfx}   Converted key '{k}' to type {val.type.__class__.__name__}")
        except (ValueError, TypeError) as e:
            pfx = elp(domError, actConvert, statError)
            logger.error(f"{pfx} Failed converting nested key '{k}': {e}")
            raise ValueError(f"Error converting nested key '{k}': {e}") from e

    obj_type = CtyObject(attribute_types=attr_types)
    logger.debug(f"{elp(domValue, actConvert, statOK)} Successfully created attribute map for CtyObject value")
    try:
        # Need to pass raw values back for validation by CtyObject
        # This assumes CtyValue has a .value property
        raw_attrs = {}
        for k, v_cty in attrs.items():
            try:
                 # Handle case where value might be None internally if created via CtyValue.null
                 raw_attrs[k] = v_cty.value if not v_cty.is_null else None
            except ValueError as e: # Catch error if trying to access .value of an unknown CtyValue
                 pfx = elp(domError, actAccess, statError)
                 logger.error(f"{pfx} Cannot get raw value for key '{k}' (possibly unknown?): {e}")
                 # How to handle unknown? Maybe pass the CtyValue itself if validator accepts it?
                 # For now, let's raise to indicate the issue clearly.
                 raise ValueError(f"Cannot get raw value for key '{k}' needed for object creation: {e}") from e

        # Assuming CtyValue.object exists and takes types dict + raw values dict
        return CtyValue.object(attr_types, raw_attrs)
    except CtyValidationError as e:
         pfx = elp(domError, actValidate, statError)
         logger.error(f"{pfx} Final object validation failed: {e}", exc_info=True)
         raise
    except AttributeError:
         # Fallback if CtyValue.object factory doesn't exist
         pfx = elp(domError, actValidate, statWarn)
         logger.warning(f"{pfx} CtyValue.object factory not found, attempting direct validation.", exc_info=True)
         return obj_type.validate(raw_attrs)


def sequence_to_cty_list(data: Union[List[Any], Tuple[Any, ...]]) -> CtyValue:
    """Converts a Python list or tuple to a CtyList value. Errors if types are inconsistent."""
    pfx_start = elp(domValue, actConvert, statStart)
    logger.debug(f"{pfx_start} Converting sequence with {len(data)} elements to CtyList value")
    if not data:
        pfx = elp(domValue, actConvert, statEmpty)
        logger.debug(f"{pfx} Sequence is empty, creating empty CtyList(CtyDynamic)")
        return CtyValue.list(CtyDynamic(), []) # Use factory method

    vals: List[CtyValue] = []
    first_type: Optional[CtyType] = None
    for i, v in enumerate(data):
        if v is None:
            err_msg = f"Bare None value encountered at index {i} in sequence; CtyList requires typed nulls."
            pfx = elp(domError, actConvert, statError)
            logger.error(f"{pfx} {err_msg}")
            raise ValueError(err_msg)
        try:
            val = python_to_cty_value(v)
            vals.append(val)
            if i == 0:
                first_type = val.type
                pfx = elp(domValue, actInfo, statOK)
                logger.debug(f"{pfx}   Inferred list element type from first element: {first_type.__class__.__name__}")
            else:
                if not first_type or not val.type.equal(first_type):
                    err_msg = f"Inconsistent types in sequence: expected {first_type.__class__.__name__ if first_type else 'N/A'}, got {val.type.__class__.__name__} at index {i}. Cannot create concrete CtyList."
                    pfx = elp(domError, actConvert, statError)
                    logger.error(f"{pfx} {err_msg}")
                    raise TypeError(err_msg) # Raise TypeError for inconsistent list elements
            pfx = elp(domValue, actConvert, statOK)
            logger.debug(f"{pfx}   Converted sequence element {i} to type {val.type.__class__.__name__}")
        except (ValueError, TypeError) as e:
            pfx = elp(domError, actConvert, statError)
            logger.error(f"{pfx} Failed converting sequence element {i}: {e}")
            raise ValueError(f"Error converting sequence element {i}: {e}") from e

    if not first_type: # Should not happen if data is not empty
         first_type = CtyDynamic() # Fallback just in case
    pfx = elp(domValue, actConvert, statOK)
    logger.debug(f"{pfx} Creating CtyList with consistent element type: {first_type.__class__.__name__}")
    # Use the factory method, passing raw values extracted from CtyValues created above
    raw_list_values = [v.value for v in vals]
    return CtyValue.list(first_type, raw_list_values)

# --- Type Description Helper ---
def describe_type(ty: CtyType) -> Any:
    """Helper function to describe a cty.Type recursively as a dict for JSON."""
    pfx = elp(domTypeSystem, actConvert, statStart)
    logger.debug(f"{pfx} Describing type: {ty.__class__.__name__}")
    result: Dict[str, Any] = {}

    try:
        if isinstance(ty, (CtyString, CtyNumber, CtyBool)):
            result["type"] = ty.__class__.__name__[3:].lower()
        elif isinstance(ty, CtyList):
            result["type"] = "list"
            result["elementType"] = describe_type(ty.element_type)
        elif isinstance(ty, CtySet):
            result["type"] = "set"
            result["elementType"] = describe_type(ty.element_type)
        elif isinstance(ty, CtyMap):
            result["type"] = "map"
            result["elementType"] = describe_type(ty.value_type) # Map value type
        elif isinstance(ty, CtyObject):
            result["type"] = "object"
            result["attributes"] = {name: describe_type(attr_ty) for name, attr_ty in ty.attribute_types.items()}
        elif isinstance(ty, CtyTuple):
            result["type"] = "tuple"
            result["elements"] = [describe_type(el_ty) for el_ty in ty.element_types]
        elif isinstance(ty, CtyDynamic):
            result["type"] = "dynamic"
        else:
            pfx_warn = elp(domTypeSystem, actConvert, statWarn)
            logger.warning(f"{pfx_warn} Unknown type encountered during description: {type(ty).__name__}")
            result["type"] = "unknown"
            result["details"] = str(ty)
    except Exception as e:
         pfx_err = elp(domError, actConvert, statError)
         logger.error(f"{pfx_err} Error describing type {type(ty).__name__}: {e}", exc_info=True)
         result["type"] = "error"
         result["details"] = str(e)

    pfx_ok = elp(domTypeSystem, actConvert, statOK)
    logger.debug(f"{pfx_ok} Finished describing type: {ty.__class__.__name__}")
    return result

# --- Main Script Logic ---
def main():
    if os.getenv("CTY_SHOW_EMOJI_MATRIX") == "true":
        print_emoji_matrix()

    logger.info(f"{elp(domTooling, actInfo, statStart)} Starting pyvider-cty generator script")

    # --- Define Basic Types ---
    logger.info(f"{elp(domTypeSystem, actDefine, statStart)} Defining basic cty types")
    string_type = CtyString()
    number_type = CtyNumber()
    bool_type = CtyBool()
    dynamic_type = CtyDynamic()
    logger.info(f"{elp(domTypeSystem, actDefine, statOK)} Basic types defined")

    # --- Define Complex Types ---
    logger.info(f"{elp(domTypeSystem, actDefine, statStart)} Defining complex cty types (network, disk, coordinate)")
    try:
        network_object_type = CtyObject(attribute_types={
            "subnet":            string_type,
            "vpc_id":            string_type,
            "security_groups":   CtyList(element_type=string_type),
            "private_endpoints": CtySet(element_type=string_type),
        })
        disk_object_type = CtyObject(
            attribute_types={
                "size_gb": number_type,
                "type":    string_type,
                "iops":    number_type,
            },
            optional_attributes=frozenset(["iops"]) # Mark iops as optional
        )
        coordinate_tuple_type = CtyTuple(element_types=(
            number_type, number_type, number_type,
        ))
        logger.info(f"{elp(domTypeSystem, actDefine, statOK)} Defined network, disk, coordinate object/tuple types")

        logger.info(f"{elp(domTypeSystem, actDefine, statStart)} Defining main server object type")

        server_object_type = CtyObject(
            attribute_types={
                "name":          string_type,
                "instance_type": string_type,
                "active":        bool_type,
                "cpu_cores":     number_type,
                "ram_gb":        number_type,
                "network":       network_object_type,
                "disks":         CtyList(element_type=disk_object_type),
                "tags":          CtyMap(key_type=string_type, value_type=string_type),
                "metadata":      CtyMap(key_type=string_type, value_type=dynamic_type),
                "location":      coordinate_tuple_type,
                "extra_config":  dynamic_type,
                "backup_policy": string_type,
                "region":        string_type,
            },
            optional_attributes=frozenset(["backup_policy", "tags", "metadata", "region"]) # Also add tags/metadata if they can be absent
        )
    except Exception as e:
        logger.critical(f"{elp(domError, actDefine, statError)} Failed to define Cty types: {e}", exc_info=True)
        sys.exit(1)

    # --- Define Raw Python Structure for Comparison ---
    logger.info(f"{elp(domTooling, actDefine, statStart)} Defining raw Python structure (dict)")
    # (Raw structure definition remains the same)
    raw_network = {
        "subnet": "subnet-abcdef01234567890", "vpc_id": "vpc-0123456789abcdef0",
        "security_groups": ["sg-web", "sg-internal"], "private_endpoints": [],
    }
    raw_disk1 = {"size_gb": 100, "type": "gp3", "iops": 3000}
    raw_disk2 = {"size_gb": 500, "type": "io2", "iops": None}
    raw_disks = [raw_disk1, raw_disk2]
    raw_tags = {"Environment": "production", "Project": "WebApp", "Owner": "PlatformTeam"}
    raw_metadata = {
        "created_by": "automation", "last_check_ok": True, "check_interval": 300,
        "nested_data": {"key": "value"},
    }
    raw_location = [45.5231, -122.6765, 15.0]
    raw_server = {
        "name": "web-server-01", "instance_type": "t3.xlarge", "active": True,
        "cpu_cores": 4, "ram_gb": 16.0, "network": raw_network, "disks": raw_disks,
        "tags": raw_tags, "metadata": raw_metadata, "location": raw_location,
        "extra_config": "some arbitrary config string",
        "backup_policy": None, "region": "__cty_unknown__",
    }
    raw_top_level = {
        "main_server": raw_server, "backup_server": None, "future_server": "__cty_unknown_object__",
    }
    logger.info(f"{elp(domTooling, actDefine, statOK)} Defined raw Python structure")

    # --- Create cty Values (Simplified Top Level) ---
    logger.info(f"{elp(domValue, actDefine, statStart)} Attempting to create top-level CtyMap value (simplified)")
    try:
        # Create the main server object first using validation (which uses helpers internally)
        # This assumes CtyObject.validate exists and works
        server_object_val = server_object_type.validate(raw_server)
        logger.info(f"{elp(domValue, actValidate, statOK)} Validated main_server data against server_object_type")

        # Assemble simplified top-level map value
        top_level_map_type = CtyMap(key_type=string_type, value_type=server_object_type)
        # Use validate to create the map value containing only the valid server object
        top_level_value = top_level_map_type.validate({
            "main_server": raw_server, # Pass raw dict again for validation by CtyMap
        })
        # Or potentially using the already validated object if CtyMap validation accepts CtyValue:
        # top_level_value = top_level_map_type.validate({
        #      "main_server": server_object_val,
        # })

        logger.info(f"{elp(domValue, actDefine, statOK)} Assembled top-level CtyMap value")
        logger.debug(f"{elp(domTooling, actInfo, statOK)} Top Level Value repr: {top_level_value!r}")


    except (AttributeError, CtyValidationError, TypeError, ValueError) as e:
         logger.critical(f"{elp(domError, actDefine, statError)} Failed to create/validate CtyValue structure: {e}", exc_info=True)
         sys.exit(1)
    except Exception as e: # Catch any other unexpected errors
        logger.critical(f"{elp(domError, actDefine, statError)} Unexpected error during CtyValue creation: {e}", exc_info=True)
        sys.exit(1)


    # --- Generate Output Files ---
    logger.info(f"{elp(domTooling, actInfo, statStart)} Generating output files...")

    # 1. Raw Python Structure JSON
    raw_file_name = "pyvider-cty-raw-structure.json"
    logger.info(f"{elp(domTooling, actMarshal, statStart)} Marshaling raw Python structure to JSON")
    try:
        with open(raw_file_name, 'w') as f:
            json.dump(raw_top_level, f, indent=2, default=str) # default=str handles Decimal etc.
        logger.info(f"{elp(domTooling, actWrite, statOK)} Successfully wrote raw structure to {raw_file_name}")
    except IOError as e:
        logger.error(f"{elp(domError, actWrite, statError)} Failed to write raw structure JSON to file '{raw_file_name}': {e}")
    except TypeError as e:
        logger.error(f"{elp(domError, actMarshal, statError)} Failed to marshal raw structure to JSON: {e}")

    # 2. Type Structure JSON
    type_file_name = "pyvider-cty-type-structure.json"
    logger.info(f"{elp(domTypeSystem, actConvert, statStart)} Describing top-level cty.Type structure")
    try:
        type_description = describe_type(top_level_map_type) # Use the defined map type
        logger.info(f"{elp(domTypeSystem, actMarshal, statStart)} Marshaling type structure to JSON")
        with open(type_file_name, 'w') as f:
            json.dump(type_description, f, indent=2, default=str)
        logger.info(f"{elp(domTooling, actWrite, statOK)} Successfully wrote type structure to {type_file_name}")
    except IOError as e:
        logger.error(f"{elp(domError, actWrite, statError)} Failed to write type structure JSON to file '{type_file_name}': {e}")
    except Exception as e:
         logger.error(f"{elp(domError, actMarshal, statError)} Failed to describe or marshal type structure: {e}", exc_info=True)

    # 3. Serialized CtyValue JSON - REMOVED
    logger.info(f"{elp(domTooling, actInfo, statOK)} Skipping generation of serialized cty value JSON file as requested.")

    print(f"\n{elp(domTooling, actInfo, statOK)} Successfully generated raw structure and type structure JSON files.")

if __name__ == "__main__":
    main()
