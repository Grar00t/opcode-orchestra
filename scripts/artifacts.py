#!/usr/bin/env python3
"""Bounded binary-format readers. Hashes prove consistency, not authenticity."""
from __future__ import annotations
import argparse
import hashlib
from pathlib import Path
import struct
import sys

MANIFEST = struct.Struct('<4sHHIIHHHH32s32s32s16s')
CONTRACT = b'OO-BUILD-1'.ljust(16, b'\0')
MAX_FILE = 1024 * 1024

class FormatError(ValueError):
    """An artifact violates its declared format."""

def need(condition: bool, message: str) -> None:
    if not condition:
        raise FormatError(message)

def read(path: Path) -> bytes:
    with path.open('rb') as stream:
        data = stream.read(MAX_FILE + 1)
    need(len(data) <= MAX_FILE, 'artifact exceeds 1 MiB inspection limit')
    return data

def score(data: bytes, runtime: int) -> dict[str, int]:
    need(len(data) >= 8 and len(data) % 4 == 0, 'score: invalid record layout')
    events = list(struct.iter_unpack('<HH', data))
    need(events[-1] == (65535, 0), 'score: missing final sentinel')
    need(all(0 <= n <= 1023 and d > 0 for n, d in events[:-1]),
         'score: invalid note/duration or early sentinel')
    total = sum(d for _, d in events[:-1])
    need(total == runtime, 'score: declared duration mismatch')
    return {'records': len(events) - 1, 'declared_cs': total}

def dataset(data: bytes) -> dict[str, int]:
    need(len(data) >= 14, 'dataset: truncated header')
    magic, version, size, count = struct.unpack_from('<8sHHH', data)
    need(magic == b'OOASMD1\0' and version == 1 and size == 10,
         'dataset: unsupported header')
    need(count > 0 and len(data) == 14 + (count + 1) * 10,
         'dataset: count/size mismatch')
    rows = list(struct.iter_unpack('<5H', data[14:]))
    need(rows[-1] == (65535,) * 5, 'dataset: final sentinel mismatch')
    need(all(s < 65535 and t < 65535 and p <= 1023 and n <= 1023 and d > 0
             for s, t, p, n, d in rows[:-1]), 'dataset: invalid record')
    return {'records': count}

def ledger(data: bytes) -> dict[str, int]:
    need(len(data) >= 14, 'ledger: truncated header')
    magic, version, ns, nc, nn, runtime = struct.unpack_from('<4s5H', data)
    need(magic == b'ODOC' and version == 1, 'ledger: unsupported header')
    need(all(1 <= n <= 255 for n in (ns, nc, nn)) and runtime > 0,
         'ledger: invalid counts/runtime')
    ids: dict[int, set[int]] = {1: set(), 2: set(), 4: set()}
    offset, total = 14, 0
    while offset < len(data):
        kind = data[offset]
        if kind == 255:
            need(offset + 1 == len(data), 'ledger: trailing bytes after sentinel')
            need(tuple(len(ids[k]) for k in (1, 2, 4)) == (ns, nc, nn),
                 'ledger: count mismatch')
            need(total == runtime, 'ledger: runtime mismatch')
            return {'sources': ns, 'claims': nc, 'scenes': nn, 'declared_cs': total}
        need(kind in ids, 'ledger: unknown record type')
        size = {1: 5, 2: 4, 4: 7}[kind]
        need(offset + size <= len(data), 'ledger: truncated record')
        record = data[offset:offset + size]
        ident, ref = record[1:3]
        need(ident > 0 and ident not in ids[kind], 'ledger: zero/duplicate ID')
        if kind == 1:
            need(ref in (1, 2, 3), 'ledger: invalid source type')
        elif kind == 2:
            need(ref in ids[1] and record[3] <= 100, 'ledger: claim reference/confidence')
        else:
            duration = int.from_bytes(record[5:7], 'little')
            need(ref in ids[2] and 1 <= record[3] <= 5 and record[4] <= 4 and duration > 0,
                 'ledger: invalid scene')
            total += duration
        ids[kind].add(ident)
        offset += size
    raise FormatError('ledger: missing sentinel')

def media(data: bytes) -> dict[str, int]:
    offset, count = 0, 0
    # Opcode definitions are the v2 NASM byte contract, not text matching.
    sizes = {1: 2, 2: 6, 3: 8, 4: 10}
    while offset < len(data):
        op = data[offset]
        if op == 0:
            need(offset + 1 == len(data), 'media: trailing data after END')
            return {'records': count}
        if op == 5:
            need(offset + 8 <= len(data), 'media: truncated text header')
            need(data[offset + 6] > 0, 'media: zero text scale')
            size = 8 + data[offset + 7]
        else:
            need(op in sizes, 'media: unknown opcode')
            size = sizes[op]
        need(offset + size <= len(data), 'media: truncated payload')
        offset += size
        count += 1
    raise FormatError('media: missing END')

def com(data: bytes, expected_source: bytes | None = None) -> dict[str, int]:
    need(MANIFEST.size < len(data) <= 64768, 'COM: invalid image size')
    (magic, version, size, runtime, flags, kind, offset, length, reserved,
     source_hash, payload_hash, body_hash, contract) = MANIFEST.unpack(data[-MANIFEST.size:])
    need(magic == b'OOMF' and version == 1 and size == MANIFEST.size and contract == CONTRACT,
         'COM: unsupported manifest')
    need(reserved == 0 and flags & ~127 == 0 and kind in range(5), 'COM: reserved manifest field')
    body = data[:-size]
    need(offset + length <= len(body), 'COM: payload outside body')
    need(hashlib.sha256(body).digest() == body_hash, 'COM: body hash mismatch')
    payload = body[offset:offset + length]
    need(hashlib.sha256(payload).digest() == payload_hash, 'COM: payload hash mismatch')
    if expected_source is not None:
        need(source_hash == expected_source, 'COM: stale source/tool contract')
    if kind == 0:
        need(length == 0 and offset == 0 and runtime == 0, 'COM: unexpected untyped payload')
    elif kind == 1:
        need(flags & 1 != 0, 'COM: score without OPL flag')
        score(payload, runtime)
    elif kind == 2:
        need(ledger(payload)['declared_cs'] == runtime, 'COM: ledger runtime mismatch')
    elif kind == 3:
        need(flags & 8 != 0 and runtime == 0, 'COM: invalid media flags/runtime')
        media(payload)
    else:
        need(flags & 4 != 0 and runtime == 0 and length > 0, 'COM: invalid PCM payload')
    return {'bytes': len(data), 'declared_cs': runtime, 'features': flags,
            'payload_kind': kind, 'payload_offset': offset, 'payload_bytes': length}

def inspect(path: Path, expected_source: bytes | None = None) -> dict[str, int]:
    data = read(path)
    if path.suffix.lower() == '.com':
        return com(data, expected_source)
    if path.suffix == '.odoc':
        return ledger(data)
    if path.suffix == '.bin':
        return dataset(data)
    raise FormatError('unsupported artifact extension')

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('paths', type=Path, nargs='+')
    args = parser.parse_args()
    try:
        for path in args.paths:
            result = inspect(path)
            fields = '\t'.join(f'{key}={result[key]}' for key in sorted(result))
            print(f'{path.name}\t{fields}\tsha256={hashlib.sha256(read(path)).hexdigest()}')
    except (OSError, FormatError) as error:
        print(f'ARTIFACT=FAIL: {error}', file=sys.stderr)
        return 1
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
