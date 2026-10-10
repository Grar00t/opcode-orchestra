#!/usr/bin/env python3
"""Two isolated core builds from public source paths, without copying voice assets."""
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
ROOT = Path(__file__).resolve().parents[1]
PUBLIC = {'engine': {'.inc'}, 'songs': {'.asm'}, 'showcase': {'.asm'},
          'datasets': {'.asm'}, 'documentary': {'.asm', '.inc'},
          'scripts': {'.py', '.sh'}, 'tests': {'.py', '.sh', '.c', '.asm'},
          'bridge': {'.c'}}

def snapshot(destination: Path) -> None:
    paths = [ROOT / 'Makefile', ROOT / '.gitignore']
    for directory, suffixes in PUBLIC.items():
        source_dir = ROOT / directory
        # Do not follow a top-level symlink to files outside the reviewed checkout.
        if source_dir.is_symlink():
            raise ValueError(f'symlink source directory rejected: {directory}')
        paths += [p for p in source_dir.rglob('*') if p.suffix in suffixes and p.is_file()]
    for path in sorted(paths):
        relative = path.relative_to(ROOT)
        # Also reject symlinked intermediate directories, not only final files.
        for member in (path, *path.parents):
            if member == ROOT.parent:
                break
            if member.is_symlink():
                raise ValueError(f'symlink source rejected: {relative}')
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)

def hashes(directory: Path) -> dict[str, str]:
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((directory / 'build').iterdir()) if p.suffix in ('.com', '.bin', '.odoc')}

def main() -> int:
    try:
        with tempfile.TemporaryDirectory(prefix='opcode-repro-') as temporary:
            roots = [Path(temporary) / 'one', Path(temporary) / 'two']
            for index, root in enumerate(roots):
                snapshot(root)
                env = os.environ.copy()
                env['LC_ALL'] = 'C'
                env['SOURCE_DATE_EPOCH'] = str(index * 1000000)
                result = subprocess.run(['make', '-j4', 'verify-all'], cwd=root, env=env,
                                        capture_output=True, text=True, timeout=120)
                if result.returncode:
                    raise ValueError(result.stdout + result.stderr)
            first, second = (hashes(root) for root in roots)
            if not first or first != second:
                raise ValueError('isolated artifact hashes differ')
            for name, digest in first.items():
                print(f'{digest}\t{name}')
            print(f'REPRODUCIBILITY=PASS isolated_builds=2 artifacts={len(first)}')
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        print(f'REPRODUCIBILITY=FAIL: {error}', file=sys.stderr)
        return 1
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
