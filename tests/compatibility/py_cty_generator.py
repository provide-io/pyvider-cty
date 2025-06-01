#!/usr/bin/env python3

import json
import os
import sys
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple, Union, cast
import yaml # Added import
import pathlib # Added import

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
    # Ensure this import path is correct based on your project structure for CtyValue
    from pyvider.cty.values.base import CtyValue as ConcreteCtyValue # Assuming CtyValue from base is needed for to_json_comparable_dict
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

# --- Type Parsing Helper ---
def parse_type_definition(type_str: str) -> CtyType:
    logger.debug(f"{elp(domTypeSystem, actConvert, statStart)} Parsing type definition string: '{type_str}'")
    if type_str == "string":
        logger.debug(f"{elp(domTypeSystem, actConvert, statOK)} Parsed to CtyString")
        return CtyString()
    elif type_str == "number":
        logger.debug(f"{elp(domTypeSystem, actConvert, statOK)} Parsed to CtyNumber")
        return CtyNumber()
    elif type_str == "bool":
        logger.debug(f"{elp(domTypeSystem, actConvert, statOK)} Parsed to CtyBool")
        return CtyBool()
    elif type_str.startswith("list(") and type_str.endswith(")"):
        inner_type_str = type_str[len("list("):-1]
        inner_type = parse_type_definition(inner_type_str) # Recursive call
        logger.debug(f"{elp(domTypeSystem, actConvert, statOK)} Parsed to CtyList with element type {inner_type.__class__.__name__}")
        return CtyList(element_type=inner_type)
    # Add more types as needed (map, object, etc.) for future expansion
    else:
        err_msg = f"Unsupported type definition string: {type_str}"
        logger.error(f"{elp(domTypeSystem, actConvert, statError)} {err_msg}")
        raise ValueError(err_msg)

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

    logger.info(f"{elp(domTooling, actInfo, statStart)} Starting pyvider-cty generator script for compatibility tests")

    test_cases_dir = pathlib.Path("tests/compatibility/testcases")
    output_base_dir = pathlib.Path("tests/compatibility/output")

    if not test_cases_dir.is_dir():
        logger.critical(f"{elp(domError, actInfo, statError)} Test cases directory not found: {test_cases_dir}")
        sys.exit(1)

    for yaml_file in test_cases_dir.glob("*.yaml"):
        logger.info(f"{elp(domTooling, actInfo, statStart)} Processing test case: {yaml_file.name}")
        try:
            with open(yaml_file, 'r') as f:
                test_case_data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            logger.error(f"{elp(domError, actRead, statError)} Error loading YAML from {yaml_file.name}: {e}")
            continue # Skip to next file
        except IOError as e:
            logger.error(f"{elp(domError, actRead, statError)} Error reading file {yaml_file.name}: {e}")
            continue


        test_case_name = test_case_data.get("name", yaml_file.stem)
        type_definition_str = test_case_data.get("type_definition")
        raw_input_data = test_case_data.get("raw_input")

        if not type_definition_str:
            logger.error(f"{elp(domError, actInfo, statWarn)} Missing 'type_definition' in {yaml_file.name}")
            continue

        try:
            cty_type = parse_type_definition(type_definition_str)
            logger.info(f"{elp(domTypeSystem, actConvert, statOK)} Parsed type for {test_case_name}: {cty_type.__class__.__name__}")

            cty_value: ConcreteCtyValue
            if raw_input_data == "__unknown__":
                cty_value = ConcreteCtyValue.unknown(cty_type)
                logger.info(f"{elp(domValue, actDefine, statOK)} Created unknown value for {test_case_name}")
            elif raw_input_data is None: # Assuming primitives allow null by default
                cty_value = ConcreteCtyValue.null(cty_type)
                logger.info(f"{elp(domValue, actDefine, statOK)} Created null value for {test_case_name}")
            else:
                # Special handling for list validation: CtyList.validate expects a list of raw values
                if isinstance(cty_type, CtyList) and isinstance(raw_input_data, list):
                    # If elements are simple, pass them directly.
                    # If elements were complex (e.g., list of objects), they'd need pre-conversion
                    # or the validator needs to handle raw Python dicts for object elements.
                    # For POC, assume simple elements or elements CtyList validator can handle.
                    cty_value = cty_type.validate(raw_input_data)
                else:
                    cty_value = cty_type.validate(raw_input_data)
                logger.info(f"{elp(domValue, actValidate, statOK)} Validated raw input for {test_case_name}")

            # Prepare output directory
            case_output_dir = output_base_dir / test_case_name
            case_output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"{elp(domTooling, actWrite, statStart)} Ensured output directory exists: {case_output_dir}")

            # Generate py_value.json
            py_value_file = case_output_dir / "py_value.json"
            logger.info(f"{elp(domEncoding, actMarshal, statStart)} Generating py_value.json for {test_case_name}")
            try:
                # Ensure CtyValue has to_json_comparable_dict method
                value_dict = cty_value.to_json_comparable_dict()
                with open(py_value_file, 'w') as f:
                    json.dump(value_dict, f, indent=2)
                logger.info(f"{elp(domTooling, actWrite, statOK)} Successfully wrote {py_value_file}")
            except AttributeError as e:
                logger.error(f"{elp(domError, actMarshal, statError)} Error: 'to_json_comparable_dict' method not found on CtyValue. {e}")
                # Potentially skip or handle error, for now, log and continue
            except Exception as e:
                logger.error(f"{elp(domError, actMarshal, statError)} Failed to generate py_value.json for {test_case_name}: {e}", exc_info=True)


            # Generate py_type.json
            py_type_file = case_output_dir / "py_type.json"
            logger.info(f"{elp(domTypeSystem, actConvert, statStart)} Generating py_type.json for {test_case_name}")
            try:
                type_description = describe_type(cty_type)
                with open(py_type_file, 'w') as f:
                    json.dump(type_description, f, indent=2)
                logger.info(f"{elp(domTooling, actWrite, statOK)} Successfully wrote {py_type_file}")
            except Exception as e:
                logger.error(f"{elp(domError, actMarshal, statError)} Failed to generate py_type.json for {test_case_name}: {e}", exc_info=True)

        except ValueError as e: # Catch errors from parse_type_definition or CtyValue creation/validation
            logger.error(f"{elp(domError, actDefine, statError)} Value error processing {yaml_file.name}: {e}")
        except CtyValidationError as e:
            logger.error(f"{elp(domError, actValidate, statError)} Validation error for {test_case_name}: {e}")
        except Exception as e: # Catch-all for other unexpected errors during processing of a single file
            logger.error(f"{elp(domError, actInfo, statError)} Unexpected error processing {yaml_file.name}: {e}", exc_info=True)

    logger.info(f"\n{elp(domTooling, actInfo, statOK)} Finished processing all test cases.")

if __name__ == "__main__":
    main()
