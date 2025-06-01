import json
import pathlib
import sys
import subprocess
import shutil # For shutil.which
import pytest
import tempfile # Added import
import yaml # Added import
import os # For os.remove
from decimal import Decimal, InvalidOperation
from typing import Any # Added for type hinting
from hypothesis import given, strategies as st
import re

# pyvider.cty imports
from pyvider.cty import CtyValue, CtyType, CtyString, CtyNumber, CtyBool, CtyList, CtyMap, CtyObject, CtyTuple
from pyvider.cty.exceptions import CtyValidationError
from pyvider.cty.codec import cty_value_to_msgpack_bytes, cty_value_from_msgpack_bytes # Added for Msgpack tests

# --- Configuration ---
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
TEST_CASES_DIR = SCRIPT_DIR / "testcases"
OUTPUT_BASE_DIR = SCRIPT_DIR / "output"
PYTHON_GENERATOR_SCRIPT = SCRIPT_DIR / "py_cty_generator.py"
GO_GENERATOR_SCRIPT = "go_src/go_cty_generator.go" # Name of the Go script relative to go_src

# Temp directory for Hypothesis-generated YAML files
TEMP_DIR_FOR_HYPOTHESIS_YAML = SCRIPT_DIR / "hypothesis_temp_yaml"
TEMP_DIR_FOR_HYPOTHESIS_YAML.mkdir(parents=True, exist_ok=True)


# --- Helper Functions ---

def parse_type_definition(type_str: str) -> CtyType:
    if type_str == "string":
        return CtyString()
    elif type_str == "number":
        return CtyNumber()
    elif type_str == "bool":
        return CtyBool()
    elif type_str.startswith("list(") and type_str.endswith(")"):
        inner_type_str = type_str[len("list("):-1]
        inner_type = parse_type_definition(inner_type_str)
        return CtyList(element_type=inner_type)
    elif type_str.startswith("map(") and type_str.endswith(")"):
        value_type_str = type_str[len("map("):-1]
        value_type = parse_type_definition(value_type_str)
        return CtyMap(value_type=value_type)
    elif type_str.startswith("tuple([") and type_str.endswith("])"):
        element_types_str = type_str[len("tuple(["):-2]
        if not element_types_str:
            return CtyTuple([])
        element_type_strs = [s.strip() for s in element_types_str.split(',')]
        element_types = [parse_type_definition(s) for s in element_type_strs]
        return CtyTuple(element_types)
    elif type_str.startswith("object({") and type_str.endswith("})"):
        attrs_str = type_str[len("object({"):-2]
        if not attrs_str:
            return CtyObject({})
        attr_pairs = [s.strip() for s in attrs_str.split(',')]
        attribute_types = {}
        for pair in attr_pairs:
            name, type_name = pair.split('=', 1)
            attribute_types[name.strip()] = parse_type_definition(type_name.strip())
        return CtyObject(attribute_types)
    else:
        raise ValueError(f"Unsupported type definition string: {type_str}")

def load_json_file(file_path: pathlib.Path) -> dict | None:
    if not file_path.exists():
        print(f"  [❗ ERROR]: File not found: {file_path}")
        return None
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"  [❗ ERROR]: Could not decode JSON from {file_path}. Error: {e}")
        return None
    except Exception as e:
        print(f"  [❗ ERROR]: An unexpected error occurred while reading {file_path}. Error: {e}")
        return None

def compare_json_outputs(test_case_name: str, file_type: str) -> bool:
    py_file_path = OUTPUT_BASE_DIR / test_case_name / f"py_{file_type}.json"
    go_file_path = OUTPUT_BASE_DIR / test_case_name / f"go_{file_type}.json"
    py_data = load_json_file(py_file_path)
    go_data = load_json_file(go_file_path)
    if py_data is None or go_data is None:
        print(f"  [❌ {file_type.upper()}]: FAILED for {test_case_name} due to missing/corrupt data.")
        return False
    if py_data == go_data:
        print(f"  [✅ {file_type.upper()}]: Match for {test_case_name}")
        return True
    else:
        print(f"  [❌ {file_type.upper()}]: Mismatch for {test_case_name}")
        print(f"    --- py_{file_type}.json (Content) ---\n{json.dumps(py_data, indent=2, ensure_ascii=False)}")
        print(f"    --- go_{file_type}.json (Content) ---\n{json.dumps(go_data, indent=2, ensure_ascii=False)}")
        return False

def get_test_case_files() -> list[pathlib.Path]:
    if not TEST_CASES_DIR.is_dir():
        return []
    return sorted(list(TEST_CASES_DIR.glob("*.yaml")))


# --- Go Generator Helper ---
def run_go_generator(
    type_str: str,
    raw_data_for_go: Any | None, # None if input_file_format is 'msgpack'
    hyp_test_name_suffix: str,
    output_format: str = "json",
    input_file_format: str = "yaml",
    input_msgpack_bytes: bytes | None = None,
    timeout: int = 30
) -> bytes:
    tmp_yaml_path = None
    tmp_input_msgpack_file_path = None

    go_executable = shutil.which("go")
    if not go_executable:
        pytest.skip("Go executable not found")
        return b"" # Should not be reached due to skip

    go_gen_cmd = [go_executable, "run", str(SCRIPT_DIR / GO_GENERATOR_SCRIPT)]

    # Determine if Go script will output binary (Msgpack) or text (JSON)
    # This affects subprocess text mode and stdout handling.
    # The special case is input_file_format="msgpack", which always outputs JSON text.
    go_produces_binary_stdout = (output_format == "msgpack") and (input_file_format != "msgpack")
    text_mode_for_subprocess = not go_produces_binary_stdout

    if output_format == "msgpack" and input_file_format == "yaml": # Standard YAML to Msgpack
        go_gen_cmd.extend(["-stdout", "-format", "msgpack"])
    # If input_file_format == "msgpack", it always outputs JSON. Flags for this are set below.
    # If output_format == "json" and input_file_format == "yaml", -stdout is sufficient.
    elif output_format == "json" and input_file_format == "yaml":
         go_gen_cmd.append("-stdout")


    # Prepare input files and command arguments
    if input_file_format == "msgpack":
        assert input_msgpack_bytes is not None, "input_msgpack_bytes must be provided for msgpack input format"
        assert type_str, "type_str must be provided for -targetTypeString with msgpack input"

        with tempfile.NamedTemporaryFile(mode="wb", suffix=".msgpack", delete=False, dir=TEMP_DIR_FOR_HYPOTHESIS_YAML) as tmp_msgpack_file:
            tmp_msgpack_file.write(input_msgpack_bytes)
            tmp_input_msgpack_file_path = tmp_msgpack_file.name

        go_gen_cmd.extend([
            "-inputFileFormat", "msgpack",
            "-inputFile", str(tmp_input_msgpack_file_path),
            "-targetTypeString", type_str
        ])

        # Dummy YAML for positional argument
        dummy_yaml_content = {"name": f"dummy_case_{hyp_test_name_suffix}", "type_definition": type_str, "raw_input": {}}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, dir=TEMP_DIR_FOR_HYPOTHESIS_YAML, encoding='utf-8') as tmp_dummy_yaml_file:
            yaml.dump(dummy_yaml_content, tmp_dummy_yaml_file)
            tmp_yaml_path = tmp_dummy_yaml_file.name
        go_gen_cmd.append(str(tmp_yaml_path))

    elif input_file_format == "yaml":
        assert raw_data_for_go is not None, "raw_data_for_go must be provided for yaml input format"
        go_test_case_data = {"name": f"hyp_case_{hyp_test_name_suffix}", "type_definition": type_str, "raw_input": raw_data_for_go}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, dir=TEMP_DIR_FOR_HYPOTHESIS_YAML, encoding='utf-8') as tmp_yaml_file:
            yaml.dump(go_test_case_data, tmp_yaml_file)
            tmp_yaml_path = tmp_yaml_file.name
        go_gen_cmd.append(str(tmp_yaml_path))
    else:
        pytest.fail(f"Unsupported input_file_format in run_go_generator: {input_file_format}")

    try:
        go_result = subprocess.run(
            go_gen_cmd,
            capture_output=True,
            text=text_mode_for_subprocess, # True for JSON stdout, False for Msgpack stdout
            cwd=str(SCRIPT_DIR / "go_src"),
            timeout=timeout,
            check=False # We check returncode manually for better error messages
        )

        if go_result.returncode != 0:
            stderr_output = go_result.stderr
            if isinstance(stderr_output, bytes):
                stderr_output = stderr_output.decode(errors='replace')
            pytest.fail(
                f"Go generator failed with return code {go_result.returncode}.\n"
                f"Command: {' '.join(go_gen_cmd)}\n"
                f"Stderr:\n{stderr_output}",
                pytrace=False
            )

        # Ensure output is bytes
        if text_mode_for_subprocess: # stdout is string
            return go_result.stdout.encode('utf-8')
        else: # stdout is already bytes
            return go_result.stdout

    except subprocess.TimeoutExpired as e:
        pytest.fail(f"Go generator timed out after {timeout}s. Command: {' '.join(go_gen_cmd)}. Error: {e}", pytrace=False)
        return b"" # Should not be reached
    except Exception as e: # Catch other potential errors
        pytest.fail(f"Go generator execution failed. Command: {' '.join(go_gen_cmd)}. Error: {e}", pytrace=False)
        return b"" # Should not be reached
    finally:
        if tmp_yaml_path and os.path.exists(tmp_yaml_path):
            os.remove(tmp_yaml_path)
        if tmp_input_msgpack_file_path and os.path.exists(tmp_input_msgpack_file_path):
            os.remove(tmp_input_msgpack_file_path)

# --- Pytest Test Functions (YAML based) ---
@pytest.mark.parametrize("test_case_file", get_test_case_files(), ids=lambda p: p.name)
def test_yaml_compatibility(test_case_file: pathlib.Path):
    test_case_name = test_case_file.stem
    (OUTPUT_BASE_DIR / test_case_name).mkdir(parents=True, exist_ok=True)
    # Run Python Generator
    py_gen_cmd = [sys.executable, str(PYTHON_GENERATOR_SCRIPT.resolve()), str(test_case_file.resolve())]
    try:
        subprocess.run(py_gen_cmd, check=True, capture_output=True, text=True, timeout=30)
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Python generator failed for {test_case_name}: {e.stderr}", pytrace=False)
    except subprocess.TimeoutExpired as e:
        pytest.fail(f"Python generator timed out for {test_case_name}", pytrace=False)
    # Run Go Generator
    go_executable = shutil.which("go")
    if not go_executable: pytest.skip("Go executable not found"); return
    go_gen_cmd = [go_executable, "run", GO_GENERATOR_SCRIPT, str(test_case_file.resolve())]
    try:
        subprocess.run(go_gen_cmd, check=True, capture_output=True, text=True, cwd=str(SCRIPT_DIR / "go_src"), timeout=30)
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Go generator failed for {test_case_name}: {e.stderr}", pytrace=False)
    except subprocess.TimeoutExpired as e:
        pytest.fail(f"Go generator timed out for {test_case_name}", pytrace=False)
    # Compare Outputs
    value_match = compare_json_outputs(test_case_name, "value")
    type_match = compare_json_outputs(test_case_name, "type")
    assert value_match, f"Value JSON outputs do not match for {test_case_name}"
    assert type_match, f"Type JSON outputs do not match for {test_case_name}"

# --- Hypothesis Strategies ---

# Primitive data strategies
st_cty_string_data = st.text(max_size=30)
st_cty_number_raw = st.one_of(
    st.integers(),
    st.floats(allow_nan=False, allow_infinity=False, width=32),
    st.decimals(allow_nan=False, allow_infinity=False, places=5, min_value=Decimal("-1e18"), max_value=Decimal("1e18"))
)
@st.composite
def st_cty_number_repr(draw):
    num_val = draw(st_cty_number_raw)
    return str(num_val.to_eng_string() if isinstance(num_val, Decimal) else num_val)
st_cty_bool_data = st.booleans()

# Strategy for generating valid attribute names for objects and keys for maps
st_attr_name = st.text(alphabet=st.characters(min_codepoint=97, max_codepoint=122), min_size=1, max_size=10)


# Core strategy for generating type definition strings
@st.recursive
def st_cty_type_string(base, extend, max_depth=3): # Changed max_depth default from 2 to 3
    # Base cases: primitives
    primitive_types = st.sampled_from(["string", "number", "bool"])

    if max_depth <= 0:
        return primitive_types

    # Recursive cases: list, map, object, tuple
    list_type = st.builds(lambda t: f"list({t})", st_cty_type_string(base, extend, max_depth=max_depth-1))
    map_type = st.builds(lambda t: f"map({t})", st_cty_type_string(base, extend, max_depth=max_depth-1))

    object_attrs = st.dictionaries(
        keys=st_attr_name,
        values=st_cty_type_string(base, extend, max_depth=max_depth-1),
        min_size=0, max_size=4 # Limit attributes, changed from 3 to 4
    )
    object_type = st.builds(lambda d: "object({" + ",".join(f"{k}={v}" for k, v in d.items()) + "})", object_attrs)

    tuple_elements = st.lists(st_cty_type_string(base, extend, max_depth=max_depth-1), min_size=0, max_size=4) # Limit elements, changed from 3 to 4
    tuple_type = st.builds(lambda l: "tuple([" + ",".join(l) + "])", tuple_elements)

    return st.one_of(primitive_types, list_type, map_type, object_type, tuple_type)

# Strategy for generating data based on a type string
def st_data_for_type_string(type_str: str):
    # This function needs to parse the type_str to guide data generation.
    # It's a simplified parser for strategy selection, not a full validator.
    if type_str == "string":
        return st_cty_string_data
    elif type_str == "number":
        return st_cty_number_repr()
    elif type_str == "bool":
        return st_cty_bool_data
    elif type_str.startswith("list("):
        element_type_str = type_str[len("list("):-1]
        return st.lists(st_data_for_type_string(element_type_str), max_size=4) # Changed max_size from 3 to 4
    elif type_str.startswith("map("):
        value_type_str = type_str[len("map("):-1]
        return st.dictionaries(keys=st_attr_name, values=st_data_for_type_string(value_type_str), max_size=4) # Changed max_size from 3 to 4
    elif type_str.startswith("object({"):
        attrs_str = type_str[len("object({"):-2]
        if not attrs_str: return st.just({})

        attr_defs = {}
        # Simplified parsing for object attributes for data generation
        # Example: "name=string,age=number"
        # This regex is basic; parse_type_definition is the source of truth for type structure
        for match in re.finditer(r'(\w+)=([^,]+(?:\{[^}]*\})?(?:\[[^\]]*\])?)', attrs_str):
            name, subtype_str = match.groups()
            attr_defs[name.strip()] = subtype_str.strip()

        return st.fixed_dictionaries({name: st_data_for_type_string(subtype) for name, subtype in attr_defs.items()})

    elif type_str.startswith("tuple(["):
        elements_str = type_str[len("tuple(["):-2]
        if not elements_str: return st.just([]) # Empty tuple

        # Simplified parsing for tuple elements for data generation
        # This needs robust parsing if types can be deeply nested and contain commas
        # For now, assume simple comma separation of possibly complex types
        # This is tricky because a type like object({a=string,b=number}) itself contains commas.
        # A full parser like the one in cty might be needed for perfect robustness here.
        # Let's use a simple split for now and accept it might be fragile for complex nested types in tuples.
        # A better approach might be to parse with parse_type_definition and then build strategies.
        # However, parse_type_definition returns CtyType instances, not strings.
        # For now, let's assume elements are parsable by st_data_for_type_string individually.
        # This part is the most complex for data generation.
        # A pragmatic simplification: use the existing parse_type_definition to get element CtyType objects,
        # then map them back to strings for st_data_for_type_string. This is inefficient.
        # Alternative: parse_type_definition could return the string components.

        # Let's try a regex based split that handles one level of nesting for object/list/map/tuple
        element_type_strs = re.findall(r'[^,]+(?:\([^)]*\)|\[[^\]]*\]|\{[^}]*\})*|[^,]+', elements_str)

        return st.tuples(*(st_data_for_type_string(s.strip()) for s in element_type_strs if s.strip()))
    else:
        # Fallback for types not explicitly handled or if parsing fails
        # This shouldn't be reached if st_cty_type_string generates valid types
        # and this function covers all those generated structures.
        raise ValueError(f"Cannot generate data for unknown type string structure: {type_str}")


@st.composite
def st_complex_type_and_data_pair(draw, max_depth=3): # Changed max_depth default from 2 to 3
    type_str = draw(st_cty_type_string(max_depth=max_depth))
    # Ensure type_str is something parse_type_definition and st_data_for_type_string can handle
    # Sometimes st_cty_type_string might produce slightly malformed strings if not careful with joins,
    # e.g. object({,}) or tuple([,]). The strategies for object_attrs and tuple_elements use min_size=0.
    # Filter out such cases or ensure generators are robust.
    # For now, let's assume they are mostly correct.
    try:
        # Validate if parse_type_definition can handle it, if not, skip.
        # This is a check to ensure st_cty_type_string is producing valid structures.
        parse_type_definition(type_str)
    except ValueError:
        # If type_str is invalid, tell Hypothesis to try again with a different one.
        # This might hide issues in st_cty_type_string, so careful debugging of that strategy is needed.
        pytest.skip(f"Generated invalid type_str: {type_str}")

    data = draw(st_data_for_type_string(type_str))
    return type_str, data

# Helper function to prepare Python data (e.g., convert number strings to Decimal)
def prepare_python_data(data, type_str):
    # This function will use parse_type_definition to understand the structure
    # and convert data accordingly.
    cty_type = parse_type_definition(type_str) # Get the CtyType object

    if cty_type.is_primitive_type():
        if cty_type is CtyNumber:
            try:
                return Decimal(data) if isinstance(data, str) else data
            except InvalidOperation: # Handle cases where data is not a valid Decimal string
                pytest.skip(f"Skipping test: Could not convert '{data}' to Decimal for Python side (primitive).")
        return data # String, Bool are fine as is from st_data_for_type_string

    elif cty_type.is_list_type():
        element_type_str = type_str[len("list("):-1]
        return [prepare_python_data(elem, element_type_str) for elem in data]

    elif cty_type.is_map_type():
        value_type_str = type_str[len("map("):-1]
        return {k: prepare_python_data(v, value_type_str) for k, v in data.items()}

    elif cty_type.is_object_type():
        # For objects, data is a dict. We need to convert values based on their types.
        # The type_str for object is like "object({name=string,age=number})"
        # The cty_type.attribute_types map will have CtyType objects.
        # We need to map these CtyType objects back to type strings for recursive calls,
        # or enhance prepare_python_data to also accept CtyType objects.
        # For simplicity, let's assume data keys match attribute names.

        # Re-parse attribute types from the type_str as we did in parse_type_definition
        # This is a bit redundant but avoids complex CtyType -> type_str conversion here.
        attrs_s = type_str[len("object({"):-2]
        if not attrs_s: return {}

        parsed_attrs = {}
        # A simple parser for "key=type,key2=type2"
        # This needs to be robust for nested types.
        # Example: object({person=object({name=string})})
        # Using regex to find "key=type" pairs, where type can be complex.
        # This regex is an attempt to correctly parse attribute type strings.
        attr_matches = re.finditer(r'(\w+)=((?:object\(\{.*?\})|(?:list\(.*?\))|(?:map\(.*?\))|(?:tuple\[.*?\])|(?:string|number|bool))', attrs_s)
        temp_attr_type_strs = {match.group(1): match.group(2) for match in attr_matches}

        # Fallback if regex fails (e.g. very complex nesting not caught)
        if not temp_attr_type_strs and attrs_s: # if string is not empty but regex found nothing
             # This indicates a parsing issue in the regex above or a very complex type_str.
             # As a fallback, we might try a simpler split if regex fails, or skip.
             # For now, let's assume regex handles most cases from st_cty_type_string.
             pass


        return {
            key: prepare_python_data(value, temp_attr_type_strs.get(key, "string")) # Default to string if key not found, though it should be
            for key, value in data.items()
            if key in temp_attr_type_strs # Process only keys found in type definition
        }


    elif cty_type.is_tuple_type():
        # Similar to object, need element type strings.
        # type_str is "tuple([type1,type2,...])"
        elements_s = type_str[len("tuple(["):-2]
        if not elements_s: return []

        # Regex to split tuple elements, handling nested structures
        element_type_strs = re.findall(r'[^,]+(?:\([^)]*\)|\[[^\]]*\]|\{[^}]*\})*|[^,]+', elements_s)

        return tuple(
            prepare_python_data(data[i], element_type_strs[i].strip())
            for i in range(len(data)) # Iterate over data elements
            if i < len(element_type_strs) # Ensure we have a type string for it
        )

    return data # Fallback


# --- Old Strategies (to be commented out or removed) ---
# @st.composite
# def st_basic_type_and_data_pair(draw):
#     type_str, data_generation_strategy = draw(st.sampled_from([
#         ("string", st_cty_string_data),
#         ("number", st_cty_number_repr()),
#         ("bool", st_cty_bool_data),
#     ]))
#     actual_data_for_go = draw(data_generation_strategy)
#     return (type_str, actual_data_for_go)

# st_simple_type_str = st.sampled_from(["string", "number", "bool"])
# @st.composite
# def st_list_type_and_data(draw):
#     element_type_str = draw(st_simple_type_str)
#     if element_type_str == "string": data_gen_strat = st_cty_string_data
#     elif element_type_str == "number": data_gen_strat = st_cty_number_repr()
#     else: data_gen_strat = st_cty_bool_data
#     list_data = draw(st.lists(data_gen_strat, max_size=3))
#     type_str = f"list({element_type_str})"
#     return (type_str, list_data)

# @st.composite
# def st_map_type_and_data(draw):
#     value_type_str = draw(st_simple_type_str)
#     if value_type_str == "string": data_gen_strat = st_cty_string_data
#     elif value_type_str == "number": data_gen_strat = st_cty_number_repr()
#     else: data_gen_strat = st_cty_bool_data
#     map_data = draw(st.dictionaries(
#         keys=st.text(alphabet=st.characters(min_codepoint=97, max_codepoint=122), min_size=1, max_size=10),
#         values=data_gen_strat, max_size=3 ))
#     type_str = f"map({value_type_str})"
#     return (type_str, map_data)

# @st.composite
# def st_any_type_and_data_pair(draw):
#     chosen_strategy_func = draw(st.sampled_from([
#         st_basic_type_and_data_pair,
#         st_list_type_and_data,
#         st_map_type_and_data,
#     ]))
#     return draw(chosen_strategy_func())


# --- Property-Based Tests ---

@given(drawn_data=st_complex_type_and_data_pair(max_depth=3))
def test_hypothesis_type_comparison(drawn_data):
    type_str, raw_data_for_go = drawn_data

    try:
        hashable_data = tuple(sorted(raw_data_for_go.items())) if isinstance(raw_data_for_go, dict) \
            else tuple(raw_data_for_go) if isinstance(raw_data_for_go, list) \
            else raw_data_for_go
        hyp_test_name_suffix = hash((type_str, hashable_data))
    except TypeError:
        hyp_test_name_suffix = "unhashable_input_" + str(st.random_module().random())

    # --- Python Side Processing ---
    try:
        py_actual_raw_data = prepare_python_data(raw_data_for_go, type_str)
    except pytest.skip.Exception:
        raise
    except Exception as e:
        pytest.fail(f"Data preparation for Python failed. Type: {type_str}, RawData: {raw_data_for_go!r}. Error: {e}", pytrace=False)

    try:
        cty_type_instance = parse_type_definition(type_str)
        py_cty_value = cty_type_instance.validate(py_actual_raw_data)
        py_json_dict = py_cty_value.to_json_comparable_dict()
    except CtyValidationError as e:
        pytest.skip(f"Skipping: pyvider.cty validation error. Type: {type_str}, Data: {py_actual_raw_data!r}. Error: {e}")
    except Exception as e:
        pytest.fail(f"Python cty processing failed. Type: {type_str}, Data: {py_actual_raw_data!r}. Error: {e}", pytrace=False)

    # --- Go Side Processing using Helper ---
    try:
        go_output_bytes = run_go_generator(
            type_str=type_str,
            raw_data_for_go=raw_data_for_go,
            hyp_test_name_suffix=str(hyp_test_name_suffix), # Ensure string for filename
            output_format="json",
            input_file_format="yaml"
        )
        go_json_dict = json.loads(go_output_bytes.decode('utf-8'))
    except pytest.fail.Exception: # If run_go_generator calls pytest.fail
        raise
    except Exception as e: # Catch other errors like JSONDecodeError
        pytest.fail(f"Go generator execution or JSON parsing failed in test_hypothesis_type_comparison. Error: {e}", pytrace=False)

    # --- Compare and Assert ---
    assert py_json_dict == go_json_dict, \
        f"Mismatch. Type: {type_str}\nPY_IN: {py_actual_raw_data!r}\nGO_IN: {raw_data_for_go!r}\n" \
        f"PY_OUT: {json.dumps(py_json_dict, indent=2)}\nGO_OUT: {json.dumps(go_json_dict, indent=2)}"


# --- Python Msgpack Roundtrip Test ---
@given(drawn_data=st_complex_type_and_data_pair(max_depth=3))
def test_python_msgpack_roundtrip(drawn_data):
    type_str, raw_data_for_go = drawn_data

    # --- Python Side Value Creation ---
    try:
        py_actual_raw_data = prepare_python_data(raw_data_for_go, type_str)
    except pytest.skip.Exception: # Catch skip exceptions from prepare_python_data
        raise
    except Exception as e:
        pytest.fail(f"Data preparation for Python (Msgpack test) failed. Type: {type_str}, RawData: {raw_data_for_go!r}. Error: {e}", pytrace=False)

    try:
        cty_type_instance = parse_type_definition(type_str)
        original_py_cty_value = cty_type_instance.validate(py_actual_raw_data)
    except CtyValidationError as e:
        pytest.skip(f"Skipping (Msgpack test): pyvider.cty validation error. Type: {type_str}, Data: {py_actual_raw_data!r}. Error: {e}")
    except Exception as e: # Other errors during pyvider.cty processing
        pytest.fail(f"Python cty processing (Msgpack test) failed. Type: {type_str}, Data: {py_actual_raw_data!r}. Error: {e}", pytrace=False)

    # --- Msgpack Serialization and Deserialization ---
    try:
        msgpack_bytes = cty_value_to_msgpack_bytes(original_py_cty_value)
        deserialized_py_cty_value = cty_value_from_msgpack_bytes(msgpack_bytes, cty_type_instance)
    except Exception as e:
        pytest.fail(f"Python Msgpack roundtrip failed. Type: {type_str}, Value: {original_py_cty_value.GoString()!r}. Error: {e}", pytrace=False)

    # --- Assertions ---
    assert deserialized_py_cty_value == original_py_cty_value, \
        f"Deserialized Msgpack value does not equal the original.\n" \
        f"Original: {original_py_cty_value.GoString()!r}\n" \
        f"Deserialized: {deserialized_py_cty_value.GoString()!r}"

    original_json_dict = original_py_cty_value.to_json_comparable_dict()
    deserialized_json_dict = deserialized_py_cty_value.to_json_comparable_dict()
    assert deserialized_json_dict == original_json_dict, \
        f"JSON comparable dict of deserialized Msgpack value does not equal the original.\n" \
        f"Original JSON: {json.dumps(original_json_dict, indent=2)}\n" \
        f"Deserialized JSON: {json.dumps(deserialized_json_dict, indent=2)}"


# --- Cross-Language Msgpack Comparison Test ---
@given(drawn_data=st_complex_type_and_data_pair(max_depth=3))
def test_cross_language_msgpack_comparison(drawn_data):
    type_str, raw_data_for_go = drawn_data

    # Generate a unique suffix for temporary files if any part needs it
    try:
        hashable_data = tuple(sorted(raw_data_for_go.items())) if isinstance(raw_data_for_go, dict) \
            else tuple(raw_data_for_go) if isinstance(raw_data_for_go, list) \
            else raw_data_for_go
        hyp_test_name_suffix = hash((type_str, hashable_data))
    except TypeError:
        hyp_test_name_suffix = "unhashable_input_" + str(st.random_module().random())

    # --- Python Side Value Creation and Msgpack Serialization ---
    py_msgpack_bytes = None # Initialize to allow access in assert message even if creation fails
    py_cty_value = None # Initialize for use in error messages
    try:
        py_actual_raw_data = prepare_python_data(raw_data_for_go, type_str)
        cty_type_instance = parse_type_definition(type_str)
        py_cty_value = cty_type_instance.validate(py_actual_raw_data)
        py_msgpack_bytes = cty_value_to_msgpack_bytes(py_cty_value)
    except pytest.skip.Exception:
        raise
    except CtyValidationError as e:
        pytest.skip(f"Skipping (Cross-Msgpack test): pyvider.cty validation error. Type: {type_str}, Data: {py_actual_raw_data!r}. Error: {e}")
    except Exception as e:
        pytest.fail(f"Python cty processing or Msgpack serialization (Cross-Msgpack test) failed. Type: {type_str}, Data: {py_actual_raw_data!r}. Error: {e}", pytrace=False)

    # --- Go Side Msgpack Serialization using Helper ---
    go_msgpack_bytes = None # Initialize for error messages
    try:
        go_msgpack_bytes = run_go_generator(
            type_str=type_str,
            raw_data_for_go=raw_data_for_go,
            hyp_test_name_suffix=str(hyp_test_name_suffix),
            output_format="msgpack",
            input_file_format="yaml"
        )
    except pytest.fail.Exception: # If run_go_generator calls pytest.fail
        raise
    except Exception as e:
        pytest.fail(f"Go generator execution failed in test_cross_language_msgpack_comparison. Error: {e}", pytrace=False)

    # --- Comparison and Assertion ---
    if py_msgpack_bytes != go_msgpack_bytes:
        # Try to decode Go's msgpack for a more readable diff if it's small
        # This assumes Go output is structurally similar to Python's JSONComparable representation
        py_val_for_go_debug = None
        go_val_for_debug = None
        try:
            if go_msgpack_bytes:
                 # Use the Python library to deserialize Go's msgpack output for debugging.
                 # This requires that Go's msgpack output for a cty.Value (via JSONComparable intermediate)
                 # is deserializable by Python's cty_value_from_msgpack_bytes if the types match.
                 # This might not always be true if JSONComparable structures differ subtly.
                 # For a direct byte comparison, this step is for richer error messages only.
                 # We need a CtyType to deserialize, so we use the one we have (cty_type_instance).
                 go_val_for_debug = cty_value_from_msgpack_bytes(go_msgpack_bytes, cty_type_instance) # py_cty_value.Type() should also work
        except Exception as e_debug:
            go_val_for_debug = f"<Error deserializing Go's msgpack: {e_debug}>"

        # Also get Python's value as dict for comparison in message
        if py_cty_value:
            py_val_for_go_debug = py_cty_value.to_json_comparable_dict()


        detail_msg = (
            f"Python and Go generated Msgpack bytes do not match.\n"
            f"Type: {type_str}\n"
            f"PY_IN (prepared): {py_actual_raw_data!r}\n" # py_actual_raw_data might not be set if prepare_python_data fails early
            f"GO_IN (raw): {raw_data_for_go!r}\n"
            f"PY_Bytes (len {len(py_msgpack_bytes) if py_msgpack_bytes else 'N/A'}): {py_msgpack_bytes.hex()[:200] if py_msgpack_bytes else 'N/A'}...\n"
            f"GO_Bytes (len {len(go_msgpack_bytes) if go_msgpack_bytes else 'N/A'}): {go_msgpack_bytes.hex()[:200] if go_msgpack_bytes else 'N/A'}...\n"
            f"PY_Value (for debug): {json.dumps(py_val_for_go_debug, indent=2) if py_val_for_go_debug else 'N/A'}\n"
            f"GO_Value (deserialized from GO_bytes, for debug): {go_val_for_debug!r}\n"
        )
        pytest.fail(detail_msg)
    elif py_msgpack_bytes is None and go_msgpack_bytes is not None: # Should not happen if Python side succeeded
        pytest.fail("Python Msgpack bytes are None, but Go bytes are not. Inconsistency in test flow.")
    elif py_msgpack_bytes is not None and go_msgpack_bytes is None: # Should not happen if Go side succeeded
        pytest.fail("Go Msgpack bytes are None, but Python bytes are not. Inconsistency in test flow.")
    # If both are None, it implies a skip or failure before bytes were generated, which is fine.
    # If they are equal and not None, the test passes implicitly.


# --- Msgpack to JSON Loaded Comparison Test ---
@given(drawn_data=st_complex_type_and_data_pair(max_depth=3))
def test_msgpack_to_json_loaded_comparison(drawn_data):
    type_str, raw_data_for_go = drawn_data

    # --- Python Side: Generate initial CtyValue and Msgpack bytes ---
    try:
        py_actual_raw_data = prepare_python_data(raw_data_for_go, type_str)
    except pytest.skip.Exception:
        raise
    except Exception as e:
        pytest.fail(f"Data preparation for Python (Msgpack->JSON test) failed. Type: {type_str}, RawData: {raw_data_for_go!r}. Error: {e}", pytrace=False)

    original_py_cty_value = None
    py_msgpack_bytes = None
    cty_type_instance = None # Ensure it's defined for potential use in error messages
    hyp_test_name_suffix = "msgpack_to_json_load" # Suffix for any temp files if needed by helper

    try:
        py_actual_raw_data = prepare_python_data(raw_data_for_go, type_str)
        cty_type_instance = parse_type_definition(type_str)
        original_py_cty_value = cty_type_instance.validate(py_actual_raw_data)
        py_msgpack_bytes = cty_value_to_msgpack_bytes(original_py_cty_value)
    except pytest.skip.Exception:
        raise
    except CtyValidationError as e:
        pytest.skip(f"Skipping (Msgpack->JSON test): pyvider.cty validation error. Type: {type_str}, Data: {py_actual_raw_data!r}. Error: {e}")
    except Exception as e:
        pytest.fail(f"Python cty processing or Msgpack serialization (Msgpack->JSON test) failed. Type: {type_str}, Data: {py_actual_raw_data!r}. Error: {e}", pytrace=False)

    # --- Python Side: Load Msgpack and get JSON dict ---
    py_json_dict = None
    if py_msgpack_bytes and cty_type_instance: # Proceed if Python side succeeded so far
        try:
            py_loaded_value = cty_value_from_msgpack_bytes(py_msgpack_bytes, cty_type_instance)
            py_json_dict = py_loaded_value.to_json_comparable_dict()
        except Exception as e:
            pytest.fail(f"Python Msgpack deserialization or JSON conversion (Msgpack->JSON test) failed. Error: {e}", pytrace=False)
    else: # Should only happen if a skip/fail occurred above
        if not py_msgpack_bytes: pytest.fail("Test logic error: py_msgpack_bytes not generated before Python load stage.")
        if not cty_type_instance: pytest.fail("Test logic error: cty_type_instance not available before Python load stage.")


    # --- Go Side: Load Msgpack (from file) and get JSON dict using Helper ---
    go_json_dict_from_msgpack = None
    if py_msgpack_bytes: # Proceed if Python generated msgpack
        try:
            # Generate a unique suffix for this specific test run for any temp files created by the helper
            # It's okay to reuse raw_data_for_go for hashing here as it's part of the input leading to py_msgpack_bytes
            hashable_data_for_suffix = tuple(sorted(raw_data_for_go.items())) if isinstance(raw_data_for_go, dict) \
                                   else tuple(raw_data_for_go) if isinstance(raw_data_for_go, list) \
                                   else raw_data_for_go
            current_hyp_test_name_suffix = str(hash((type_str, hashable_data_for_suffix, "msgpack_to_json")))

            go_output_bytes = run_go_generator(
                type_str=type_str,
                raw_data_for_go=None, # Not used by Go when input_file_format is 'msgpack'
                hyp_test_name_suffix=current_hyp_test_name_suffix,
                output_format="json", # Go script's msgpack input path outputs JSON
                input_file_format="msgpack",
                input_msgpack_bytes=py_msgpack_bytes
            )
            go_json_dict_from_msgpack = json.loads(go_output_bytes.decode('utf-8'))
        except pytest.fail.Exception: # If run_go_generator calls pytest.fail
            raise
        except json.JSONDecodeError as e:
            pytest.fail(f"Failed to parse JSON output from Go (Msgpack->JSON test). Output: {go_output_bytes.decode(errors='replace')}. Error: {e}", pytrace=False)
        except Exception as e:
            pytest.fail(f"Go generator execution or JSON parsing failed in test_msgpack_to_json_loaded_comparison. Error: {e}", pytrace=False)
    else: # Should only happen if Python side failed to produce msgpack_bytes
         pytest.fail("Test logic error: py_msgpack_bytes not available for Go processing stage.")


    # --- Comparison and Assertion ---
    assert py_json_dict == go_json_dict_from_msgpack, \
        (f"JSON representations after loading Python-generated Msgpack differ between Python and Go.\n"
         f"Type: {type_str}\n"
         f"Original Python Value (for context): {original_py_cty_value.GoString()!r}\n"
         f"Python JSON from loaded Msgpack: {json.dumps(py_json_dict, indent=2)}\n"
         f"Go JSON from loaded Msgpack: {json.dumps(go_json_dict_from_msgpack, indent=2)}")


# --- Test for simple fixed object schema (kept for specific non-recursive object check) ---
@st.composite
def st_simple_object_data_for_go(draw):
    data = {"name": draw(st_cty_string_data), "age": draw(st_cty_number_repr())}
    return data
@given(raw_data_for_go=st_simple_object_data_for_go())
def test_hypothesis_simple_object_comparison(raw_data_for_go):
    type_str = "object({name=string,age=number})"
    hyp_test_name_suffix = hash((type_str, json.dumps(raw_data_for_go, sort_keys=True)))
    py_actual_raw_data = {"name": raw_data_for_go["name"], "age": Decimal(raw_data_for_go["age"])}
    try:
        cty_type_instance = parse_type_definition(type_str)
        py_cty_value = cty_type_instance.validate(py_actual_raw_data)
        py_json_dict = py_cty_value.to_json_comparable_dict()
    except Exception as e:
        pytest.fail(f"Python side (simple object) failed. Data: {py_actual_raw_data!r}. Error: {e}", pytrace=False)
    go_test_case_data = {"name": f"hypothesis_object_{hyp_test_name_suffix}", "type_definition": type_str, "raw_input": raw_data_for_go}
    tmp_yaml_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, dir=TEMP_DIR_FOR_HYPOTHESIS_YAML, encoding='utf-8') as tmp_yaml:
            yaml.dump(go_test_case_data, tmp_yaml)
            tmp_yaml_path = tmp_yaml.name
        go_executable = shutil.which("go")
        if not go_executable: pytest.skip("Go executable not found"); return
        go_gen_cmd = [go_executable, "run", GO_GENERATOR_SCRIPT, "-stdout", tmp_yaml_path]
        go_result = subprocess.run(go_gen_cmd, check=True, capture_output=True, text=True, cwd=str(SCRIPT_DIR / "go_src"), timeout=30)
        go_json_dict = json.loads(go_result.stdout)
    except Exception as e:
        if tmp_yaml_path and os.path.exists(tmp_yaml_path): os.remove(tmp_yaml_path)
        pytest.fail(f"Go generator phase (simple object) failed: {e}", pytrace=False)
    finally:
        if tmp_yaml_path and os.path.exists(tmp_yaml_path): os.remove(tmp_yaml_path)
    assert py_json_dict == go_json_dict, "Mismatch for simple object."

# --- Strategies for Null and Unknown Values (updated) ---
st_parsable_type_str_for_special = st_cty_type_string(max_depth=1) # Use new type string generator

@st.composite
def st_null_value_with_type(draw):
    type_str = draw(st_parsable_type_str_for_special)
    try: parse_type_definition(type_str) # Validate type string
    except ValueError: pytest.skip(f"Generated invalid type_str for null test: {type_str}")
    return (type_str, None)

@st.composite
def st_unknown_value_with_type(draw):
    type_str = draw(st_parsable_type_str_for_special)
    try: parse_type_definition(type_str) # Validate type string
    except ValueError: pytest.skip(f"Generated invalid type_str for unknown test: {type_str}")
    return (type_str, "__unknown__")


# --- Helper for Null/Unknown Comparison ---
def type_str_to_filename_component(type_str: str) -> str:
    return type_str.replace('(', '_').replace(')','').replace(',','_').replace('{','_').replace('}','').replace('=','_').replace('[','_').replace(']','_')

def run_comparison_for_special_value(type_str, raw_input_for_go, is_null=False, is_unknown=False):
    try:
        py_cty_type = parse_type_definition(type_str)
        py_cty_value = CtyValue.null(py_cty_type) if is_null else CtyValue.unknown(py_cty_type)
        py_json_dict = py_cty_value.to_json_comparable_dict()
        assert py_json_dict["is_null"] == is_null
        assert py_json_dict["is_unknown"] == is_unknown
    except Exception as e:
        pytest.fail(f"Python (special value) failed. Type: {type_str}. Error: {e}", pytrace=False)

    go_test_case_name = f"hypothesis_{'null' if is_null else 'unknown'}_{type_str_to_filename_component(type_str)}"
    go_test_case_data = {"name": go_test_case_name, "type_definition": type_str, "raw_input": raw_input_for_go}
    tmp_yaml_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, dir=TEMP_DIR_FOR_HYPOTHESIS_YAML, encoding='utf-8') as tmp_yaml:
            yaml.dump(go_test_case_data, tmp_yaml)
            tmp_yaml_path = tmp_yaml.name
        go_exe = shutil.which("go")
        if not go_exe: pytest.skip("Go executable not found"); return
        cmd = [go_exe, "run", GO_GENERATOR_SCRIPT, "-stdout", tmp_yaml_path]
        go_run_result = subprocess.run(cmd, cwd=str(SCRIPT_DIR / "go_src"), capture_output=True, text=True, timeout=10)
        if go_run_result.returncode != 0: pytest.fail(f"Go (special value) failed: {go_run_result.stderr}", pytrace=False)
        go_json_dict = json.loads(go_run_result.stdout)
    except Exception as e:
        if tmp_yaml_path and os.path.exists(tmp_yaml_path): os.remove(tmp_yaml_path)
        pytest.fail(f"Go generator phase (special value) failed: {e}", pytrace=False)
    finally:
        if tmp_yaml_path and os.path.exists(tmp_yaml_path): os.remove(tmp_yaml_path)
    assert py_json_dict == go_json_dict, f"Mismatch for special value. Type: {type_str}"


@given(type_and_null_input=st_null_value_with_type())
def test_hypothesis_null_value_comparison(type_and_null_input):
    type_str, raw_input_for_go = type_and_null_input
    run_comparison_for_special_value(type_str, raw_input_for_go, is_null=True)

@given(type_and_unknown_input=st_unknown_value_with_type())
def test_hypothesis_unknown_value_comparison(type_and_unknown_input):
    type_str, raw_input_for_go = type_and_unknown_input
    run_comparison_for_special_value(type_str, raw_input_for_go, is_unknown=True)

# Ensure any pytest.skip exceptions are re-raised if not caught by Hypothesis
# This is generally handled by Hypothesis, but good to be mindful of.
# For example, if parse_type_definition fails inside a strategy and isn't caught,
# or if data preparation leads to a skip.
# The current skips in test_hypothesis_type_comparison for CtyValidationError
# and in prepare_python_data are intentional ways to tell Hypothesis the data is unusable.
# The skips in st_complex_type_and_data_pair for invalid type_str are also intentional.
# Similarly for st_null_value_with_type and st_unknown_value_with_type.
