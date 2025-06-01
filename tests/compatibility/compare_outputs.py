#!/usr/bin/env python3
# compare_outputs.py
#

import json
import pathlib
import sys

def compare_json_files(file1_path: pathlib.Path, file2_path: pathlib.Path) -> bool:
    """Loads two JSON files and compares their content."""
    try:
        with open(file1_path, 'r') as f1, open(file2_path, 'r') as f2:
            data1 = json.load(f1)
            data2 = json.load(f2)

            if data1 == data2:
                return True
            else:
                print(f"    Mismatch details for {file1_path.name} vs {file2_path.name}:")
                print(f"    --- {file1_path.name} ---")
                json.dump(data1, sys.stdout, indent=2)
                print("\n    --- ---")
                print(f"    --- {file2_path.name} ---")
                json.dump(data2, sys.stdout, indent=2)
                print("\n    --- ---")
                return False
    except FileNotFoundError:
        print(f"  [❗ ERROR]: One or both files not found: {file1_path}, {file2_path}")
        return False
    except json.JSONDecodeError as e:
        print(f"  [❗ ERROR]: JSON decoding error in {file1_path} or {file2_path}: {e}")
        return False

def main():
    script_dir = pathlib.Path(__file__).resolve().parent
    output_base_dir = script_dir / "output"
    all_match = True

    if not output_base_dir.is_dir():
        print(f"[❗ ERROR]: Base output directory not found: {output_base_dir}")
        sys.exit(1)

    test_case_dirs = sorted([d for d in output_base_dir.iterdir() if d.is_dir()])

    if not test_case_dirs:
        print(f"[*] No test case output directories found in {output_base_dir}.")
        sys.exit(0)


    for test_case_dir in test_case_dirs:
        print(f"--- 🧪 Test Case: {test_case_dir.name} ---")

        py_value_path = test_case_dir / "py_value.json"
        go_value_path = test_case_dir / "go_value.json"
        py_type_path = test_case_dir / "py_type.json"
        go_type_path = test_case_dir / "go_type.json"

        # Compare *_value.json files
        print("  Comparing VALUE files...")
        if py_value_path.exists() and go_value_path.exists():
            value_match = compare_json_files(py_value_path, go_value_path)
            if value_match:
                print("  [✅ VALUE]: Match")
            else:
                print("  [❌ VALUE]: Mismatch")
                all_match = False
        else:
            print(f"  [❌ VALUE]: Missing one or both value files.")
            if not py_value_path.exists(): print(f"    [❗ ERROR]: Missing: {py_value_path}")
            if not go_value_path.exists(): print(f"    [❗ ERROR]: Missing: {go_value_path}")
            all_match = False


        # Compare *_type.json files
        print("  Comparing TYPE files...")
        if py_type_path.exists() and go_type_path.exists():
            type_match = compare_json_files(py_type_path, go_type_path)
            if type_match:
                print("  [✅ TYPE]: Match")
            else:
                print("  [❌ TYPE]: Mismatch")
                all_match = False
        else:
            print(f"  [❌ TYPE]: Missing one or both type files.")
            if not py_type_path.exists(): print(f"    [❗ ERROR]: Missing: {py_type_path}")
            if not go_type_path.exists(): print(f"    [❗ ERROR]: Missing: {go_type_path}")
            all_match = False

        print("-" * (20 + len(test_case_dir.name) + 4)) # Print separator + emoji length

    if not all_match:
        print(f"\n[💔💔💔] Overall: One or more test cases FAILED. [💔💔💔]")
        sys.exit(1)
    else:
        print(f"\n[🎉🎉🎉] Overall: All test cases PASSED! [🎉🎉🎉]")
        sys.exit(0)

if __name__ == "__main__":
    main()

# 🐍🌊
