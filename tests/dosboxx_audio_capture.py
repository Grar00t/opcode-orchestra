#!/usr/bin/env python3
"""Verify emulated OPL output capture in DOSBox-X; not listening or hardware proof."""
import hashlib
import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import wave

ROOT = Path(__file__).resolve().parents[1]
DOSBOXX = os.environ.get('DOSBOXX', 'dosbox-x')
DRO_HEADER = struct.Struct('<8sHHIIBBBBBB')

def need(condition, message):
    if not condition:
        raise ValueError(message)

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def pcm16le(data):
    need(len(data) % 2 == 0, 'PCM16 byte length is not even')
    return [sample for (sample,) in struct.iter_unpack('<h', data)]

def inspect_wav(path):
    with wave.open(str(path), 'rb') as source:
        channels = source.getnchannels()
        width = source.getsampwidth()
        rate = source.getframerate()
        frames = source.getnframes()
        pcm = source.readframes(frames)
    need(channels == 2, f'WAV channels={channels}, expected stereo capture')
    need(width == 2, f'WAV sample width={width}, expected PCM16')
    need(rate == 49716, f'WAV rate={rate}, expected configured OPL rate')
    need(frames > 0 and len(pcm) == frames * channels * width, 'WAV PCM length mismatch')
    samples = pcm16le(pcm)
    peak = max((abs(sample) for sample in samples), default=0)
    nonzero = sum(sample != 0 for sample in samples)
    clipped = sum(sample in (-32768, 32767) for sample in samples)
    left_nonzero = sum(samples[i] != 0 for i in range(0, len(samples), 2))
    right_nonzero = sum(samples[i] != 0 for i in range(1, len(samples), 2))
    duration = frames / rate
    need(2.5 <= duration <= 8.0, f'WAV duration outside smoke window: {duration:.3f}s')
    need(peak > 0, 'WAV is digital silence')
    need(clipped == 0, f'WAV contains full-scale clipped samples: {clipped}')
    need(nonzero >= rate * channels, 'WAV contains less than one second-equivalent of nonzero PCM')
    need(left_nonzero >= rate // 2 and right_nonzero >= rate // 2,
         'WAV does not contain sustained signal in both stereo channels')
    return {'rate': rate, 'channels': channels, 'frames': frames,
            'duration': duration, 'peak': peak, 'nonzero': nonzero,
            'clipped': clipped, 'left_nonzero': left_nonzero,
            'right_nonzero': right_nonzero}

def inspect_dro(path):
    data = path.read_bytes()
    need(len(data) >= DRO_HEADER.size, 'DRO truncated header')
    (magic, major, minor, commands, milliseconds, hardware, layout,
     compression, short_delay, long_delay, map_len) = DRO_HEADER.unpack_from(data)
    need(magic == b'DBRAWOPL', 'DRO magic mismatch')
    need((major, minor) == (2, 0), f'DRO version={(major, minor)}, expected 2.0')
    need(layout == 0 and compression == 0, 'DRO unsupported layout/compression')
    need(0 < map_len <= 128 and commands > 0, 'DRO empty/invalid command map')
    need(len(data) == DRO_HEADER.size + map_len + commands * 2, 'DRO size/header mismatch')
    need(2000 <= milliseconds <= 4500, f'DRO OPL interval outside smoke window: {milliseconds}ms')
    mapping = data[DRO_HEADER.size:DRO_HEADER.size + map_len]
    encoded = data[DRO_HEADER.size + map_len:]
    writes = []
    for offset in range(0, len(encoded), 2):
        code, value = encoded[offset:offset + 2]
        if code in (short_delay, long_delay):
            continue
        index = code & 0x7f
        need(index < map_len, f'DRO register index outside map: {index}')
        register = mapping[index] | (0x100 if code & 0x80 else 0)
        writes.append((register, value))
    need(hardware == 0, f'raw OPL2 smoke unexpectedly used hardware mode {hardware}')
    key_on = 0
    key_off = 0
    key_state = False
    for register, value in writes:
        if register != 0xb0:
            continue
        new_state = bool(value & 0x20)
        if new_state == key_state:
            continue
        if new_state:
            key_on += 1
        else:
            key_off += 1
        key_state = new_state
    need(key_on == 1, f'DRO expected one channel-0 key-on transition, got {key_on}')
    need(key_off == 1, f'DRO expected one channel-0 key-off transition, got {key_off}')
    return {'commands': commands, 'milliseconds': milliseconds,
            'hardware': hardware, 'writes': len(writes),
            'key_on': key_on, 'key_off': key_off}

def main():
    try:
        executable = shutil.which(DOSBOXX)
        need(executable, f'DOSBox-X missing: set DOSBOXX or install dosbox-x')
        smoke = ROOT / 'build' / 'oplsmoke.com'
        need(smoke.is_file(), 'missing build/oplsmoke.com; build smoke target first')
        build = ROOT / 'build'
        with tempfile.TemporaryDirectory(prefix='dosboxx-audio-', dir=build) as directory:
            work = Path(directory)
            capture = work / 'capture'
            capture.mkdir()
            shutil.copy2(smoke, work / 'OPLSMOKE.COM')
            config = work / 'run.conf'
            config.write_text(f'''[dosbox]
captures={capture.as_posix()}
[sdl]
output=surface
fullscreen=false
[cpu]
core=normal
cycles=fixed 20000
[mixer]
nosound=false
rate=49716
blocksize=1024
prebuffer=25
[midi]
mpu401=none
mididevice=none
[sblaster]
sbtype=sb16
sbbase=220
irq=7
dma=1
hdma=5
oplmode=opl2
oplemu=nuked
oplrate=49716
''', encoding='ascii')
            with config.open('a', encoding='ascii') as stream:
                stream.write(f'''[speaker]
pcspeaker=false
[autoexec]
mount c "{work.as_posix()}"
c:
DX-CAPTURE /A /O OPLSMOKE.COM
exit
''')
            env = os.environ.copy()
            env['SDL_VIDEODRIVER'] = 'dummy'
            env['SDL_AUDIODRIVER'] = 'dummy'
            result = subprocess.run([executable, '-nogui', '-fastlaunch', '-conf', str(config)],
                                    cwd=work, env=env, capture_output=True, text=True, timeout=45)
            need(result.returncode == 0, f'DOSBox-X exit={result.returncode}: {result.stderr[-1000:]}')
            waves = list(capture.glob('*.wav'))
            dros = list(capture.glob('*.dro'))
            need(len(waves) == 1 and len(dros) == 1,
                 f'capture count wav={len(waves)} dro={len(dros)}')
            wav = inspect_wav(waves[0])
            dro = inspect_dro(dros[0])
            print('DOSBOXX_AUDIO_CAPTURE=PASS')
            print(f"WAV rate={wav['rate']} channels={wav['channels']} frames={wav['frames']} "
                  f"duration={wav['duration']:.3f} peak={wav['peak']} nonzero={wav['nonzero']} "
                  f"clipped={wav['clipped']} left_nonzero={wav['left_nonzero']} "
                  f"right_nonzero={wav['right_nonzero']} sha256={sha256(waves[0])}")
            print(f"DRO commands={dro['commands']} milliseconds={dro['milliseconds']} "
                  f"hardware={dro['hardware']} writes={dro['writes']} key_on={dro['key_on']} "
                  f"key_off={dro['key_off']} sha256={sha256(dros[0])}")
            print('AUDIBLE_QUALITY=NOT_VERIFIED PHYSICAL_HARDWARE=NOT_TESTED')
    except (OSError, ValueError, subprocess.SubprocessError, wave.Error) as error:
        print(f'DOSBOXX_AUDIO_CAPTURE=FAIL: {error}', file=os.sys.stderr)
        return 1
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
