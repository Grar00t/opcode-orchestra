#!/usr/bin/env python3
"""Static binary checks only; no claim of audible output or hardware timing."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import build

if __name__ == '__main__':
    sys.argv[1:] = ['verify', 'documentary']
    raise SystemExit(build.main())
