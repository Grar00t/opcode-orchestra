# OOMF build manifest, version 1

Canonical `.COM` builds append a 136-byte little-endian trailer after the
executable body. Runtime execution does not parse or authenticate it. `.bin`
and `.odoc` retain their v1 layouts without trailers.

| File-relative trailer offset | Width | Field |
|---|---|---|
| 0 | 4 | ASCII OOMF |
| 4 | u16 | version=1 |
| 6 | u16 | size=136 |
| 8 | u32 | declared runtime in centiseconds; 0 means unspecified |
| 12 | u32 | feature flags |
| 16 | u16 | payload kind |
| 18 | u16 | payload file offset (not offset including PSP) |
| 20 | u16 | payload byte length |
| 22 | u16 | reserved=0 |
| 24 | 32 | SHA-256 of the defined source input sequence |
| 56 | 32 | SHA-256 of the exact payload bytes |
| 88 | 32 | SHA-256 of executable body, excluding trailer |
| 120 | 16 | ASCII OO-BUILD-1 padded with zero bytes |

Feature bits: 0 OPL, 1 OPL3 required, 2 PCM, 3 VGA, 4 PC speaker,
5 declared score/scene timing, 6 interactive. Other bits are rejected.
These are build declarations, not successful capability-probe results.

Payload kinds: 0 none, 1 score, 2 ODOC ledger, 3 media stream, 4 PCM sample.
Kind 0 uses offset/length/runtime zero. Kind-specific validators check the
payload and runtime. The repository verifier additionally requires the target's
exact features/kind, not merely a syntactically legal manifest.

The source hash is SHA-256 over sorted relative UTF-8 path names, each followed
by zero, an eight-byte little-endian byte length, and exact file bytes. Inputs
are defined by `source_paths()` in `scripts/build.py`; timestamps, absolute host
paths, and Git commit metadata are excluded. It deliberately includes all
engine includes, even an include unused by one target, for a conservative
build contract.

NASM's private OOLC locator is 20 bytes: magic, kind u16, features u16,
runtime u32, offset u16, length u16, body_size u32. The build replaces it; an
OOLC artifact is not a finished canonical COM. NASM checks the final COM ceiling
of 64,768 bytes, reserving 512 bytes above PSP+file for the initial stack.
That size check is not a whole-program worst-case stack proof.

Verification checks bounded file size, version, size, reserved bytes, target
contract, body/payload hashes, payload offsets and source hash against the
checkout. Mutating code and recomputing all hashes is not prevented. This is
integrity relative to trusted inputs, not a digital signature, provenance
certificate, legal claim, or protection against a malicious compiler.
