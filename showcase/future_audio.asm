BITS 16
ORG 100h
jmp start

%include "status.inc"

%include "vga13.inc"
%include "opl2.inc"
%include "fnum_notes.inc"
%include "instruments.inc"
%include "opl3.inc"
%include "percussion.inc"

; Future Audio Pack demo:
; OPL3 stereo + instrument switching + rhythm mode + 4-op + VGA sync.

start:
    push cs
    pop ds
    cld
    call vga_mode13
    jc video_failure
    mov al, 0
    call vga_clear

    call opl_init
    jc opl_failure
    call opl3_enable
    jc opl3_failure
    call opl3_stereo_default
    call opl_rhythm_init

    mov al, INSTR_LEAD
    call instrument_select

    mov ax, 18
    mov bx, 40
    mov cx, 90
    mov dl, 11
    call vga_hline
    mov ax, N_C
    mov cx, 20
    call opl_play

    mov al, DRUM_BD
    mov cx, 6
    call opl_drum_hit
    mov al, INSTR_BASS
    call instrument_select
    mov ax, 52
    mov bx, 70
    mov cx, 120
    mov dl, 13
    call vga_hline
    mov ax, N_G
    mov cx, 20
    call opl_play

    mov al, DRUM_SD | DRUM_HH
    mov cx, 6
    call opl_drum_hit

    mov al, INSTR_BELL
    call instrument_select
    mov ax, 86
    mov bx, 100
    mov cx, 150
    mov dl, 14
    call vga_hline
    mov ax, N_E
    mov cx, 20
    call opl_play

    call opl3_4op_voice_init
    mov ax, N_C
    call opl3_4op_key_on
    mov cx, 30
    call wait_cs
    call opl3_4op_off
    call opl3_4op_disable_all

    mov al, DRUM_CYM | DRUM_TOM
    mov cx, 8
    call opl_drum_hit

    xor ah, ah
    int 16h
    call opl_rhythm_off
    call opl_all_off
    call vga_text_mode
    call opl_shutdown
    mov ax, 4C00h
    int 21h

video_failure:
    mov al, OO_VIDEO
    jmp program_failure

opl_failure:
    mov al, OO_OPL
    jmp program_failure

opl3_failure:
    mov al, OO_OPL3
    jmp program_failure

program_failure:
    push ax
    call opl_shutdown
    call vga_text_mode
    pop ax
    jmp oo_fail
