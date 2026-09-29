; Stable DOS process statuses. DS=CS, DF=0. oo_fail does not return.
%ifndef OO_STATUS_INC
%define OO_STATUS_INC 1
OO_VIDEO equ 2
OO_OPL equ 3
OO_OPL3 equ 4
OO_MEDIA equ 5
OO_PCM equ 6
OO_ARGUMENT equ 7
oo_fail:
    mov bl, al
    xor bh, bh
    cmp bl, 2
    jb .unknown
    cmp bl, 7
    ja .unknown
    sub bx, 2
    shl bx, 1
    mov dx, [oo_errors + bx]
    jmp .print
.unknown:
    mov dx, oo_unknown
.print:
    push ax
    mov ah, 09h
    int 21h
    pop ax
    mov ah, 4ch
    int 21h
oo_errors: dw oo_video, oo_opl, oo_opl3, oo_media, oo_pcm, oo_argument
oo_video: db 'VGA mode 13h unavailable',13,10,'$'
oo_opl: db 'OPL timer/status probe failed',13,10,'$'
oo_opl3: db 'This program requires OPL3',13,10,'$'
oo_media: db 'Invalid or truncated media stream',13,10,'$'
oo_pcm: db 'PCM setup, transfer or cleanup failed',13,10,'$'
oo_argument: db 'Invalid engine argument',13,10,'$'
oo_unknown: db 'Unknown runtime error',13,10,'$'
%endif
