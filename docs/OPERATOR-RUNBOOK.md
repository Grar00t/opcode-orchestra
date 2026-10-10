# Opcode Orchestra operator runbook

This runbook applies to `Grar00t/opcode-orchestra`, **not** the adjacent
Casper, ALLaM, or TokenVampire repositories. No unrelated local checkout is
modified. Every command must be invoked from this repository's root.

## Prepare WSL / Ubuntu

Prerequisites for the core test profile are GNU Make >= 4.3, NASM, Bash and
Python >= 3.10; the host profile adds ShellCheck, a C compiler and GNU binutils.

```bash
sudo apt-get update
sudo apt-get install --no-install-recommends -y \
    git make nasm python3 bash shellcheck binutils clang dosbox

git clone https://github.com/Grar00t/opcode-orchestra.git
cd opcode-orchestra

python3 scripts/lab.py doctor --profile core
python3 scripts/lab.py verify --profile core
```

`doctor` prints a missing prerequisite explicitly; it installs nothing.
Use `python3 scripts/lab.py verify --profile host` for all host gates including
ShellCheck and Linux ELF execution. These are build and emulator-proxy results,
not real sound-card tests.

## Verify profiles

| Profile | What is actually run | Prerequisite boundary |
| --- | --- | --- |
| `core` | `make -j4 verify-all`, `make reproducible`, `make inspect` | NASM/Make/Python/Bash |
| `host` | `make -j4 check`, `make reproducible`, `make inspect` | ShellCheck, C compiler/linker; CPU emulator not included |
| `emulator` | `make -j4 verify-all`, `make verify-emulator`, `make inspect` | DOSBox 0.74-3-compatible command, guest exit/state only |
| `capture` | `make build/oplsmoke.com`, `make verify-audio-capture` | DOSBox-X, WAV/DROv2 capture contract |
| `cpu` | `make -j4 verify-all`, `make verify-cpu` | Unicorn in the selected Python environment |
| `bridge` | `make verify-bridge` | Reviewed local MLAsm tree configured with `MLASM_DIR` |

```bash
python3 scripts/lab.py doctor --profile emulator
python3 scripts/lab.py verify --profile emulator

python3 scripts/lab.py doctor --profile capture
python3 scripts/lab.py verify --profile capture
```

The audio-capture profile proves the exact stereo PCM16/WAV and DROv2
conditions in `tests/dosboxx_audio_capture.py`. It does **not** prove that the
score is aesthetically good, sample-perfect, or compatible with a physical OPL
or Sound Blaster card. The optional `bridge` and `cpu` profiles do not
install packages or fetch MLAsm code automatically. For CPU test wheel setup,
use `tests/requirements-cpu.txt` and the pinned installation procedure in
[BUILD-VERIFICATION.md](BUILD-VERIFICATION.md).

## Play a DOS .COM program

Install DOSBox-X on your machine, and make sure its executable is visible in
`PATH` (or set `DOSBOXX` to the full executable path). Interactive playback
requires a usable graphical desktop. Windows users can build inside WSL and
run DOSBox-X using WSLg; alternatively use a Windows DOSBox-X installation
against the WSL-produced `build/` directory.

```bash
python3 scripts/lab.py play b567
python3 scripts/lab.py play ode
python3 scripts/lab.py play bach
python3 scripts/lab.py play future
python3 scripts/lab.py play docfilm
```

The permitted program names are `b567`, `wledger`, `ode`, `bach`,
`future`, `docfilm`, `media`, `sbpcm`, `oplsmoke`. The operator uses
DOS-friendly 8.3 aliases `future.com` and `docfilm.com` and never accepts an
arbitrary command, argument or script path. The `media` VGA program awaits a
key in DOS. `--stay-open` leaves the emulator window open after the guest
process exits. The Sound Blaster PCM demo requires the configured SB16
IRQ/DMA, which should **never** be assumed on a physical card.

The operator does not synthesize audio. The DOS assembly writes OPL registers;
DOSBox-X provides emulated sound.

## Receipts, CI and limitations

A successful local `verify` creates:

```text
build/operator-core.log
build/operator-core.json
```

The JSON stores the attempted commands, observed exit codes, UTC timestamps,
elapsed seconds, commit SHA if Git is available, working-tree-dirty flag and
SHA-256 of the local log. On failure it records `FAIL`, returns nonzero and
stops executing later gates. These logs are local and ignored by Git. A `PASS`
describes the executed gate **only**, never listening/hardware/compliance proof.
The receipt SHA does not authenticate a third party or prove a claim's truth.

Existing `.github/workflows/build.yml` runs automatically for pushes and PRs.
To rerun on demand: open the repository **Actions > build-and-verify >
Run workflow**, choose the desired branch, and run the workflow. The workflow
uses read-only contents permissions and uploads only intended verification
records; it does not publish releases or push source changes.

The local operator intentionally never cleans the tree, installs packages,
fetches binary models, handles voice references, pushes branches or writes
outside the ignored `build/` directory. The pre-existing `make clean`
remains an explicit, destructive-to-generated-build-only operation.
