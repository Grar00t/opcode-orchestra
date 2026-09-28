#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/datasets/wrapper_ledger_music_dataset.asm"
BIN="$ROOT/build/wledger-dataset.bin"
TMP="$(mktemp --suffix=.asm)"
BAD="$(mktemp --suffix=.bin)"
trap 'rm -f "$TMP" "$BAD"' EXIT

[ -s "$BIN" ]
[ "$(wc -c < "$BIN")" -eq 264 ]

magic="$(od -An -tx1 -N8 "$BIN" | tr -d ' \n')"
[ "$magic" = "4f4f41534d443100" ]

header="$(od -An -tu2 -j10 -N4 "$BIN" | xargs)"
[ "$header" = "10 24" ]

echo "ASM_DATASET_HEADER_GATE=PASS"
echo "ASM_DATASET_RECORD_SIZE=10"
echo "ASM_DATASET_RECORDS=24"

sed 's/DATASET_BEGIN 24/DATASET_BEGIN 23/' "$SRC" > "$TMP"
if nasm -Wall -I "$ROOT/engine/" -f bin "$TMP" -o "$BAD" >/dev/null 2>&1; then
    echo "ASM_DATASET_NEGATIVE_GATE=FAIL"
    exit 1
fi

echo "ASM_DATASET_NEGATIVE_GATE=PASS"
