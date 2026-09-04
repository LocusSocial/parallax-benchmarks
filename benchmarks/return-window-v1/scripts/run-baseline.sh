#!/bin/sh
set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
benchmark_dir=$(dirname -- "$script_dir")
repository=$(CDPATH= cd -- "$benchmark_dir/../.." && pwd)
workspace=$(mktemp -d "${TMPDIR:-/tmp}/parallax-return-window.XXXXXX")
trap 'rm -rf -- "$workspace"' EXIT HUP INT TERM

rm -rf -- "$workspace"
python3 "$script_dir/prepare.py" --arm baseline "$workspace" >/dev/null

echo "Visible tests (expected: PASS)"
(cd "$workspace" && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v)

echo
echo "Independent business-goal oracle (seeded baseline; failures are expected)"
python3 "$script_dir/score.py" "$workspace"
