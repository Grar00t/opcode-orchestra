#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[1]
src = (root / "showcase/documentary.asm").read_text()
cin = (root / "engine/cinematic.inc").read_text()
story = (root / "documentary/assembly_beneath_wrapper.inc").read_text()
com = (root / "build/documentary.com").read_bytes()
ledger = (root / "build/assembly-documentary.odoc").read_bytes()

required_src = [
    '%include "assembly_beneath_wrapper.inc"',
    'cinema_palette_init', 'cinema_wipe_black',
    'cinema_lower_third', 'cinema_letterbox',
    'opl3_stereo_default', 'opl3_4op_voice_init',
    'OPL_RHYTHM_REG', 'DRUM_BD', 'DRUM_HH',
    'DOC_SCENE2_CS / 100', 'DOC_SCENE3_CS / 100',
    'DOC_SCENE5_CS / 100', 'DOC_SCENE6_CS / 100',
    'mov cx, DOC_SCENE7_CS',
]
for token in required_src:
    assert token in src, token

for i in range(1, 8):
    assert f'scene {i} choreography drift' in src

assert 'DOC_TOTAL_CS  4500' in story
assert len(ledger) > 32 and ledger.startswith(b'ODOC')
assert ledger in com
assert 1024 < len(com) < 65536

assert 'mov cx, 48' in cin
assert 'cinema_frame:' in cin
assert 'cinema_text:' in cin
assert 'cinema_fill_rect:' in cin

print('DOCUMENTARY_EMBEDDED_LEDGER_GATE=PASS')
print('DOCUMENTARY_CINEMATIC_GATE=PASS')
print('DOCUMENTARY_AUDIO_SYNC_GATE=PASS')
print('DOCUMENTARY_RUNTIME_STATIC_GATE=PASS')
print(f'DOCUMENTARY_COM_BYTES={len(com)}')
print(f'DOCUMENTARY_LEDGER_BYTES={len(ledger)}')
