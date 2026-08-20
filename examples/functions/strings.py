#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""The string functions, including the four where a Python instinct is wrong.

Every function answers what go-cty answers, because that is what Terraform links.
Most of the time that is also what Python would answer; the exceptions are
gathered at the bottom of this file, and in
`docs/user-guide/advanced/going-from-python.md`.
"""

from pathlib import Path
import sys

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from examples.example_utils import configure_for_example, stdlib_call as call  # noqa: E402

configure_for_example()


# --------------------------------------------------------------------------- #
# Case, trimming and padding
# --------------------------------------------------------------------------- #

assert call("upper", "hello") == "HELLO"
assert call("lower", "HELLO") == "hello"
assert call("title", "hello world") == "Hello World"
assert call("trimspace", "  padded  ") == "padded"
assert call("trim", "xxhelloxx", "x") == "hello"
assert call("trimprefix", "https://example.com", "https://") == "example.com"
assert call("trimsuffix", "archive.tar.gz", ".gz") == "archive.tar"

# --------------------------------------------------------------------------- #
# Splitting, joining and searching
# --------------------------------------------------------------------------- #

assert call("split", ",", "a,b,c") == ["a", "b", "c"]
assert call("join", "-", ["a", "b", "c"]) == "a-b-c"
assert call("replace", "a-b-c", "-", "+") == "a+b+c"
assert call("substr", "hello world", 6, 5) == "world"
assert call("chomp", "line\n") == "line"

# --------------------------------------------------------------------------- #
# Length is about graphemes, and is not `length`
# --------------------------------------------------------------------------- #

# `strlen` counts *grapheme clusters*, which is what a person calls a character:
# a flag emoji is one, whatever its code points do.
assert call("strlen", "hello") == 5
assert call("strlen", "🇺🇸") == 1
assert len("🇺🇸") == 2  # Python counts code points

# `length` refuses a string outright, matching go-cty, which leaves strings to
# `strlen`. This is a common surprise, so it raises rather than guessing.
try:
    call("length", "hello")
    raise AssertionError("length does not take a string")
except Exception as exc:
    assert "string" in str(exc).lower()

# --------------------------------------------------------------------------- #
# Regular expressions: RE2, not Python's `re`
# --------------------------------------------------------------------------- #

# The argument order is (pattern, string), which is go-cty's and the reverse of
# `re.match`. Both arguments are strings, so a swapped call still type-checks --
# audit call sites rather than waiting for an exception.
assert call("regex", "[0-9]+", "abc123") == "123"
assert call("regexall", "[0-9]+", "a1b22c333") == ["1", "22", "333"]

# RE2 defines the Perl classes over ASCII only, where Python's are Unicode-aware.
assert call("regexall", r"\w", "²") == []

# `regex` returns the capture groups when there are any, not the whole match.
assert call("regex", "([0-9]+)-([0-9]+)", "10-20") == ["10", "20"]

# --------------------------------------------------------------------------- #
# Where a Python instinct is wrong
# --------------------------------------------------------------------------- #

# `indent` takes a *number of spaces*, not a prefix string, and leaves the first
# line alone -- it is for continuing an already-indented block.
assert call("indent", 2, "a\nb") == "a\n  b"

# `format` is Go's printf, not Python's. `%q` is `ctyjson.Marshal`, and Go's
# `encoding/json` escapes HTML characters by default, so these bytes are what
# reaches a state file.
assert call("format", "%q", "a<b>") == '"a\\u003cb\\u003e"'
assert call("format", "%s has %d", "x", 2) == "x has 2"

print("String function examples ran successfully.")

# 🌊🪢🔚
