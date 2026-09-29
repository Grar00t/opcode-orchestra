.RECIPEPREFIX := >
.DEFAULT_GOAL := all
.DELETE_ON_ERROR:

NASM ?= nasm
PYTHON ?= python3
CC ?= cc
export NASM
export LC_ALL := C
export PYTHONDONTWRITEBYTECODE := 1

ENGINE := $(wildcard engine/*.inc)
BUILD_INPUTS := $(ENGINE) Makefile scripts/build.py scripts/artifacts.py
CORE := b567 wledger ode bach media future documentary sbpcm oplsmoke dataset ledger
COMS := build/b567.com build/wledger.com build/ode.com build/bach.com build/media-v2.com build/future-audio.com build/documentary.com build/sbpcm.com build/oplsmoke.com
DATA := build/wledger-dataset.bin build/assembly-documentary.odoc

.PHONY: all media score dataset future-audio documentary-ledger documentary smoke core clean verify verify-media verify-score verify-dataset verify-future verify-documentary-ledger verify-documentary verify-all verify-contracts verify-parsers verify-cpu verify-shell verify-syntax verify-bridge verify-linux verify-emulator check reproducible inspect

all: build/b567.com
media: build/media-v2.com
score: build/wledger.com
dataset: build/wledger-dataset.bin
future-audio: build/future-audio.com build/future.com build/sbpcm.com build/ode.com build/bach.com
documentary-ledger: build/assembly-documentary.odoc
documentary: build/documentary.com build/docfilm.com
smoke: build/oplsmoke.com
core: $(COMS) $(DATA) build/future.com build/docfilm.com

build/b567.com: songs/beethoven_67s.asm $(BUILD_INPUTS)
>$(PYTHON) scripts/build.py build b567
build/wledger.com: songs/wrapper_ledger_theme.asm $(BUILD_INPUTS)
>$(PYTHON) scripts/build.py build wledger
build/ode.com: songs/ode_to_joy.asm $(BUILD_INPUTS)
>$(PYTHON) scripts/build.py build ode
build/bach.com: songs/bach_c_major_fragment.asm $(BUILD_INPUTS)
>$(PYTHON) scripts/build.py build bach
build/media-v2.com: showcase/media_opcode_v2.asm $(BUILD_INPUTS)
>$(PYTHON) scripts/build.py build media
build/future-audio.com build/future.com &: showcase/future_audio.asm $(BUILD_INPUTS)
>$(PYTHON) scripts/build.py build future
build/documentary.com build/docfilm.com &: showcase/documentary.asm documentary/assembly_beneath_wrapper.inc $(BUILD_INPUTS)
>$(PYTHON) scripts/build.py build documentary
build/sbpcm.com: showcase/sbpcm_demo.asm $(BUILD_INPUTS)
>$(PYTHON) scripts/build.py build sbpcm
build/oplsmoke.com: tests/opl2_smoke.asm $(BUILD_INPUTS)
>$(PYTHON) scripts/build.py build oplsmoke
build/wledger-dataset.bin: datasets/wrapper_ledger_music_dataset.asm $(BUILD_INPUTS)
>$(PYTHON) scripts/build.py build dataset
build/assembly-documentary.odoc: documentary/assembly_beneath_wrapper.asm documentary/assembly_beneath_wrapper.inc $(BUILD_INPUTS)
>$(PYTHON) scripts/build.py build ledger

verify: all
>$(PYTHON) scripts/build.py verify b567
verify-media: media
>$(PYTHON) tests/media_opcode_static.py
verify-score: score
>$(PYTHON) scripts/build.py verify wledger
>bash tests/asm_score_gate.sh
verify-dataset: dataset
>$(PYTHON) scripts/build.py verify dataset
>bash tests/asm_dataset_gate.sh
verify-future: future-audio
>$(PYTHON) tests/future_audio_static.py
verify-documentary-ledger: documentary-ledger
>$(PYTHON) scripts/build.py verify ledger
>bash tests/documentary_gate.sh
verify-documentary: documentary documentary-ledger
>$(PYTHON) tests/documentary_runtime_static.py
verify-contracts:
>$(PYTHON) tests/test_contracts.py
verify-parsers: core
>$(PYTHON) tests/test_artifacts.py
verify-all: core verify-contracts verify-parsers
>$(PYTHON) scripts/build.py verify $(CORE)
>$(PYTHON) tests/future_audio_static.py
>$(PYTHON) tests/documentary_runtime_static.py
>$(PYTHON) tests/media_opcode_static.py
verify-cpu:
>$(PYTHON) tests/cpu_contracts.py
verify-syntax:
>$(PYTHON) scripts/check_sources.py syntax
verify-shell:
>$(PYTHON) scripts/check_sources.py shell
>$(PYTHON) tests/test_host_tools.py
verify-bridge:
>bash scripts/build-mlasm-showcase.sh
>$(PYTHON) tests/bridge_contracts.py
verify-linux:
>bash scripts/build-linux-showcase.sh
>$(PYTHON) tests/test_linux_showcase.py
verify-emulator: core
>$(PYTHON) tests/dosbox_execution.py
check: verify-all verify-syntax verify-shell verify-linux
reproducible:
>$(PYTHON) scripts/reproduce.py
inspect: core
>$(PYTHON) scripts/artifacts.py $(COMS) $(DATA)
clean:
>$(PYTHON) scripts/build.py clean
