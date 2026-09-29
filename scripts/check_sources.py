#!/usr/bin/env python3
"""Syntax and ShellCheck gates, without executing optional/private workflows."""
import argparse
import ast
from pathlib import Path
import shutil
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('syntax', 'shell'))
    args = parser.parse_args()
    try:
        shell = sorted(ROOT.glob('scripts/*.sh')) + sorted(ROOT.glob('tests/*.sh')) + sorted(ROOT.glob('voice/*.sh'))
        if args.mode == 'syntax':
            for path in sorted(ROOT.glob('scripts/*.py')) + sorted(ROOT.glob('tests/*.py')):
                ast.parse(path.read_text(encoding='utf-8'), filename=str(path.relative_to(ROOT)))
            for path in shell:
                subprocess.run(['bash', '-n', str(path)], check=True)
        else:
            if not shutil.which('shellcheck'):
                raise ValueError('required tool missing: shellcheck')
            subprocess.run(['shellcheck', '--severity=style', *(str(p) for p in shell)], check=True)
        print(f'{args.mode.upper()}=PASS')
    except (OSError, ValueError, SyntaxError, subprocess.CalledProcessError) as error:
        print(f'{args.mode.upper()}=FAIL: {error}', file=sys.stderr)
        return 1
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
