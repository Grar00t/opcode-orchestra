BITS 16
ORG 100h

jmp start

%include "vga13.inc"
%include "font5x7.inc"
%include "media_ops.inc"
%include "opl2.inc"
%include "mlasm_scene.inc"

%define N_C  0159h
%define N_EB 019Ah
%define N_G  0205h
%define N_BB 0267h

start:
    push cs
    pop ds
    cld

    call vga_mode13
    mov si, scene
    call media_execute

    call opl_init
    mov ax, N_C
    mov cx, 18
    call opl_play
    mov ax, N_EB
    mov cx, 18
    call opl_play
    mov ax, N_G
    mov cx, 18
    call opl_play
    mov ax, N_BB
    mov cx, 28
    call opl_play
    call opl_all_off

    xor ah, ah
    int 16h

    call vga_text_mode
    mov ax, 4C00h
    int 21h

scene:
    M_CLEAR THEME_BG

    ; luminous frame
    M_RECT 0, 0, 320, 4, THEME_ACCENT1
    M_RECT 0, 196, 320, 4, THEME_ACCENT2
    M_RECT 0, 0, 4, 200, THEME_ACCENT3
    M_RECT 316, 0, 4, 200, THEME_LINE

    ; layered neon horizon
    M_RECT 4, 70, 312, 18, 1
    M_RECT 4, 88, 312, 18, 5
    M_RECT 4, 106, 312, 18, 4
    M_RECT 4, 124, 312, 18, 6
    M_RECT 4, 142, 312, 18, 8
    ; ASSEMBLY banner - per-letter vertical offsets come from MLAsm
    M_TEXT 40, 18 + WAVE_0, THEME_ACCENT1, 5, 1, "A"
    M_TEXT 70, 18 + WAVE_1, THEME_ACCENT2, 5, 1, "S"
    M_TEXT 100,18 + WAVE_2, THEME_ACCENT3, 5, 1, "S"
    M_TEXT 130,18 + WAVE_3, THEME_LINE,    5, 1, "E"
    M_TEXT 160,18 + WAVE_4, THEME_ACCENT1,5, 1, "M"
    M_TEXT 190,18 + WAVE_5, THEME_ACCENT2,5, 1, "B"
    M_TEXT 220,18 + WAVE_6, THEME_ACCENT3,5, 1, "L"
    M_TEXT 250,18 + WAVE_7, THEME_LINE,    5, 1, "Y"

    M_TEXT 74, 58, 15, 1, 25, "MLASM TO OPCODE ORCHESTRA"

    ; central processor / circuit board
    M_RECT 56, 92, 208, 58, 8
    M_RECT 60, 96, 200, 50, THEME_PANEL
    M_RECT 104, 101, 112, 40, 0
    M_RECT 108, 105, 104, 32, THEME_PANEL
    M_TEXT 115, 110, THEME_LINE, 3, 5, "MLASM"

    ; chip pins
    M_RECT 42, 98, 14, 4, THEME_ACCENT1
    M_RECT 42, 110,14, 4, THEME_ACCENT2
    M_RECT 42, 122,14, 4, THEME_ACCENT3
    M_RECT 42, 134,14, 4, THEME_LINE
    M_RECT 264, 98, 14, 4, THEME_ACCENT1
    M_RECT 264, 110,14, 4, THEME_ACCENT2
    M_RECT 264, 122,14, 4, THEME_ACCENT3
    M_RECT 264, 134,14, 4, THEME_LINE

    ; circuit traces
    M_HLINE 12, 84, 92, THEME_ACCENT1
    M_HLINE 216,84, 92, THEME_ACCENT2
    M_HLINE 18, 156, 86, THEME_ACCENT3
    M_HLINE 216,156, 86, THEME_LINE
    M_PIXEL 12,84,15
    M_PIXEL 307,84,15
    M_PIXEL 18,156,15
    M_PIXEL 301,156,15

    M_TEXT 106, 151, 15, 1, 17, "SIMD MEDIA BRIDGE"
    M_TEXT 58, 174, THEME_ACCENT2, 2, 17, "FAREWELL WRAPPERS"
    M_END
scene_end:

%if MEDIA_VERSION != 2
    %error "unexpected media opcode version"
%endif

%if (scene_end - scene) <= 1
    %error "empty MLAsm showcase scene"
%endif

%if (scene_end - scene) > 2048
    %error "MLAsm showcase exceeds 2 KiB scene contract"
%endif
