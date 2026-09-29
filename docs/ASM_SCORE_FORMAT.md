# NASM score format, version 1

Canonical data is NASM source. Each event emits two little-endian unsigned words:
OPL F-number (0..1023) and duration in centiseconds (1..65535). F-number zero is
a rest. The unique four-byte terminator is `FF FF 00 00`; ordinary events cannot
collide with it. There is no score header inside the event payload. Canonical
COM builds identify its kind, offset, length and declared runtime in OOMF v1.

This complete data-only example compiles without a note-name include:

```asm
%include "score.inc"
SCORE_BEGIN 100
    EV 577, 75
    EV 0, 25
SCORE_END
```

`SCORE_BEGIN` accepts 1..2147483647 total centiseconds, rejects nesting, and
resets the event accumulator. `EV` outside an active score, invalid pitch,
zero/overflowing duration, empty scores, duration drift, and inserted bytes
that violate four-byte record alignment fail compilation. `SCORE_END` closes
the score and emits the sentinel. The canonical build finalizer rejects an
unclosed score; a standalone NASM invocation without that finalizer does not
perform the end-of-file closure check.

The runtime uses DS:SI to load word pairs and stops on the sentinel. This is a
trusted compiled score, not an arbitrary external runtime file parser. The host
binary verifier separately requires exact termination, valid fields and the
manifest's declared total. Full COM size is additionally bounded by the build
ceiling; the u32 runtime range does not imply an unlimited-size COM can exist.

`notes.inc` contains integer-Hz constants for the PC-speaker path.
`fnum_notes.inc` contains OPL F-numbers. These units are not interchangeable.
The existing tuning tables and composition content are retained; this format
specification is not a frequency-calibration certificate.

Compatibility: valid pre-hardening v1 event bytes remain unchanged. Previously
accepted out-of-range/truncated declarations are intentionally rejected. There
is no automatic format migration and no high-level score converter.
