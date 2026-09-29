#!/usr/bin/env python3
"""Binary rejection tests; valid bytes originate in the NASM build."""
import hashlib
from pathlib import Path
import struct
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import artifacts as a
import build

class Artifacts(unittest.TestCase):
    def test_valid(self):
        for target in build.TARGETS:
            if target != 'mlasm':
                with self.subTest(target=target):
                    build.verify(target)

    def test_target_feature_mutation(self):
        path = build.ROOT / 'build/b567.com'
        data = path.read_bytes()
        fields = list(a.MANIFEST.unpack(data[-a.MANIFEST.size:]))
        fields[4] ^= 2  # A valid feature bit, but not this target's contract.
        changed = data[:-a.MANIFEST.size] + a.MANIFEST.pack(*fields)
        a.com(changed, build.source_hash('b567'))
        with patch.object(a, 'read', return_value=changed):
            with self.assertRaisesRegex(a.FormatError, 'target contract'):
                build.verify('b567')

    def test_dataset_truncation_and_corruption(self):
        data = (build.ROOT / 'build/wledger-dataset.bin').read_bytes()
        for length in range(len(data)):
            with self.assertRaises(a.FormatError):
                a.dataset(data[:length])
        for offset in (0, 8, 10, 12, len(data) - 1):
            changed = bytearray(data)
            changed[offset] ^= 1
            with self.assertRaises(a.FormatError):
                a.dataset(changed)
        with self.assertRaises(a.FormatError):
            a.dataset(data + b'\0')

    def test_ledger_truncation_and_corruption(self):
        data = (build.ROOT / 'build/assembly-documentary.odoc').read_bytes()
        for length in range(len(data)):
            with self.assertRaises(a.FormatError):
                a.ledger(data[:length])
        for offset, value in ((0, 0), (4, 2), (6, 255), (12, 0), (14, 3), (15, 0), (16, 4), (len(data)-1, 0)):
            changed = bytearray(data)
            changed[offset] = value
            with self.assertRaises(a.FormatError, msg=str(offset)):
                a.ledger(changed)
        with self.assertRaises(a.FormatError):
            a.ledger(data + b'\0')

    def test_score(self):
        data = struct.pack('<4H', 1023, 65535, 65535, 0)
        a.score(data, 65535)
        for bad in (b'', data[:-1], data + b'\0' * 4, struct.pack('<4H', 1024,1,65535,0),
                    struct.pack('<4H', 1,0,65535,0)):
            with self.assertRaises(a.FormatError):
                a.score(bad, 65535)
        with self.assertRaises(a.FormatError):
            a.score(data, 1)

    def test_media(self):
        data = bytes((1, 7, 5, 0, 0, 0, 0, 15, 1, 1, 65, 0))
        a.media(data)
        for length in range(len(data)):
            with self.assertRaises(a.FormatError):
                a.media(data[:length])
        for bad in (b'\xff', b'\0\0', bytes((5,0,0,0,0,1,0,0,0))):
            with self.assertRaises(a.FormatError):
                a.media(bad)

    def test_manifest(self):
        data = (build.ROOT / 'build/documentary.com').read_bytes()
        a.com(data, build.source_hash('documentary'))
        for length in range(len(data)):
            with self.assertRaises(a.FormatError):
                a.com(data[:length])
        for offset in (0, 100, len(data)-1, len(data)-136):
            changed = bytearray(data)
            changed[offset] ^= 1
            with self.assertRaises(a.FormatError):
                a.com(changed)
        with self.assertRaises(a.FormatError):
            a.com(data, b'\0' * 32)
        fields = list(a.MANIFEST.unpack(data[-136:]))
        for index, value in ((1,2), (2,135), (4,128), (5,9), (6,65535), (7,65535), (8,1)):
            changed = fields.copy()
            changed[index] = value
            with self.assertRaises(a.FormatError):
                a.com(data[:-136] + a.MANIFEST.pack(*changed))
        # Rehash a malformed ledger: inner parser must still reject it.
        body = bytearray(data[:-136])
        body[fields[6] + 14] = 3
        fields[11] = hashlib.sha256(body).digest()
        fields[10] = hashlib.sha256(body[fields[6]:fields[6]+fields[7]]).digest()
        with self.assertRaises(a.FormatError):
            a.com(bytes(body) + a.MANIFEST.pack(*fields))

if __name__ == '__main__':
    unittest.main(verbosity=2)
