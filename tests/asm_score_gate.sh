#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)
exec "${PYTHON:-python3}" "$root/tests/test_contracts.py" Contracts.test_score
