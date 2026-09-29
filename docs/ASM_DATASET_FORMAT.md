# NASM dataset format, version 1

All fields are little-endian; no padding or host-native struct layout is used.
The 14-byte header is `OOASMD1` followed by a zero byte, then three u16 fields:
version=1, record_size=10, declared_record_count (1..65535).

A record is five u16 fields: section (0..65534), step (0..65534), previous OPL
F-number (0..1023), target OPL F-number (0..1023), duration_cs (1..65535).
The final sentinel is five `FFFF` words. File length must be exactly
`14 + 10 * count + 10`; there are no trailing bytes.

```asm
%include "dataset.inc"
DATASET_BEGIN 2
    DS_SAMPLE 0, 0, 0, 577, 50
    DS_SAMPLE 0, 1, 577, 0, 50
DATASET_END
```

NASM checks active declaration scope, field ranges, exact count, record byte
alignment and sentinel exclusion. The canonical build finalizer additionally
rejects a missing END. The independent binary parser rejects unsupported
headers, invalid fields, count/size drift, every truncated prefix and trailing
data. A standalone `.bin` has no appended manifest: its original v1 bytes are
preserved. Structural verification alone does not bind it to a particular source
checkout; rebuild and compare hashes when source identity matters.

The dataset is an example-record format. Its existence does not prove a trained
model, a training run, measured quality, or any inference-system capability.
