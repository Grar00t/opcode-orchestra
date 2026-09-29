; Opcode Orchestra - PC Speaker engine
PIT_CH2 equ 42h
PIT_CONTROL equ 43h
SPKR_PORT equ 61h

speaker_off:
    in al, SPKR_PORT
    and al, 0FCh
    out SPKR_PORT, al
    ret


; CX:DX = atomic BIOS day ticks. Does not consume the midnight flag.
speaker_clock_ticks:
    push ax
    push es
    pushf
    cli
    mov ax, 40h
    mov es, ax
    mov dx, [es:6ch]
    mov cx, [es:6eh]
    popf
    pop es
    pop ax
    ret

; CX = 0..65535 ticks. All GP/segments and IF/DF preserved.
; Requires an advancing BIOS clock; no real-time bound is claimed.
wait_ticks:
    pusha
    mov si, cx
    test si, si
    jz .done
    call speaker_clock_ticks
    mov bx, dx
    mov di, cx
.wait:
    call speaker_clock_ticks
    mov ax, dx
    sub ax, bx
    cmp cx, di
    je .delta
    test cx, cx
    jnz .delta
    add ax, 00b0h           ; BIOS day length 0018:00B0 ticks
.delta:
    mov bx, dx
    mov di, cx
    cmp ax, si
    jae .done
    sub si, ax
    jmp .wait
.done:
    popa
    ret

; BX=0 (rest) or 19..65535 Hz, CX=BIOS ticks; CF=1 on invalid pitch.
play_note:
    test bx, bx
    jz .valid
    cmp bx, 19               ; smaller divisors overflow the 16-bit DIV quotient
    jb .invalid
.valid:
    push ax
    push bx
    push cx
    push dx
    test bx, bx
    jz .delay
    mov dx, 0012h
    mov ax, 34DEh
    div bx
    mov dx, ax
    mov al, 0B6h
    out PIT_CONTROL, al
    mov ax, dx
    out PIT_CH2, al
    mov al, ah
    out PIT_CH2, al
    in al, SPKR_PORT
    or al, 03h
    out SPKR_PORT, al
.delay:
    call wait_ticks
    call speaker_off
    pop dx
    pop cx
    pop bx
    pop ax
    clc
    ret
.invalid:
    stc
    ret

play_song:
.next:
    lodsw
    cmp ax, 0FFFFh
    je .done
    mov bx, ax
    lodsw
    mov cx, ax
    call play_note
    jmp .next
.done:
    call speaker_off
    ret
