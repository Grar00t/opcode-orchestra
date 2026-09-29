# Architecture

## Ownership and execution

The canonical musical and documentary data is NASM source. `songs/` contains
OPL F-number/duration records; `datasets/` contains typed example records;
`documentary/` contains source, claim, and scene declarations. Their macros emit
little-endian bytes and reject invalid declarations at assembly time.

`engine/` contains real-mode routines, macro contracts, and data tables. DOS
entry points establish `DS=CS` and clear DF. Programs call device acquisition,
render/play the compiled data, then shut down owned hardware and exit through
DOS. There is no resident service and no IRQ hook left installed intentionally.

`showcase/` has two execution models. All files except `google_script.asm` are
16-bit DOS flat binaries. `google_script.asm` is a separate Linux x86-64 syscall
program; it must be assembled as ELF64 and linked, not run as a DOS `.COM`.
`tests/opl2_smoke.asm` is the retained raw diagnostic, not a capability-aware
application.

## Build boundary

`Makefile` calls `scripts/build.py`, which invokes NASM on the original source
through a small finalizer. NASM owns code generation and payload offsets.
`engine/manifest.inc` emits an internal locator; the host replaces that locator
with a deterministic OOMF manifest containing source/body/payload hashes.
Standalone NASM builds still produce code without that canonical-build manifest.

`build.py` stages output privately inside `build/`, validates it, then atomically
replaces each output. It checks source hashes before and after assembly. A
concurrent source mutation makes the build fail. Alias files are individually
atomic, not an atomic multi-file transaction; verification detects disagreement.

All engine includes are conservative Make dependencies. This may rebuild more
than necessary but prevents omitted transitive include dependencies. Core
builds need neither Git nor an external ML library.

## Components

| Component | Responsibility | Principal verification |
|---|---|---|
| `opl2.inc`, `isa_delay.inc` | Port writes, timer/status probe, three-voice playback, shutdown, DOS clock waits | `verify-cpu`, DOS execution |
| `opl3.inc`, `instruments.inc`, `percussion.inc` | Bank-1 access, routing, 4-op pair 0+3, rhythm operators, four patches | Compile/allocation tests, scripted register traces |
| `sbpcm.inc` | Bounded DSP protocol, DMA1 programming, SB16 routing checks, temporary IRQ ownership, blocking transfer | Scripted fault/completion tests and DOSBox PCM receipt |
| `vga13.inc`, `font5x7.inc`, `cinematic.inc` | Mode lifecycle, clipped drawing, A-Z glyphs, original cinematic drawing | Boundary/DF/state tests; frame appearance is a manual check |
| `media_ops.inc` | NASM media macros and bounded runtime decoder | Negative compile tests, binary parser, truncated execution tests |
| `score.inc`, `dataset.inc`, `documentary.inc` | Canonical DSLs and layouts | Negative NASM tests and independent binary validation |
| `notes.inc`, `fnum_notes.inc` | Integer-Hz and OPL F-number constants respectively | Range/build checks; pitch calibration is not established |
| `pcspeaker.inc` | PIT2 gate/pitch and BIOS-tick waits | Divide-boundary and midnight instruction tests |
| `bridge/` | Optional real MLAsm integration, NASM constant output | Strict compilers, fault double, sanitizers, repeat comparison |
| `scripts/`, `tests/` | Build, parsing, publication policy and layered verification | `check`, `reproducible`, optional test targets |
| `voice/` | Optional local voice script and original text | Stub process/interlock tests; no synthesis or listening claim |
| `.github/workflows/` | Same local gates on a hosted runner | actionlint and the actual run attached to the reviewed commit |

## State model

OPL, VGA, media scratch state, and PCM state are single-instance and non-reentrant.
The program owns its selected devices for its lifetime. OPL shutdown establishes
quiet/reset routing; it does not reconstruct someone else's music. VGA restores
mode/page/ES, not prior pixels or a full arbitrary palette. PCM restores its IRQ
vector and original mask bit and leaves DMA1 masked; it does not restore a
pre-existing transfer. Shared TSR/device ownership is unsupported.

No new runtime library is linked into the DOS programs. Python, Unicorn,
ShellCheck, actionlint, DOSBox, and the optional C dependency are build or test
tools, not DOS runtime dependencies.
