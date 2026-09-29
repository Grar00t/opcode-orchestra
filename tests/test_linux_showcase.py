#!/usr/bin/env python3
"""Execute the Linux ELF and inspect permissions; creative text is not audit evidence."""
from pathlib import Path
import struct
import subprocess
import unittest
ROOT = Path(__file__).resolve().parents[1]
BINARY = ROOT / 'build/google-script'

class LinuxShowcase(unittest.TestCase):
    def test_output_and_determinism(self):
        first = subprocess.run([str(BINARY)], capture_output=True, timeout=10, check=True).stdout
        second = subprocess.run([str(BINARY)], capture_output=True, timeout=10, check=True).stdout
        self.assertEqual(first, second)
        self.assertIn(b'SELECTIVE FEAR', first)
        self.assertGreater(len(first), 1000)

    def test_output_failure(self):
        with open('/dev/full', 'wb') as full:
            result = subprocess.run([str(BINARY)], stdout=full, timeout=10)
        self.assertEqual(result.returncode, 1)

    def test_elf_permissions(self):
        data = BINARY.read_bytes()
        self.assertEqual(data[:6], b'\x7fELF\x02\x01')
        phoff = struct.unpack_from('<Q', data, 32)[0]
        size, count = struct.unpack_from('<HH', data, 54)
        stack = False
        executable = False
        for n in range(count):
            kind, flags = struct.unpack_from('<II', data, phoff + n*size)
            if kind == 1:
                self.assertNotEqual(flags & 3, 3, 'writable executable LOAD segment')
                executable |= bool(flags & 1)
            if kind == 0x6474e551:
                stack = True
                self.assertEqual(flags & 1, 0, 'executable stack')
        self.assertTrue(stack and executable)

if __name__ == '__main__':
    unittest.main(verbosity=2)
