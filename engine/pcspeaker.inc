; Opcode Orchestra - PC Speaker engine
PIT_CH2 equ 42h
PIT_CONTROL equ 43h
SPKR_PORT equ 61h

speaker_off:
    in al, SPKR_PORT
    and al, 0FCh
    out SPKR_PORT, al
    ret

wait_ticks:
    push ax
    push bx
    push dx
    push si
    mov bx, cx
    test bx, bx
    jz .done
    xor ah, ah
    int 1Ah
    mov si, dx
.wait:
    xor ah, ah
    int 1Ah
    sub dx, si
    cmp dx, bx
    jb .wait
.done:
    pop si
    pop dx
    pop bx
    pop ax
    ret

play_note:
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
