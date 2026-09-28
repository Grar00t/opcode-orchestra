# ASM-native dataset format

Opcode Orchestra can store training/example data directly as NASM source.
There is no JSONL dataset and no dataset-to-Assembly converter.

```asm
%include "dataset.inc"

DATASET_BEGIN 24
DS_SAMPLE 0, 0, R,   N_C, 50
DS_SAMPLE 0, 1, N_C, N_G, 50
DATASET_END
```

Each `DS_SAMPLE` is a fixed 10-byte record:

1. section id (`u16`)
2. step id (`u16`)
3. previous note/F-number (`u16`)
4. target note/F-number (`u16`)
5. duration in centiseconds (`u16`)

The binary header contains magic `OOASMD1`, format version, record size, and declared record count.
`DATASET_END` rejects count drift at NASM compile time.
