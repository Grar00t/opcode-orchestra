BITS 16
ORG 100h

jmp start

%include "opl2.inc"
%include "score.inc"

; =============================================================================
; WRAPPER LEDGER - 24-second original OPL2 theme
; Canonical source format: NASM score DSL.
; There is intentionally no JSONL or conversion step.
; =============================================================================

%define N_C   0159h
%define N_D   0183h
%define N_EB  019Ah
%define N_F   01CCh
%define N_G   0205h
%define N_AB  0223h
%define N_BB  0267h
%define R     0000h

start:
    cld
    call opl_init
    mov si, score

.next:
    lodsw
    cmp ax, 0FFFFh
    je .finished
    mov dx, ax
    lodsw
    mov cx, ax
    mov ax, dx
    call opl_play
    jmp .next

.finished:
    call opl_all_off
    mov ax, 4C00h
    int 21h

score:
    SCORE_BEGIN 2400

; 00:00 - BOOT PULSE (4.00 s)
    EV N_C,   50
    EV N_G,   50
    EV N_EB,  50
    EV N_BB,  50
    EV N_C,   50
    EV N_G,   50
    EV N_F,   50
    EV N_D,   50

; 00:04 - RISE (6.00 s)
    EV N_C,   50
    EV N_D,   50
    EV N_EB,  50
    EV N_F,   50
    EV N_G,   50
    EV N_AB,  50
    EV N_BB,  50
    EV N_AB,  50
    EV N_G,   50
    EV N_F,   50
    EV N_EB,  50
    EV N_D,   50

; 00:10 - LEDGER PULSE (8.00 s)
    EV N_C,  100
    EV N_G,  100
    EV N_BB, 100
    EV N_G,  100
    EV N_EB, 100
    EV N_BB, 100
    EV N_F,  100
    EV N_D,  100

; 00:18 - FAREWELL WRAPPERS CODA (6.00 s)
    EV N_G,  100
    EV N_F,  100
    EV N_EB, 100
    EV N_D,  100
    EV N_C,  200

    SCORE_END
