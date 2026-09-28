; Opcode Orchestra - VGA Mode 13h primitives
; 320x200, 256-color linear framebuffer at A000:0000.

VGA_SEGMENT equ 0A000h
VGA_WIDTH   equ 320
VGA_HEIGHT  equ 200

vga_mode13:
    mov ax, 0013h
    int 10h
    mov ax, VGA_SEGMENT
    mov es, ax
    ret

vga_text_mode:
    mov ax, 0003h
    int 10h
    ret

; AL = palette index
vga_clear:
    push ax
    push cx
    push di
    mov ah, al
    xor di, di
    mov cx, (VGA_WIDTH * VGA_HEIGHT) / 2
    cld
    rep stosw
    pop di
    pop cx
    pop ax
    ret

; AX=x, BX=y, CL=color
vga_putpixel:
    push ax
    push bx
    push cx
    push dx
    push di
    cmp ax, VGA_WIDTH - 1
    ja .done
    cmp bx, VGA_HEIGHT - 1
    ja .done
    mov dx, bx
    shl bx, 6
    shl dx, 8
    add bx, dx
    add bx, ax
    mov di, bx
    mov al, cl
    mov [es:di], al
.done:
    pop di
    pop dx
    pop cx
    pop bx
    pop ax
    ret

; AX=x, BX=y, CX=length, DL=color
vga_hline:
    push ax
    push bx
    push cx
    push dx
    push si
    push di
    cmp bx, VGA_HEIGHT - 1
    ja .done
    cmp ax, VGA_WIDTH - 1
    ja .done
    test cx, cx
    jz .done
    mov si, bx
    shl bx, 6
    shl si, 8
    add bx, si
    add bx, ax
    mov di, bx
    mov al, dl
    cld
    rep stosb
.done:
    pop di
    pop si
    pop dx
    pop cx
    pop bx
    pop ax
    ret
