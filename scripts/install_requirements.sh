#!/usr/bin/env bash
set -euxo pipefail
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "${DIR}"/..

cd ./requirements
pip install -U -r ./install.txt -r ./dev.in
