; Opcode Orchestra - OPL3 extensions (YMF262 compatible)
; Bank 0 uses 388/389, bank 1 uses 38A/38B.

%ifndef OPCODE_ORCHESTRA_OPL3_INC
%define OPCODE_ORCHESTRA_OPL3_INC 1

OPL3_PORT_B equ 038Ah
OPL3_PAN_LEFT  equ 10h
OPL3_PAN_RIGHT equ 20h
OPL3_PAN_BOTH  equ 30h

opl3_write1:
    push dx
    mov dx, OPL3_PORT_B
    call opl_write_port
    pop dx
    ret

opl3_enable:
    cmp byte [opl_kind], 3
    jne .unavailable
    mov byte [opl3_active], 1
    mov al, 05h
    mov bl, 01h
    call opl3_write1
    clc
    ret
.unavailable:
    stc
    ret
; DL=channel 0..8, BL=OPL3_PAN_*, CL=feedback/connection low nibble
opl3_set_pan:
    cmp byte [opl3_active], 1
    jne .invalid
    cmp dl, 8
    ja .invalid
    test bl, 0cfh
    jnz .invalid
    cmp cl, 15
    ja .invalid
    push ax
    push si
    xor ax, ax
    mov al, dl
    mov si, ax
    mov [opl_pan + si], bl
    or bl, cl
    mov al, 0c0h
    add al, dl
    call opl_write
    pop si
    pop ax
    clc
    ret
.invalid:
    stc
    ret

opl3_stereo_default:
    mov dl, 0
    mov bl, OPL3_PAN_LEFT
    mov cl, 04h
    call opl3_set_pan
    mov dl, 1
    mov bl, OPL3_PAN_BOTH
    mov cl, 04h
    call opl3_set_pan
    mov dl, 2
    mov bl, OPL3_PAN_RIGHT
    mov cl, 04h
    call opl3_set_pan
    ret

; Enable 4-operator pair channels 0+3 via register 0x104 bit 0.
opl3_4op_enable_pair0:
    mov al, 04h
    mov bl, 01h
    call opl3_write1
    ret

opl3_4op_disable_all:
    mov al, 04h
    xor bl, bl
    call opl3_write1
    ret
; Simple 4-op voice using channel pair 0+3.
opl3_4op_voice_init:
    call opl3_enable
    jc .done
    call opl3_4op_enable_pair0
    ; Explicit waveform state for all four operators, not inherited timbre.
    REQUIRE_OPL_ALLOCATION 3, 6, 1, 1
%assign __op 0
%rep 4
    %if __op = 0
        %assign __offset 0
    %elif __op = 1
        %assign __offset 3
    %elif __op = 2
        %assign __offset 8
    %else
        %assign __offset 11
    %endif
    REQUIRE_OPL_OPERATOR __offset
    mov al, 0e0h + __offset
    xor bl, bl
    call opl_write
    %assign __op __op + 1
%endrep
    ; operators: ch0 mod/car = 00/03, ch3 mod/car = 08/0B
    mov al, 20h
    mov bl, 21h
    call opl_write
    mov al, 23h
    mov bl, 22h
    call opl_write
    mov al, 28h
    mov bl, 31h
    call opl_write
    mov al, 2Bh
    mov bl, 21h
    call opl_write
    mov al, 40h
    mov bl, 18h
    call opl_write
    mov al, 43h
    mov bl, 10h
    call opl_write
    mov al, 48h
    mov bl, 20h
    call opl_write
    mov al, 4Bh
    mov bl, 00h
    call opl_write
    mov al, 60h
    mov bl, 0F2h
    call opl_write
    mov al, 63h
    mov bl, 0F2h
    call opl_write
    mov al, 68h
    mov bl, 0E3h
    call opl_write
    mov al, 6Bh
    mov bl, 0F2h
    call opl_write
    mov al, 80h
    mov bl, 35h
    call opl_write
    mov al, 83h
    mov bl, 25h
    call opl_write
    mov al, 88h
    mov bl, 45h
    call opl_write
    mov al, 8Bh
    mov bl, 25h
    call opl_write
    mov al, 0C0h
    mov bl, OPL3_PAN_BOTH | 00h
    call opl_write
    mov al, 0C3h
    mov bl, OPL3_PAN_BOTH | 01h
    call opl_write
    clc
.done:
    ret

; AX = F-number, channels 0+3 form the 4-op voice at block 4.
opl3_4op_key_on:
    cmp byte [opl3_active], 1
    jne .invalid
    cmp ax, 1023
    ja .invalid
    push ax
    push bx
    push si
    mov si, ax
    mov bx, si
    mov al, 0A0h
    call opl_write
    mov bx, si
    mov bl, bh
    and bl, 03h
    or bl, 30h
    mov al, 0B0h
    call opl_write
    mov bx, si
    mov al, 0A3h
    call opl_write
    mov bx, si
    mov bl, bh
    and bl, 03h
    or bl, 30h
    mov al, 0B3h
    call opl_write
    pop si
    pop bx
    pop ax
    clc
    ret
.invalid:
    stc
    ret

opl3_4op_off:
    mov al, 0B0h
    xor bl, bl
    call opl_write
    mov al, 0B3h
    xor bl, bl
    call opl_write
    ret

%endif
