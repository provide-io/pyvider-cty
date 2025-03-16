#!/usr/bin/env zsh

OUTPUT_DIR="./docs" # Output directory for markdown files

mkdir -p "$OUTPUT_DIR"

# Base module path to strip (e.g., github.com/hashicorp)
BASE_MODULE="github.com/hashicorp/terraform-plugin-framework"

declare -A PKG_MAP # Associative array for mapping package names to files

# Function to generate markdown docs for a package
generate_docs() {
  local dir="$1"

  # Get the package import path
  local pkg
  pkg=$(go list -f '{{.ImportPath}}' "$dir" 2>/dev/null)

  if [[ -n "$pkg" && -f "$dir/doc.go" ]]; then
    echo "Generating documentation for $pkg..."

    # Strip the base module and format as dashed filename
    local stripped_pkg="${pkg#$BASE_MODULE/}"
    stripped_pkg="${stripped_pkg#$BASE_MODULE}" # Handle root case

    # Transform package path to dashed filename
    local output_file
    output_file=$(echo "$stripped_pkg" | sed 's|/|-|g').md
    [[ -z "$output_file" ]] && output_file="root.md"

    # Store package mapping
    PKG_MAP["$pkg"]="$output_file"

    # Generate markdown
    godocdown "$pkg" >"$OUTPUT_DIR/$output_file"
    echo "Saved to $OUTPUT_DIR/$output_file"
  else
    echo "Skipping $dir (no valid Go package or doc.go missing)"
  fi
}

# Recursively find directories with doc.go
find . -type f -name "doc.go" | while read -r file; do
  dir=$(dirname "$file")
  generate_docs "$dir"
done

# Post-process markdown to add cross-references
linkify_docs() {
  for file in "$OUTPUT_DIR"/*.md; do
    echo "Updating links in $file..."

    for pkg in "${!PKG_MAP[@]}"; do
      link="file://$OUTPUT_DIR/${PKG_MAP[$pkg]}"
      # Replace exact package references with links
      sed -i '' "s|\b$pkg\b|[$pkg]($link)|g" "$file"
    done
  done
}

linkify_docs

echo "Cross-referenced markdown documentation generated in $OUTPUT_DIR"
