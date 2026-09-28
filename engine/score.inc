; =============================================================================
; Opcode Orchestra - ASM-native score contract
;
; The score source IS Assembly. No JSONL, no parser, no conversion layer.
;
; Usage:
;   SCORE_BEGIN 2400
;   EV N_G, 25
;   EV R,   10
;   SCORE_END
;
; Timing unit: 1 = 1 centisecond.
; SCORE_END emits the runtime sentinel and rejects duration drift at build time.
; =============================================================================

%ifndef OPCODE_ORCHESTRA_SCORE_INC
%define OPCODE_ORCHESTRA_SCORE_INC 1

%assign SCORE_CS 0
%assign SCORE_EVENTS 0
%assign SCORE_EXPECTED_CS -1

%macro SCORE_BEGIN 1
    %assign SCORE_CS 0
    %assign SCORE_EVENTS 0
    %assign SCORE_EXPECTED_CS %1
%endmacro

%macro EV 2
    dw %1, %2
    %assign SCORE_CS SCORE_CS + %2
    %assign SCORE_EVENTS SCORE_EVENTS + 1
%endmacro

%macro SCORE_END 0
    dw 0FFFFh, 0
    %if SCORE_EXPECTED_CS < 0
        %error "SCORE_BEGIN was not declared"
    %endif
    %if SCORE_EVENTS = 0
        %error "Score contains no events"
    %endif
    %if SCORE_CS != SCORE_EXPECTED_CS
        %error "Score duration does not match SCORE_BEGIN contract"
    %endif
%endmacro

%endif
