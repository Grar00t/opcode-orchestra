; Opcode Orchestra - ASM-native Documentary DSL
%ifndef OPCODE_ORCHESTRA_DOCUMENTARY_INC
%define OPCODE_ORCHESTRA_DOCUMENTARY_INC 1

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
    db DOC_REC_SOURCE, %1, %2
    dw %3
    %assign DOC_SOURCES DOC_SOURCES + 1
%endmacro

%macro DOC_CLAIM 3
    %if %3 > 100
        %error "Documentary confidence must be 0..100"
    %endif
    db DOC_REC_CLAIM, %1, %2, %3
    %assign DOC_CLAIMS DOC_CLAIMS + 1
%endmacro
%macro DOC_SCENE 5
    db DOC_REC_SCENE, %1, %2, %4, %5
    dw %3
    %assign DOC_SCENES DOC_SCENES + 1
    %assign DOC_RUNTIME_CS DOC_RUNTIME_CS + %3
%endmacro

%macro DOC_END 0
    db DOC_REC_END
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
