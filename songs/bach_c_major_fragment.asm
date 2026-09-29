BITS 16
ORG 100h
jmp start

%include "status.inc"

%include "opl2.inc"
%include "fnum_notes.inc"
%include "score.inc"
%include "instruments.inc"

; J.S. Bach, Prelude in C major BWV 846 - compact public domain arpeggio study.
start:
    push cs
    pop ds
    cld
    call opl_init
    jc opl_failure
    mov al, INSTR_BELL
    call instrument_select
    mov si, score
.next:
    lodsw
    cmp ax, 0FFFFh
    je .done
    mov dx, ax
    lodsw
    mov cx, ax
    mov ax, dx
    call opl_play
    jmp .next
.done:
    call opl_all_off
    call opl_shutdown
    mov ax, 4C00h
    int 21h

score:
    SCORE_BEGIN 800
    EV N_C, 40
    EV N_E, 40
    EV N_G, 40
    EV N_C, 40
    EV N_E, 40
    EV N_G, 40
    EV N_C, 40
    EV N_E, 40
    EV N_D, 40
    EV N_F, 40
    EV N_A, 40
    EV N_D, 40
    EV N_F, 40
    EV N_A, 40
    EV N_D, 40
    EV N_F, 40
    EV N_C, 40
    EV N_E, 40
    EV N_G, 40
    EV R,   40
    SCORE_END

opl_failure:
    mov al, OO_OPL
    jmp program_failure

program_failure:
    push ax
    call opl_shutdown
    pop ax
    jmp oo_fail
