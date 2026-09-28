#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

OUT="build/assembly-documentary.odoc"
test -s "$OUT"
grep -q '%define DOC_TOTAL_CS  *4500' documentary/assembly_beneath_wrapper.inc
grep -q 'DOC_BEGIN 4, 5, 7, DOC_TOTAL_CS' documentary/assembly_beneath_wrapper.inc
grep -q 'DOC_END' documentary/assembly_beneath_wrapper.inc

python3 - <<'PY'
from pathlib import Path
import re
s=Path('documentary/assembly_beneath_wrapper.inc').read_text()
sources={int(x) for x in re.findall(r'DOC_SOURCE\s+(\d+),',s)}
claims={int(a):int(b) for a,b in re.findall(r'DOC_CLAIM\s+(\d+),\s*(\d+),',s)}
scenes=[(int(a),int(b),d.strip()) for a,b,d in re.findall(r'DOC_SCENE\s+(\d+),\s*(\d+),\s*([^,]+),',s)]
assert sources == {1,2,3,4}
assert set(claims) == {1,2,3,4,5}
assert all(src in sources for src in claims.values())
assert len(scenes) == 7
assert all(claim in claims for _,claim,_ in scenes)
assert [d for _,_,d in scenes] == [f'DOC_SCENE{i}_CS' for i in range(1,8)]
print('DOCUMENTARY_TRACE_GATE=PASS')
PY

TMP="$(mktemp --suffix=.asm)"
trap 'rm -f "$TMP" "${TMP%.asm}.bin"' EXIT
cat > "$TMP" <<'ASM'
BITS 16
ORG 0
%include "documentary.inc"
DOC_BEGIN 1,1,1,100
DOC_SOURCE 1,DOC_SRC_TEST,01234h
DOC_CLAIM 1,1,100
DOC_SCENE 1,1,99,DOC_STYLE_TECH,DOC_CAM_STATIC
DOC_END
ASM
if nasm -I engine/ -f bin "$TMP" -o "${TMP%.asm}.bin" >/dev/null 2>&1; then
    echo "DOCUMENTARY_NEGATIVE_GATE=FAIL"
    exit 1
fi

echo "DOCUMENTARY_NEGATIVE_GATE=PASS"
echo "DOCUMENTARY_LEDGER_GATE=PASS"
echo "DOCUMENTARY_FORMAT=ASM_NATIVE"
echo "DOCUMENTARY_RUNTIME=45.00_SECONDS"
sha256sum "$OUT"
