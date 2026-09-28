#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
checks = {
    "OPL3_REGISTER_GATE": (root / "engine/opl3.inc", ["OPL3_PORT_B equ 038Ah", "mov al, 05h", "mov al, 04h"]),
    "STEREO_ROUTE_GATE": (root / "engine/opl3.inc", ["OPL3_PAN_LEFT", "OPL3_PAN_RIGHT", "OPL3_PAN_BOTH"]),
    "FOUR_OP_REGISTER_GATE": (root / "engine/opl3.inc", ["opl3_4op_enable_pair0", "opl3_4op_voice_init", "opl3_4op_key_on"]),
    "RHYTHM_REGISTER_GATE": (root / "engine/percussion.inc", ["OPL_RHYTHM_REG equ 0BDh", "DRUM_BD", "DRUM_CYM"]),
    "SB16_DSP_GATE": (root / "engine/sbpcm.inc", ["SB_DSP_RESET", "SB_DSP_WRITE", "mov al, 14h"]),
    "DMA_PROGRAMMING_GATE": (root / "engine/sbpcm.inc", ["DMA1_ADDR", "DMA1_COUNT", "DMA1_PAGE", "out DMA_MODE, al"]),
    "INSTRUMENT_BANK_GATE": (root / "engine/instruments.inc", ["INSTR_COUNT equ 4", "instrument_select", "instrument_bell"]),
    "AUDIO_REACTIVE_GATE": (root / "showcase/future_audio.asm", ["call vga_hline", "call opl_play", "call opl_drum_hit"]),
}

failed = False
for name, (path, needles) in checks.items():
    text = path.read_text(encoding="ascii")
    ok = all(n in text for n in needles)
    print(f"{name}={'PASS' if ok else 'FAIL'}")
    failed |= not ok
public_scores = [
    root / "songs/ode_to_joy.asm",
    root / "songs/bach_c_major_fragment.asm",
]
public_ok = all(p.exists() and "public domain" in p.read_text(encoding="ascii").lower() for p in public_scores)
print(f"PUBLIC_DOMAIN_SCORE_GATE={'PASS' if public_ok else 'FAIL'}")
failed |= not public_ok

if failed:
    sys.exit(1)

print("FUTURE_AUDIO_STATIC_GATE=PASS")
