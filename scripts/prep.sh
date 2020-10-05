#!/usr/bin/env bash
# Autoformat and test
set -euxo pipefail
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "${DIR}"/

./autoformat.sh
./test.sh
