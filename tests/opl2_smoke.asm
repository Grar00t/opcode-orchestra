BITS 16
ORG 100h

jmp start

; ------------------------------------------------------------
; Raw AdLib / OPL2 test
; Channel 0, operators 0 and 3
; No project engine involved.
; ------------------------------------------------------------

opl_write:
    push ax
    push cx
    push dx

    mov dx, 0388h
    out dx, al

    mov cx, 6
.d1:
    in al, dx
    loop .d1

    inc dx
    mov al, bl
    out dx, al

    dec dx
    mov cx, 35
.d2:
    in al, dx
    loop .d2

    pop dx
    pop cx
    pop ax
    ret

wait_3s:
    push ax
    push bx
    push cx
    push dx

    xor ah, ah
    int 1Ah
    mov bx, dx

.wait:
    xor ah, ah
    int 1Ah
    sub dx, bx
    cmp dx, 55
    jb .wait

    pop dx
    pop cx
    pop bx
    pop ax
    ret

start:

    ; Reset key-on
    mov al, 0B0h
    mov bl, 00h
    call opl_write

    ; Enable waveform selection
    mov al, 01h
    mov bl, 20h
    call opl_write

    ; Modulator:
    ; sustain enabled, multiplier 1
    mov al, 20h
    mov bl, 21h
    call opl_write

    ; Carrier:
    ; sustain enabled, multiplier 1
    mov al, 23h
    mov bl, 21h
    call opl_write

    ; Modulator quiet
    mov al, 40h
    mov bl, 3Fh
    call opl_write

    ; Carrier loud
    mov al, 43h
    mov bl, 00h
    call opl_write

    ; Instant attack, zero decay
    mov al, 60h
    mov bl, 0F0h
    call opl_write

    mov al, 63h
    mov bl, 0F0h
    call opl_write

    ; Sustain at full level, slow/no release
    mov al, 80h
    mov bl, 00h
    call opl_write

    mov al, 83h
    mov bl, 00h
    call opl_write

    ; Sine waveform
    mov al, 0E0h
    mov bl, 00h
    call opl_write

    mov al, 0E3h
    mov bl, 00h
    call opl_write

    ; FM connection
    mov al, 0C0h
    mov bl, 00h
    call opl_write

    ; A4 ≈ 440 Hz
    ; FNUM = 0244h, BLOCK = 4

    mov al, 0A0h
    mov bl, 44h
    call opl_write

    ; FNUM high=2
    ; BLOCK 4 = 100b << 2 = 10h
    ; KEYON = 20h
    ; total = 32h

    mov al, 0B0h
    mov bl, 32h
    call opl_write

    call wait_3s

    ; Key off
    mov al, 0B0h
    mov bl, 12h
    call opl_write

    mov ax, 4C00h
    int 21h
