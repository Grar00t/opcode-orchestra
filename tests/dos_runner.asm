; Test-only DOS parent. Executes an UNMODIFIED child COM via DOS 4B00h.
; Receipt: guest exit status, restored mode/PIC/vector, and BIOS ticks.
BITS 16
ORG 100h
%ifndef TEST_PROGRAM
    %error "TEST_PROGRAM must name a built DOS 8.3 executable"
%endif
start:
    cli
    mov ax, cs
    mov ss, ax
    mov sp, stack_top
    sti
    mov ds, ax
    mov es, ax
    cld
    mov [params+4], ax
    mov [params+8], ax
    mov [params+12], ax
    mov bx, (stack_top + 15 - $$ + 100h) / 16
    mov ah, 4ah
    int 21h
    jc execution_failed
    mov ah, 0fh
    int 10h
    mov [saved_mode], al
    in al, 21h
    mov [saved_pic], al
    mov ax, 350fh
    int 21h
    mov [saved_vector], bx
    mov [saved_vector+2], es
    call ticks
    mov [receipt+8], dx
    mov [receipt+10], cx
    ; Enter for the child's BIOS keyboard wait; no changes to the child.
    mov ah, 05h
    mov cx, 1c0dh
    int 16h
    push ds
    pop es
    mov bx, params
    mov dx, program
    mov ax, 4b00h
    int 21h
    jc execution_failed
    mov ah, 4dh
    int 21h
    mov [cs:receipt+5], al
    push cs
    pop ds
    call ticks
    mov [receipt+12], dx
    mov [receipt+14], cx
    mov ah, 0fh
    int 10h
    cmp al, [saved_mode]
    je .video_ok
    or byte [receipt+6], 1
.video_ok:
    in al, 21h
    cmp al, [saved_pic]
    je .pic_ok
    or byte [receipt+6], 4
.pic_ok:
    mov ax, 350fh
    int 21h
    cmp bx, [saved_vector]
    jne .vector_bad
    mov ax, es
    cmp ax, [saved_vector+2]
    je save
.vector_bad:
    or byte [receipt+6], 2
    jmp save
execution_failed:
    push cs
    pop ds
    or byte [receipt+6], 8
save:
    mov dx, filename
    xor cx, cx
    mov ah, 3ch
    int 21h
    jc failed
    mov bx, ax
    mov dx, receipt
    mov cx, 16
    mov ah, 40h
    int 21h
    jc failed
    cmp ax, 16
    jne failed
    mov ah, 3eh
    int 21h
    jc failed
    mov ax, 4c00h
    int 21h
failed:
    mov ax, 4c01h
    int 21h
ticks:
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
program db TEST_PROGRAM,0
filename db 'RECEIPT.BIN',0
params dw 0, tail, 0, 5ch, 0, 6ch, 0
tail db 0,13
saved_mode db 0
saved_pic db 0
saved_vector dd 0
receipt db 'OORT',1,255,0,0
        dd 0,0
times 256 db 0
stack_top:
