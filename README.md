# Opcode Orchestra

An Assembly-first x86 music and graphics laboratory. NASM compiles scores,
datasets, documentary ledgers, and DOS programs. The DOS programs use direct
OPL, VGA, and, in a separate demonstration, Sound Blaster DSP/DMA I/O.

Python checks declarations and binary layouts, hashes artifacts, and runs tests;
it does not synthesize or perform the scores. There is no MIDI player, JSON score
format, external media engine, or mandatory model dependency.

## Build

The core requires GNU Make 4.3 or newer, NASM, and Python 3.10 or newer.
The audit exercised NASM 2.16.01; other versions are not thereby certified.
Run from a checkout of this repository:

```sh
make clean
make
make verify
make verify-future
make -j4 check
make reproducible
make inspect
```

`make` builds only `build/b567.com`. `make check` also requires Bash,
ShellCheck, a Linux x86-64 host, and GNU binutils for the separate Linux showcase.
`make verify-all` is the core Assembly/binary/negative-test gate without those
optional host checks. No target treats a missing required tool as a passing test.
Detailed prerequisites and optional tests are in [the build guide](docs/BUILD-VERIFICATION.md).

## Programs and data

| Target | Output | Contract |
|---|---|---|
| `all` | `build/b567.com` | OPL score; 6,700 declared centiseconds |
| `score` | `build/wledger.com` | OPL score; 2,400 declared centiseconds |
| `media` | `build/media-v2.com` | VGA opcode stream; waits for a key |
| `future-audio` | `future-audio.com`, `future.com`, `sbpcm.com`, `ode.com`, `bach.com` in `build/` | OPL3 showcase, separate PCM demonstration, two score studies |
| `documentary-ledger` | `build/assembly-documentary.odoc` | Version-1 typed ledger |
| `documentary` | `build/documentary.com`, `build/docfilm.com` | OPL3/VGA; 4,500 declared centiseconds |
| `dataset` | `build/wledger-dataset.bin` | Version-1 10-byte records |
| `smoke` | `build/oplsmoke.com` | Original direct OPL diagnostic |
| `core` | All of the above | Includes the two identical DOS 8.3 aliases |

`ode.com` and `bach.com` each declare 800 centiseconds. Declared duration is the
sum of score/scene fields, not a measured wall-clock duration. Rendering, I/O,
DOS-clock granularity, and per-event scheduling add error. See [hardware and timing](docs/HARDWARE.md).

## DOS execution

Use a DOS environment with the documented devices, not a protected-mode host
shell. The supplied `dosbox-x.conf` requests SB16 at 220h, IRQ 7, DMA 1 and OPL3.
For an interactive DOSBox-X session from the repository root:

```sh
dosbox-x -conf dosbox-x.conf -c "mount c build" -c "c:" -c "b567.com"
```

`future.com` and `docfilm.com` are 8.3 aliases. OPL3-only programs reject an OPL2
signature; they do not silently substitute a different arrangement. The PCM
demonstration requires the implemented SB16 configuration and returns an error
if detection, transfer, or cleanup fails. Its public playback call is blocking.

`make verify-emulator` uses **DOSBox 0.74-3**, not DOSBox-X, with headless output.
It checks guest exit codes and selected restored state. It does not listen to
sound or inspect rendered frames.

`make verify-audio-capture` is a separate DOSBox-X gate. It runs the raw OPL2
smoke program through `DX-CAPTURE /A /O`, validates stereo PCM16/WAV structure
and sustained non-silence, parses DROv2, and requires channel-0 key-on/key-off
register writes. This establishes emulated synthesized-output capture only; it
does not establish audible quality or physical-card compatibility.

## Optional bridge and voice tools

`bridge/mlasm_scene.c` uses an explicitly supplied MLAsm checkout to generate
small NASM scene constants. The actual integration tested by this audit is
`Grar00t/MLAsm` commit `16e5598ad8b4870f95cf19b9f413050b87cffd34`.
It remains outside the core build. `make verify-bridge` requires `MLASM_DIR`.

`voice/render_xtts_after_training.sh` is optional local tooling, not an
Assembly-native voice implementation. It requires explicit tool/model settings
and an original or authorized speaker input. No voice rendering is performed
by build, CI, reproducibility, or publication checks.
See [voice boundaries](docs/XTTS-LOCAL-VERIFICATION.md).

The publisher is now a non-mutating checker by default:

```sh
bash scripts/publish-repo.sh --check
```

It checks committed `HEAD`, not uncommitted edits. `--push` is explicit and
requires a clean tree and the existing exact repository origin. It never
regenerates files, stages changes, commits, or creates a public repository.
See [security and publication](docs/SECURITY.md).

## Evidence boundaries

Compilation, binary validation, scripted x86 instruction tests, DOS execution,
audio capture, listening, and physical-hardware tests are distinct. A passing
aggregate build target does not combine them into a hardware or audio claim.
[The verification matrix](docs/BUILD-VERIFICATION.md#verification-matrix) specifies
what each target proves. No production-readiness or compliance certification is asserted.

## Documentation

- [Architecture and component map](docs/ARCHITECTURE.md)
- [Build, verification, reproducibility, and manual checks](docs/BUILD-VERIFICATION.md)
- [Assembly conventions and calling contracts](docs/ASSEMBLY-CONVENTIONS.md)
- [Error and exit-code reference](docs/ERROR-CODES.md)
- [OPL, DMA, VGA, speaker, and timing model](docs/HARDWARE.md)
- [Score](docs/ASM_SCORE_FORMAT.md), [dataset](docs/ASM_DATASET_FORMAT.md),
  [documentary ledger](docs/DOCUMENTARY-MODE.md), and [manifest](docs/BINARY-MANIFEST.md) formats
- [Audio direction](docs/AUDIO-DIRECTION.md), [audio backends](docs/FUTURE-AUDIO.md),
  [security](docs/SECURITY.md), [contribution/release checklist](CONTRIBUTING.md),
  and [migration notes](CHANGELOG.md)

Code is distributed under [LICENSE](LICENSE). Existing composition attribution
and original documentary/voice text are retained. A source's stated confidence
or a recorded hash does not independently establish the truth of its claims.
