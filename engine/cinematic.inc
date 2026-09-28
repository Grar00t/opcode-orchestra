; Opcode Orchestra - cinematic VGA helpers
%ifndef OPCODE_ORCHESTRA_CINEMATIC_INC
%define OPCODE_ORCHESTRA_CINEMATIC_INC 1

CIN_BLACK equ 0
CIN_NAVY  equ 1
CIN_BLUE  equ 2
CIN_TEAL  equ 3
CIN_GOLD  equ 4
CIN_AMBER equ 5
CIN_WHITE equ 6
CIN_GRAY  equ 7
CIN_RED   equ 8
CIN_GREEN equ 9
CIN_CYAN  equ 10
CIN_INK   equ 11
CIN_SAND  equ 12
CIN_SKY   equ 13
CIN_NIGHT equ 14
CIN_HOT   equ 15

cinematic_palette:
    db 00,00,00,  03,05,12,  05,10,24,  04,20,22
    db 48,32,06,  63,38,08,  58,58,55,  22,24,28
    db 42,08,06,  08,36,18,  08,42,48,  02,03,05
    db 42,28,12,  18,34,52,  04,07,16,  63,22,04

cinema_palette_init:
    push ax
    push cx
    push dx
    push si
    mov dx, 03C8h
    xor al, al
    out dx, al
    inc dx
    mov si, cinematic_palette
    mov cx, 48
.next:
    lodsb
    out dx, al
    loop .next
    pop si
    pop dx
    pop cx
    pop ax
    ret

; AX=x, BX=y, CX=width, SI=height, DL=color
cinema_fill_rect:
    push ax
    push bx
    push cx
    push dx
    push si
    push di
    mov di, si
.row:
    test di, di
    jz .done
    call vga_hline
    inc bx
    dec di
    jmp .row
.done:
    pop di
    pop si
    pop dx
    pop cx
    pop bx
    pop ax
    ret

; DS:SI=zero-terminated text, BX=x, DX=y, CL=color, CH=scale
cinema_text:
    push ax
    push bx
    push cx
    push dx
    push si
    push di
.next_char:
    lodsb
    test al, al
    jz .done
    call vga_draw_char5x7
    xor ax, ax
    mov al, ch
    mov di, ax
    shl ax, 1
    add ax, di
    shl ax, 1
    add bx, ax
    jmp .next_char
.done:
    pop di
    pop si
    pop dx
    pop cx
    pop bx
    pop ax
    ret

; AX=x, BX=y, CX=height, DL=color
cinema_vline:
    push ax
    push bx
    push cx
    push dx
.loop:
    test cx, cx
    jz .done
    push cx
    mov cl, dl
    call vga_putpixel
    pop cx
    inc bx
    dec cx
    jmp .loop
.done:
    pop dx
    pop cx
    pop bx
    pop ax
    ret

cinema_letterbox:
    push ax
    push bx
    push cx
    push dx
    push si
    xor ax, ax
    xor bx, bx
    mov cx, 320
    mov si, 12
    mov dl, CIN_BLACK
    call cinema_fill_rect
    xor ax, ax
    mov bx, 188
    mov cx, 320
    mov si, 12
    mov dl, CIN_BLACK
    call cinema_fill_rect
    pop si
    pop dx
    pop cx
    pop bx
    pop ax
    ret

cinema_frame:
    push ax
    push bx
    push cx
    push dx
    mov ax, 10
    mov bx, 10
    mov cx, 300
    mov dl, CIN_GOLD
    call vga_hline
    mov bx, 189
    call vga_hline
    mov ax, 10
    mov bx, 10
    mov cx, 180
    mov dl, CIN_GOLD
    call cinema_vline
    mov ax, 309
    call cinema_vline
    pop dx
    pop cx
    pop bx
    pop ax
    ret

; DS:SI=text
cinema_lower_third:
    push ax
    push bx
    push cx
    push dx
    push si
    mov ax, 16
    mov bx, 154
    mov cx, 288
    mov si, 26
    mov dl, CIN_INK
    call cinema_fill_rect
    mov ax, 16
    mov bx, 154
    mov cx, 288
    mov dl, CIN_GOLD
    call vga_hline
    pop si
    mov bx, 24
    mov dx, 163
    mov cl, CIN_WHITE
    mov ch, 1
    call cinema_text
    pop dx
    pop cx
    pop bx
    pop ax
    ret

cinema_wipe_black:
    push ax
    push bx
    push cx
    push dx
    push si
    xor ax, ax
.wipe:
    cmp ax, 320
    jae .done
    push ax
    xor bx, bx
    mov cx, 16
    mov si, 200
    mov dl, CIN_BLACK
    call cinema_fill_rect
    pop ax
    add ax, 16
    jmp .wipe
.done:
    pop si
    pop dx
    pop cx
    pop bx
    pop ax
    ret

%endif
