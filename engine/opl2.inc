; =============================================================================
; Opcode Orchestra — known-good AdLib / OPL2 engine
; Based on the raw port-388h test verified audible on DOSBox-X.
;
; Timing:
;   DOS INT 21h / AH=2Ch
;   1 unit = 1/100 second
;
; Audio:
;   three OPL2 channels
;   lower / middle / upper octave
;
; No INT 15h.
; No PC speaker.
; =============================================================================

OPL_PORT equ 0388h

; -----------------------------------------------------------------------------
; AL = register
; BL = value
; -----------------------------------------------------------------------------

opl_write:
    push ax
    push cx
    push dx

    mov dx, OPL_PORT
    out dx, al

    mov cx, 6
.addr_delay:
    in al, dx
    loop .addr_delay

    inc dx
    mov al, bl
    out dx, al

    dec dx
    mov cx, 35
.data_delay:
    in al, dx
    loop .data_delay

    pop dx
    pop cx
    pop ax
    ret

; -----------------------------------------------------------------------------
; Return AX = centiseconds inside current minute, 0..5999
; -----------------------------------------------------------------------------

clock_cs:
    push cx
    push dx
    push di

    mov ah, 2Ch
    int 21h

    ; DH = second
    ; DL = hundredths

    xor cx, cx
    mov cl, dl

    xor ax, ax
    mov al, dh

    mov di, 100
    mul di

    add ax, cx

    pop di
    pop dx
    pop cx
    ret

; -----------------------------------------------------------------------------
; CX = centiseconds
; -----------------------------------------------------------------------------

wait_cs:
    push ax
    push bx
    push cx
    push dx
    push si
    push di

    mov si, cx
    test si, si
    jz .done

    call clock_cs
    mov bx, ax

.wait:
    call clock_cs

    sub ax, bx
    jns .positive

    add ax, 6000

.positive:
    cmp ax, si
    jb .wait

.done:
    pop di
    pop si
    pop dx
    pop cx
    pop bx
    pop ax
    ret

; -----------------------------------------------------------------------------
; Key all three voices off.
; Release rate is non-zero now: no ten-second zombie note.
; -----------------------------------------------------------------------------

opl_all_off:
    push ax
    push bx

    mov al, 0B0h
    xor bl, bl
    call opl_write

    mov al, 0B1h
    xor bl, bl
    call opl_write

    mov al, 0B2h
    xor bl, bl
    call opl_write

    pop bx
    pop ax
    ret

; -----------------------------------------------------------------------------
; Initialise channel 0,1,2.
;
; Channel 0 = principal voice
; Channel 1 = lower octave
; Channel 2 = upper octave
;
; Carrier multiplier remains 1 so pitch stays correct.
; Modulators vary slightly for a richer attack.
; -----------------------------------------------------------------------------

opl_init:
    call opl_all_off

    ; waveform select enable
    mov al, 01h
    mov bl, 20h
    call opl_write

    ; -------------------------------------------------------------------------
    ; Channel 0
    ; modulator op 0, carrier op 3
    ; -------------------------------------------------------------------------

    mov al, 20h
    mov bl, 22h            ; sustain + multiplier 2
    call opl_write

    mov al, 23h
    mov bl, 21h            ; sustain + multiplier 1
    call opl_write

    mov al, 40h
    mov bl, 24h            ; modulator level
    call opl_write

    mov al, 43h
    mov bl, 00h            ; carrier loud
    call opl_write

    mov al, 60h
    mov bl, 0F3h           ; fast attack, modest decay
    call opl_write

    mov al, 63h
    mov bl, 0F2h
    call opl_write

    mov al, 80h
    mov bl, 36h            ; sustain + real release
    call opl_write

    mov al, 83h
    mov bl, 26h
    call opl_write

    mov al, 0E0h
    xor bl, bl
    call opl_write

    mov al, 0E3h
    xor bl, bl
    call opl_write

    mov al, 0C0h
    mov bl, 04h            ; feedback, FM connection
    call opl_write

    ; -------------------------------------------------------------------------
    ; Channel 1 — lower octave, slightly quieter
    ; -------------------------------------------------------------------------

    mov al, 21h
    mov bl, 21h
    call opl_write

    mov al, 24h
    mov bl, 21h
    call opl_write

    mov al, 41h
    mov bl, 28h
    call opl_write

    mov al, 44h
    mov bl, 0Ch
    call opl_write

    mov al, 61h
    mov bl, 0F3h
    call opl_write

    mov al, 64h
    mov bl, 0F2h
    call opl_write

    mov al, 81h
    mov bl, 36h
    call opl_write

    mov al, 84h
    mov bl, 26h
    call opl_write

    mov al, 0E1h
    xor bl, bl
    call opl_write

    mov al, 0E4h
    xor bl, bl
    call opl_write

    mov al, 0C1h
    mov bl, 04h
    call opl_write

    ; -------------------------------------------------------------------------
    ; Channel 2 — upper octave, quieter again
    ; -------------------------------------------------------------------------

    mov al, 22h
    mov bl, 23h            ; stronger harmonic modulator
    call opl_write

    mov al, 25h
    mov bl, 21h
    call opl_write

    mov al, 42h
    mov bl, 2Ch
    call opl_write

    mov al, 45h
    mov bl, 16h
    call opl_write

    mov al, 62h
    mov bl, 0F4h
    call opl_write

    mov al, 65h
    mov bl, 0F2h
    call opl_write

    mov al, 82h
    mov bl, 46h
    call opl_write

    mov al, 85h
    mov bl, 26h
    call opl_write

    mov al, 0E2h
    xor bl, bl
    call opl_write

    mov al, 0E5h
    xor bl, bl
    call opl_write

    mov al, 0C2h
    mov bl, 04h
    call opl_write

    ret

; -----------------------------------------------------------------------------
; AX = F-number
;
; Three octave layers:
;   ch0 block 4
;   ch1 block 3
;   ch2 block 5
; -----------------------------------------------------------------------------

opl_key_on:
    push ax
    push bx
    push si

    mov si, ax

    ; channel 0
    mov bx, si
    mov al, 0A0h
    call opl_write

    mov bx, si
    mov bl, bh
    and bl, 03h
    or bl, 30h             ; keyon + block 4
    mov al, 0B0h
    call opl_write

    ; channel 1
    mov bx, si
    mov al, 0A1h
    call opl_write

    mov bx, si
    mov bl, bh
    and bl, 03h
    or bl, 2Ch             ; keyon + block 3
    mov al, 0B1h
    call opl_write

    ; channel 2
    mov bx, si
    mov al, 0A2h
    call opl_write

    mov bx, si
    mov bl, bh
    and bl, 03h
    or bl, 34h             ; keyon + block 5
    mov al, 0B2h
    call opl_write

    pop si
    pop bx
    pop ax
    ret

; -----------------------------------------------------------------------------
; AX = F-number
; CX = duration in centiseconds
;
; 0 F-number = rest
;
; A short release gap separates repeated notes.
; -----------------------------------------------------------------------------

opl_play:
    push ax
    push bx
    push cx
    push dx
    push si

    mov si, ax
    mov dx, cx

    test si, si
    jz .rest

    mov ax, si
    call opl_key_on

    ; reserve ~30 ms for articulation on normal notes
    mov cx, dx
    cmp cx, 6
    jb .whole

    sub cx, 3
    call wait_cs

    call opl_all_off

    mov cx, 3
    call wait_cs
    jmp .done

.whole:
    call wait_cs
    call opl_all_off
    jmp .done

.rest:
    call opl_all_off
    mov cx, dx
    call wait_cs

.done:
    pop si
    pop dx
    pop cx
    pop bx
    pop ax
    ret
