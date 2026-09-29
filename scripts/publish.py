#!/usr/bin/env python3
"""Check tracked/outgoing content; pushing requires an explicit --push."""
import argparse
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = frozenset('.wav .mp3 .ogg .flac .aac .opus .m4a .mp4 .webm .pth .pt .ckpt .safetensors .gguf .com .bin .odoc .o .a .so .dll .exe .pem .key .p12 .pfx .zip .tar'.split())
PRIVATE_DIRS = ('build/', 'generated/', 'voice/raw/', 'voice/models/', 'voice/private/',
                'voice/final/', 'voice/processed/', 'voice/downloads-normalized/')
SECRET = re.compile(rb'-----BEGIN [A-Z ]*PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}')

def git(*args: str) -> bytes:
    return subprocess.run(['git', '-C', str(ROOT), *args], check=True, capture_output=True, timeout=30).stdout

def check_entry(mode: str, name: str, data: bytes) -> None:
    path = Path(name)
    if (mode not in ('100644', '100755') or name.startswith(PRIVATE_DIRS)
            or path.suffix.lower() in FORBIDDEN or path.name == '.env'
            or path.name.startswith('.env.') or any(c in name for c in '\r\n\t')):
        raise ValueError(f'publication policy rejects tracked path: {name!r}')
    if len(data) > 1024 * 1024 or b'\0' in data or SECRET.search(data):
        raise ValueError(f'publication policy rejects binary/oversized/credential-like content: {name!r}')

def check_tree(ref: str) -> None:
    for entry in git('ls-tree', '-r', '-z', ref).split(b'\0'):
        if not entry:
            continue
        header, name = entry.split(b'\t', 1)
        mode, kind, oid = header.decode('ascii').split()
        if kind != 'blob':
            raise ValueError('submodules are outside the publication policy')
        check_entry(mode, name.decode('utf-8'), git('cat-file', 'blob', oid))

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    option = parser.add_mutually_exclusive_group()
    option.add_argument('--check', action='store_true', help='inspect HEAD without changing anything (default)')
    option.add_argument('--push', action='store_true', help='push a clean, checked branch to its existing origin')
    args = parser.parse_args()
    try:
        if Path(git('rev-parse', '--show-toplevel').decode().strip()).resolve() != ROOT:
            raise ValueError('script must belong to the repository root')
        check_tree('HEAD')
        if not args.push:
            print('PUBLICATION_CHECK=PASS scope=HEAD PUSH=NOT_REQUESTED')
            return 0
        if git('status', '--porcelain'):
            raise ValueError('push requires a clean working tree; this tool never stages or commits')
        branch = git('symbolic-ref', '--short', 'HEAD').decode().strip()
        git('check-ref-format', '--branch', branch)
        origin = git('remote', 'get-url', '--push', 'origin').decode().strip()
        if origin not in ('https://github.com/Grar00t/opcode-orchestra.git',
                          'https://github.com/Grar00t/opcode-orchestra',
                          'git@github.com:Grar00t/opcode-orchestra.git'):
            raise ValueError('origin does not match Grar00t/opcode-orchestra')
        # A fetched main ref is required to define the outgoing history boundary.
        git('rev-parse', '--verify', 'refs/remotes/origin/main^{commit}')
        commits = git('rev-list', 'HEAD', '--not', '--remotes=origin').decode().splitlines()
        for commit in commits:
            check_tree(commit)
        subprocess.run(['git', '-C', str(ROOT), 'push', '--', 'origin',
                        f'HEAD:refs/heads/{branch}'], check=True, timeout=120)
        print('PUSH=PASS')
    except (OSError, ValueError, UnicodeError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        print(f'PUBLICATION=FAIL: {error}', file=sys.stderr)
        return 1
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
