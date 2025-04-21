#
# pyvider cty env.sh
#

ENV_SCRIPT_DIR=$(dirname ${0})

CWD=$(pwd)

cd ${ENV_SCRIPT_DIR}

uv venv
uv sync --all-groups --dev
uv pip install -e ../pyvider-telemetry
uv pip install -e ../pyvider-core

source .venv/bin/activate

export PYTHONPATH=$(pwd)/src:$(pwd)

alias get-pytest-errors="grep -E '(_ test_|^E)' | sed -E 's/ ?___+__+ /\n*** /g'"

cd ${CWD}
