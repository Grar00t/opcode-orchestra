# Documentary ledger and runtime

The NASM ledger relates declared sources, claims and scenes. A source ID/tag
records an association, not proof that a source is truthful. Confidence is an
author-supplied integer, not a calibrated probability or audit verdict.

## ODOC version 1

The 14-byte header is ASCII `ODOC`, then five little-endian u16 fields:
version=1, source_count, claim_count, scene_count, runtime_cs. Counts are 1..255;
runtime is 1..65535. Records are packed with no padding:

| Type | Bytes | Fields after type |
|---|---|---|
| 1: source | 5 | id u8, source_kind u8, tag u16 |
| 2: claim | 4 | id u8, source_id u8, confidence u8 |
| 4: scene | 7 | id u8, claim_id u8, style u8, camera u8, duration_cs u16 |
| 255: end | 1 | None; must end the file |

IDs are 1..255 and unique within their record type. Referenced sources/claims
must have been declared earlier. Source kind is 1..3; confidence 0..100;
scene duration 1..65535; style 1..5; camera 0..4. NASM rejects invalid ranges,
missing/duplicate IDs, count drift, runtime drift, nested declarations and bad
scope. Canonical finalization rejects a missing END. No ledger checksum was
added to the v1 file itself; hashes are supplied by artifact inspection and the
embedding COM's manifest.

A complete minimal ledger:

```asm
%include "documentary.inc"
DOC_BEGIN 1, 1, 1, 100
DOC_SOURCE 1, DOC_SRC_CODE, 0A31Fh
DOC_CLAIM 1, 1, 100
DOC_SCENE 1, 1, 100, DOC_STYLE_TITLE, DOC_CAM_PUSH
DOC_END
```

## Runtime and embedding

`make documentary-ledger` assembles the standalone `.odoc`.
`make documentary` builds the OPL3/VGA executable and its `docfilm.com` alias.
`verify-documentary` compares the exact bounded embedded ledger against the
standalone bytes and validates both layouts, counts, references and declared
runtime. The audit retained the original 104-byte ledger unchanged.

The cinematic path uses an original 16-entry palette, A-Z 5x7 glyphs, letterbox
and framing primitives, scene drawing and OPL cues. Its spectrum animation is
procedural: it is not a measurement of rendered audio. The repaired spectrum
routine preserves the outer scene loop's BP register. Drawing is clipped to
320x200, but the glyph set is not a complete ASCII renderer.

4,500 declared centiseconds is a scene-budget contract. DOS scheduling,
rendering and device-write overhead are not subtracted from that budget.
A matching ledger does not establish an exact 45-second measured film, the
truth of documentary claims, audible synthesis, or visual quality.
