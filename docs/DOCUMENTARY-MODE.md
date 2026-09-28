# Documentary Mode

Opcode Orchestra can describe a documentary as Assembly source.
There is no JSON or JSONL in the canonical story path.

```text
source -> claim -> scene -> cut
```

The documentary ledger is compiled by NASM into a compact `.odoc` binary.
NASM also enforces source/claim/scene counts and total runtime.

## Why this exists

The goal is not to clone another notebook UI. The goal is a source-grounded documentary compiler where every scene can be traced back to an explicit claim and source ID.

## Canonical grammar

```asm
DOC_BEGIN 4, 5, 7, 4500
DOC_SOURCE 1, DOC_SRC_CODE, 0A31Fh
DOC_CLAIM 1, 1, 100
DOC_SCENE 1, 1, 600, DOC_STYLE_TITLE, DOC_CAM_PUSH
DOC_END
```

`4500` means 45.00 seconds because documentary time is measured in centiseconds.
