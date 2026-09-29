; Opcode Orchestra - Media Opcode v2
; Deterministic drawing bytecode interpreted by 16-bit x86.

%include "contracts.inc"
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
    REQUIRE_RANGE %1, 0, 255, "Media color must be u8"
    db OP_CLEAR, %1
%endmacro

%macro M_PIXEL 3
    REQUIRE_RANGE %1, 0, 65535, "Media x must be u16"
    REQUIRE_RANGE %2, 0, 65535, "Media y must be u16"
    REQUIRE_RANGE %3, 0, 255, "Media color must be u8"
    db OP_PIXEL
    dw %1, %2
    db %3
%endmacro

%macro M_HLINE 4
    REQUIRE_RANGE %1, 0, 65535, "Media x must be u16"
    REQUIRE_RANGE %2, 0, 65535, "Media y must be u16"
    REQUIRE_RANGE %3, 0, 65535, "Media width must be u16"
    REQUIRE_RANGE %4, 0, 255, "Media color must be u8"
    db OP_HLINE
    dw %1, %2, %3
    db %4
%endmacro
%macro M_RECT 5
    REQUIRE_RANGE %1, 0, 65535, "Media x must be u16"
    REQUIRE_RANGE %2, 0, 65535, "Media y must be u16"
    REQUIRE_RANGE %3, 0, 65535, "Media width must be u16"
    REQUIRE_RANGE %4, 0, 65535, "Media height must be u16"
    REQUIRE_RANGE %5, 0, 255, "Media color must be u8"
    db OP_RECT
    dw %1, %2, %3, %4
    db %5
%endmacro

; x,y,color,scale,length,"TEXT"
%macro M_TEXT 6
    REQUIRE_RANGE %1, 0, 65535, "Media x must be u16"
    REQUIRE_RANGE %2, 0, 65535, "Media y must be u16"
    REQUIRE_RANGE %3, 0, 255, "Media color must be u8"
    REQUIRE_RANGE %4, 1, 255, "Media scale must be 1..255"
    REQUIRE_RANGE %5, 0, 255, "Media text length must be u8"
    %strlen %%length %6
    %if %%length != (%5)
        %error "Media text length mismatch"
    %endif
    db OP_TEXT
    dw %1, %2
    db %3, %4, %5
    db %6
%endmacro

media_end       dw 0
media_x         dw 0
media_y         dw 0
media_w         dw 0
media_h         dw 0
media_color     db 0
media_scale     db 1
media_text_len  db 0

; DS:SI -> stream; DI -> exclusive end, no segment wrap allowed.
; CF=0 iff exactly terminated; CF=1 malformed. Never exits DOS internally.
; Clobbers AX,BX,CX,DX,SI,BP, arithmetic flags; preserves DI/segments/IF/DF.
media_execute:
    mov [media_end], di
    cmp si, di
    jae .invalid
.next:
    mov cx, 1
    call .need
    jc .invalid
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
    mov cx, 1
    call .need
    jc .invalid
    lodsb
    call vga_clear
    jmp .next

.pixel:
    mov cx, 5
    call .need
    jc .invalid
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
    mov cx, 7
    call .need
    jc .invalid
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
    mov cx, 9
    call .need
    jc .invalid
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
    cmp word [media_x], VGA_WIDTH
    jae .next
    mov ax, [media_y]
    cmp ax, VGA_HEIGHT
    jae .next
    mov bx, VGA_HEIGHT
    sub bx, ax
    cmp [media_h], bx
    jbe .rect_clipped
    mov [media_h], bx
.rect_clipped:
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
    mov cx, 7
    call .need
    jc .invalid
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
    xor cx, cx
    mov cl, al
    call .need
    jc .invalid
    cmp byte [media_scale], 0
    je .invalid
.text_loop:
    cmp byte [media_text_len], 0
    je .next
    lodsb
    cmp word [media_x], VGA_WIDTH
    jae .text_skip
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
.text_skip:
    dec byte [media_text_len]
    jmp .text_loop

.need:
    mov ax, [media_end]
    sub ax, si
    jc .need_fail
    cmp ax, cx
    ret
.need_fail:
    stc
    ret
.invalid:
    stc
    ret
.done:
    cmp si, [media_end]
    jne .invalid
    clc
    ret
