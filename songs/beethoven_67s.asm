BITS 16
ORG 100h

jmp start

%include "status.inc"

%include "opl2.inc"
%include "score.inc"

; =============================================================================
; Opcode Orchestra
; Beethoven 5 — 67-second OPL2 study
;
; The opening uses the public-domain Symphony No. 5 motif.
; Following sections are original FM variations built for this demo.
;
; Timing unit:
;   1 = 1 centisecond
;
; Score runtime:
;   exactly 6700 centiseconds = 67.00 seconds
;   excluding the final FM release tail.
; =============================================================================

%define N_C   0159h
%define N_D   0183h
%define N_EB  019Ah
%define N_F   01CCh
%define N_G   0205h
%define N_AB  0223h
%define N_BB  0267h
%define R     0000h

%define EIGHTH 28


start:
    push cs
    pop ds
    cld

    call opl_init
    jc opl_failure

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

    call opl_shutdown
    mov ax, 4C00h
    int 21h

score:
    SCORE_BEGIN 6700

; =============================================================================
; 00:00.00 — ORIGINAL OPENING
; Runtime: 6.84 s
; =============================================================================

    EV R,     28
    EV N_G,   28
    EV N_G,   28
    EV N_G,   28
    EV N_EB, 180

    EV R,     28
    EV N_F,   28
    EV N_F,   28
    EV N_F,   28
    EV N_D,  280

; =============================================================================
; 00:06.84 — VARIATION A
; Runtime: 8.00 s
; =============================================================================

    EV N_G,  50
    EV N_G,  50
    EV N_EB, 50
    EV N_F,  50

    EV N_G,  50
    EV N_G,  50
    EV N_EB, 50
    EV N_D,  50

    EV N_F,  50
    EV N_F,  50
    EV N_D,  50
    EV N_EB, 50

    EV N_G,  50
    EV N_F,  50
    EV N_EB, 50
    EV N_D,  50

; =============================================================================
; 00:14.84 — VARIATION A REPRISE
; Runtime: 8.00 s
; =============================================================================

    EV N_G,  50
    EV N_G,  50
    EV N_EB, 50
    EV N_F,  50

    EV N_G,  50
    EV N_G,  50
    EV N_EB, 50
    EV N_D,  50

    EV N_F,  50
    EV N_F,  50
    EV N_D,  50
    EV N_EB, 50

    EV N_G,  50
    EV N_F,  50
    EV N_EB, 50
    EV N_D,  50

; =============================================================================
; 00:22.84 — VARIATION B
; Runtime: 8.00 s
; =============================================================================

    EV N_C,  100
    EV N_G,  100
    EV N_EB, 100
    EV N_F,  100

    EV N_D,  100
    EV N_F,  100
    EV N_EB, 100
    EV N_D,  100

; =============================================================================
; 00:30.84 — VARIATION B REPRISE
; Runtime: 8.00 s
; =============================================================================

    EV N_C,  100
    EV N_G,  100
    EV N_EB, 100
    EV N_F,  100

    EV N_D,  100
    EV N_F,  100
    EV N_EB, 100
    EV N_D,  100

; =============================================================================
; 00:38.84 — DARK BRIDGE
; Runtime: 10.00 s
; =============================================================================

    EV N_C,  100
    EV N_D,  100
    EV N_EB, 100
    EV N_F,  100
    EV N_G,  100

    EV N_AB, 100
    EV N_G,  100
    EV N_F,  100
    EV N_EB, 100
    EV N_D,  100

; =============================================================================
; 00:48.84 — OPENING REPRISE
; Runtime: 6.84 s
; =============================================================================

    EV R,     28
    EV N_G,   28
    EV N_G,   28
    EV N_G,   28
    EV N_EB, 180

    EV R,     28
    EV N_F,   28
    EV N_F,   28
    EV N_F,   28
    EV N_D,  280

; =============================================================================
; 00:55.68 — CODA
; Runtime: 11.32 s
; =============================================================================

    EV N_G,  100
    EV N_G,  100
    EV N_G,  100
    EV N_EB, 100

    EV N_F,  150
    EV N_F,  150
    EV N_D,  166
    EV N_C,  266

    SCORE_END

opl_failure:
    mov al, OO_OPL
    jmp program_failure

program_failure:
    push ax
    call opl_shutdown
    pop ax
    jmp oo_fail
