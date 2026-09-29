; NASM-native score v1: little-endian u16 F-number, u16 centiseconds.
; F-number 0 is rest; FFFF,0000 is the unique final sentinel.
%ifndef OPCODE_ORCHESTRA_SCORE_INC
%define OPCODE_ORCHESTRA_SCORE_INC 1
%include "contracts.inc"
%assign SCORE_ACTIVE 0
%assign SCORE_CS 0
%assign SCORE_EVENTS 0
%assign SCORE_EXPECTED_CS -1
%macro SCORE_BEGIN 1
    %if SCORE_ACTIVE
        %error "Nested SCORE_BEGIN"
    %endif
    REQUIRE_RANGE %1, 1, 0x7fffffff, "Score runtime must be positive signed-32-bit centiseconds"
    %assign SCORE_ACTIVE 1
    %assign SCORE_CS 0
    %assign SCORE_EVENTS 0
    %assign SCORE_EXPECTED_CS %1
    %xdefine SCORE_DATA_BEGIN %%start
%%start:
%endmacro
%macro EV 2
    %if !SCORE_ACTIVE
        %error "EV requires SCORE_BEGIN"
    %endif
    REQUIRE_RANGE %1, 0, 1023, "Score note must be an OPL F-number 0..1023"
    REQUIRE_RANGE %2, 1, 65535, "Score event duration must be 1..65535"
    dw %1, %2
    %assign SCORE_CS SCORE_CS + %2
    %assign SCORE_EVENTS SCORE_EVENTS + 1
%endmacro
%macro SCORE_END 0
    %if !SCORE_ACTIVE
        %error "SCORE_END requires SCORE_BEGIN"
        %exitmacro
    %endif
    %if SCORE_EVENTS = 0
        %error "Score contains no events"
    %endif
    %if SCORE_CS != SCORE_EXPECTED_CS
        %error "Score duration does not match SCORE_BEGIN contract"
    %endif
    %if ($ - SCORE_DATA_BEGIN) != SCORE_EVENTS * 4
        %error "Score record alignment mismatch"
    %endif
    dw 0xffff, 0
    %xdefine SCORE_DATA_END %%end
%%end:
    %assign SCORE_ACTIVE 0
%endmacro
%endif
