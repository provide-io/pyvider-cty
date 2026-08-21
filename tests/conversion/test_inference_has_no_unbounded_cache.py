#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Inferring a type from a raw value leaves nothing behind at module scope.

`raw_to_cty` once kept a process-global dict keyed by every distinct primitive
it had ever seen, so a long-lived provider process grew by one entry per unique
string in every configuration it touched. The singleton type table is the only
module-level dict allowed to change, and it is bounded by the number of
primitive types.
"""

from pyvider.cty.conversion import infer_cty_type_from_raw, raw_to_cty


def _module_dict_sizes() -> dict[str, int]:
    return {
        name: len(obj)
        for name, obj in vars(raw_to_cty).items()
        if isinstance(obj, dict) and name != "_SINGLETONS"
    }


def test_unique_primitives_do_not_accumulate_at_module_scope() -> None:
    infer_cty_type_from_raw(["warm-up"])  # let lazy singletons settle
    before = _module_dict_sizes()
    for i in range(500):
        infer_cty_type_from_raw([f"unique-{i}", i, float(i)])
    assert _module_dict_sizes() == before
