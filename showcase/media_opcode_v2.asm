BITS 16
ORG 100h

jmp start

%include "status.inc"

%include "vga13.inc"
%include "font5x7.inc"
%include "media_ops.inc"

start:
    push cs
    pop ds
    cld
    call vga_mode13
    jc video_failure

    mov si, scene
    mov di, scene_end
    call media_execute
    jc media_failure

    xor ah, ah
    int 16h

    call vga_text_mode
    mov ax, 4C00h
    int 21h

; Media Opcode v2 demo: desert sunset + tower.
scene:
    M_CLEAR 1
    M_RECT 0, 120, 320, 80, 6
    M_HLINE 0, 119, 320, 9

    ; sun
    M_RECT 252, 35, 20, 20, 14
    M_RECT 248, 41, 28, 8, 14

    ; layered dunes
    M_HLINE 0, 128, 110, 14
    M_HLINE 18, 127, 92, 14
    M_HLINE 40, 126, 70, 14
    M_HLINE 205, 134, 115, 12
    M_HLINE 230, 133, 90, 12
    M_HLINE 255, 132, 65, 12

    ; tower silhouette
    M_RECT 145, 72, 30, 68, 8
    M_RECT 151, 62, 18, 10, 8
    M_RECT 157, 52, 6, 10, 8
    M_RECT 150, 82, 5, 7, 11
    M_RECT 165, 82, 5, 7, 11
    M_RECT 150, 98, 5, 7, 11
    M_RECT 165, 98, 5, 7, 11
    M_RECT 157, 119, 6, 21, 0

    ; foreground markers prove single-pixel opcode path
    M_PIXEL 16, 180, 15
    M_PIXEL 303, 180, 15
    M_END
scene_end:

%if MEDIA_VERSION != 2
    %error "unexpected media opcode version"
%endif

%if (scene_end - scene) <= 1
    %error "empty media opcode stream"
%endif

%if (scene_end - scene) > 512
    %error "media opcode demo exceeds 512-byte contract"
%endif

video_failure:
    mov al, OO_VIDEO
    jmp program_failure

media_failure:
    mov al, OO_MEDIA
    jmp program_failure

program_failure:
    push ax
    call vga_text_mode
    pop ax
    jmp oo_fail
