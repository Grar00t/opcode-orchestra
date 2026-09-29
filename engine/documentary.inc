; Opcode Orchestra - ASM-native Documentary DSL
%ifndef OPCODE_ORCHESTRA_DOCUMENTARY_INC
%define OPCODE_ORCHESTRA_DOCUMENTARY_INC 1
%include "contracts.inc"
%assign DOC_ACTIVE 0

DOC_VERSION equ 1
DOC_REC_SOURCE  equ 01h
DOC_REC_CLAIM   equ 02h
DOC_REC_SCENE   equ 04h
DOC_REC_END     equ 0FFh

DOC_SRC_CODE equ 1
DOC_SRC_DOC  equ 2
DOC_SRC_TEST equ 3

DOC_STYLE_TITLE    equ 1
DOC_STYLE_EVIDENCE equ 2
DOC_STYLE_NATURE   equ 3
DOC_STYLE_TECH     equ 4
DOC_STYLE_CODA     equ 5

DOC_CAM_STATIC equ 0
DOC_CAM_PAN_L  equ 1
DOC_CAM_PAN_R  equ 2
DOC_CAM_PUSH   equ 3
DOC_CAM_PULL   equ 4

%assign DOC_SOURCES 0
%assign DOC_CLAIMS 0
%assign DOC_SCENES 0
%assign DOC_RUNTIME_CS 0
%assign DOC_EXPECT_SOURCES -1
%assign DOC_EXPECT_CLAIMS -1
%assign DOC_EXPECT_SCENES -1
%assign DOC_EXPECT_RUNTIME -1

%macro DOC_BEGIN 4
    %if DOC_ACTIVE
        %error "Nested DOC_BEGIN"
    %endif
    REQUIRE_RANGE %1, 1, 255, "Documentary source count must be 1..255"
    REQUIRE_RANGE %2, 1, 255, "Documentary claim count must be 1..255"
    REQUIRE_RANGE %3, 1, 255, "Documentary scene count must be 1..255"
    REQUIRE_RANGE %4, 1, 65535, "Documentary runtime must be 1..65535"
    %assign DOC_ACTIVE 1
    %assign __doc_i 1
    %rep 255
        %undef __doc_source_%[__doc_i]
        %undef __doc_claim_%[__doc_i]
        %undef __doc_scene_%[__doc_i]
        %assign __doc_i __doc_i + 1
    %endrep
    %xdefine DOC_DATA_BEGIN %%start
%%start:
    db 'O','D','O','C'
    dw DOC_VERSION
    dw %1, %2, %3, %4
    %assign DOC_SOURCES 0
    %assign DOC_CLAIMS 0
    %assign DOC_SCENES 0
    %assign DOC_RUNTIME_CS 0
    %assign DOC_EXPECT_SOURCES %1
    %assign DOC_EXPECT_CLAIMS %2
    %assign DOC_EXPECT_SCENES %3
    %assign DOC_EXPECT_RUNTIME %4
%endmacro

%macro DOC_SOURCE 3
    %if !DOC_ACTIVE
        %error "DOC_SOURCE requires DOC_BEGIN"
    %endif
    REQUIRE_RANGE %1, 1, 255, "Documentary source ID must be 1..255"
    REQUIRE_RANGE %2, 1, 3, "Invalid documentary source type"
    REQUIRE_RANGE %3, 0, 65535, "Documentary source tag must be u16"
    %assign __doc_id %1
    %ifdef __doc_source_%[__doc_id]
        %error "Duplicate documentary source ID"
    %endif
    %define __doc_source_%[__doc_id] 1
    db DOC_REC_SOURCE, %1, %2
    dw %3
    %assign DOC_SOURCES DOC_SOURCES + 1
%endmacro

%macro DOC_CLAIM 3
    %if !DOC_ACTIVE
        %error "DOC_CLAIM requires DOC_BEGIN"
    %endif
    REQUIRE_RANGE %1, 1, 255, "Documentary claim ID must be 1..255"
    REQUIRE_RANGE %2, 1, 255, "Documentary source reference must be 1..255"
    REQUIRE_RANGE %3, 0, 100, "Documentary confidence must be 0..100"
    %assign __doc_id %1
    %assign __doc_ref %2
    %ifdef __doc_claim_%[__doc_id]
        %error "Duplicate documentary claim ID"
    %endif
    %ifndef __doc_source_%[__doc_ref]
        %error "Undefined documentary source reference"
    %endif
    %define __doc_claim_%[__doc_id] 1
    db DOC_REC_CLAIM, %1, %2, %3
    %assign DOC_CLAIMS DOC_CLAIMS + 1
%endmacro
%macro DOC_SCENE 5
    %if !DOC_ACTIVE
        %error "DOC_SCENE requires DOC_BEGIN"
    %endif
    REQUIRE_RANGE %1, 1, 255, "Documentary scene ID must be 1..255"
    REQUIRE_RANGE %2, 1, 255, "Documentary claim reference must be 1..255"
    REQUIRE_RANGE %3, 1, 65535, "Documentary scene duration must be 1..65535"
    REQUIRE_RANGE %4, 1, 5, "Invalid documentary style"
    REQUIRE_RANGE %5, 0, 4, "Invalid documentary camera"
    %assign __doc_id %1
    %assign __doc_ref %2
    %ifdef __doc_scene_%[__doc_id]
        %error "Duplicate documentary scene ID"
    %endif
    %ifndef __doc_claim_%[__doc_ref]
        %error "Undefined documentary claim reference"
    %endif
    %define __doc_scene_%[__doc_id] 1
    db DOC_REC_SCENE, %1, %2, %4, %5
    dw %3
    %assign DOC_SCENES DOC_SCENES + 1
    %assign DOC_RUNTIME_CS DOC_RUNTIME_CS + %3
%endmacro

%macro DOC_END 0
    %if !DOC_ACTIVE
        %error "DOC_END requires DOC_BEGIN"
    %endif
    %assign DOC_ACTIVE 0
    db DOC_REC_END
    %xdefine DOC_DATA_END %%end
%%end:
    %if DOC_EXPECT_SOURCES < 0
        %error "DOC_BEGIN was not declared"
    %endif
    %if DOC_SOURCES != DOC_EXPECT_SOURCES
        %error "Documentary source count mismatch"
    %endif
    %if DOC_CLAIMS != DOC_EXPECT_CLAIMS
        %error "Documentary claim count mismatch"
    %endif
    %if DOC_SCENES != DOC_EXPECT_SCENES
        %error "Documentary scene count mismatch"
    %endif
    %if DOC_RUNTIME_CS != DOC_EXPECT_RUNTIME
        %error "Documentary runtime mismatch"
    %endif
%endmacro

%endif
