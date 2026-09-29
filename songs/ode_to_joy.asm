BITS 16
ORG 100h
jmp start

%include "status.inc"

%include "opl2.inc"
%include "fnum_notes.inc"
%include "score.inc"
%include "instruments.inc"

; Beethoven, Symphony No. 9 - Ode to Joy opening phrase (public domain).
start:
    push cs
    pop ds
    cld
    call opl_init
    jc opl_failure
    mov al, INSTR_BRASS
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
    EV N_E, 50
    EV N_E, 50
    EV N_F, 50
    EV N_G, 50
    EV N_G, 50
    EV N_F, 50
    EV N_E, 50
    EV N_D, 50
    EV N_C, 50
    EV N_C, 50
    EV N_D, 50
    EV N_E, 50
    EV N_E, 50
    EV N_D, 50
    EV N_D, 50
    EV R,   50
    SCORE_END

opl_failure:
    mov al, OO_OPL
    jmp program_failure

program_failure:
    push ax
    call opl_shutdown
    pop ax
    jmp oo_fail
