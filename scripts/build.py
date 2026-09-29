#!/usr/bin/env python3
"""Atomic NASM builds; runtime code and payload offsets remain Assembly-owned."""
from __future__ import annotations
import argparse
import hashlib
import os
from pathlib import Path
import shutil
import stat
import struct
import subprocess
import sys
import tempfile
import artifacts
import nasm_policy

ROOT = Path(__file__).resolve().parents[1]
# source, output, feature bits, media stream, PCM sample
TARGETS = {
    'b567': ('songs/beethoven_67s.asm', 'b567.com', 33, False, False),
    'wledger': ('songs/wrapper_ledger_theme.asm', 'wledger.com', 33, False, False),
    'ode': ('songs/ode_to_joy.asm', 'ode.com', 33, False, False),
    'bach': ('songs/bach_c_major_fragment.asm', 'bach.com', 33, False, False),
    'media': ('showcase/media_opcode_v2.asm', 'media-v2.com', 72, True, False),
    'future': ('showcase/future_audio.asm', 'future-audio.com', 75, False, False),
    'documentary': ('showcase/documentary.asm', 'documentary.com', 43, False, False),
    'sbpcm': ('showcase/sbpcm_demo.asm', 'sbpcm.com', 68, False, True),
    'oplsmoke': ('tests/opl2_smoke.asm', 'oplsmoke.com', 1, False, False),
    'dataset': ('datasets/wrapper_ledger_music_dataset.asm', 'wledger-dataset.bin', 0, False, False),
    'ledger': ('documentary/assembly_beneath_wrapper.asm', 'assembly-documentary.odoc', 0, False, False),
    'mlasm': ('showcase/mlasm_orchestra.asm', 'mlasm.com', 73, True, False),
}
ALIASES = {'future': 'future.com', 'documentary': 'docfilm.com'}
LOCATOR = struct.Struct('<4sHHIHHI')

def source_paths(target: str) -> list[Path]:
    source = TARGETS[target][0]
    names = {source, 'Makefile', 'scripts/build.py', 'scripts/artifacts.py', 'scripts/nasm_policy.py'}
    names.update(str(p.relative_to(ROOT)) for p in (ROOT / 'engine').glob('*.inc'))
    if target in ('documentary', 'ledger'):
        names.add('documentary/assembly_beneath_wrapper.inc')
    if target == 'mlasm':
        names.add('build/generated/mlasm_scene.inc')
    return [ROOT / name for name in sorted(names)]

def source_hash(target: str) -> bytes:
    digest = hashlib.sha256()
    for path in source_paths(target):
        if path.is_symlink() or any(p.is_symlink() for p in path.parents if p != ROOT.parent):
            raise ValueError(f'symlink source not allowed: {path.relative_to(ROOT)}')
        data = path.read_bytes()
        digest.update(path.relative_to(ROOT).as_posix().encode('utf-8') + b'\0')
        digest.update(len(data).to_bytes(8, 'little'))
        digest.update(data)
    return digest.digest()

def build_directory() -> Path:
    path = ROOT / 'build'
    if path.is_symlink():
        raise ValueError('build must not be a symlink')
    path.mkdir(exist_ok=True)
    if not stat.S_ISDIR(path.stat().st_mode):
        raise ValueError('build must be a directory')
    return path

def build(target: str) -> Path:
    source, name, flags, has_media, has_pcm = TARGETS[target]
    destination = build_directory() / name
    digest = source_hash(target)
    assembler = os.environ.get('NASM', 'nasm')
    if not shutil.which(assembler):
        raise ValueError(f'required NASM executable not found: {assembler}')
    is_com = name.endswith('.com')
    with tempfile.TemporaryDirectory(prefix='.assemble-', dir=destination.parent) as directory:
        temporary = Path(directory)
        wrapper = temporary / 'input.asm'
        output = temporary / 'output.bin'
        wrapper.write_text(f'%define OO_BUILD_COM {int(is_com)}\n'
                           f'%define OO_BUILD_FEATURES {flags}\n'
                           f'%define OO_BUILD_MEDIA {int(has_media)}\n'
                           f'%define OO_BUILD_PCM {int(has_pcm)}\n'
                           f'%include "{source}"\n'
                           '%include "manifest.inc"\nOO_FINALIZE\n', encoding='ascii')
        subprocess.run([assembler, *nasm_policy.strict_args(assembler, 'reloc-abs-word'),
                        '-I', 'engine/', '-I', 'documentary/', '-I', 'build/', '-I', 'build/generated/',
                        '-f', 'bin', str(wrapper), '-o', str(output)],
                       cwd=ROOT, check=True, timeout=60)
        data = output.read_bytes()
        if is_com:
            artifacts.need(len(data) > LOCATOR.size, 'missing NASM locator')
            magic, kind, actual_flags, runtime, offset, length, body_size = LOCATOR.unpack(data[-LOCATOR.size:])
            body = data[:-LOCATOR.size]
            artifacts.need(magic == b'OOLC' and body_size == len(body) and actual_flags == flags,
                           'invalid NASM locator')
            artifacts.need(offset + length <= len(body), 'NASM payload outside image')
            data = body + artifacts.MANIFEST.pack(
                b'OOMF', 1, artifacts.MANIFEST.size, runtime, flags, kind, offset, length, 0,
                digest, hashlib.sha256(body[offset:offset + length]).digest(),
                hashlib.sha256(body).digest(), artifacts.CONTRACT)
            artifacts.com(data, digest)
        elif name.endswith('.bin'):
            artifacts.dataset(data)
        else:
            artifacts.ledger(data)
        if source_hash(target) != digest:
            raise ValueError('source changed during assembly; refusing mixed-input artifact')
        output.write_bytes(data)
        output.chmod(0o644)
        os.replace(output, destination)
        if target in ALIASES:
            alias = temporary / 'alias.com'
            alias.write_bytes(data)
            alias.chmod(0o644)
            os.replace(alias, destination.parent / ALIASES[target])
    print(f'BUILT {name} bytes={len(data)} sha256={hashlib.sha256(data).hexdigest()}')
    return destination

def verify(target: str) -> None:
    path = ROOT / 'build' / TARGETS[target][1]
    if path.is_symlink():
        raise ValueError('refusing verification of symlinked artifact')
    result = artifacts.inspect(path, source_hash(target) if path.suffix == '.com' else None)
    if path.suffix == '.com':
        expected_kind = (1 if target in ('b567', 'wledger', 'ode', 'bach') else
                         2 if target == 'documentary' else
                         3 if TARGETS[target][3] else 4 if TARGETS[target][4] else 0)
        artifacts.need(result['features'] == TARGETS[target][2] and
                       result['payload_kind'] == expected_kind, 'manifest target contract mismatch')
    if target in ALIASES:
        artifacts.need(path.read_bytes() == (path.parent / ALIASES[target]).read_bytes(), 'stale DOS alias')
    if target == 'documentary':
        data = path.read_bytes()
        start, length = result['payload_offset'], result['payload_bytes']
        artifacts.need(data[start:start + length] == (ROOT / 'build/assembly-documentary.odoc').read_bytes(),
                       'documentary embedded ledger differs from standalone ledger')
    print(f'STATIC_BINARY=PASS target={target} ' + ' '.join(f'{k}={v}' for k, v in sorted(result.items())))

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('build', 'verify', 'clean'))
    parser.add_argument('targets', nargs='*', choices=tuple(TARGETS))
    args = parser.parse_args()
    try:
        if args.operation == 'clean':
            if args.targets:
                parser.error('clean accepts no targets')
            path = ROOT / 'build'
            if path.is_symlink():
                raise ValueError('refusing cleanup of a symlinked build directory')
            if path.exists():
                shutil.rmtree(path)
            return 0
        if not args.targets:
            parser.error('at least one target required')
        for target in args.targets:
            (build if args.operation == 'build' else verify)(target)
    except (OSError, ValueError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        print(f'BUILD=FAIL: {error}', file=sys.stderr)
        return 1
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
