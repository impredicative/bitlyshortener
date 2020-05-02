#!/usr/bin/env bash
# Update the vulture whitelist.
set -euxo pipefail
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "${DIR}"/..

vulture --make-whitelist . >./vulture.txt
