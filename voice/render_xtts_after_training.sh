#!/usr/bin/env bash
# Optional local voice tooling, never part of the Assembly or publication build.
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)
: "${TTS_EXE:?Set TTS_EXE to an inspected local executable}"
: "${MODEL_DIR:?Set MODEL_DIR to an existing local XTTS model directory}"
backend=${TTS_BACKEND:-native}
text=${TEXT:-$root/voice/selective_fear_spoken.txt}
speaker=${SPEAKER:-$root/voice/speaker.wav}
speaker_idx=${SPEAKER_IDX:-}
test -x "$TTS_EXE"
for name in model.pth config.json vocab.json; do test -f "$MODEL_DIR/$name"; done
test -f "$text"
# Preserve the existing training-interlock default. pgrep errors must not mean idle.
set +e
pgrep -f -- "${TRAINING_PATTERN:-[n]iyah-train}" >/dev/null
active=$?
set -e
case "$active" in
    0) printf '%s\n' 'TRAINING_ACTIVE=YES XTTS_STARTED=NO'; exit 20 ;;
    1) ;;
    *) printf '%s\n' 'TRAINING_CHECK=FAILED XTTS_STARTED=NO' >&2; exit 22 ;;
esac
if [[ -z "$speaker_idx" && ! -f "$speaker" ]]; then
    printf '%s\n' 'An original/authorized SPEAKER or SPEAKER_IDX is required.' >&2
    exit 21
fi
if [[ "$backend" != native && "$backend" != wsl-windows ]]; then
    printf '%s\n' 'TTS_BACKEND must be native or wsl-windows' >&2; exit 2
fi
test ! -L "$root/voice"
test ! -L "$root/voice/raw"
mkdir -p -- "$root/voice/raw"
work=$(mktemp -d "$root/voice/raw/.render-XXXXXXXX")
trap 'rm -rf -- "$work"' EXIT
out="$work/speech.wav"
convert() {
    if [[ "$backend" == wsl-windows ]]; then wslpath -w "$1"; else printf '%s\n' "$1"; fi
}
args=(--text "$(tr '\n' ' ' < "$text")"
      --model_path "$(convert "$MODEL_DIR/model.pth")"
      --config_path "$(convert "$MODEL_DIR/config.json")"
      --language_idx en --out_path "$(convert "$out")")
if [[ -n "$speaker_idx" ]]; then
    args+=(--speaker_idx "$speaker_idx")
else
    args+=(--speaker_wav "$(convert "$speaker")")
fi
# Tool output may contain private paths: keep it in the ignored private directory.
"$TTS_EXE" "${args[@]}" > "$work/render.log" 2>&1
test -s "$out"
test ! -L "$out"
mv -f -- "$out" "$root/voice/raw/selective-fear-xtts.wav"
mv -f -- "$work/render.log" "$root/voice/raw/render.log"
printf '%s\n' 'XTTS_PROCESS=PASS OUTPUT=voice/raw/selective-fear-xtts.wav'
# A nonempty file proves process output, not voice quality, speaker consent, or validity.
