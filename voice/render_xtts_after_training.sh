#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)}"
VOICE="$ROOT/voice"

TTS_EXE="${TTS_EXE:-/mnt/d/AI/venvs/tts/Scripts/tts.exe}"
MODEL_DIR="${MODEL_DIR:-/mnt/c/Users/A/AppData/Local/tts/tts_models--multilingual--multi-dataset--xtts_v2}"
TEXT="${TEXT:-$VOICE/selective_fear_spoken.txt}"
SPEAKER="${SPEAKER:-$VOICE/speaker.wav}"
SPEAKER_IDX="${SPEAKER_IDX:-}"
OUT="${OUT:-$VOICE/raw/selective-fear-xtts.wav}"

echo "============================================================"
echo "OPCODE ORCHESTRA — OPTIONAL LOCAL XTTS VOICE RENDER"
echo "MODEL=XTTS_V2"
echo "ASM_NATIVE_CORE=NO"
echo "============================================================"

test -x "$TTS_EXE"
test -f "$MODEL_DIR/model.pth"
test -f "$MODEL_DIR/config.json"
test -f "$MODEL_DIR/vocab.json"
test -f "$TEXT"
if pgrep -af '[n]iyah-train' >/dev/null; then
    echo "NIYAH_TRAINING_ACTIVE=YES"
    echo "XTTS_STARTED=NO"
    exit 20
fi

echo "NIYAH_TRAINING_ACTIVE=NO"

if [ -z "$SPEAKER_IDX" ] && [ ! -f "$SPEAKER" ]; then
    echo "NO_SPEAKER_SOURCE=YES"
    echo "Set SPEAKER_IDX or provide an original/authorized SPEAKER file."
    echo "XTTS_STARTED=NO"
    exit 21
fi

TEXT_WIN="$(wslpath -w "$TEXT")"
if [ -f "$SPEAKER" ]; then
    SPEAKER_WIN="$(wslpath -w "$SPEAKER")"
else
    SPEAKER_WIN=""
fi
OUT_WIN="$(wslpath -w "$OUT")"
MODEL_WIN="$(wslpath -w "$MODEL_DIR")"

mkdir -p "$(dirname "$OUT")"
echo "TEXT=$TEXT"
echo "SPEAKER=$SPEAKER"
echo "OUTPUT=$OUT"

ARGS=(
    --text "$(tr '\n' ' ' < "$TEXT" | sed 's/  */ /g')"
    --model_path "$MODEL_WIN\\model.pth"
    --config_path "$MODEL_WIN\\config.json"
    --language_idx en
    --out_path "$OUT_WIN"
)

if [ -n "$SPEAKER_IDX" ]; then
    ARGS+=(--speaker_idx "$SPEAKER_IDX")
else
    ARGS+=(--speaker_wav "$SPEAKER_WIN")
fi

"$TTS_EXE" "${ARGS[@]}"

test -s "$OUT"

echo
echo "XTTS_RENDER=PASS"
sha256sum "$OUT"
