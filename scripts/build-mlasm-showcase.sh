#!/usr/bin/env bash
set -euo pipefail

MLASM="/home/a/projects/MLAsm"
ORCH="/home/a/projects/opcode-orchestra"
WIN_OUT="/mnt/c/Users/A/opcode-orchestra-run"

printf '%s\n' '============================================================'
printf '%s\n' ' MLASM x OPCODE ORCHESTRA — ASSEMBLY SHOWCASE'
printf '%s\n' ' no downloads / local build only'
printf '%s\n' '============================================================'

test -d "$MLASM/.git"
test -d "$ORCH/.git"

echo '=== 1. BUILD MLASM ==='
make -C "$MLASM" all >/dev/null

test -s "$MLASM/lib/libmlasm.a"
echo 'MLASM_BUILD=PASS'

echo '=== 2. BUILD HOST BRIDGE ==='
mkdir -p "$ORCH/build" "$ORCH/generated" "$WIN_OUT"

gcc -O2 -mavx2 -mfma \
  -I"$MLASM/include" \
  "$ORCH/bridge/mlasm_scene.c" \
  "$MLASM/lib/libmlasm.a" -lm \
  -o "$ORCH/build/mlasm-scene"
"$ORCH/build/mlasm-scene" "$ORCH/generated/mlasm_scene.inc" \
  | tee "$ORCH/build/mlasm-bridge.log"

grep -q '^MLASM_BRIDGE=PASS$' "$ORCH/build/mlasm-bridge.log"
grep -q '^CPU_SUPPORTED=YES$' "$ORCH/build/mlasm-bridge.log"
echo 'MLASM_BRIDGE_GATE=PASS'

echo '=== 3. BUILD 16-BIT SHOWCASE ==='
nasm -Wall \
  -I "$ORCH/engine/" \
  -I "$ORCH/generated/" \
  -f bin "$ORCH/showcase/mlasm_orchestra.asm" \
  -o "$ORCH/build/mlasm-orchestra.com"

test -s "$ORCH/build/mlasm-orchestra.com"
strings "$ORCH/build/mlasm-orchestra.com" | grep -q 'FAREWELL WRAPPERS'
strings "$ORCH/build/mlasm-orchestra.com" | grep -q 'MLASM TO OPCODE ORCHESTRA'
echo 'ORCHESTRA_MEDIA_GATE=PASS'

echo '=== 4. EXPORT WINDOWS RUN FOLDER ==='
cp -f "$ORCH/build/mlasm-orchestra.com" "$WIN_OUT/assembly.com"
cp -f "$ORCH/build/mlasm-bridge.log" "$WIN_OUT/mlasm-bridge.log"
cp -f "$ORCH/generated/mlasm_scene.inc" "$WIN_OUT/mlasm_scene.inc"

sha256sum "$ORCH/build/mlasm-orchestra.com" \
  | tee "$WIN_OUT/SHA256.txt"
echo
echo 'SHOWCASE_BUILD=PASS'
echo "DOS_ARTIFACT=$WIN_OUT/assembly.com"
echo "BRIDGE_LOG=$WIN_OUT/mlasm-bridge.log"
echo 'RUN_ON_WINDOWS:'
echo '  powershell -ExecutionPolicy Bypass -File C:\Users\A\run-opcode-showcase.ps1'
