#!/usr/bin/env python3
"""Strict NASM warning policy with version-safe optional-class exceptions."""
from __future__ import annotations
from functools import lru_cache
import re
import subprocess

@lru_cache(maxsize=None)
def version(assembler: str) -> tuple[int, int]:
    result = subprocess.run(
        [assembler, '-v'], capture_output=True, text=True, timeout=10, check=False
    )
    match = re.search(r'NASM version\s+(\d+)\.(\d+)', result.stdout + result.stderr)
    if result.returncode != 0 or not match:
        raise ValueError(f'cannot determine NASM version: {assembler}')
    return int(match.group(1)), int(match.group(2))

def strict_args(assembler: str, *intentional: str) -> list[str]:
    """Keep every warning fatal; NASM 3.01+ may suppress proven relocation classes."""
    args = ['-w+all', '-Werror']
    if version(assembler) >= (3, 1):
        args.extend(f'-w-{warning}' for warning in intentional)
    return args
