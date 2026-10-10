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
import nasm_policy
import lab
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parent))
import dosboxx_audio_capture as audio_capture

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

    def test_nasm_warning_policy_is_version_gated(self):
        original = nasm_policy.version
        try:
            nasm_policy.version = lambda assembler: (2, 16)
            self.assertEqual(nasm_policy.strict_args('nasm', 'reloc-abs-word'), ['-w+all', '-Werror'])
            nasm_policy.version = lambda assembler: (3, 1)
            self.assertEqual(nasm_policy.strict_args('nasm', 'reloc-abs-word'),
                             ['-w+all', '-Werror', '-w-reloc-abs-word'])
        finally:
            nasm_policy.version = original

    def test_audio_pcm16le_and_clipping_endpoints(self):
        self.assertEqual(audio_capture.pcm16le(b'\xff\x7f\x00\x80\x01\x80'), [32767, -32768, -32767])
        samples = [32766, -32767] * (49716 * 3)
        wav = Path(self.temporary.name) / 'near-full-scale.wav'
        import wave, struct
        with wave.open(str(wav), 'wb') as out:
            out.setnchannels(2); out.setsampwidth(2); out.setframerate(49716)
            out.writeframes(struct.pack('<' + 'h' * len(samples), *samples))
        self.assertEqual(audio_capture.inspect_wav(wav)['clipped'], 0)
        samples[0] = 32767
        with wave.open(str(wav), 'wb') as out:
            out.setnchannels(2); out.setsampwidth(2); out.setframerate(49716)
            out.writeframes(struct.pack('<' + 'h' * len(samples), *samples))
        with self.assertRaisesRegex(ValueError, 'full-scale clipped'):
            audio_capture.inspect_wav(wav)

    def test_repro_snapshot_rejects_symlinked_directory_before_copying(self):
        candidate = Path(self.temporary.name) / 'evil-source'
        candidate.mkdir()
        (candidate/'Makefile').write_text('.PHONY: all\\nall:\\n\\t@true\\n')
        (candidate/'.gitignore').write_text('build/\\n')
        private = Path(self.temporary.name) / 'outside-private'
        private.mkdir()
        (private/'secret.inc').write_text('PRIVATE_FIXTURE_DO_NOT_COPY')
        (candidate/'engine').symlink_to(private, target_is_directory=True)
        destination = Path(self.temporary.name) / 'destination'
        with patch.object(reproduce, 'ROOT', candidate):
            with self.assertRaisesRegex(ValueError, 'symlink source directory'):
                reproduce.snapshot(destination)
        self.assertFalse((destination/'engine'/'secret.inc').exists())

    def test_linux_showcase_accepts_nasm_executable_path_with_spaces(self):
        executable = shutil.which('nasm')
        self.assertIsNotNone(executable, 'NASM is a required host-check tool')
        tool_dir = Path(self.temporary.name) / 'tool directory with spaces'
        tool_dir.mkdir()
        linked = tool_dir / 'nasm binary'
        linked.symlink_to(executable)
        env = os.environ.copy()
        env['NASM'] = str(linked)
        result = self.command('bash', 'scripts/build-linux-showcase.sh', env=env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((self.root / 'build/google-script').exists(), True)

    def test_operator_gate_profiles_do_not_promote_optional_audio_to_core(self):
        self.assertIn(('make', 'reproducible'), lab.PROFILES['core'])
        self.assertNotIn(('make', 'verify-audio-capture'), lab.PROFILES['core'])
        self.assertNotIn(('make', 'verify-emulator'), lab.PROFILES['host'])
        self.assertIn(('make', 'verify-audio-capture'), lab.PROFILES['capture'])
        self.assertEqual(lab.DOS_PROGRAMS['docfilm'], ('build/docfilm.com', 'docfilm.com'))

    def test_operator_missing_nasm_fails_closed_and_keeps_receipt(self):
        env = os.environ.copy()
        env['NASM'] = '/nonexistent-opcode-assembler'
        result = self.command(sys.executable, 'scripts/lab.py',
                              'verify', '--profile', 'core', env=env)
        self.assertNotEqual(result.returncode, 0)
        import json
        record = json.loads((self.root/'build/operator-core.json').read_text())
        self.assertEqual(record['status'], 'FAIL')
        self.assertEqual(record['steps'], [])
        self.assertTrue(len(record['log_sha256']) == 64)
        self.assertEqual(record['boundaries']['physical_hardware'], 'NOT_TESTED')
        self.assertEqual(record['boundaries']['audio_capture'], 'NOT_RUN')

    def test_operator_refuses_unapproved_dos_program(self):
        result = self.command(sys.executable, 'scripts/lab.py', 'play', 'SHELL.COM')
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.root/'build').exists())

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
