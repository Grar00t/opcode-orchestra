; Opcode Orchestra - VGA Mode 13h primitives
; 320x200, 256-color linear framebuffer at A000:0000.

VGA_SEGMENT equ 0A000h
VGA_WIDTH   equ 320
VGA_HEIGHT  equ 200

vga_saved_mode db 3
vga_saved_page db 0
vga_saved_es dw 0
vga_active db 0

; CF=0 when BIOS reports mode 13h, ES=A000; GP registers preserved.
; CF=1 on failure/nested acquisition. No silent text-mode fallback.
vga_mode13:
    cmp byte [vga_active], 0
    jne .fail
    pusha
    mov [vga_saved_es], es
    mov ah, 0fh
    int 10h
    and al, 7fh
    mov [vga_saved_mode], al
    mov [vga_saved_page], bh
    mov byte [vga_active], 1
    mov ax, 0013h
    int 10h
    mov ah, 0fh
    int 10h
    and al, 7fh
    cmp al, 13h
    jne .restore
    mov ax, VGA_SEGMENT
    mov es, ax
    popa
    clc
    ret
.restore:
    call vga_text_mode
    popa
.fail:
    stc
    ret

; Historical name retained: restores entry mode/page, not always text mode 3.
; Does NOT restore previous framebuffer pixels or arbitrary custom palettes.
vga_text_mode:
    cmp byte [vga_active], 0
    je .done
    pusha
    xor ax, ax
    mov al, [vga_saved_mode]
    int 10h
    mov ah, 05h
    mov al, [vga_saved_page]
    int 10h
    mov es, [vga_saved_es]
    mov byte [vga_active], 0
    popa
.done:
    ret

; AL = palette index
vga_clear:
    pushf
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
    popf
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
    pushf
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
    ; Clip before adding to the framebuffer offset (no u16 wrap).
    mov si, VGA_WIDTH
    sub si, ax
    cmp cx, si
    jbe .clipped
    mov cx, si
.clipped:
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
    popf
    ret
