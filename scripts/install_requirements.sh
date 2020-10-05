#!/usr/bin/env bash
set -euxo pipefail
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "${DIR}"/..

pip install -U pip wheel
cd ./requirements
pip install --use-feature=2020-resolver -U -r ./install.in -U -r ./dev.in
