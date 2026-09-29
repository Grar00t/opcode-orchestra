; Opcode Orchestra - compact 5x7 uppercase font renderer
; AL=ASCII, BX=x, DX=y, CL=color, CH=scale

font_base_x  dw 0
font_base_y  dw 0
font_draw_x  dw 0
font_draw_y  dw 0
font_color   db 0
font_scale   db 1
font_bits    db 0
font_row     db 0
font_col     db 0
font_fill    db 0

vga_draw_char5x7:
    push ax
    push bx
    push cx
    push dx
    push si
    push di
    push bp

    cmp bx, VGA_WIDTH
    jae .done
    cmp dx, VGA_HEIGHT
    jae .done
    test ch, ch
    jz .done
    mov [font_base_x], bx
    mov [font_base_y], dx
    mov [font_color], cl
    mov [font_scale], ch
    cmp al, ' '
    je .done
    cmp al, 'A'
    jb .done
    cmp al, 'Z'
    ja .done

    sub al, 'A'
    xor ah, ah
    mov di, ax
    mov ax, di
    shl ax, 3
    sub ax, di
    mov si, font5x7_data
    add si, ax

    mov byte [font_row], 0
.row_loop:
    cmp byte [font_row], 7
    jae .done
    lodsb
    mov [font_bits], al
    mov byte [font_col], 0

.col_loop:
    cmp byte [font_col], 5
    jae .next_row
    mov al, [font_bits]
    mov ah, 10h
    mov cl, [font_col]
    shr ah, cl
    test al, ah
    jz .skip_pixel

    xor ax, ax
    mov al, [font_col]
    mov cl, [font_scale]
    mul cl
    add ax, [font_base_x]
    mov [font_draw_x], ax

    xor ax, ax
    mov al, [font_row]
    mov cl, [font_scale]
    mul cl
    add ax, [font_base_y]
    mov [font_draw_y], ax

    mov byte [font_fill], 0
.fill_loop:
    mov al, [font_fill]
    cmp al, [font_scale]
    jae .skip_pixel
    mov ax, [font_draw_x]
    mov bx, [font_draw_y]
    xor cx, cx
    mov cl, [font_scale]
    mov dl, [font_color]
    call vga_hline
    inc word [font_draw_y]
    inc byte [font_fill]
    jmp .fill_loop
.skip_pixel:
    inc byte [font_col]
    jmp .col_loop

.next_row:
    inc byte [font_row]
    jmp .row_loop

.done:
    pop bp
    pop di
    pop si
    pop dx
    pop cx
    pop bx
    pop ax
    ret

; A-Z, 5 bits per row, 7 rows per glyph.
font5x7_data:
    db 0Eh,11h,11h,1Fh,11h,11h,11h ; A
    db 1Eh,11h,11h,1Eh,11h,11h,1Eh ; B
    db 0Fh,10h,10h,10h,10h,10h,0Fh ; C
    db 1Eh,11h,11h,11h,11h,11h,1Eh ; D
    db 1Fh,10h,10h,1Eh,10h,10h,1Fh ; E
    db 1Fh,10h,10h,1Eh,10h,10h,10h ; F
    db 0Fh,10h,10h,17h,11h,11h,0Fh ; G
    db 11h,11h,11h,1Fh,11h,11h,11h ; H
    db 1Fh,04h,04h,04h,04h,04h,1Fh ; I
    db 07h,02h,02h,02h,12h,12h,0Ch ; J
    db 11h,12h,14h,18h,14h,12h,11h ; K
    db 10h,10h,10h,10h,10h,10h,1Fh ; L
    db 11h,1Bh,15h,15h,11h,11h,11h ; M
    db 11h,19h,15h,13h,11h,11h,11h ; N
    db 0Eh,11h,11h,11h,11h,11h,0Eh ; O
    db 1Eh,11h,11h,1Eh,10h,10h,10h ; P
    db 0Eh,11h,11h,11h,15h,12h,0Dh ; Q
    db 1Eh,11h,11h,1Eh,14h,12h,11h ; R
    db 0Fh,10h,10h,0Eh,01h,01h,1Eh ; S
    db 1Fh,04h,04h,04h,04h,04h,04h ; T
    db 11h,11h,11h,11h,11h,11h,0Eh ; U
    db 11h,11h,11h,11h,11h,0Ah,04h ; V
    db 11h,11h,11h,15h,15h,1Bh,11h ; W
    db 11h,11h,0Ah,04h,0Ah,11h,11h ; X
    db 11h,11h,0Ah,04h,04h,04h,04h ; Y
    db 1Fh,01h,02h,04h,08h,10h,1Fh ; Z

%if ($ - font5x7_data) != 26 * 7
    %error "Font table must contain 26 seven-row glyphs"
%endif
