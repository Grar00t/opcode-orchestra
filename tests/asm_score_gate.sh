#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/songs/wrapper_ledger_theme.asm"
TMP="$(mktemp --suffix=.asm)"
OUT="$(mktemp --suffix=.com)"
trap 'rm -f "$TMP" "$OUT"' EXIT

sed 's/SCORE_BEGIN 2400/SCORE_BEGIN 2399/' "$SRC" > "$TMP"

if nasm -Wall -I "$ROOT/engine/" -f bin "$TMP" -o "$OUT" >/dev/null 2>&1; then
    echo "ASM_SCORE_NEGATIVE_GATE=FAIL"
    exit 1
fi

echo "ASM_SCORE_NEGATIVE_GATE=PASS"
