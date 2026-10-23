#!/bin/sh
set -eu
project=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
python3 "$project/tests/ppc/make_fixtures.py"
python3 "$project/tests/ppc/run_tests.py"
python3 "$project/tests/ppc/probe_original.py"
