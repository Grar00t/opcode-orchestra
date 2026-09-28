# Opcode Orchestra

**Assembly music from raw hardware I/O.**

> Assembly is simple: the CPU does exactly what you tell it.  
> No prompt roulette. No guessed intent. No synthetic stand-ins.  
> Just opcodes, timers, and FM.

Opcode Orchestra is a small x86 Assembly music laboratory built around
direct hardware-style programming.

The current backend talks directly to the AdLib / OPL2 interface at
I/O port `0x388`.

No game engine.  
No DAW.  
No MIDI file playback.  
No generated performer.

The program writes FM synthesis registers itself.

And no synthetic humans were generated during this build.

---

## ASM-native score format

Music is authored directly as NASM source. The Assembly is the data format.
There is no JSONL score and no score-to-Assembly converter.

```asm
SCORE_BEGIN 2400
EV N_G,  25
EV R,    10
EV N_EB, 50
SCORE_END
```

`SCORE_END` emits the runtime sentinel and validates the declared duration at assembly time.
See `docs/ASM_SCORE_FORMAT.md` and `songs/wrapper_ledger_theme.asm`.

---

## ASM-native dataset format

Training/example data can also be authored directly as NASM source.
The dataset is Assembly, not JSONL. NASM emits a fixed-record binary dataset and validates record count at build time.

```asm
DATASET_BEGIN 24
DS_SAMPLE 0, 0, R,   N_C, 50
DS_SAMPLE 0, 1, N_C, N_G, 50
DATASET_END
```

See `docs/ASM_DATASET_FORMAT.md` and `datasets/wrapper_ledger_music_dataset.asm`.

---

## Demo

The primary demo is:

**Beethoven 5 — 67-second OPL2 study**

Runtime:

```text
67.00 seconds

The opening uses the famous public-domain Symphony No. 5 motif.
The remainder is an original set of OPL2 variations created as a
technical demonstration rather than a claim of reproducing the full
orchestral score.
The assembler contains a compile-time duration gate. If the score no
longer totals exactly 6,700 centiseconds, NASM rejects the build.
What this repository demonstrates
- 16-bit x86 NASM
- DOS .COM executables
- direct OPL2 register I/O
- AdLib port 0x388
- operator envelopes
- FM synthesis
- multi-octave layering
- deterministic score timing
- DOSBox-X hardware emulation
- no dependency on MIDI playback
Architecture
score
  |
  v
x86 COM program
  |
  v
engine/opl2.inc
  |
  +--> OPL register writes
  +--> operator envelopes
  +--> note key-on / key-off
  +--> centisecond timing
  |
  v
AdLib / YM3812-compatible FM synthesis

Why Assembly?
High-level tools are useful.
But sometimes the shortest path to understanding a machine is to stop
asking software to infer what you intended and explicitly tell the
hardware what to do.
Here:
OUT 0x388, register
OUT 0x389, value

means exactly that.
No interpretation layer needs to guess the request.
Build
Requirements:
- NASM
- GNU Make
Build:
make

Verify:
make verify

Expected result:
BUILD_GATE=PASS
SCORE_RUNTIME=67.00_SECONDS

The DOS executable is:
build/b567.com

The short filename is intentional for compatibility with classic DOS
8.3 naming.
Run with DOSBox-X
A tested configuration is included in:
dosbox-x.conf

Example:
mount c build
c:
b567.com

The configuration uses:
OPL2
Nuked OPL emulator
49716 Hz OPL rate
PC speaker disabled
MIDI disabled

This keeps the test focused on direct FM synthesis.
Repository layout
opcode-orchestra/
├── engine/
│   ├── opl2.inc
│   ├── notes.inc
│   └── pcspeaker.inc
├── songs/
│   └── beethoven_67s.asm
├── tests/
│   └── opl2_smoke.asm
├── docs/
│   └── ARCHITECTURE.md
├── scripts/
├── build/
├── dosbox-x.conf
├── Makefile
├── LICENSE
└── README.md

build/ is generated and is not committed.
## Current pipeline

```text
ASM dataset -> NASM binary records
ASM score   -> NASM -> x86 .COM -> OPL2
Media Opcode v2 -> VGA Mode 13h
MLAsm bridge -> deterministic scene parameters
```

## Optional local voice

XTTS v2 is supported only as an optional local voice layer. It is not part of the ASM-native core. Public commits contain code and verification metadata only; model weights, speaker references, generated voice WAV files, and downloaded reference audio stay local. See `docs/XTTS-LOCAL-VERIFICATION.md`.

Future Audio Pack

The repository now includes OPL3 mode, stereo routing, a 4-op voice path, OPL rhythm percussion, four switchable OPL instruments, a Sound Blaster 8-bit PCM/DMA backend, two additional public-domain score studies, and an audio-reactive VGA demo. `make verify-future` builds every artifact and runs source-contract gates. Audible hardware/emulator verification remains a separate verification layer. See `docs/FUTURE-AUDIO.md`.


## ASM Documentary Ledger

A documentary can now be described as Assembly source: `source -> claim -> scene -> cut`. NASM compiles the story ledger to `.odoc` and rejects source-count, claim-count, scene-count, confidence, or runtime drift. The canonical story path contains no JSON/JSONL. See `docs/DOCUMENTARY-MODE.md`.

Project rule
A successful build is not proof of correct music.
The project keeps these concepts separate:
COMPILES
MUSICAL TIMING
SYNTHESIS
AUDIBLE OUTPUT

Each needs its own verification.
Roadmap
- [x] Raw OPL2 smoke test
- [x] Known-good OPL2 register writer
- [x] Multi-octave FM voice
- [x] Centisecond timing
- [x] 67-second demonstration
- [x] Compile-time runtime gate
- [x] Additional public-domain scores
- [x] Multiple instruments
- [x] OPL3 mode
- [x] 4-operator OPL3 voices
- [x] Stereo placement
- [x] Percussion channel
- [x] ASM-native score DSL (NASM is the compiler)
- [x] Assembly-generated visualizer
- [x] PCM / Sound Blaster backend
- [x] ASM-native dataset records + negative compile gate
- [x] Media Opcode v2 + VGA text renderer
- [x] MLAsm host bridge
- [x] XTTS local verification receipt (optional/non-ASM)
- [x] ASM documentary source/claim/scene ledger
License
Code is MIT licensed.
Public-domain compositions remain public domain.
Original arrangements and technical examples in this repository may be
used under the repository license.
