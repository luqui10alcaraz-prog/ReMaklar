#!/bin/sh
set -eu
project=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
gcc -m32 "$project/tests/ppc/probe_low_mapping.c" -o "$project/build/probe-low-mapping"
"$project/build/probe-low-mapping"
