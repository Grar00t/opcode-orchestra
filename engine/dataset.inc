; NASM-native dataset v1. See docs/ASM_DATASET_FORMAT.md.
%ifndef OPCODE_ORCHESTRA_DATASET_INC
%define OPCODE_ORCHESTRA_DATASET_INC 1
%include "contracts.inc"
%assign DATASET_ACTIVE 0
%assign DATASET_COUNT 0
%assign DATASET_EXPECTED 0
%macro DATASET_BEGIN 1
    %if DATASET_ACTIVE
        %error "Nested DATASET_BEGIN"
    %endif
    REQUIRE_RANGE %1, 1, 65535, "Dataset count must be 1..65535"
    %assign DATASET_ACTIVE 1
    db 'OOASMD1',0
    dw 1, 10, %1
    %assign DATASET_EXPECTED %1
    %assign DATASET_COUNT 0
    %xdefine DATASET_DATA_BEGIN %%start
%%start:
%endmacro
; section, step, previous_note, target_note, duration_cs
%macro DS_SAMPLE 5
    %if !DATASET_ACTIVE
        %error "DS_SAMPLE requires DATASET_BEGIN"
    %endif
    REQUIRE_RANGE %1, 0, 65534, "Dataset section collides with sentinel or exceeds u16"
    REQUIRE_RANGE %2, 0, 65534, "Dataset step collides with sentinel or exceeds u16"
    REQUIRE_RANGE %3, 0, 1023, "Dataset previous note must be 0..1023"
    REQUIRE_RANGE %4, 0, 1023, "Dataset target note must be 0..1023"
    REQUIRE_RANGE %5, 1, 65535, "Dataset duration must be 1..65535"
    dw %1, %2, %3, %4, %5
    %assign DATASET_COUNT DATASET_COUNT + 1
%endmacro
%macro DATASET_END 0
    %if !DATASET_ACTIVE
        %error "DATASET_END requires DATASET_BEGIN"
        %exitmacro
    %endif
    %if DATASET_COUNT != DATASET_EXPECTED
        %error "Dataset record count does not match DATASET_BEGIN"
    %endif
    %if ($ - DATASET_DATA_BEGIN) != DATASET_COUNT * 10
        %error "Dataset record alignment mismatch"
    %endif
    dw 0xffff, 0xffff, 0xffff, 0xffff, 0xffff
    %assign DATASET_ACTIVE 0
%endmacro
%endif
