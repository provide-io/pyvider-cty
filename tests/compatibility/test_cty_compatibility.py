import json
import pathlib
import sys
import subprocess
import shutil # For shutil.which
import pytest
import tempfile # Added import
import yaml # Added import
import os # For os.remove
from decimal import Decimal
from hypothesis import given, strategies as st

# pyvider.cty imports
from pyvider.cty import CtyValue, CtyType, CtyString, CtyNumber, CtyBool, CtyList, CtyMap, CtyObject, CtyTuple # Added Map, Object, Tuple
from pyvider.cty.exceptions import CtyValidationError

# --- Configuration ---
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
TEST_CASES_DIR = SCRIPT_DIR / "testcases"
OUTPUT_BASE_DIR = SCRIPT_DIR / "output"
PYTHON_GENERATOR_SCRIPT = SCRIPT_DIR / "py_cty_generator.py"
GO_GENERATOR_SCRIPT = "go_cty_generator.go" # Name of the Go script

# Temp directory for Hypothesis-generated YAML files
TEMP_DIR_FOR_HYPOTHESIS_YAML = SCRIPT_DIR / "hypothesis_temp_yaml"
TEMP_DIR_FOR_HYPOTHESIS_YAML.mkdir(parents=True, exist_ok=True)


# --- Helper Functions (including parse_type_definition moved here) ---

# Copied and adapted from py_cty_generator.py
# For Hypothesis tests, logger might not be available or desired in the same way.
# We can simplify it or make logger optional for utils.
# For now, removing logger calls from this utility function.
def parse_type_definition(type_str: str) -> CtyType:
    # print(f"DEBUG: Parsing type definition string: '{type_str}'") # Optional debug print
    if type_str == "string":
        return CtyString()
    elif type_str == "number":
        return CtyNumber()
    elif type_str == "bool":
        return CtyBool()
    elif type_str.startswith("list(") and type_str.endswith(")"):
        inner_type_str = type_str[len("list("):-1]
        inner_type = parse_type_definition(inner_type_str) # Recursive call
        return CtyList(element_type=inner_type)
    elif type_str.startswith("map(") and type_str.endswith(")"):
        value_type_str = type_str[len("map("):-1]
        value_type = parse_type_definition(value_type_str)
        # cty spec implies string keys for maps, so CtyMap's key_type defaults to CtyString
        return CtyMap(value_type=value_type)
    elif type_str.startswith("tuple([") and type_str.endswith("])"):
        element_types_str = type_str[len("tuple(["):-2]
        if not element_types_str: # Empty tuple
            return CtyTuple([])
        element_type_strs = [s.strip() for s in element_types_str.split(',')]
        element_types = [parse_type_definition(s) for s in element_type_strs]
        return CtyTuple(element_types)
    elif type_str.startswith("object({") and type_str.endswith("})"):
        attrs_str = type_str[len("object({"):-2]
        if not attrs_str: # Empty object
            return CtyObject({})
        attr_pairs = [s.strip() for s in attrs_str.split(',')]
        attribute_types = {}
        for pair in attr_pairs:
            name, type_name = pair.split('=', 1)
            attribute_types[name.strip()] = parse_type_definition(type_name.strip())
        return CtyObject(attribute_types)
    else:
        err_msg = f"Unsupported type definition string for property-based testing: {type_str}"
        # print(f"ERROR: {err_msg}") # Optional error print
        raise ValueError(err_msg)


def load_json_file(file_path: pathlib.Path) -> dict | None:
    """
    Loads a JSON file and returns its content as a dictionary.
    Prints an error message and returns None if loading fails.
    """
    if not file_path.exists():
        print(f"  [❗ ERROR]: File not found: {file_path}")
        return None
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"  [❗ ERROR]: Could not decode JSON from {file_path}. Error: {e}")
        return None
    except Exception as e: # Catch other potential errors like permission issues
        print(f"  [❗ ERROR]: An unexpected error occurred while reading {file_path}. Error: {e}")
        return None

def compare_json_outputs(test_case_name: str, file_type: str) -> bool:
    """
    Compares Python and Go generated JSON files for a specific test case and file type.

    Args:
        test_case_name: The name of the test case (directory name).
        file_type: The type of file to compare (e.g., "value", "type").

    Returns:
        True if the files match or if essential files are missing (error printed by load_json_file),
        False if there's a mismatch.
    """
    py_file_path = OUTPUT_BASE_DIR / test_case_name / f"py_{file_type}.json"
    go_file_path = OUTPUT_BASE_DIR / test_case_name / f"go_{file_type}.json"

    print(f"  Comparing {file_type.upper()} files for test case: {test_case_name}...")
    print(f"    Python file: {py_file_path}")
    print(f"    Go file    : {go_file_path}")

    py_data = load_json_file(py_file_path)
    go_data = load_json_file(go_file_path)

    if py_data is None or go_data is None:
        # load_json_file already prints the specific error (file not found or JSON decode error)
        # We mark this as a failure for the comparison.
        print(f"  [❌ {file_type.upper()}]: FAILED for {test_case_name} due to missing/corrupt data.")
        return False

    if py_data == go_data:
        print(f"  [✅ {file_type.upper()}]: Match for {test_case_name}")
        return True
    else:
        print(f"  [❌ {file_type.upper()}]: Mismatch for {test_case_name}")
        # Outputting the diff directly can be very verbose for large files.
        # Consider using a diff library or summarizing differences if this becomes an issue.
        # For POC, full dump is acceptable.
        print(f"    --- py_{file_type}.json (Content) ---")
        print(json.dumps(py_data, indent=2, ensure_ascii=False))
        print(f"    --- End of py_{file_type}.json ---")
        print(f"    --- go_{file_type}.json (Content) ---")
        print(json.dumps(go_data, indent=2, ensure_ascii=False))
        print(f"    --- End of go_{file_type}.json ---")
        return False

# --- Test Case Discovery (YAML based) ---

def get_test_case_files() -> list[pathlib.Path]:
    """Scans the testcases directory and returns a list of YAML file paths."""
    if not TEST_CASES_DIR.is_dir():
        print(f"[❗ ERROR]: Test cases directory not found: {TEST_CASES_DIR}")
        return []
    return sorted(list(TEST_CASES_DIR.glob("*.yaml")))

# --- Pytest Test Functions ---

@pytest.mark.parametrize("test_case_file", get_test_case_files(), ids=lambda p: p.name)
def test_yaml_compatibility(test_case_file: pathlib.Path):
    """
    Runs the Python and Go generators for a given YAML test case,
    then compares their JSON outputs.
    """
    test_case_name = test_case_file.stem
    print(f"\n--- 🧪 Test Case: {test_case_name} ---")

    # Ensure output directory for the test case exists
    # (though generators should also ensure this, good to have here too)
    (OUTPUT_BASE_DIR / test_case_name).mkdir(parents=True, exist_ok=True)

    # Run Python Generator
    print(f"  🐍 Running Python generator for: {test_case_file.name}")
    py_gen_cmd = [
        sys.executable,
        str(PYTHON_GENERATOR_SCRIPT.resolve()),
        str(test_case_file.resolve())
    ]
    try:
        py_result = subprocess.run(py_gen_cmd, check=True, capture_output=True, text=True, timeout=30)
        print(f"  🐍 Python generator STDOUT for {test_case_name}:\n{py_result.stdout}")
        if py_result.stderr:
            print(f"  🐍 Python generator STDERR for {test_case_name}:\n{py_result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"  [❌ ERROR]: Python generator failed for {test_case_name}.")
        print(f"    Command: {' '.join(e.cmd)}")
        print(f"    Return Code: {e.returncode}")
        print(f"    Stdout:\n{e.stdout}")
        print(f"    Stderr:\n{e.stderr}")
        pytest.fail(f"Python generator failed for {test_case_name}", pytrace=False)
    except subprocess.TimeoutExpired as e:
        print(f"  [❌ ERROR]: Python generator timed out for {test_case_name}.")
        print(f"    Command: {' '.join(e.cmd)}")
        print(f"    Stdout:\n{e.stdout}")
        print(f"    Stderr:\n{e.stderr}")
        pytest.fail(f"Python generator timed out for {test_case_name}", pytrace=False)


    # Run Go Generator
    go_executable = shutil.which("go")
    if not go_executable:
        pytest.skip("Go executable not found, skipping Go generator part.")
        return # Skip if Go is not available

    print(f"  🐹 Running Go generator for: {test_case_file.name}")
    # Pass absolute path to test case file to Go script.
    # The Go script itself will determine its output location based on this.
    # The CWD is set to the directory of the Go script to handle `go.mod` correctly.
    go_gen_cmd = [
        go_executable,
        "run",
        GO_GENERATOR_SCRIPT, # Just the script name, as cwd is its directory
        str(test_case_file.resolve())
    ]
    try:
        # Run the Go generator from its own directory so it can find go.mod
        go_result = subprocess.run(go_gen_cmd, check=True, capture_output=True, text=True, cwd=str(SCRIPT_DIR), timeout=30)
        print(f"  🐹 Go generator STDOUT for {test_case_name}:\n{go_result.stdout}")
        if go_result.stderr:
            print(f"  🐹 Go generator STDERR for {test_case_name}:\n{go_result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"  [❌ ERROR]: Go generator failed for {test_case_name}.")
        print(f"    Command: {' '.join(e.cmd)}")
        print(f"    Return Code: {e.returncode}")
        print(f"    Stdout:\n{e.stdout}")
        print(f"    Stderr:\n{e.stderr}")
        pytest.fail(f"Go generator failed for {test_case_name}", pytrace=False)
    except subprocess.TimeoutExpired as e:
        print(f"  [❌ ERROR]: Go generator timed out for {test_case_name}.")
        print(f"    Command: {' '.join(e.cmd)}")
        print(f"    Stdout:\n{e.stdout}")
        print(f"    Stderr:\n{e.stderr}")
        pytest.fail(f"Go generator timed out for {test_case_name}", pytrace=False)


    # Compare Outputs
    print(f"  🔍 Comparing outputs for {test_case_name}...")
    value_match = compare_json_outputs(test_case_name, "value")
    type_match = compare_json_outputs(test_case_name, "type")

    if not value_match:
        print(f"  [❌ VALUE MISMATCH] for {test_case_name}")
    if not type_match:
        print(f"  [❌ TYPE MISMATCH] for {test_case_name}")

    assert value_match, f"Value JSON outputs do not match for test case: {test_case_name}"
    assert type_match, f"Type JSON outputs do not match for test case: {test_case_name}"

    print(f"--- ✅ Test Case PASSED: {test_case_name} ---")

# Note: The old_main_style_runner and if __name__ == "__main__": block
# should be removed as pytest will now manage test execution.

# --- Hypothesis Strategies ---
st_cty_string_data = st.text(max_size=100) # Limit size for sanity

# Raw data strategy for numbers (before string conversion for Go)
st_cty_number_raw = st.one_of(
    st.integers(),
    st.floats(allow_nan=False, allow_infinity=False, width=32),
    # Limit decimals to avoid excessively large numbers that go beyond typical float64 capabilities in Go
    # or cause performance issues with string conversion / Decimal parsing.
    st.decimals(allow_nan=False, allow_infinity=False, places=5, min_value=Decimal("-1e18"), max_value=Decimal("1e18"))
)

@st.composite
def st_cty_number_repr(draw):
    """
    Generates numbers and converts them to a string representation
    suitable for YAML/JSON and then for pyvider.cty's Decimal conversion.
    """
    num_val = draw(st_cty_number_raw)
    if isinstance(num_val, Decimal):
        # Use to_eng_string() for Decimal to avoid scientific notation if possible,
        # which can be problematic for some cross-language parsers if not handled carefully.
        return num_val.to_eng_string()
    return str(num_val)

st_cty_bool_data = st.booleans()

@st.composite
def st_basic_type_and_data_pair(draw):
    """
    Generates a pair of (type_string, raw_data_for_go_yaml).
    raw_data_for_go_yaml is in a format suitable for YAML dumping (e.g., numbers as strings).
    """
    type_str, data_generation_strategy = draw(st.sampled_from([
        ("string", st_cty_string_data),
        ("number", st_cty_number_repr()),
        ("bool", st_cty_bool_data),
    ]))
    actual_data_for_go = draw(data_generation_strategy)
    return (type_str, actual_data_for_go)

# Strategy for a simple type string like "string", "number", "bool"
st_simple_type_str = st.sampled_from(["string", "number", "bool"])

@st.composite
def st_list_type_and_data(draw):
    element_type_str = draw(st_simple_type_str)
    # Get the data generation strategy for the element type
    if element_type_str == "string":
        data_gen_strat = st_cty_string_data
    elif element_type_str == "number":
        data_gen_strat = st_cty_number_repr()
    else: # bool
        data_gen_strat = st_cty_bool_data

    list_data = draw(st.lists(data_gen_strat, max_size=3)) # Keep lists small
    type_str = f"list({element_type_str})"
    return (type_str, list_data)

@st.composite
def st_map_type_and_data(draw):
    value_type_str = draw(st_simple_type_str)
    if value_type_str == "string":
        data_gen_strat = st_cty_string_data
    elif value_type_str == "number":
        data_gen_strat = st_cty_number_repr()
    else: # bool
        data_gen_strat = st_cty_bool_data

    # Keys for maps are simple strings
    map_data = draw(st.dictionaries(
        keys=st.text(alphabet=st.characters(min_codepoint=97, max_codepoint=122), min_size=1, max_size=10),
        values=data_gen_strat,
        max_size=3
    ))
    type_str = f"map({value_type_str})" # Assumes string keys, only specifies value type
    return (type_str, map_data)

# Combined strategy for any type (basic, list, map)
@st.composite
def st_any_type_and_data_pair(draw):
    chosen_strategy_func = draw(st.sampled_from([
        st_basic_type_and_data_pair,
        st_list_type_and_data,
        st_map_type_and_data,
    ]))
    return draw(chosen_strategy_func())


# --- Property-Based Tests ---

@given(drawn_data=st_any_type_and_data_pair()) # Use the new combined strategy
def test_hypothesis_type_comparison(drawn_data): # Renamed test function
    type_str, raw_data_for_go = drawn_data

    # Unique name for the test case, can be based on hash or a counter if needed for non-file based
    # For temporary YAML, the tempfile name itself is unique.
    # For logging/debugging, a descriptive name is good.
    # Hashing raw_data might be unstable if it's a complex mutable type, but for primitives/strings it's fine.
    try:
        hyp_test_name_suffix = hash((type_str, raw_data_for_go))
    except TypeError: # Unhashable type
        hyp_test_name_suffix = "unhashable_input"

    print(f"\n--- 🔮 Hypothesis Test Case ---")
    print(f"  Type: {type_str}")
    print(f"  Raw Data (for Go YAML): {raw_data_for_go!r}")

    # --- Python Side Processing ---
    # This part needs to correctly interpret raw_data_for_go based on type_str for pyvider.cty
    py_actual_raw_data = raw_data_for_go
    if type_str == "number":
        try:
            py_actual_raw_data = Decimal(raw_data_for_go)
        except Exception as e: # Handles potential conversion errors for ill-formatted number strings
            pytest.skip(f"Skipping test: Could not convert '{raw_data_for_go}' to Decimal for Python side. Error: {e}")
    elif type_str.startswith("list("):
        if type_str.endswith("(number)"): # list(number)
            try:
                py_actual_raw_data = [Decimal(x) for x in raw_data_for_go]
            except Exception as e:
                pytest.skip(f"Skipping test: Error converting elements of list(number) '{raw_data_for_go}' to Decimal. Error: {e}")
        # For list(string) or list(bool), raw_data_for_go is already fine
    elif type_str.startswith("map("):
        if type_str.endswith("(number)"): # map(number)
            try:
                py_actual_raw_data = {k: Decimal(v) for k, v in raw_data_for_go.items()}
            except Exception as e:
                 pytest.skip(f"Skipping test: Error converting values of map(number) '{raw_data_for_go}' to Decimal. Error: {e}")
        # For map(string) or map(bool), raw_data_for_go is already fine

    # For bools that might be strings from complex strategies (though current ones are direct bools)
    elif type_str == "bool" and isinstance(raw_data_for_go, str):
        py_actual_raw_data = raw_data_for_go.lower() == 'true'


    try:
        cty_type_instance = parse_type_definition(type_str)
        py_cty_value = cty_type_instance.validate(py_actual_raw_data)
        py_json_dict = py_cty_value.to_json_comparable_dict()
        print(f"  🐍 Python JSON: {json.dumps(py_json_dict, indent=2, ensure_ascii=False)}")
    except CtyValidationError as e:
        # This can happen if Hypothesis generates data that's valid for YAML but not for cty
        # e.g. a number string that Decimal can't parse, or a type mismatch not caught by strategy.
        pytest.skip(f"Skipping test: pyvider.cty validation error for type '{type_str}', data {py_actual_raw_data!r}. Error: {e}")
    except Exception as e:
        pytest.fail(f"Python side processing failed for type '{type_str}', data {py_actual_raw_data!r}: {e}", pytrace=False)

    # --- Prepare Temporary YAML for Go ---
    go_test_case_data = {
        "name": f"hypothesis_case_{hyp_test_name_suffix}",
        "type_definition": type_str,
        "raw_input": raw_data_for_go
    }

    tmp_yaml_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding='utf-8') as tmp_yaml:
            yaml.dump(go_test_case_data, tmp_yaml)
            tmp_yaml_path = tmp_yaml.name
        print(f"  📝 Temp YAML for Go: {tmp_yaml_path}")

        # --- Run Go Generator ---
        go_executable = shutil.which("go")
        if not go_executable:
            pytest.skip("Go executable not found, skipping Go generator part and comparison.")
            return

        print(f"  🐹 Running Go generator for temp YAML: {tmp_yaml_path}")
        go_gen_cmd = [
            go_executable, "run", GO_GENERATOR_SCRIPT, "-stdout", tmp_yaml_path
        ]
        go_result = subprocess.run(go_gen_cmd, check=True, capture_output=True, text=True, cwd=str(SCRIPT_DIR), timeout=30)

        if go_result.stderr: # Go generator often prints logs to stderr
            print(f"  🐹 Go generator STDERR:\n{go_result.stderr}")

        go_json_str = go_result.stdout
        print(f"  🐹 Go generator STDOUT (JSON):\n{go_json_str}")

        try:
            go_json_dict = json.loads(go_json_str)
        except json.JSONDecodeError as e:
            pytest.fail(f"Failed to decode JSON from Go generator output. Error: {e}\nOutput was:\n{go_json_str}", pytrace=False)

    except subprocess.CalledProcessError as e:
        pytest.fail(f"Go generator failed.\nCmd: {' '.join(e.cmd)}\nRC: {e.returncode}\nStdout:\n{e.stdout}\nStderr:\n{e.stderr}", pytrace=False)
    except subprocess.TimeoutExpired as e:
        pytest.fail(f"Go generator timed out.\nCmd: {' '.join(e.cmd)}\nStdout:\n{e.stdout}\nStderr:\n{e.stderr}", pytrace=False)
    except Exception as e: # Catch any other errors during Go processing or temp file handling
        pytest.fail(f"An error occurred during Go generator phase: {e}", pytrace=False)
    finally:
        if tmp_yaml_path and os.path.exists(tmp_yaml_path):
            os.remove(tmp_yaml_path)
            print(f"  🗑️ Cleaned up temp YAML: {tmp_yaml_path}")

    # --- Compare and Assert ---
    print(f"  🔍 Comparing Python and Go JSON outputs...")
    if py_json_dict != go_json_dict:
        # Pretty print diff using pytest's built-in diffing for dicts on assert
        # This will be more readable than manual printouts if assertion fails.
        # However, printing them here can be useful if pytest output truncates.
        # For CI, rely on pytest's diff. For local debugging, these prints can help.
        # print("  Difference detected:")
        # print(f"    🐍 Python JSON: {json.dumps(py_json_dict, indent=2, ensure_ascii=False)}")
        # print(f"    🐹 Go JSON    : {json.dumps(go_json_dict, indent=2, ensure_ascii=False)}")
        pass # Pytest assertion below will handle the detailed diff.

    assert py_json_dict == go_json_dict, \
        f"Mismatch between Python and Go JSON outputs for Hypothesis test.\n" \
        f"Type: {type_str}, Input for Go: {raw_data_for_go!r}\n" \
        f"Python Dict: {json.dumps(py_json_dict, indent=2, ensure_ascii=False)}\n" \
        f"Go Dict    : {json.dumps(go_json_dict, indent=2, ensure_ascii=False)}"

    print("  [✅✅✅] Python and Go outputs MATCH for this Hypothesis case.")


# Separate test for the fixed-schema object for now
@st.composite
def st_simple_object_data_for_go(draw):
    # Data for Go YAML: age will be string, name will be string.
    data = {
        "name": draw(st_cty_string_data),
        "age": draw(st_cty_number_repr())
    }
    return data

@given(raw_data_for_go=st_simple_object_data_for_go())
def test_hypothesis_simple_object_comparison(raw_data_for_go):
    type_str = "object({name=string,age=number})" # Fixed type string

    hyp_test_name_suffix = hash((type_str, json.dumps(raw_data_for_go, sort_keys=True))) # Make dict hashable for name

    print(f"\n--- 🔮 Hypothesis Test Case (Simple Object) ---")
    print(f"  Type: {type_str}")
    print(f"  Raw Data (for Go YAML): {raw_data_for_go!r}")

    # --- Python Side Processing ---
    py_actual_raw_data = {
        "name": raw_data_for_go["name"],
        "age": Decimal(raw_data_for_go["age"]) # Convert age to Decimal for Python
    }
    try:
        cty_type_instance = parse_type_definition(type_str)
        py_cty_value = cty_type_instance.validate(py_actual_raw_data)
        py_json_dict = py_cty_value.to_json_comparable_dict()
        print(f"  🐍 Python JSON: {json.dumps(py_json_dict, indent=2, ensure_ascii=False)}")
    except Exception as e:
        pytest.fail(f"Python side processing failed for type '{type_str}', data {py_actual_raw_data!r}: {e}", pytrace=False)

    # --- Go Side Processing ---
    go_test_case_data = {
        "name": f"hypothesis_object_{hyp_test_name_suffix}",
        "type_definition": type_str,
        "raw_input": raw_data_for_go
    }
    tmp_yaml_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding='utf-8') as tmp_yaml:
            yaml.dump(go_test_case_data, tmp_yaml)
            tmp_yaml_path = tmp_yaml.name
        print(f"  📝 Temp YAML for Go: {tmp_yaml_path}")

        go_executable = shutil.which("go")
        if not go_executable:
            pytest.skip("Go executable not found, skipping Go generator part.")
            return

        print(f"  🐹 Running Go generator for temp YAML: {tmp_yaml_path}")
        go_gen_cmd = [go_executable, "run", GO_GENERATOR_SCRIPT, "-stdout", tmp_yaml_path]
        go_result = subprocess.run(go_gen_cmd, check=True, capture_output=True, text=True, cwd=str(SCRIPT_DIR), timeout=30)
        if go_result.stderr: print(f"  🐹 Go generator STDERR:\n{go_result.stderr}")
        go_json_str = go_result.stdout
        print(f"  🐹 Go generator STDOUT (JSON):\n{go_json_str}")
        go_json_dict = json.loads(go_json_str)

    except Exception as e: # Broad exception catch for Go phase
        if tmp_yaml_path and os.path.exists(tmp_yaml_path): os.remove(tmp_yaml_path) # Ensure cleanup on error
        pytest.fail(f"Go generator phase failed: {e}", pytrace=False)
    finally:
        if tmp_yaml_path and os.path.exists(tmp_yaml_path):
            os.remove(tmp_yaml_path)
            print(f"  🗑️ Cleaned up temp YAML: {tmp_yaml_path}")

    # --- Compare ---
    print(f"  🔍 Comparing Python and Go JSON outputs for simple object...")
    assert py_json_dict == go_json_dict, \
        f"Mismatch for simple object. Type: {type_str}, Input: {raw_data_for_go!r}\n" \
        f"PY: {json.dumps(py_json_dict, indent=2)}\nGO: {json.dumps(go_json_dict, indent=2)}"
    print("  [✅✅✅] Python and Go outputs MATCH for this simple object case.")


# --- Strategies for Null and Unknown Values ---

st_parsable_type_str = st.sampled_from([
    "string", "number", "bool",
    "list(string)", "list(number)", "list(bool)",
    "map(string)", "map(number)", "map(bool)",
    "object({name=string,age=number})",
    "tuple([string,number,bool])"
])

@st.composite
def st_null_value_with_type(draw):
    type_str = draw(st_parsable_type_str)
    return (type_str, None) # None will represent null in raw_input for YAML

@st.composite
def st_unknown_value_with_type(draw):
    type_str = draw(st_parsable_type_str)
    return (type_str, "__unknown__") # Special string for unknown


# --- Helper for Null/Unknown Comparison ---
def type_str_to_filename_component(type_str: str) -> str:
    """Converts a type string to a safe component for a filename."""
    return type_str.replace('(', '_').replace(')','').replace(',','_').replace('{','_').replace('}','').replace('=','_').replace('[','_').replace(']','_')

def run_comparison_for_special_value(type_str, raw_input_for_go, is_null=False, is_unknown=False):
    print(f"\n--- 🔮 Hypothesis Test Case (Special Value) ---")
    print(f"  Type: {type_str}")
    print(f"  Input for Go: {raw_input_for_go!r}")

    # --- Python Side Processing ---
    try:
        py_cty_type = parse_type_definition(type_str)
        if py_cty_type is None: # Should not happen if parse_type_definition raises ValueError
            pytest.fail(f"Python Type parsing failed for: {type_str}")

        if is_null:
            py_cty_value = CtyValue.null(py_cty_type)
        elif is_unknown:
            py_cty_value = CtyValue.unknown(py_cty_type)
        else:
            pytest.fail("Special value test called without specifying null or unknown.")
            return

        py_json_dict = py_cty_value.to_json_comparable_dict()
        assert py_json_dict["is_null"] == is_null, "Python side is_null flag mismatch"
        assert py_json_dict["is_unknown"] == is_unknown, "Python side is_unknown flag mismatch"
        print(f"  🐍 Python JSON: {json.dumps(py_json_dict, indent=2, ensure_ascii=False)}")

    except Exception as e:
        pytest.fail(f"Python side processing failed for special value. Type: {type_str}, Input: {raw_input_for_go!r}. Error: {e}", pytrace=False)

    # --- Go-cty side (via temp YAML and subprocess) ---
    go_test_case_name = f"hypothesis_{'null' if is_null else 'unknown'}_{type_str_to_filename_component(type_str)}"

    go_test_case_data = {
        "name": go_test_case_name,
        "type_definition": type_str,
        "raw_input": raw_input_for_go
    }

    tmp_yaml_path = None
    try:
        # Use a consistent temporary directory for these YAML files
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, dir=TEMP_DIR_FOR_HYPOTHESIS_YAML, encoding='utf-8') as tmp_yaml:
            yaml.dump(go_test_case_data, tmp_yaml)
            tmp_yaml_path = tmp_yaml.name
        print(f"  📝 Temp YAML for Go: {tmp_yaml_path}")

        go_exe = shutil.which("go")
        if not go_exe:
            pytest.skip("Go executable not found, skipping Go comparison part.")
            return

        cmd = [go_exe, "run", GO_GENERATOR_SCRIPT, "-stdout", tmp_yaml_path] # GO_GENERATOR_SCRIPT defined at top
        go_run_result = subprocess.run(cmd, cwd=str(SCRIPT_DIR), capture_output=True, text=True, timeout=10)

        if go_run_result.returncode != 0:
            pytest.fail(f"Go generator failed for {type_str} with {'null' if is_null else 'unknown'}:\nSTDOUT:\n{go_run_result.stdout}\nSTDERR:\n{go_run_result.stderr}", pytrace=False)

        go_json_str = go_run_result.stdout
        print(f"  🐹 Go generator STDOUT (JSON):\n{go_json_str}")
        go_json_dict = json.loads(go_json_str)

    except json.JSONDecodeError as e:
        pytest.fail(f"Failed to decode JSON from Go for {type_str} with {'null' if is_null else 'unknown'}:\n{go_json_str}\nError: {e}", pytrace=False)
    except subprocess.TimeoutExpired:
        pytest.fail(f"Go generator timed out for {type_str} with {'null' if is_null else 'unknown'}", pytrace=False)
    except Exception as e:
        pytest.fail(f"Error running Go generator for {type_str} with {'null' if is_null else 'unknown'}: {e}", pytrace=False)
    finally:
        if tmp_yaml_path and os.path.exists(tmp_yaml_path):
            os.remove(tmp_yaml_path)
            # print(f"  🗑️ Cleaned up temp YAML: {tmp_yaml_path}") # Can be noisy

    # --- Comparison ---
    print(f"  🔍 Comparing Python and Go JSON outputs for special value ({'null' if is_null else 'unknown'}, type: {type_str})...")
    if py_json_dict != go_json_dict:
        # Rely on pytest's diff for assert
        pass

    assert py_json_dict == go_json_dict, \
        f"Mismatch for special value. Type: {type_str}, Input: {'null' if is_null else '__unknown__'}\n" \
        f"PY: {json.dumps(py_json_dict, indent=2, ensure_ascii=False)}\n" \
        f"GO: {json.dumps(go_json_dict, indent=2, ensure_ascii=False)}"

    print(f"  [✅✅✅] Match for type {type_str}, input: {'null' if is_null else '__unknown__'}")


@given(type_and_null_input=st_null_value_with_type())
def test_hypothesis_null_value_comparison(type_and_null_input):
    type_str, raw_input_for_go = type_and_null_input
    run_comparison_for_special_value(type_str, raw_input_for_go, is_null=True)

@given(type_and_unknown_input=st_unknown_value_with_type())
def test_hypothesis_unknown_value_comparison(type_and_unknown_input):
    type_str, raw_input_for_go = type_and_unknown_input
    run_comparison_for_special_value(type_str, raw_input_for_go, is_unknown=True)
```
