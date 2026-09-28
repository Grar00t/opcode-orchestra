; Opcode Orchestra - Media Opcode v2
; Deterministic drawing bytecode interpreted by 16-bit x86.

MEDIA_VERSION equ 2

OP_END    equ 00h
OP_CLEAR  equ 01h
OP_PIXEL  equ 02h
OP_HLINE  equ 03h
OP_RECT   equ 04h
OP_TEXT   equ 05h

%macro M_END 0
    db OP_END
%endmacro

%macro M_CLEAR 1
    db OP_CLEAR, %1
%endmacro

%macro M_PIXEL 3
    db OP_PIXEL
    dw %1, %2
    db %3
%endmacro

%macro M_HLINE 4
    db OP_HLINE
    dw %1, %2, %3
    db %4
%endmacro
%macro M_RECT 5
    db OP_RECT
    dw %1, %2, %3, %4
    db %5
%endmacro

; x,y,color,scale,length,"TEXT"
%macro M_TEXT 6
    db OP_TEXT
    dw %1, %2
    db %3, %4, %5
    db %6
%endmacro

media_x         dw 0
media_y         dw 0
media_w         dw 0
media_h         dw 0
media_color     db 0
media_scale     db 1
media_text_len  db 0

; DS:SI -> Media Opcode stream
media_execute:
.next:
    lodsb
    cmp al, OP_END
    je .done
    cmp al, OP_CLEAR
    je .clear
    cmp al, OP_PIXEL
    je .pixel
    cmp al, OP_HLINE
    je .hline
    cmp al, OP_RECT
    je .rect
    cmp al, OP_TEXT
    je .text
    jmp .invalid

.clear:
    lodsb
    call vga_clear
    jmp .next

.pixel:
    lodsw
    mov [media_x], ax
    lodsw
    mov bx, ax
    lodsb
    mov cl, al
    mov ax, [media_x]
    call vga_putpixel
    jmp .next

.hline:
    lodsw
    mov [media_x], ax
    lodsw
    mov [media_y], ax
    lodsw
    mov cx, ax
    lodsb
    mov dl, al
    mov ax, [media_x]
    mov bx, [media_y]
    call vga_hline
    jmp .next

.rect:
    lodsw
    mov [media_x], ax
    lodsw
    mov [media_y], ax
    lodsw
    mov [media_w], ax
    lodsw
    mov [media_h], ax
    lodsb
    mov [media_color], al
    xor bp, bp
.rect_row:
    cmp bp, [media_h]
    jae .next
    mov ax, [media_x]
    mov bx, [media_y]
    add bx, bp
    mov cx, [media_w]
    mov dl, [media_color]
    call vga_hline
    inc bp
    jmp .rect_row
.text:
    lodsw
    mov [media_x], ax
    lodsw
    mov [media_y], ax
    lodsb
    mov [media_color], al
    lodsb
    mov [media_scale], al
    lodsb
    mov [media_text_len], al

.text_loop:
    cmp byte [media_text_len], 0
    je .next
    lodsb
    mov bx, [media_x]
    mov dx, [media_y]
    mov cl, [media_color]
    mov ch, [media_scale]
    call vga_draw_char5x7

    xor ax, ax
    mov al, [media_scale]
    mov bl, 6
    mul bl
    add [media_x], ax
    dec byte [media_text_len]
    jmp .text_loop

.invalid:
    mov ax, 4C02h
    int 21h
.done:
    ret
