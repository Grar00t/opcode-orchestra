# Build and verification

## Prerequisites

Core: GNU Make >=4.3, NASM, Python >=3.10. Host checks additionally use Bash,
ShellCheck and, for the Linux showcase, x86-64 Linux with GNU `ld`.
The reference audit used NASM 2.16.01, Make 4.4.1, GCC 14.2, Clang 17,
Python 3.13.5, ShellCheck 0.9.0, actionlint 1.7.7, Unicorn 2.1.4, and DOSBox
0.74-3. This is an inventory, not a claim of compatibility with every version.

On Debian/Ubuntu, the package prerequisites can be installed with:

```sh
sudo apt-get update
sudo apt-get install --no-install-recommends -y nasm make python3 python3-venv bash shellcheck binutils clang dosbox
```

Run all subsequent commands from the repository root. Tool variables identify
one executable, not a shell fragment: `NASM`, `PYTHON`, `CC`, and `DOSBOX`.
Their selection and the operating system are trusted. A malicious compiler is
outside the in-repository threat boundary.

## Core and host commands

```sh
make clean
make
make verify
make verify-future
make -j4 check
make reproducible
make inspect
bash scripts/publish-repo.sh --check
```

`verify-all` builds every core artifact, runs compile rejection/acceptance tests
and independent binary parsers. `check` adds Python AST parsing, Bash syntax,
ShellCheck, isolated shell/filesystem behavior tests, and Linux ELF execution.
Existing `verify-media`, `verify-score`, `verify-dataset`,
`verify-documentary-ledger`, and `verify-documentary` remain available.
Individual test scripts fail nonzero on errors; negative compilation tests
require the expected diagnostic, not merely any failing assembler command.

`clean` removes only the repository's `build/` and refuses a symlink at that
boundary. It does not clean an external MLAsm checkout or private voice files.
The containing checkout and parent directories must not be concurrently
replaced by an attacker.

## Scripted x86 instruction tests

The optional Linux x86-64 test wheel is hash-pinned, not a runtime dependency:

```sh
python3 -m venv .audit-tools
.audit-tools/bin/python -m pip install --require-hashes --only-binary=:all: -r tests/requirements-cpu.txt
make verify-cpu PYTHON="$PWD/.audit-tools/bin/python"
```

These tests execute assembled instructions with scripted I/O, interrupt, and
clock responses. They test actual branch behavior, register preservation,
framebuffer bounds, decoder truncation, failure propagation, DMA arithmetic,
IRQ cleanup, and device-register ordering. They do not emulate electrical bus
timing or an FM synthesizer.

## Optional C bridge

Supply an inspected local MLAsm checkout, then run:

```sh
test -n "$MLASM_DIR"
make verify-bridge
```

The CI reference is `Grar00t/MLAsm` commit
`16e5598ad8b4870f95cf19b9f413050b87cffd34`. The script rebuilds its static library
with explicit AVX2/FMA flags. It compiles this repository's bridge with strict
warnings-as-errors, runs the real library twice, compares NASM output, and
builds `build/mlasm.com`. It does not copy or execute files on Windows.
`tests/bridge_contracts.py` additionally compiles a fault-injecting double against
the real header with Clang address/undefined/float-cast sanitizers. That double
is test-only; passing it does not validate the internals of the external library.

## DOS execution

```sh
make verify-emulator
python3 tests/dosbox_execution.py --quick
```

The full target requires DOSBox and NASM, runs the built binaries without
modifying them, and checks guest DOS exit status, BIOS video mode, the IRQ7
vector and PIC mask before/after. The optional MLAsm program is included only
when built. Each case has a 150-second host timeout. The quick command excludes
the 67-, 45-, and 24-second declared-score programs. Headless audio is disabled;
device emulation still runs. Fixed emulated CPU cycles are a configuration, not
a physical bus/timing guarantee.

## Reproducibility policy

`make reproducible` copies only public core source paths into two fresh temporary
roots, varies `SOURCE_DATE_EPOCH`, runs parallel `verify-all` in both, and compares
all 13 core `.com`, `.bin`, and `.odoc` files including aliases. Identical inputs
and toolchain must produce identical bytes. Paths, wall-clock timestamps, Git
commit metadata, and voice assets do not enter the manifest.

The source digest includes the target source, all engine includes, the build and
parser scripts, Makefile, and applicable ledger/generated-scene input. Therefore
a comment in an engine include intentionally changes the manifest digest even
when instruction bytes do not change. The optional C library, host ELF linker,
APT repositories, and cross-version NASM behavior are not covered by this
same-toolchain core reproducibility claim. CI records versions but is not a
fully hermetic package snapshot.

## Verification matrix

| Layer | Command/evidence | Does not establish |
|---|---|---|
| Source syntax | `verify-syntax`, `verify-shell` | Hardware execution or absence of all defects |
| NASM invariants | `verify-contracts` | Semantic correctness of every legal composition |
| Static binary layout | `verify-all`, `inspect` | Audio, elapsed wall time, source truth, authenticity |
| Scripted instructions | `verify-cpu` | Physical hardware, actual bus delays, full DOS |
| C/ELF execution | `verify-bridge`, `verify-linux` | External-library correctness under every input |
| Isolated build identity | `reproducible` | Cross-toolchain identity or supply-chain authenticity |
| DOS emulation | `verify-emulator` | DOSBox-X equivalence, listening, frame appearance, physical compatibility |
| Audio capture | Saved PCM/FM capture with device/config/hash | Human perception or real-card behavior |
| Human listening | Recorded listener, passage, observations | Automated timing/electrical proof |
| Physical hardware | Identified card/system, measured traces, cleanup receipt | Compatibility with untested cards |

## Manual acceptance requirements

Before a hardware/audio release, record the exact commit, artifact hash, CPU,
DOS version, card/chip revision, base/IRQ/DMA routing, and emulator version where
applicable. Do not run the PCM demo on a shared DMA/IRQ configuration.

Run each score and record wall-clock start/end separately from declared runtime.
Capture the OPL stereo channels and PCM demonstration to a private output;
inspect duration, non-silence, clipping, left/right routing, key-off tails and
missing/repeated notes. Have a listener document the specific checked passages.
An audible result must not be inferred from a receipt or nonempty WAV alone.

On physical hardware, measure address/data write delays and DSP reset hold time;
verify the DMA page/address/count and IRQ acknowledgement sequence with suitable
instrumentation. Exercise missing-card, wrong-routing and timeout cases. Confirm
that no DMA continues after return and that vectors/masks/video mode are restored.
Inspect actual VGA frames and palette transitions, including clipped boundaries.
Record results per device, not as a general hardware guarantee.
