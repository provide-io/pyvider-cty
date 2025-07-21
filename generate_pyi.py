import os
import subprocess
from pathlib import Path

def generate_pyi_files():
    """
    Generates .pyi files for the src directory.
    """
    src_dir = Path("src")
    if not src_dir.is_dir():
        print(f"Error: Directory '{src_dir}' not found.")
        return

    for py_file in src_dir.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue

        pyi_file = py_file.with_suffix(".pyi")
        print(f"Generating {pyi_file} for {py_file}...")
        subprocess.run(
            ["stubgen", "-o", ".", str(py_file)],
            check=True,
        )

if __name__ == "__main__":
    generate_pyi_files()
