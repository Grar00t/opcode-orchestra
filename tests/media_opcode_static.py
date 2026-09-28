#!/usr/bin/env python3
from pathlib import Path
import re
import sys

src = Path(__file__).resolve().parents[1] / "showcase" / "media_opcode_v2.asm"
text = src.read_text(encoding="ascii")

counts = {"M_CLEAR": 0, "M_PIXEL": 0, "M_HLINE": 0, "M_RECT": 0, "M_END": 0}
errors = []

for raw in text.splitlines():
    line = raw.split(";", 1)[0].strip()
    if not line.startswith("M_"):
        continue
    name, *tail = line.split(None, 1)
    if name not in counts:
        continue
    counts[name] += 1
    if name in ("M_CLEAR", "M_END"):
        continue
    args = [int(x.strip(), 0) for x in tail[0].split(",")]
    if name == "M_PIXEL":
        x, y, color = args
        if not (0 <= x < 320 and 0 <= y < 200 and 0 <= color <= 255):
            errors.append(line)
    elif name == "M_HLINE":
        x, y, width, color = args
        if not (0 <= x < 320 and 0 <= y < 200 and width > 0 and x + width <= 320 and 0 <= color <= 255):
            errors.append(line)
    elif name == "M_RECT":
        x, y, width, height, color = args
        if not (0 <= x < 320 and 0 <= y < 200 and width > 0 and height > 0 and x + width <= 320 and y + height <= 200 and 0 <= color <= 255):
            errors.append(line)

if counts["M_END"] != 1:
    errors.append(f"M_END count={counts['M_END']}")
if counts["M_CLEAR"] < 1:
    errors.append("missing M_CLEAR")

if errors:
    print("MEDIA_STATIC_GATE=FAIL")
    for error in errors:
        print("ERROR", error)
    sys.exit(1)

print("MEDIA_STATIC_GATE=PASS")
print("OP_COUNTS=" + ",".join(f"{k}:{v}" for k, v in counts.items()))
