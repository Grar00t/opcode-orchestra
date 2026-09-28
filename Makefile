.RECIPEPREFIX := >

NASM ?= nasm
PYTHON ?= python3

MUSIC_TARGET := build/b567.com
MUSIC_SOURCE := songs/beethoven_67s.asm
MUSIC_ENGINE := engine/opl2.inc engine/score.inc

MEDIA_TARGET := build/media-v2.com
MEDIA_SOURCE := showcase/media_opcode_v2.asm
MEDIA_ENGINE := engine/vga13.inc engine/font5x7.inc engine/media_ops.inc
MEDIA_TEST := tests/media_opcode_static.py

ASM_SCORE_TARGET := build/wledger.com
ASM_SCORE_SOURCE := songs/wrapper_ledger_theme.asm
ASM_SCORE_ENGINE := engine/opl2.inc engine/score.inc

DATASET_TARGET := build/wledger-dataset.bin
DATASET_SOURCE := datasets/wrapper_ledger_music_dataset.asm
DATASET_ENGINE := engine/dataset.inc

FUTURE_TARGET := build/future-audio.com
FUTURE_SOURCE := showcase/future_audio.asm
SBPCM_TARGET := build/sbpcm.com
SBPCM_SOURCE := showcase/sbpcm_demo.asm
ODE_TARGET := build/ode.com
BACH_TARGET := build/bach.com
FUTURE_TEST := tests/future_audio_static.py

.PHONY: all media score dataset future-audio verify verify-media verify-score verify-dataset verify-future verify-all clean

all: $(MUSIC_TARGET)

media: $(MEDIA_TARGET)

score: $(ASM_SCORE_TARGET)

dataset: $(DATASET_TARGET)

future-audio: $(FUTURE_TARGET) $(SBPCM_TARGET) $(ODE_TARGET) $(BACH_TARGET)

build:
>mkdir -p build

$(MUSIC_TARGET): $(MUSIC_SOURCE) $(MUSIC_ENGINE) | build
>$(NASM) -Wall -I engine/ -f bin $(MUSIC_SOURCE) -o $(MUSIC_TARGET)
>@printf "BUILT %-24s %s bytes\n" "$(MUSIC_TARGET)" "$$(wc -c < $(MUSIC_TARGET))"

$(MEDIA_TARGET): $(MEDIA_SOURCE) $(MEDIA_ENGINE) | build
>$(NASM) -Wall -I engine/ -f bin $(MEDIA_SOURCE) -o $(MEDIA_TARGET)
>@printf "BUILT %-24s %s bytes\n" "$(MEDIA_TARGET)" "$$(wc -c < $(MEDIA_TARGET))"

$(ASM_SCORE_TARGET): $(ASM_SCORE_SOURCE) $(ASM_SCORE_ENGINE) | build
>$(NASM) -Wall -I engine/ -f bin $(ASM_SCORE_SOURCE) -o $(ASM_SCORE_TARGET)
>@printf "BUILT %-24s %s bytes\n" "$(ASM_SCORE_TARGET)" "$$(wc -c < $(ASM_SCORE_TARGET))"

$(DATASET_TARGET): $(DATASET_SOURCE) $(DATASET_ENGINE) | build
>$(NASM) -Wall -I engine/ -f bin $(DATASET_SOURCE) -o $(DATASET_TARGET)
>@printf "BUILT %-24s %s bytes\n" "$(DATASET_TARGET)" "$$(wc -c < $(DATASET_TARGET))"

$(FUTURE_TARGET): $(FUTURE_SOURCE) engine/opl2.inc engine/opl3.inc engine/instruments.inc engine/percussion.inc engine/vga13.inc engine/fnum_notes.inc | build
>$(NASM) -Wall -I engine/ -f bin $(FUTURE_SOURCE) -o $(FUTURE_TARGET)

$(SBPCM_TARGET): $(SBPCM_SOURCE) engine/sbpcm.inc | build
>$(NASM) -Wall -I engine/ -f bin $(SBPCM_SOURCE) -o $(SBPCM_TARGET)

$(ODE_TARGET): songs/ode_to_joy.asm engine/opl2.inc engine/instruments.inc engine/fnum_notes.inc engine/score.inc | build
>$(NASM) -Wall -I engine/ -f bin songs/ode_to_joy.asm -o $(ODE_TARGET)

$(BACH_TARGET): songs/bach_c_major_fragment.asm engine/opl2.inc engine/instruments.inc engine/fnum_notes.inc engine/score.inc | build
>$(NASM) -Wall -I engine/ -f bin songs/bach_c_major_fragment.asm -o $(BACH_TARGET)

verify: all
>@test -s $(MUSIC_TARGET)
>@grep -q "SCORE_BEGIN 6700" $(MUSIC_SOURCE)
>@grep -q "SCORE_END" $(MUSIC_SOURCE)
>@echo "BUILD_GATE=PASS"
>@echo "SCORE_RUNTIME=67.00_SECONDS"
>@sha256sum $(MUSIC_TARGET)

verify-media: media
>@test -s $(MEDIA_TARGET)
>$(PYTHON) $(MEDIA_TEST)
>@echo "MEDIA_BUILD_GATE=PASS"
>@echo "MEDIA_FORMAT=OPCODE_V2"
>@echo "VIDEO_MODE=13H_320x200x256"
>@sha256sum $(MEDIA_TARGET)

verify-score: score
>@test -s $(ASM_SCORE_TARGET)
>@grep -q "SCORE_BEGIN 2400" $(ASM_SCORE_SOURCE)
>@grep -q "SCORE_END" $(ASM_SCORE_SOURCE)
>bash tests/asm_score_gate.sh
>@echo "ASM_SCORE_GATE=PASS"
>@echo "ASM_SCORE_FORMAT=NASM_NATIVE"
>@echo "SCORE_RUNTIME=24.00_SECONDS"
>@sha256sum $(ASM_SCORE_TARGET)

verify-dataset: dataset
>@test -s $(DATASET_TARGET)
>bash tests/asm_dataset_gate.sh
>@echo "ASM_DATASET_GATE=PASS"
>@echo "ASM_DATASET_FORMAT=NASM_NATIVE"
>@sha256sum $(DATASET_TARGET)

verify-future: future-audio
>@test -s $(FUTURE_TARGET)
>@test -s $(SBPCM_TARGET)
>@test -s $(ODE_TARGET)
>@test -s $(BACH_TARGET)
>$(PYTHON) $(FUTURE_TEST)
>@echo "FUTURE_AUDIO_BUILD_GATE=PASS"
>@sha256sum $(FUTURE_TARGET) $(SBPCM_TARGET) $(ODE_TARGET) $(BACH_TARGET)

verify-all: verify verify-media verify-score verify-dataset verify-future
>@echo "OPCODE_ORCHESTRA_GATE=PASS"

clean:
>rm -rf build
