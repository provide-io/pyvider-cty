#!/usr/bin/env python3

import os
import re
import subprocess
from pathlib import Path

OUTPUT_DIR = Path("./docs")
BASE_MODULE = "github.com/hashicorp/terraform-plugin-framework"
PKG_MAP = {}  # Store package-to-file mapping


def run_command(command, cwd=None):
    """Run a shell command and return the output."""
    result = subprocess.run(command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
    if result.returncode != 0:
        print(f"Error running {' '.join(command)}: {result.stderr}")
    return result.stdout.strip()


def pre_build_package_map(module_root):
    """Pre-map all packages to markdown filenames."""
    global PKG_MAP
    package_dirs = find_doc_go_files(module_root)

    for pkg_dir in package_dirs:
        go_list_cmd = ["go", "list", "-f", "{{.ImportPath}}", str(pkg_dir)]
        pkg = run_command(go_list_cmd, cwd=module_root)

        if pkg:
            stripped_pkg = re.sub(f"^{BASE_MODULE}/?", "", pkg)
            output_file = f"{stripped_pkg.replace('/', '-') or 'root'}.md"
            PKG_MAP[pkg] = output_file


def resolve_import(pkg):
    """Resolve import paths to correct file paths."""
    if pkg in PKG_MAP:
        return f"[{pkg}](file://{OUTPUT_DIR / PKG_MAP[pkg]})"
    return pkg  # Fallback to plain text if unresolved


def inject_links(markdown, pkg):
    """Inject links for imports and inline references during markdown generation."""
    def replace_import(match):
        full_pkg = match.group(1)
        return f'import "{resolve_import(full_pkg)}"'

    def replace_inline_ref(match):
        full_ref = match.group(1)
        if full_ref.startswith(BASE_MODULE):
            return resolve_import(full_ref)
        return full_ref  # Return as-is if not part of the base module

    # Replace imports and inline references
    markdown = re.sub(r'import "([^"]+)"', replace_import, markdown)
    markdown = re.sub(r'`([^`]+)`', replace_inline_ref, markdown)  # Inline code blocks

    return markdown


def generate_docs(package_dir, module_root):
    """Generate markdown docs for a Go package with doc.go."""
    go_list_cmd = ["go", "list", "-f", "{{.ImportPath}}", str(package_dir)]
    pkg = run_command(go_list_cmd, cwd=module_root)

    if pkg and (package_dir / "doc.go").exists():
        print(f"Generating documentation for {pkg}...")

        stripped_pkg = re.sub(f"^{BASE_MODULE}/?", "", pkg)
        output_file = f"{stripped_pkg.replace('/', '-') or 'root'}.md"

        markdown = run_command(["godocdown", pkg], cwd=module_root)
        markdown = inject_links(markdown, pkg)

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        (OUTPUT_DIR / output_file).write_text(markdown)
        print(f"Saved to {OUTPUT_DIR / output_file}")


def find_doc_go_files(root="."):
    """Find all directories containing doc.go recursively."""
    return [path.parent for path in Path(root).rglob("doc.go")]


def main():
    module_root = Path(run_command(["go", "env", "PWD"])).resolve()
    if not (module_root / "go.mod").exists():
        print("Error: go.mod not found. Ensure you're running this from a Go module.")
        return

    os.environ["GO111MODULE"] = "on"

    # Pre-build the package map to inject accurate links
    pre_build_package_map(module_root)

    package_dirs = find_doc_go_files(module_root)
    for pkg_dir in package_dirs:
        generate_docs(pkg_dir, module_root)

    print(f"\nCross-referenced markdown documentation generated in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
