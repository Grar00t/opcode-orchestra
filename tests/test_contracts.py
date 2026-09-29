#!/usr/bin/env python3
"""NASM success/failure tests. A missing assembler is an error, never a pass."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

class Contracts(unittest.TestCase):
    def compile(self, source, expected=None):
        nasm = os.environ.get('NASM', 'nasm')
        self.assertIsNotNone(shutil.which(nasm), f'required tool not found: {nasm}')
        with tempfile.TemporaryDirectory(prefix='opcode-contract-') as directory:
            source_file = Path(directory) / 'case.asm'
            source_file.write_text(source + '\n%define OO_BUILD_COM 0\n%include "manifest.inc"\nOO_FINALIZE\n')
            result = subprocess.run([nasm, '-w+all', '-Werror', '-I', str(ROOT / 'engine') + '/',
                                     '-f', 'bin', str(source_file), '-o', str(Path(directory) / 'case.bin')],
                                    capture_output=True, text=True, timeout=10)
            if expected is None:
                self.assertEqual(result.returncode, 0, result.stderr)
            else:
                self.assertNotEqual(result.returncode, 0, 'invalid declaration was accepted')
                self.assertIn(expected, result.stderr)

    def test_score(self):
        prefix = '%include "score.inc"\n'
        valid = 'SCORE_BEGIN 65536\nEV 0,65535\nEV 1023,1\nSCORE_END\n'
        self.compile(prefix + valid)
        cases = [
            ('SCORE_BEGIN 1\nEV 1,2\nSCORE_END', 'duration does not match'),
            ('SCORE_BEGIN 1\nEV 1024,1\nSCORE_END', 'F-number 0..1023'),
            ('SCORE_BEGIN 1\nEV -1,1\nSCORE_END', 'F-number 0..1023'),
            ('SCORE_BEGIN 1\nEV 65535,1\nSCORE_END', 'F-number 0..1023'),
            ('SCORE_BEGIN 1\nEV 1,0\nSCORE_END', 'duration must be'),
            ('SCORE_BEGIN 65536\nEV 1,65536\nSCORE_END', 'duration must be'),
            ('SCORE_BEGIN 0\nSCORE_END', 'runtime must be'),
            ('SCORE_BEGIN 1\nSCORE_END', 'no events'),
            ('EV 1,1', 'EV requires'),
            ('SCORE_END', 'SCORE_END requires'),
            ('SCORE_BEGIN 1\nEV 1,1', 'Missing SCORE_END'),
            ('SCORE_BEGIN 1\nSCORE_BEGIN 1', 'Nested SCORE_BEGIN'),
            ('SCORE_BEGIN 1\nEV 1,1\ndb 0\nSCORE_END', 'alignment mismatch'),
        ]
        for source, error in cases:
            with self.subTest(source=source):
                self.compile(prefix + source, error)

    def test_dataset(self):
        prefix = '%include "dataset.inc"\n'
        valid = 'DATASET_BEGIN 1\nDS_SAMPLE 65534,65534,0,1023,65535\nDATASET_END'
        self.compile(prefix + valid)
        cases = [
            (valid.replace('BEGIN 1', 'BEGIN 2'), 'record count'),
            (valid.replace('65534,65534', '65535,65534'), 'section collides'),
            (valid.replace('65534,65534', '65534,-1'), 'step collides'),
            (valid.replace(',0,1023,', ',1024,1023,'), 'previous note'),
            (valid.replace(',0,1023,', ',0,1024,'), 'target note'),
            (valid.replace(',65535', ',0'), 'duration must'),
            (valid.replace('DATASET_END', ''), 'Missing DATASET_END'),
            ('DATASET_BEGIN 65536', 'count must'),
            ('DS_SAMPLE 1,1,1,1,1', 'requires DATASET_BEGIN'),
            ('DATASET_BEGIN 1\nDATASET_BEGIN 1', 'Nested DATASET_BEGIN'),
        ]
        for source, error in cases:
            with self.subTest(source=source):
                self.compile(prefix + source, error)

    def test_documentary(self):
        prefix = '%include "documentary.inc"\n'
        valid = 'DOC_BEGIN 1,1,1,1\nDOC_SOURCE 1,1,65535\nDOC_CLAIM 1,1,100\nDOC_SCENE 1,1,1,1,0\nDOC_END'
        self.compile(prefix + valid)
        self.compile(prefix + valid.replace('1,1,100', '1,1,0'))
        cases = [
            (valid.replace('1,1,100', '1,1,101'), 'confidence'),
            (valid.replace('1,1,100', '1,1,-1'), 'confidence'),
            (valid.replace('SOURCE 1,1', 'SOURCE 0,1'), 'source ID'),
            (valid.replace('SOURCE 1,1', 'SOURCE 1,4'), 'source type'),
            (valid.replace('CLAIM 1,1', 'CLAIM 1,2'), 'Undefined documentary source'),
            (valid.replace('SCENE 1,1', 'SCENE 1,2'), 'Undefined documentary claim'),
            (valid.replace('SCENE 1,1,1,1,0', 'SCENE 1,1,1,6,0'), 'style'),
            (valid.replace('SCENE 1,1,1,1,0', 'SCENE 1,1,1,1,5'), 'camera'),
            (valid.replace('SCENE 1,1,1,1,0', 'SCENE 1,1,0,1,0'), 'scene duration'),
            (valid.replace('BEGIN 1,1,1,1', 'BEGIN 1,1,1,2'), 'runtime mismatch'),
            (valid.replace('BEGIN 1,1,1,1', 'BEGIN 2,1,1,1'), 'source count mismatch'),
            (valid.replace('BEGIN 1,1,1,1', 'BEGIN 256,1,1,1'), 'count must'),
            (valid.replace('DOC_END', ''), 'Missing DOC_END'),
            (valid.replace('DOC_CLAIM', 'DOC_SOURCE 1,1,5\nDOC_CLAIM'), 'Duplicate documentary source'),
            (valid.replace('DOC_SCENE', 'DOC_CLAIM 1,1,90\nDOC_SCENE'), 'Duplicate documentary claim'),
            (valid.replace('DOC_END', 'DOC_SCENE 1,1,1,1,0\nDOC_END'), 'Duplicate documentary scene'),
        ]
        for source, error in cases:
            with self.subTest(source=source):
                self.compile(prefix + source, error)

    def test_hardware(self):
        prefix = '%include "contracts.inc"\n'
        self.compile(prefix + 'REQUIRE_OPL_CHANNEL 8\nREQUIRE_OPL_OPERATOR 21\n'
                     'REQUIRE_OPL_ALLOCATION 3,6,1,1\nREQUIRE_DMA_BUFFER 65535,1\n')
        cases = [
            ('REQUIRE_OPL_CHANNEL 9', 'channel'),
            ('REQUIRE_OPL_CHANNEL -1', 'channel'),
            ('REQUIRE_OPL_OPERATOR 6', 'operator'),
            ('REQUIRE_OPL_OPERATOR 22', 'operator'),
            ('REQUIRE_OPL_ALLOCATION 4,0,0,0', 'OPL'),
            ('REQUIRE_OPL_ALLOCATION 2,0,0,1', 'requires OPL3'),
            ('REQUIRE_OPL_ALLOCATION 3,64,1,0', 'Rhythm and melodic'),
            ('REQUIRE_OPL_ALLOCATION 3,8,0,1', 'Four-op and melodic'),
            ('REQUIRE_DMA_BUFFER 65535,2', '64 KiB'),
            ('REQUIRE_DMA_BUFFER 0,0', 'length'),
            ('REQUIRE_DMA_BUFFER 1048576,1', 'address outside'),
        ]
        for source, error in cases:
            with self.subTest(source=source):
                self.compile(prefix + source, error)

    def test_media(self):
        prefix = 'BITS 16\n%include "vga13.inc"\n%include "font5x7.inc"\n%include "media_ops.inc"\n'
        self.compile(prefix + 'M_TEXT 0,0,255,255,1,"A"\nM_END')
        for body, error in [('M_TEXT 0,0,0,1,2,"A"', 'length mismatch'),
                            ('M_TEXT 0,0,0,0,1,"A"', 'scale must'),
                            ('M_RECT -1,0,1,1,0', 'x must'),
                            ('M_CLEAR 256', 'color must')]:
            with self.subTest(body=body):
                self.compile(prefix + body, error)

if __name__ == '__main__':
    unittest.main(verbosity=2)
