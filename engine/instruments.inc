; Opcode Orchestra - compact OPL2 instrument bank
; Each record: mod20,car20,mod40,car40,mod60,car60,mod80,car80,modE0,carE0,C0

%ifndef OPCODE_ORCHESTRA_INSTRUMENTS_INC
%define OPCODE_ORCHESTRA_INSTRUMENTS_INC 1

INSTR_LEAD  equ 0
INSTR_BASS  equ 1
INSTR_BELL  equ 2
INSTR_BRASS equ 3
INSTR_COUNT equ 4
INSTR_SIZE  equ 11

instrument_select:
    cmp al, INSTR_COUNT
    jae .invalid
    push ax
    push bx
    push si
    cmp al, INSTR_BASS
    je .bass
    cmp al, INSTR_BELL
    je .bell
    cmp al, INSTR_BRASS
    je .brass
    mov si, instrument_lead
    jmp .apply
.bass:
    mov si, instrument_bass
    jmp .apply
.bell:
    mov si, instrument_bell
    jmp .apply
.brass:
    mov si, instrument_brass
.apply:
    ; Apply the same timbre to layered channels 0..2.
%assign __ch 0
%rep 3
    mov al, 20h + __ch
    mov bl, [si + 0]
    call opl_write
    mov al, 23h + __ch
    mov bl, [si + 1]
    call opl_write
    mov al, 40h + __ch
    mov bl, [si + 2]
    call opl_write
    mov al, 43h + __ch
    mov bl, [si + 3]
    call opl_write
    mov al, 60h + __ch
    mov bl, [si + 4]
    call opl_write
    mov al, 63h + __ch
    mov bl, [si + 5]
    call opl_write
    mov al, 80h + __ch
    mov bl, [si + 6]
    call opl_write
    mov al, 83h + __ch
    mov bl, [si + 7]
    call opl_write
    mov al, 0E0h + __ch
    mov bl, [si + 8]
    call opl_write
    mov al, 0E3h + __ch
    mov bl, [si + 9]
    call opl_write
    mov al, 0C0h + __ch
    mov bl, [si + 10]
    or bl, [opl_pan + __ch]     ; timbre must not erase OPL3 stereo routing
    call opl_write
%assign __ch __ch + 1
%endrep
    pop si
    pop bx
    pop ax
    clc
    ret
.invalid:
    stc
    ret

instrument_lead:
    db 22h,21h,24h,00h,0F3h,0F2h,36h,26h,00h,00h,04h
instrument_bass:
    db 21h,21h,18h,04h,0F4h,0E2h,47h,27h,00h,00h,06h
instrument_bell:
    db 35h,21h,10h,02h,0F1h,0F1h,05h,05h,01h,00h,02h
instrument_brass:
    db 32h,21h,1Ch,00h,0E3h,0F2h,54h,34h,00h,00h,05h

%if ($ - instrument_lead) != (INSTR_COUNT * INSTR_SIZE)
    %error "instrument bank size mismatch"
%endif

%endif
