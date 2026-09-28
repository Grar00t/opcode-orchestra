; =============================================================================
; Opcode Orchestra - ASM-native dataset contract
; Canonical dataset source is NASM. No JSONL and no conversion layer.
; =============================================================================

%ifndef OPCODE_ORCHESTRA_DATASET_INC
%define OPCODE_ORCHESTRA_DATASET_INC 1

%assign DATASET_COUNT 0
%assign DATASET_EXPECTED 0

%macro DATASET_BEGIN 1
    db 'OOASMD1',0
    dw 1                 ; format version
    dw 10                ; record size in bytes
    dw %1                ; declared record count
    %assign DATASET_EXPECTED %1
    %assign DATASET_COUNT 0
%endmacro

; section, step, previous_note, target_note, duration_cs
%macro DS_SAMPLE 5
    dw %1, %2, %3, %4, %5
    %assign DATASET_COUNT DATASET_COUNT + 1
%endmacro

%macro DATASET_END 0
    dw 0FFFFh, 0FFFFh, 0FFFFh, 0FFFFh, 0FFFFh
    %if DATASET_EXPECTED = 0
        %error "DATASET_BEGIN missing or zero record count"
    %endif
    %if DATASET_COUNT != DATASET_EXPECTED
        %error "Dataset record count does not match DATASET_BEGIN"
    %endif
%endmacro

%endif
