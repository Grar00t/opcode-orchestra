#!/usr/bin/env bash
# No source generation, staging, commit, repository creation, or implicit push.
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)
exec "${PYTHON:-python3}" "$root/scripts/publish.py" "$@"
