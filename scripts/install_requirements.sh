#!/usr/bin/env bash
set -euxo pipefail
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "${DIR}"/..

cd ./requirements
pip install --use-feature=2020-resolver -U -r ./install.txt -U -r ./dev.in
