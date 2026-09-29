# Changes from 5070ae12d1c955d4320a3b0dffe1f025262302c4

## 2026-09-29 follow-up verification

NASM 3.01 compatibility now keeps warnings-as-errors while allowing the specific
`reloc-abs-word` class required by ordinary 16-bit absolute addresses in flat
DOS binaries. A regression compiles that exact construct. `.gitattributes`
forces LF for executable/source text so Windows checkout policy cannot break
Bash verification or alter source bytes used by deterministic manifests.

A new optional `verify-audio-capture` target uses DOSBox-X `DX-CAPTURE /A /O`
to validate an actual emulated OPL smoke WAV and DROv2 register stream. This is
explicitly not a listening test or physical-hardware certification.

## Runtime repairs

Clipped VGA writes and text origins; restored DF around bulk writes; preserved
the documentary outer-loop register; fixed multi-minute DOS waits and PC-speaker
divisor/midnight handling. Centralized OPL writes and added explicit probing,
mode rejection, routing preservation and full owned-channel shutdown.

The PCM public call now blocks through completion/cleanup, validates the full
buffer/routing contract, checks every DSP write, and temporarily owns/restores
the IRQ vector/mask. Support is intentionally limited to verified protocol
assumptions for SB16 DSP4.x at base220/DMA1/compiledIRQ; it is not a general
BLASTER parser or silent SB1/SB2 fallback.

## Format/build changes

Valid score, dataset and ODOC v1 bytes are preserved. Invalid/truncated/range-
overflowing declarations previously accepted are now rejected. Canonical COM
builds gain the deterministic OOMF v1 trailer. Raw standalone NASM output has
no such trailer and is not accepted as a canonical inspected artifact.

Old Make targets remain. New layered tests, isolated reproducibility, safe
atomic output and 8.3 aliases are provided. The Linux syscall showcase is built
as ELF64 with non-executable stack and separate code/data pages, not as a COM.
No public-domain score was replaced or imported from a recording.

## Host behavior changes

The MLAsm bridge checks library returns, finite/ranged results and all output
operations; generated NASM scene values are retained under the tested library.
Its build script requires an explicit inspected `MLASM_DIR` and no longer copies
to hardcoded Windows locations or invokes PowerShell implicitly.

The old publication script regenerated repository files, staged/committed,
created a public repository and pushed. That destructive implicit behavior is
retired. Default/`--check` now inspects committed HEAD only. Explicit `--push`
requires a clean checkout, matching existing origin and checked outgoing trees.

The voice script requires explicit tools/models, keeps private output confined
to ignored voice/raw, preserves the training interlock, and never exports or
publishes implicitly. Custom legacy output paths are no longer accepted.
Historical voice claims are retained as unverified records, not presented as
new audit evidence.

## Verification limits

The CI workflow is read-only, SHA-pinned and runs the documented layers. Package
sources are not a hermetic snapshot. Scripted instruction execution and DOSBox
receipts do not establish audio quality, exact wall time, physical DMA behavior,
electrical compatibility or production readiness.
