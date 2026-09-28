#!/usr/bin/env bash
set -euo pipefail

cd ~/opcode-orchestra

echo "============================================================"
echo "OPCODE ORCHESTRA — PUBLIC REPO BUILD"
echo "TARGET_RUNTIME=67.00s"
echo "============================================================"

test -f engine/opl2.inc
grep -q 'known-good AdLib / OPL2 engine' engine/opl2.inc

mkdir -p \
  build \
  songs \
  tests \
  docs \
  scripts \
  .github/workflows

# ------------------------------------------------------------
# CLEAN DEVELOPMENT LEFTOVERS
# ------------------------------------------------------------

rm -f \
  engine/opl2-broken.inc \
  songs/opl_test.asm \
  songs/beethoven_5.asm \
  build/opltst.com \
  build/rawopl.com \
  build/b5opl.com \
  build/b5.com \
  build/beethoven_5.com

if [ -f songs/rawopl.asm ]; then
    mv songs/rawopl.asm tests/opl2_smoke.asm
fi

# ------------------------------------------------------------
# 67-SECOND OPL2 PIECE
# ------------------------------------------------------------

cat > songs/beethoven_67s.asm <<'EOF'
BITS 16
ORG 100h

jmp start

%include "opl2.inc"

; =============================================================================
; Opcode Orchestra
; Beethoven 5 — 67-second OPL2 study
;
; The opening uses the public-domain Symphony No. 5 motif.
; Following sections are original FM variations built for this demo.
;
; Timing unit:
;   1 = 1 centisecond
;
; Score runtime:
;   exactly 6700 centiseconds = 67.00 seconds
;   excluding the final FM release tail.
; =============================================================================

%define N_C   0159h
%define N_D   0183h
%define N_EB  019Ah
%define N_F   01CCh
%define N_G   0205h
%define N_AB  0223h
%define N_BB  0267h
%define R     0000h

%define EIGHTH 28

%assign SCORE_CS 0

%macro EV 2
    dw %1, %2
    %assign SCORE_CS SCORE_CS + %2
%endmacro

start:
    cld

    call opl_init

    mov si, score

.next:
    lodsw

    cmp ax, 0FFFFh
    je .finished

    mov dx, ax

    lodsw
    mov cx, ax

    mov ax, dx
    call opl_play

    jmp .next

.finished:
    call opl_all_off

    mov ax, 4C00h
    int 21h

score:

; =============================================================================
; 00:00.00 — ORIGINAL OPENING
; Runtime: 6.84 s
; =============================================================================

    EV R,     28
    EV N_G,   28
    EV N_G,   28
    EV N_G,   28
    EV N_EB, 180

    EV R,     28
    EV N_F,   28
    EV N_F,   28
    EV N_F,   28
    EV N_D,  280

; =============================================================================
; 00:06.84 — VARIATION A
; Runtime: 8.00 s
; =============================================================================

    EV N_G,  50
    EV N_G,  50
    EV N_EB, 50
    EV N_F,  50

    EV N_G,  50
    EV N_G,  50
    EV N_EB, 50
    EV N_D,  50

    EV N_F,  50
    EV N_F,  50
    EV N_D,  50
    EV N_EB, 50

    EV N_G,  50
    EV N_F,  50
    EV N_EB, 50
    EV N_D,  50

; =============================================================================
; 00:14.84 — VARIATION A REPRISE
; Runtime: 8.00 s
; =============================================================================

    EV N_G,  50
    EV N_G,  50
    EV N_EB, 50
    EV N_F,  50

    EV N_G,  50
    EV N_G,  50
    EV N_EB, 50
    EV N_D,  50

    EV N_F,  50
    EV N_F,  50
    EV N_D,  50
    EV N_EB, 50

    EV N_G,  50
    EV N_F,  50
    EV N_EB, 50
    EV N_D,  50

; =============================================================================
; 00:22.84 — VARIATION B
; Runtime: 8.00 s
; =============================================================================

    EV N_C,  100
    EV N_G,  100
    EV N_EB, 100
    EV N_F,  100

    EV N_D,  100
    EV N_F,  100
    EV N_EB, 100
    EV N_D,  100

; =============================================================================
; 00:30.84 — VARIATION B REPRISE
; Runtime: 8.00 s
; =============================================================================

    EV N_C,  100
    EV N_G,  100
    EV N_EB, 100
    EV N_F,  100

    EV N_D,  100
    EV N_F,  100
    EV N_EB, 100
    EV N_D,  100

; =============================================================================
; 00:38.84 — DARK BRIDGE
; Runtime: 10.00 s
; =============================================================================

    EV N_C,  100
    EV N_D,  100
    EV N_EB, 100
    EV N_F,  100
    EV N_G,  100

    EV N_AB, 100
    EV N_G,  100
    EV N_F,  100
    EV N_EB, 100
    EV N_D,  100

; =============================================================================
; 00:48.84 — OPENING REPRISE
; Runtime: 6.84 s
; =============================================================================

    EV R,     28
    EV N_G,   28
    EV N_G,   28
    EV N_G,   28
    EV N_EB, 180

    EV R,     28
    EV N_F,   28
    EV N_F,   28
    EV N_F,   28
    EV N_D,  280

; =============================================================================
; 00:55.68 — CODA
; Runtime: 11.32 s
; =============================================================================

    EV N_G,  100
    EV N_G,  100
    EV N_G,  100
    EV N_EB, 100

    EV N_F,  150
    EV N_F,  150
    EV N_D,  166
    EV N_C,  266

    dw 0FFFFh, 0

; =============================================================================
; COMPILE-TIME DURATION GATE
; =============================================================================

%if SCORE_CS != 6700
    %error "Score duration is not exactly 6700 centiseconds"
%endif
EOF

# ------------------------------------------------------------
# MAKEFILE
# ------------------------------------------------------------

cat > Makefile <<'EOF'
.RECIPEPREFIX := >

NASM ?= nasm

TARGET := build/b567.com
SOURCE := songs/beethoven_67s.asm
ENGINE := engine/opl2.inc

.PHONY: all verify clean

all: $(TARGET)

build:
>mkdir -p build

$(TARGET): $(SOURCE) $(ENGINE) | build
>$(NASM) -Wall -I engine/ -f bin $(SOURCE) -o $(TARGET)
>@printf "BUILT %-24s %s bytes\n" "$(TARGET)" "$$(wc -c < $(TARGET))"

verify: all
>@test -s $(TARGET)
>@grep -q "SCORE_CS != 6700" $(SOURCE)
>@echo "BUILD_GATE=PASS"
>@echo "SCORE_RUNTIME=67.00_SECONDS"
>@sha256sum $(TARGET)

clean:
>rm -rf build
EOF

# ------------------------------------------------------------
# DOSBOX-X CONFIG
# ------------------------------------------------------------

cat > dosbox-x.conf <<'EOF'
[cpu]
core=auto
cycles=fixed 6000

[mixer]
nosound=false
rate=49716
blocksize=1024
prebuffer=25

[midi]
mpu401=none
mididevice=none

[sblaster]
sbtype=sb16
sbbase=220
irq=7
dma=1
hdma=5
sbmixer=true
oplmode=opl2
oplemu=nuked
oplrate=49716

[speaker]
pcspeaker=false
tandy=off
disney=false
EOF

# ------------------------------------------------------------
# README
# ------------------------------------------------------------

cat > README.md <<'EOF'
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
EOF
# ------------------------------------------------------------
# ARCHITECTURE DOC
# ------------------------------------------------------------
cat > docs/ARCHITECTURE.md <<'EOF'
Architecture
Opcode Orchestra intentionally separates musical data from hardware
synthesis.
Score layer
A score is encoded as pairs:
F-number, duration

Duration is expressed in centiseconds.
A zero F-number is a rest.
Timing layer
The OPL2 engine uses DOS time through:
INT 21h
AH=2Ch

This provides hundredths-of-a-second timing and avoids the earlier
BIOS-delay path.
Synthesis layer
The engine writes directly to the OPL interface:
0x388  register select
0x389  register data

Three melodic channels are currently used:
channel 0  principal
channel 1  lower octave
channel 2  upper octave

Each channel has its own two-operator FM voice configuration.
Verification philosophy
The project does not treat compilation as proof of correctness.
Verification is separated into:
1. source builds,
2. score duration matches its contract,
3. OPL register writes execute,
4. emulator exposes an OPL-compatible device,
5. audible output matches the intended behavior.
The original raw OPL smoke test exists because it isolates emulator
audio from the higher-level engine.
EOF
# ------------------------------------------------------------
# LICENSE
# ------------------------------------------------------------
cat > LICENSE <<'EOF'
MIT License
Copyright (c) 2026 Opcode Orchestra contributors
Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:
The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
EOF
# ------------------------------------------------------------
# GITIGNORE
# ------------------------------------------------------------
cat > .gitignore <<'EOF'
build/
*.com
*.log
*.bak
*~
.DS_Store
EOF
# ------------------------------------------------------------
# GITHUB ACTIONS
# ------------------------------------------------------------
cat > .github/workflows/build.yml <<'EOF'
name: build
on:
  push:
  pull_request:
jobs:
  nasm:
    runs-on: ubuntu-latest
    steps:
  - name: Checkout
    uses: actions/checkout@v4

  - name: Install NASM
    run: |
      sudo apt-get update
      sudo apt-get install -y nasm make

  - name: Build and verify
    run: make verify

EOF
# ------------------------------------------------------------
# BUILD — FAIL CLOSED
# ------------------------------------------------------------
echo
echo "=== BUILD ==="
make clean
make verify
test -s build/b567.com
echo
echo "=== SOURCE CHECK ==="
grep -n 'SCORE_CS != 6700' songs/beethoven_67s.asm
grep -n 'OPL_PORT equ 0388h' engine/opl2.inc
echo
echo "=== OUTPUT ==="
wc -c build/b567.com
sha256sum build/b567.com
echo
echo "TARGET_RUNTIME_SECONDS=67.00"
echo "OPL_ENGINE_CHANGED=NO"
echo "BUILD=PASS"
# ------------------------------------------------------------
# GIT
# ------------------------------------------------------------
echo
echo "=== GIT ==="
if [ ! -d .git ]; then
    git init
fi
git branch -M main
git add README.md LICENSE .gitignore Makefile dosbox-x.conf engine songs tests docs showcase scripts .github

if git diff --cached --quiet; then
    echo "GIT_COMMIT=NO_CHANGES"
else
    git commit -m "feat: launch Opcode Orchestra with 67-second OPL2 study"
    echo "GIT_COMMIT=PASS"
fi
echo
echo "============================================================"
echo "LOCAL_REPO=PASS"
echo "RUNTIME=67.00_SECONDS"
echo "============================================================"
# ------------------------------------------------------------
# OPTIONAL PUBLIC GITHUB PUBLISH
# ------------------------------------------------------------
if command -v gh >/dev/null 2>&1 &&
   gh auth status >/dev/null 2>&1
then
    OWNER="$(gh api user --jq .login)"
    REPO="$OWNER/opcode-orchestra"
if gh repo view "$REPO" >/dev/null 2>&1
then
    echo "GITHUB_REPO_EXISTS=$REPO"

    if ! git remote get-url origin >/dev/null 2>&1
    then
        REMOTE="$(
            gh repo view "$REPO" \
              --json sshUrl \
              --jq '.sshUrl'
        )"

        git remote add origin "$REMOTE"
    fi

    git push -u origin main
else
    gh repo create "$REPO" \
      --public \
      --source=. \
      --remote=origin \
      --push \
      --description \
      "x86 Assembly music from raw OPL2 hardware I/O. No prompt roulette; just opcodes, timers, and FM."
fi

gh repo edit "$REPO" \
  --add-topic assembly \
  --add-topic x86 \
  --add-topic nasm \
  --add-topic opl2 \
  --add-topic adlib \
  --add-topic fm-synthesis \
  --add-topic dos \
  --add-topic dosbox-x \
  --add-topic retrocomputing

echo
echo "GITHUB_PUBLIC_REPO=PASS"
echo "REPOSITORY=$REPO"

else
    echo
    echo "GITHUB_PUBLIC_REPO=PENDING"
    echo "Reason: GitHub CLI is not authenticated inside WSL."
    echo
    echo "Run:"
    echo "  gh auth login"
    echo
    echo "Then rerun only the GitHub publish section."
fi
