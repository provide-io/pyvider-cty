#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""JSON, CSV, bytes and timestamps -- the functions that cross a boundary.

Everything here produces or consumes text that leaves the process, so "close
enough to Go" is not close enough: the bytes are compared by Terraform, and a
document Python accepts and Go rejects becomes state Terraform would have
refused.
"""

from decimal import Decimal
from pathlib import Path
import sys

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from examples.example_utils import configure_for_example, stdlib_call as call  # noqa: E402
from pyvider.cty import CtyList, CtyNumber, CtyObject, CtyString  # noqa: E402
from pyvider.cty.types import BytesCapsule  # noqa: E402

configure_for_example()

S, N = CtyString(), CtyNumber()

# --------------------------------------------------------------------------- #
# JSON
# --------------------------------------------------------------------------- #

record = CtyObject(attribute_types={"name": S, "port": N}).validate({"name": "web", "port": 8080})
encoded = call("jsonencode", record)
assert encoded == '{"name":"web","port":8080}'

# No spaces after the separators: this is `encoding/json`, not `json.dumps`,
# and the difference is bytes in a state file.
decoded = call("jsondecode", '{"a": 1}')
assert decoded == {"a": Decimal(1)}

# Go's `encoding/json` escapes HTML characters by default, so a string with a
# tag in it comes out escaped where Python's would not.
assert call("jsonencode", "a<b>") == '"a\\u003cb\\u003e"'

# A byte buffer is base64, which is what `encoding/json` does with a `[]byte`.
assert call("jsonencode", BytesCapsule.validate(b"hi")) == '"aGk="'

# --------------------------------------------------------------------------- #
# CSV
# --------------------------------------------------------------------------- #

# The first row is the header, and every row becomes an object with those keys.
rows = call("csvdecode", "name,port\nweb,8080\ndb,5432")
assert rows == [{"name": "web", "port": "8080"}, {"name": "db", "port": "5432"}]

# Go's reader is strict where Python's `csv` module has no strict mode at all.
# Each of these parses happily in Python and is refused here, because go-cty
# refuses it -- accepting one would build state Terraform rejects.
for malformed in ('"unterminated', 'a,b\n1,2"3', "a,b\n1,2,3", ""):
    try:
        call("csvdecode", malformed)
        raise AssertionError(f"should have refused {malformed!r}")
    except Exception as exc:
        assert "csvdecode" in str(exc)

# --------------------------------------------------------------------------- #
# Bytes
# --------------------------------------------------------------------------- #

buffer = BytesCapsule.validate(b"hello")
assert call("byteslen", buffer) == Decimal(5)

# The third argument is a *length*, not an end index -- go-cty computes
# `end := offset + length`. The two spellings agree whenever the offset is zero,
# which is exactly why getting it wrong is easy to miss.
assert call("bytesslice", buffer, 1, 3) == b"ell"

# The bounds are checked rather than clamped. Python slicing accepts everything:
# a past-the-end range yields a short buffer and a negative one counts back from
# the far end, and neither is what go-cty answers.
assert b"hello"[1:99] == b"ello"
try:
    call("bytesslice", buffer, 1, 99)
    raise AssertionError("go-cty checks the bounds")
except Exception as exc:
    assert "bytesslice" in str(exc)

# --------------------------------------------------------------------------- #
# Timestamps
# --------------------------------------------------------------------------- #

# `timeadd` shifts an RFC3339 instant by a Go duration string, and rounds
# nothing: the instant carries its own nanoseconds even though a `datetime`
# resolves only to microseconds.
assert call("timeadd", "2020-01-02T03:04:05Z", "1h") == "2020-01-02T04:04:05Z"
assert call("timeadd", "2020-01-02T03:04:05Z", "-90m") == "2020-01-02T01:34:05Z"
assert call("timeadd", "0002-01-01T00:00:00Z", "-1ns") == "0001-12-31T23:59:59Z"

# The nanosecond in the timestamp cancels the one in the duration exactly.
assert call("timeadd", "0002-01-01T00:00:00.000000001Z", "-1ns") == "0002-01-01T00:00:00Z"

# `formatdate` uses cty's own token vocabulary -- YYYY, MM, DD and so on -- and
# not Go's reference-layout dates.
assert call("formatdate", "YYYY-MM-DD", "2020-01-02T03:04:05Z") == "2020-01-02"
assert call("formatdate", "hh:mm:ss", "2020-01-02T03:04:05Z") == "03:04:05"

# A Go reference layout is refused rather than returned as literal text, which
# is the one place this library deliberately disagrees with go-cty: returning
# "2006-01-02" unchanged silently produces a wrong date in state.
try:
    call("formatdate", "2006-01-02", "2020-01-02T03:04:05Z")
    raise AssertionError("a Go reference layout is refused here")
except Exception as exc:
    assert "formatdate" in str(exc)

# --------------------------------------------------------------------------- #
# Formatting a list
# --------------------------------------------------------------------------- #

# `formatlist` broadcasts scalars and iterates lists, which is how a set of
# per-item strings is built in configuration.
hosts = CtyList(element_type=S).validate(["a", "b"])
assert call("formatlist", "https://%s/", hosts) == ["https://a/", "https://b/"]

print("Encoding and time function examples ran successfully.")

# 🌊🪢🔚
