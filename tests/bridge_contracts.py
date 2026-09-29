#!/usr/bin/env python3
"""Strict C + ASan/UBSan fault injection. Requires the actual MLAsm header.

MLASM_DIR=/path/to/MLAsm CC=clang python3 tests/bridge_contracts.py
OO_BRIDGE_SOURCE is for differential tests against a baseline source only.
"""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
class BridgeContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory=os.environ.get('MLASM_DIR')
        if not directory or not (Path(directory)/'include/ml_assembly.h').is_file():
            raise RuntimeError('MLASM_DIR must contain the real include/ml_assembly.h')
        cc=os.environ.get('CC','clang')
        if not shutil.which(cc): raise RuntimeError(f'required compiler missing: {cc}')
        cls.tmp=tempfile.TemporaryDirectory(prefix='oo-bridge-test-')
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.root=Path(cls.tmp.name);cls.binary=cls.root/'bridge'
        source=os.environ.get('OO_BRIDGE_SOURCE',str(ROOT/'bridge/mlasm_scene.c'))
        flags=['-std=c11','-Wall','-Wextra','-Wpedantic','-Wconversion','-Wshadow',
               '-Wformat=2','-Werror','-fsanitize=address,undefined,float-cast-overflow',
               '-fno-sanitize-recover=all','-fno-omit-frame-pointer','-g',
               '-I',str(Path(directory)/'include')]
        subprocess.run([cc,*flags,'-Dmain=bridge_main','-c',source,'-o',str(cls.root/'bridge.o')],check=True)
        subprocess.run([cc,*flags,str(cls.root/'bridge.o'),str(ROOT/'tests/mlasm_test_double.c'),
                        '-lm','-o',str(cls.binary)],check=True)
    def invoke(self,*args,fault='',stdout=subprocess.PIPE):
        env={**os.environ,'OO_TEST_FAULT':fault,'ASAN_OPTIONS':'detect_leaks=1:halt_on_error=1'}
        return subprocess.run([str(self.binary),*map(str,args)],env=env,stdout=stdout,
                              stderr=subprocess.PIPE,timeout=15)
    def test_valid_and_deterministic(self):
        outputs=[]
        for i,mode in enumerate(('', '', 'round_down')):
            target=self.root/f'valid-{i}.inc'
            result=self.invoke(target,fault=mode)
            self.assertEqual(result.returncode,0,result.stderr.decode())
            outputs.append(target.read_bytes())
        self.assertEqual(outputs[0],outputs[1]);self.assertEqual(outputs[0],outputs[2])
    def test_faults_reject_without_replacing_destination(self):
        faults={'cpu':3,'init':3,'alloc':4,'set_vector':5,'set_matrix':5,
                'matvec':5,'softmax':5,'index':6,'nan':6,'infinity':6,'version':6}
        for fault,code in faults.items():
            with self.subTest(fault=fault):
                target=self.root/f'fail-{fault}.inc';target.write_bytes(b'KEEP')
                result=self.invoke(target,fault=fault)
                self.assertEqual(result.returncode,code,result.stderr.decode())
                self.assertEqual(target.read_bytes(),b'KEEP')
                self.assertNotIn(b'MLASM_BRIDGE=PASS',result.stdout)
    def test_large_finite_values_are_clamped_before_conversion(self):
        target=self.root/'huge.inc';result=self.invoke(target,fault='huge')
        self.assertEqual(result.returncode,0,result.stderr.decode())
        self.assertIn(b'%define WAVE_0 5\n%define WAVE_1 -5\n',target.read_bytes())
    def test_usage_and_output_failures(self):
        self.assertEqual(self.invoke().returncode,2)
        self.assertEqual(self.invoke('a','b').returncode,2)
        self.assertEqual(self.invoke('').returncode,2)
        self.assertEqual(self.invoke(self.root/'missing'/'out.inc').returncode,7)
        self.assertEqual(self.invoke(self.root).returncode,7)
        self.assertEqual(self.invoke('/dev/full').returncode,7)
    def test_symlink_and_hardlink_safety(self):
        real=self.root/'real.inc';real.write_bytes(b'KEEP')
        link=self.root/'link.inc';link.symlink_to(real)
        self.assertEqual(self.invoke(link).returncode,7)
        self.assertEqual(real.read_bytes(),b'KEEP')
        hard=self.root/'hard.inc';os.link(real,hard)
        self.assertEqual(self.invoke(hard).returncode,0)
        self.assertEqual(real.read_bytes(),b'KEEP')
        self.assertNotEqual(hard.read_bytes(),b'KEEP')
    def test_broken_stdout_is_failure(self):
        with open('/dev/full','wb') as stream:
            self.assertEqual(self.invoke(self.root/'stdout.inc',stdout=stream).returncode,7)
    def test_no_temporary_files_left(self):
        self.assertEqual(list(self.root.glob('*.tmp.*')),[])

if __name__=='__main__':unittest.main(verbosity=2)
