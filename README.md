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
- [ ] Additional public-domain scores
- [ ] Multiple instruments
- [ ] OPL3 mode
- [ ] 4-operator OPL3 voices
- [ ] Stereo placement
- [ ] Percussion channel
- [ ] Score compiler
- [ ] Assembly-generated visualizer
- [ ] PCM / Sound Blaster backend
License
Code is MIT licensed.
Public-domain compositions remain public domain.
Original arrangements and technical examples in this repository may be
used under the repository license.
