; Opcode Orchestra - OPL rhythm/percussion backend

%ifndef OPCODE_ORCHESTRA_PERCUSSION_INC
%define OPCODE_ORCHESTRA_PERCUSSION_INC 1

OPL_RHYTHM_REG equ 0BDh
DRUM_BD equ 10h
DRUM_SD equ 08h
DRUM_TOM equ 04h
DRUM_CYM equ 02h
DRUM_HH equ 01h

opl_rhythm_init:
    ; Shared melodic voices use 0..2; rhythm exclusively owns 6..8.
    REQUIRE_OPL_ALLOCATION 3, 7, 1, 0
%assign __p 0
%rep 6
    REQUIRE_OPL_OPERATOR (16 + __p)
    mov al, 80h + 16 + __p
    mov bl, 26h
    call opl_write
    mov al, 0e0h + 16 + __p
    xor bl, bl
    call opl_write
    %assign __p __p + 1
%endrep
%assign __p 6
%rep 3
    mov al, 0b0h + __p
    xor bl, bl
    call opl_write
    mov al, 0c0h + __p
    mov bl, 30h               ; both OPL3 outputs; ignored in OPL2 mode
    call opl_write
    %assign __p __p + 1
%endrep
    ; Basic percussion operator setup on channels 6..8.
    mov al, 30h
    mov bl, 21h
    call opl_write
    mov al, 33h
    mov bl, 21h
    call opl_write
    mov al, 31h
    mov bl, 21h
    call opl_write
    mov al, 34h
    mov bl, 21h
    call opl_write
    mov al, 32h
    mov bl, 21h
    call opl_write
    mov al, 35h
    mov bl, 21h
    call opl_write
    mov al, 50h
    mov bl, 10h
    call opl_write
    mov al, 53h
    mov bl, 00h
    call opl_write
    mov al, 51h
    mov bl, 18h
    call opl_write
    mov al, 54h
    mov bl, 08h
    call opl_write
    mov al, 52h
    mov bl, 18h
    call opl_write
    mov al, 55h
    mov bl, 08h
    call opl_write
    mov al, 70h
    mov bl, 0F2h
    call opl_write
    mov al, 73h
    mov bl, 0F2h
    call opl_write
    mov al, 71h
    mov bl, 0F2h
    call opl_write
    mov al, 74h
    mov bl, 0F2h
    call opl_write
    mov al, 72h
    mov bl, 0F2h
    call opl_write
    mov al, 75h
    mov bl, 0F2h
    call opl_write
    ; Seed rhythm-channel pitches before enabling rhythm mode.
    mov al, 0A6h
    mov bl, 80h
    call opl_write
    mov al, 0B6h
    mov bl, 0Ch
    call opl_write
    mov al, 0A7h
    mov bl, 50h
    call opl_write
    mov al, 0B7h
    mov bl, 0Ch
    call opl_write
    mov al, 0A8h
    mov bl, 30h
    call opl_write
    mov al, 0B8h
    mov bl, 10h
    call opl_write
    mov al, OPL_RHYTHM_REG
    mov bl, 20h
    call opl_write
    ret

; AL = DRUM_* mask, CX = hit length in centiseconds.
opl_drum_hit:
    test al, 0e0h
    jnz .invalid
    push ax
    push bx
    push cx
    mov bl, al
    or bl, 20h
    mov al, OPL_RHYTHM_REG
    call opl_write
    call wait_cs
    mov al, OPL_RHYTHM_REG
    mov bl, 20h
    call opl_write
    pop cx
    pop bx
    pop ax
    clc
    ret
.invalid:
    stc
    ret

opl_rhythm_off:
    mov al, OPL_RHYTHM_REG
    xor bl, bl
    call opl_write
    ret

%endif
