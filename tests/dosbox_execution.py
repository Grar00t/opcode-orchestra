#!/usr/bin/env python3
"""Headless DOSBox execution, not audible, VGA-image, or real-hardware validation."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import time
ROOT = Path(__file__).resolve().parents[1]
JOBS = [('b567.com','sb16','opl3',7,0), ('ode.com','sb16','opl3',7,0),
        ('bach.com','sb16','opl3',7,0), ('wledger.com','sb16','opl3',7,0),
        ('docfilm.com','sb16','opl3',7,0), ('future.com','sb16','opl3',7,0),
        ('media-v2.com','sb16','opl3',7,0), ('sbpcm.com','sb16','opl3',7,0),
        ('oplsmoke.com','sb16','opl3',7,0), ('ode.com','sb16','opl2',7,0),
        ('future.com','sb16','opl2',7,4), ('sbpcm.com','none','none',7,6),
        ('sbpcm.com','sb16','opl3',5,6)]

def execute(job):
    name, card, opl, irq, expected = job
    with tempfile.TemporaryDirectory(prefix='opcode-dos-') as temporary:
        drive = Path(temporary)
        source = ROOT / 'build' / name
        shutil.copy2(source, drive / name.upper())
        subprocess.run([os.environ.get('NASM','nasm'), '-w+all', '-Werror', '-w-reloc-abs-word', '-f','bin',
                        f'-DTEST_PROGRAM="{name.upper()}"', str(ROOT/'tests/dos_runner.asm'),
                        '-o',str(drive/'RUNNER.COM')], check=True, capture_output=True, timeout=10)
        config = drive / 'run.conf'
        config.write_text(f'''[sdl]
output=surface
fullscreen=false
[dosbox]
machine=svga_s3
memsize=16
[cpu]
core=normal
cycles=fixed 20000
[mixer]
nosound=true
[midi]
mpu401=none
[sblaster]
sbtype={card}
sbbase=220
irq={irq}
dma=1
oplmode={opl}
[autoexec]
mount c "{drive}"
c:
runner.com
exit
''', encoding='ascii')
        env = os.environ.copy()
        env['SDL_VIDEODRIVER'] = 'dummy'
        env['SDL_AUDIODRIVER'] = 'dummy'
        started = time.monotonic()
        result = subprocess.run([os.environ.get('DOSBOX','dosbox'), '-conf', str(config), '-noconsole'],
                                cwd=drive, env=env, capture_output=True, timeout=150)
        elapsed = time.monotonic() - started
        receipt = drive / 'RECEIPT.BIN'
        if not receipt.exists():
            raise ValueError(f'{job}: missing DOS receipt; emulator rc={result.returncode}; {result.stdout[-1000:]!r}')
        raw = receipt.read_bytes()
        if len(raw) != 16:
            raise ValueError(f'{job}: truncated receipt')
        magic, version, status, failures, begin, end = struct.unpack('<4sBBHII', raw)
        if result.returncode or magic != b'OORT' or version != 1 or status != expected or failures:
            raise ValueError(f'{job}: emulator_rc={result.returncode} exit={status} state_failures={failures} receipt={raw.hex()}')
        ticks = (end-begin) % 0x1800b0
        return f'{name}\t{card}\t{opl}\t{irq}\t{status}\t{failures}\t{ticks}\t{elapsed:.3f}\t{hashlib.sha256(source.read_bytes()).hexdigest()}'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--quick', action='store_true', help='exclude the 67/45/24-second declared-score programs')
    args = parser.parse_args()
    try:
        if not shutil.which(os.environ.get('DOSBOX','dosbox')):
            raise ValueError('required emulator missing: set DOSBOX or install dosbox')
        jobs = [j for j in JOBS if not args.quick or j[0] not in ('b567.com','docfilm.com','wledger.com')]
        if (ROOT/'build/mlasm.com').is_file():
            jobs.append(('mlasm.com','sb16','opl3',7,0))
        print('artifact\tcard\topl\tirq\tdos_exit\tstate_failures\tguest_ticks\thost_seconds\tsha256',flush=True)
        with ThreadPoolExecutor(max_workers=3) as pool:
            for row in pool.map(execute, jobs):
                print(row,flush=True)
        print(f'DOSBOX_EXECUTION=PASS cases={len(jobs)} AUDIO_CAPTURE=NOT_PERFORMED HARDWARE=NOT_TESTED')
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(f'DOSBOX_EXECUTION=FAIL: {error}', file=sys.stderr)
        return 1
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
