#
# env.sh
#

ENV_SCRIPT_DIR=$(dirname ${0})

CWD=$(pwd)

cd ${ENV_SCRIPT_DIR}

uv venv
uv sync --all-groups --dev

source .venv/bin/activate

export PYTHONPATH=$(pwd)/src:$(pwd)
export PATH=$(pwd)

cd ${CWD}
