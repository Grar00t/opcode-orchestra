; Short I/O setup delays using the already-running PC PIT, not CPU loops.
; Assumes channel 0: reload 65536, mode 2 or 3, 1.193182 MHz. No reprogramming.
; Mode 3 may decrement by two: 8 counts >= 3.35 us, 200 >= 83.8 us.
; CF=1 if the counter does not advance within 65535 observations.
; GP/segment registers, IF and DF preserved; arithmetic flags otherwise undefined.
%ifndef OO_ISA_DELAY_INC
%define OO_ISA_DELAY_INC 1
isa_pit_read:
    pushf
    cli                         ; serialize the shared latch + low/high reads
    mov al, 0
    out 43h, al
    in al, 40h
    mov ah, al
    in al, 40h
    xchg al, ah
    popf
    ret
; CX = minimum down-counter counts. Used only for 8 and 200 counts here.
isa_delay_min:
    push ax
    push bx
    push si
    push di
    call isa_pit_read
    mov si, ax
    mov di, 65535
.wait:
    call isa_pit_read
    mov bx, si
    sub bx, ax
    cmp bx, cx
    jae .ready
    dec di
    jnz .wait
    stc
    jmp .done
.ready:
    clc
.done:
    pop di
    pop si
    pop bx
    pop ax
    ret
%endif
