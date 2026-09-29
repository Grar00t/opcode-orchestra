#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)
cd -- "$root"
"${PYTHON:-python3}" -c 'import sys; sys.path.insert(0,"scripts"); import build; build.build_directory()'
work=$(mktemp -d "$root/build/.linux-XXXXXXXX")
trap 'rm -rf -- "$work"' EXIT
"${NASM:-nasm}" -w+all -Werror -w-reloc-rel-dword -f elf64 showcase/google_script.asm -o "$work/google.o"
"${LD:-ld}" -z noexecstack -z separate-code --build-id=none -o "$work/google-script" "$work/google.o"
mv -f -- "$work/google-script" "$root/build/google-script"
printf '%s\n' 'LINUX_ELF_BUILD=PASS'
