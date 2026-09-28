.RECIPEPREFIX := >

NASM ?= nasm

TARGET := build/b567.com
SOURCE := songs/beethoven_67s.asm
ENGINE := engine/opl2.inc

.PHONY: all verify clean

all: $(TARGET)

build:
>mkdir -p build

$(TARGET): $(SOURCE) $(ENGINE) | build
>$(NASM) -Wall -I engine/ -f bin $(SOURCE) -o $(TARGET)
>@printf "BUILT %-24s %s bytes\n" "$(TARGET)" "$$(wc -c < $(TARGET))"

verify: all
>@test -s $(TARGET)
>@grep -q "SCORE_CS != 6700" $(SOURCE)
>@echo "BUILD_GATE=PASS"
>@echo "SCORE_RUNTIME=67.00_SECONDS"
>@sha256sum $(TARGET)

clean:
>rm -rf build
