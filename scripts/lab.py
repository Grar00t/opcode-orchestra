#!/usr/bin/env python3
"""Local-only Opcode Orchestra build, verification and DOSBox-X operator entry point.

All verification gates are existing project targets. A receipt records execution,
not musical quality, electrical hardware compatibility or external authenticity.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
PROFILES: dict[str, tuple[tuple[str, ...], ...]] = {
    "core": (("make", "-j4", "verify-all"), ("make", "reproducible"), ("make", "inspect")),
    "host": (("make", "-j4", "check"), ("make", "reproducible"), ("make", "inspect")),
    "emulator": (("make", "-j4", "verify-all"), ("make", "verify-emulator"), ("make", "inspect")),
    "capture": (("make", "build/oplsmoke.com"), ("make", "verify-audio-capture")),
    "cpu": (("make", "-j4", "verify-all"), ("make", "verify-cpu")),
    "bridge": (("make", "verify-bridge"),),
}
DOS_PROGRAMS: dict[str, tuple[str, str]] = {
    "b567": ("build/b567.com", "b567.com"),
    "wledger": ("build/wledger.com", "wledger.com"),
    "ode": ("build/ode.com", "ode.com"),
    "bach": ("build/bach.com", "bach.com"),
    "future": ("build/future.com", "future.com"),
    "docfilm": ("build/docfilm.com", "docfilm.com"),
    "media": ("build/media-v2.com", "media-v2.com"),
    "sbpcm": ("build/sbpcm.com", "sbpcm.com"),
    "oplsmoke": ("build/oplsmoke.com", "oplsmoke.com"),
}


def tool_requirements(profile: str) -> tuple[tuple[str, str], ...]:
    required = [("GNU Make", "make"), ("NASM", os.environ.get("NASM", "nasm"))]
    if profile in ("core", "host", "emulator", "cpu", "bridge"):
        required.append(("Bash", "bash"))
    if profile == "host":
        required.extend([("ShellCheck", "shellcheck"),
                         ("C compiler", os.environ.get("CC", "cc")),
                         ("ELF linker", os.environ.get("LD", "ld"))])
    if profile == "bridge":
        required.append(("C compiler", os.environ.get("CC", "cc")))
    if profile == "emulator":
        required.append(("DOSBox", os.environ.get("DOSBOX", "dosbox")))
    if profile == "capture":
        required.append(("DOSBox-X", os.environ.get("DOSBOXX", "dosbox-x")))
    if profile == "bridge":
        required.append(("MLASM_DIR", os.environ.get("MLASM_DIR", "")))
    return tuple(required)


def doctor(profile: str) -> bool:
    valid_python = sys.version_info >= (3, 10)
    print(f"PYTHON={sys.version.split()[0]} {'OK' if valid_python else 'UNSUPPORTED'}")
    ready = valid_python
    for label, executable in tool_requirements(profile):
        if label == "MLASM_DIR":
            path = Path(executable) if executable else None
            found = str(path) if path and (path / "include/ml_assembly.h").is_file() else None
        else:
            found = shutil.which(executable) if executable else None
        print(f"{label}={'OK' if found else 'MISSING'}")
        ready = ready and found is not None
    if profile == "cpu":
        try:
            import unicorn  # noqa: F401
        except ImportError:
            print("Unicorn=MISSING (install hash-pinned tests/requirements-cpu.txt)")
            ready = False
        else:
            print("Unicorn=OK")
    return ready


def git_metadata() -> tuple[str | None, bool | None]:
    try:
        sha = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                             check=True, capture_output=True, text=True, timeout=10).stdout.strip()
        dirty = bool(subprocess.run(
            ["git", "-C", str(ROOT), "status", "--porcelain", "--untracked-files=normal"],
            check=True, capture_output=True, text=True, timeout=10).stdout.strip())
        return sha, dirty
    except (OSError, subprocess.SubprocessError):
        return None, None


def verify(profile: str) -> int:
    # No implicit clean, package install, push, external upload, or voice operation.
    output_dir = ROOT / "build"
    if output_dir.is_symlink():
        print("OPERATOR=FAIL: build directory is a symlink", file=sys.stderr)
        return 1
    try:
        output_dir.mkdir(exist_ok=True)
        if not output_dir.is_dir():
            raise OSError("build path is not a directory")
    except OSError as error:
        print(f"OPERATOR=FAIL: {error}", file=sys.stderr)
        return 1
    started = datetime.now(timezone.utc).isoformat()
    revision, dirty = git_metadata()
    receipt: dict[str, object] = {
        "schema": "opcode-orchestra-operator-v1",
        "profile": profile, "git_commit": revision, "working_tree_dirty": dirty,
        "started_utc": started, "status": "FAIL",
        "steps": [], "boundaries": {
            "listening": "NOT_TESTED", "physical_hardware": "NOT_TESTED",
            "audio_capture": "RUN" if profile == "capture" else "NOT_RUN"
        }
    }
    steps: list[dict[str, object]] = []
    receipt["steps"] = steps
    log_path = output_dir / f"operator-{profile}.log"
    ready = doctor(profile)
    environment = os.environ.copy()
    environment.setdefault("PYTHON", sys.executable)
    with log_path.open("w", encoding="utf-8") as log:
        if not ready:
            log.write("PREFLIGHT=FAIL missing prerequisites; no verification executed\n")
        else:
            for command in PROFILES[profile]:
                started_clock = time.monotonic()
                log.write(f"RUN {' '.join(command)}\n")
                log.flush()
                print(f"RUN {' '.join(command)}", flush=True)
                failure = None
                try:
                    proc = subprocess.run(command, cwd=ROOT, env=environment, stdout=log,
                                          stderr=subprocess.STDOUT, timeout=1200, check=False)
                    code = proc.returncode
                except subprocess.TimeoutExpired:
                    code, failure = 124, "TIMEOUT"
                except OSError:
                    code, failure = 127, "LAUNCH_ERROR"
                result = {
                    "argv": list(command), "exit_code": code,
                    "status": "PASS" if code == 0 else "FAIL",
                    "elapsed_seconds": round(time.monotonic() - started_clock, 3)
                }
                if failure:
                    result["error_kind"] = failure
                steps.append(result)
                print(f"{result['status']} {command[-1]} exit={code}", flush=True)
                if code:
                    break
    receipt["status"] = "PASS" if ready and len(steps) == len(PROFILES[profile]) and all(
        step["status"] == "PASS" for step in steps) else "FAIL"
    receipt["finished_utc"] = datetime.now(timezone.utc).isoformat()
    receipt["log_sha256"] = hashlib.sha256(log_path.read_bytes()).hexdigest()
    target = output_dir / f"operator-{profile}.json"
    staging = output_dir / f".operator-{profile}.{os.getpid()}.tmp"
    try:
        staging.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        os.replace(staging, target)
    except OSError as error:
        staging.unlink(missing_ok=True)
        print(f"OPERATOR=FAIL: receipt write error: {error}", file=sys.stderr)
        return 1
    print(f"OPERATOR={receipt['status']} profile={profile} receipt={target.relative_to(ROOT)} "
          f"log={log_path.relative_to(ROOT)}")
    if receipt["status"] != "PASS":
        # Bounded local error context; never upload log contents automatically.
        with log_path.open("rb") as stream:
            stream.seek(0, os.SEEK_END)
            stream.seek(max(0, stream.tell() - 4000))
            print(stream.read().decode("utf-8", "replace"), file=sys.stderr)
    return 0 if receipt["status"] == "PASS" else 1


def play(name: str, stay_open: bool) -> int:
    target, filename = DOS_PROGRAMS[name]
    dosbox = os.environ.get("DOSBOXX", "dosbox-x")
    if not shutil.which(dosbox):
        print("PLAY=FAIL: DOSBox-X not found (set DOSBOXX or install it)", file=sys.stderr)
        return 1
    mount = str((ROOT / "build").resolve())
    if '"' in mount:
        print("PLAY=FAIL: unsupported quote in mount path", file=sys.stderr)
        return 1
    commands = [
        ["make", target],
        [dosbox, "-conf", str(ROOT / "dosbox-x.conf"),
         "-c", f'mount c "{mount}"', "-c", "c:", "-c", filename]
    ]
    if not stay_open:
        commands[-1].extend(["-c", "exit"])
    print("AUDIO_QUALITY=UNKNOWN PHYSICAL_HARDWARE=NOT_TESTED", flush=True)
    for command in commands:
        try:
            result = subprocess.run(command, cwd=ROOT, check=False)
        except OSError:
            print("PLAY=FAIL: could not launch required tool", file=sys.stderr)
            return 1
        if result.returncode:
            print(f"PLAY=FAIL: tool exited {result.returncode}", file=sys.stderr)
            return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    preflight = sub.add_parser("doctor", help="check required commands without installing anything")
    preflight.add_argument("--profile", choices=tuple(PROFILES), default="core")
    audit = sub.add_parser("verify", help="run a bounded gate profile and write a local JSON receipt")
    audit.add_argument("--profile", choices=tuple(PROFILES), default="core")
    demo = sub.add_parser("play", help="build and launch an allowlisted DOS .COM in DOSBox-X")
    demo.add_argument("program", choices=tuple(DOS_PROGRAMS))
    demo.add_argument("--stay-open", action="store_true", help="leave DOSBox-X open after the guest exits")
    args = parser.parse_args()
    if args.command == "doctor":
        return 0 if doctor(args.profile) else 1
    if args.command == "verify":
        return verify(args.profile)
    return play(args.program, args.stay_open)


if __name__ == "__main__":
    raise SystemExit(main())
