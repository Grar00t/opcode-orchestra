# ASM-native score format

Opcode Orchestra uses NASM source as the canonical score representation.
There is no JSONL score, parser, or conversion layer.

## Contract

```asm
%include "opl2.inc"
%include "score.inc"

score:
    SCORE_BEGIN 2400
    EV N_G, 25
    EV R,   10
    EV N_EB, 50
    SCORE_END
```

`EV pitch, duration` emits two 16-bit words directly into the DOS `.COM` score stream.
Duration is measured in centiseconds.

`SCORE_END` emits the `0xFFFF,0` runtime sentinel and performs compile-time validation.
If the accumulated event duration differs from `SCORE_BEGIN`, NASM rejects the build.
