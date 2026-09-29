#!/usr/bin/env python3
"""Isolated filesystem/CLI regressions; never invokes live publication or TTS."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import reproduce
import publish

class HostTools(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='opcode-host-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / 'source with spaces'
        reproduce.snapshot(self.root)

    def command(self, *args, env=None):
        return subprocess.run(args, cwd=self.root, env=env, capture_output=True, text=True, timeout=30)

    def test_missing_tool_and_atomic_failure(self):
        self.assertEqual(self.command(sys.executable, 'scripts/build.py', 'build', 'b567').returncode, 0)
        target = self.root / 'build/b567.com'
        original = target.read_bytes()
        env = os.environ.copy(); env['NASM'] = '/nonexistent-opcode-assembler'
        failed = self.command(sys.executable, 'scripts/build.py', 'build', 'b567', env=env)
        self.assertNotEqual(failed.returncode, 0)
        self.assertIn('required NASM', failed.stderr)
        self.assertEqual(target.read_bytes(), original)
        source = self.root / 'songs/beethoven_67s.asm'
        source.write_text(source.read_text() + '\n%error "forced failure"\n')
        failed = self.command(sys.executable, 'scripts/build.py', 'build', 'b567')
        self.assertNotEqual(failed.returncode, 0)
        self.assertEqual(target.read_bytes(), original)
        self.assertFalse(list((self.root / 'build').glob('.assemble-*')))

    def test_build_and_cleanup_symlink_boundary(self):
        outside = Path(self.temporary.name) / 'outside'
        outside.mkdir(); (outside / 'keep').write_text('untouched')
        (self.root / 'build').symlink_to(outside, target_is_directory=True)
        for args in [('build','b567'), ('clean',)]:
            result = self.command(sys.executable, 'scripts/build.py', *args)
            self.assertNotEqual(result.returncode, 0)
        self.assertEqual((outside / 'keep').read_text(), 'untouched')
        self.assertEqual(len(list(outside.iterdir())), 1)

    def test_incremental_dependencies_and_stale_detection(self):
        self.assertEqual(self.command('make', 'all').returncode, 0)
        target = self.root / 'build/b567.com'
        before = target.read_bytes()
        engine = self.root / 'engine/contracts.inc'
        engine.write_text(engine.read_text() + '\n; dependency regression\n')
        os.utime(engine, ns=(target.stat().st_mtime_ns + 2000000000,)*2)
        self.assertNotEqual(self.command(sys.executable, 'scripts/build.py', 'verify', 'b567').returncode, 0)
        self.assertEqual(self.command('make', 'all').returncode, 0)
        self.assertNotEqual(before, target.read_bytes())
        self.assertEqual(self.command(sys.executable, 'scripts/build.py', 'verify', 'b567').returncode, 0)
        self.assertEqual(self.command(sys.executable, 'scripts/build.py', 'clean').returncode, 0)
        self.assertFalse((self.root / 'build').exists())

    def test_publication_check_does_not_stage_or_push(self):
        for args in [('init','-q'), ('config','user.name','Fixture'), ('config','user.email','fixture@example.invalid'),
                     ('add','.'), ('commit','-qm','fixture')]:
            self.assertEqual(self.command('git', *args).returncode, 0)
        head = self.command('git','rev-parse','HEAD').stdout
        result = self.command('bash','scripts/publish-repo.sh','--check')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.command('git','rev-parse','HEAD').stdout, head)
        self.assertEqual(self.command('git','status','--porcelain').stdout, '')
        self.assertNotEqual(self.command('bash','scripts/publish-repo.sh','--push').returncode, 0)

    def test_publication_policy(self):
        for path in ('voice/speaker.wav','build/key.com','local.pth','.env','voice/private/note.txt'):
            with self.assertRaises(ValueError):
                publish.check_entry('100644', path, b'private')
        with self.assertRaises(ValueError):
            publish.check_entry('120000', 'link', b'/private/file')
        with self.assertRaises(ValueError):
            publish.check_entry('100644', 'key.txt', b'-----BEGIN ' + b'PRIVATE KEY-----')
        publish.check_entry('100644', 'engine/score.inc', b'; NASM source\n')

    def test_voice_interlock_and_atomic_output_with_stub(self):
        voice = self.root / 'voice'
        voice.mkdir()
        shutil.copy2(reproduce.ROOT/'voice/render_xtts_after_training.sh', voice)
        (voice/'selective_fear_spoken.txt').write_text('Fixture only.')
        model = Path(self.temporary.name)/'private model'
        model.mkdir()
        for name in ('model.pth', 'config.json', 'vocab.json'):
            (model/name).write_text('fixture')
        tools = Path(self.temporary.name)/'tools'; tools.mkdir()
        pgrep = tools/'pgrep'
        pgrep.write_text('#!/bin/sh\nexit "${PROBE_STATUS:-1}"\n'); pgrep.chmod(0o755)
        fake = tools/'tts'
        fake.write_text('#!/bin/sh\nset -eu\n'
                        'while [ "$#" -gt 0 ]; do\n'
                        '  if [ "$1" = --out_path ]; then shift; out=$1; fi\n'
                        '  shift\ndone\n'
                        'test "${FAKE_FAIL:-0}" = 0\nprintf fixture > "$out"\n')
        fake.chmod(0o755)
        env = os.environ.copy()
        env.update(PATH=str(tools)+os.pathsep+env['PATH'], TTS_EXE=str(fake),
                   MODEL_DIR=str(model), SPEAKER_IDX='fixture', TTS_BACKEND='native')
        command = ('bash', 'voice/render_xtts_after_training.sh')
        for probe, code in (('0',20), ('2',22)):
            with self.subTest(probe=probe):
                env['PROBE_STATUS'] = probe
                result = self.command(*command, env=env)
                self.assertEqual(result.returncode, code, result.stderr)
                self.assertFalse((voice/'raw').exists())
        env['PROBE_STATUS'] = '1'
        result = self.command(*command, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn(str(model), result.stdout+result.stderr)
        output = voice/'raw/selective-fear-xtts.wav'
        self.assertEqual(output.read_bytes(), b'fixture')
        output.write_bytes(b'preserved')
        env['FAKE_FAIL'] = '1'
        self.assertNotEqual(self.command(*command, env=env).returncode, 0)
        self.assertEqual(output.read_bytes(), b'preserved')
        self.assertFalse(list((voice/'raw').glob('.render-*')))
        env.pop('SPEAKER_IDX')
        env['SPEAKER'] = str(model/'absent-reference')
        self.assertEqual(self.command(*command, env=env).returncode, 21)

    def test_optional_tools_fail_without_configuration(self):
        env = os.environ.copy()
        for name in ('MLASM_DIR','TTS_EXE','MODEL_DIR'):
            env.pop(name, None)
        self.assertNotEqual(self.command('bash','scripts/build-mlasm-showcase.sh',env=env).returncode, 0)
        # Copy only the script, never local speaker/model/generated media.
        (self.root / 'voice').mkdir()
        shutil.copy2(reproduce.ROOT/'voice/render_xtts_after_training.sh', self.root/'voice')
        self.assertNotEqual(self.command('bash','voice/render_xtts_after_training.sh',env=env).returncode, 0)

if __name__ == '__main__':
    unittest.main(verbosity=2)
