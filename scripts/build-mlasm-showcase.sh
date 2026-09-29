#!/usr/bin/env bash
# Optional real MLAsm integration. No downloads and no implicit export.
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)
: "${MLASM_DIR:?Set MLASM_DIR to an inspected local MLAsm checkout}"
cc=${CC:-cc}
python=${PYTHON:-python3}
command -v "$cc" >/dev/null
command -v "$python" >/dev/null
command -v "${NASM:-nasm}" >/dev/null
test -f "$MLASM_DIR/include/ml_assembly.h"
test -f "$MLASM_DIR/Makefile"
cd -- "$root"
"$python" -c 'import sys; sys.path.insert(0,"scripts"); import build; build.build_directory()'
work=$(mktemp -d "$root/build/.mlasm-XXXXXXXX")
trap 'rm -rf -- "$work"' EXIT
# This rebuilds the external library, not its source. Record external flags/version separately.
make -B -C "$MLASM_DIR" NASM="${NASM:-nasm}" CC="$cc" CPU_FEATURES= \
    ASM_FLAGS='-f elf64' CC_FLAGS='-std=c99 -Wall -Wextra -O2 -mavx2 -mfma' lib/libmlasm.a
"$cc" -std=c11 -O2 -Wall -Wextra -Wpedantic -Wconversion -Wshadow -Werror \
    -I "$MLASM_DIR/include" "$root/bridge/mlasm_scene.c" \
    "$MLASM_DIR/lib/libmlasm.a" -lm -o "$work/mlasm-scene"
"$work/mlasm-scene" "$work/mlasm_scene.inc" > "$work/bridge.log"
"$work/mlasm-scene" "$work/repeat.inc" > "$work/repeat.log"
cmp "$work/mlasm_scene.inc" "$work/repeat.inc"
test ! -L "$root/build/generated"
mkdir -p -- "$root/build/generated"
mv -f -- "$work/mlasm_scene.inc" "$root/build/generated/mlasm_scene.inc"
mv -f -- "$work/mlasm-scene" "$root/build/mlasm-scene"
mv -f -- "$work/bridge.log" "$root/build/mlasm-bridge.log"
"$python" scripts/build.py build mlasm
"$python" scripts/build.py verify mlasm
printf '%s\n' 'MLASM_INTEGRATION=PASS EXPORT=NOT_REQUESTED'
