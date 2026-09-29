BITS 16
ORG 100h

jmp start

%include "status.inc"

%include "vga13.inc"
%include "font5x7.inc"
%include "cinematic.inc"
%include "opl2.inc"
%include "fnum_notes.inc"
%include "instruments.inc"
%include "opl3.inc"
%include "percussion.inc"
%include "documentary.inc"

documentary_ledger:
%include "assembly_beneath_wrapper.inc"
%if DOC_SCENE1_CS != 600
    %error "scene 1 choreography drift"
%endif
%if DOC_SCENE2_CS != 700
    %error "scene 2 choreography drift"
%endif
%if DOC_SCENE3_CS != 700
    %error "scene 3 choreography drift"
%endif
%if DOC_SCENE4_CS != 700
    %error "scene 4 choreography drift"
%endif
%if DOC_SCENE5_CS != 600
    %error "scene 5 choreography drift"
%endif
%if DOC_SCENE6_CS != 700
    %error "scene 6 choreography drift"
%endif
%if DOC_SCENE7_CS != 500
    %error "scene 7 choreography drift"
%endif

scene_offset dw 0
scene_phase  dw 0

start:
    push cs
    pop ds
    cld
    call vga_mode13
    jc video_failure
    call cinema_palette_init
    call opl_init
    jc opl_failure
    call opl3_enable
    jc opl3_failure
    call opl3_stereo_default
    call opl_rhythm_init

    call scene_title
    call cinema_wipe_black
    call scene_machine
    call cinema_wipe_black
    call scene_evidence_flow
    call cinema_wipe_black
    call scene_trace
    call cinema_wipe_black
    call scene_landscape
    call cinema_wipe_black
    call scene_spectrum
    call cinema_wipe_black
    call scene_coda

    call opl_rhythm_off
    call opl_all_off
    call vga_text_mode
    call opl_shutdown
    mov ax, 4C00h
    int 21h

play_100:
    mov cx, 100
    call opl_play
    ret

scene_title:
    mov al, CIN_NIGHT
    call vga_clear
    call cinema_frame
    mov si, txt_assembly
    mov bx, 88
    mov dx, 58
    mov cl, CIN_GOLD
    mov ch, 3
    call cinema_text
    mov si, txt_beneath
    mov bx, 102
    mov dx, 94
    mov cl, CIN_WHITE
    mov ch, 1
    call cinema_text
    mov si, txt_compiled
    call cinema_lower_third
    call cinema_letterbox

    mov al, INSTR_BRASS
    call instrument_select
    mov ax, N_C
    call play_100
    mov ax, N_G
    call play_100
    mov ax, N_EB
    call play_100
    mov ax, N_F
    call play_100
    mov ax, N_G
    call play_100
    mov ax, N_C
    call play_100
    ret

draw_machine_frame:
    mov al, CIN_NAVY
    call vga_clear
    call cinema_frame
    mov si, txt_machine
    mov bx, 94
    mov dx, 28
    mov cl, CIN_WHITE
    mov ch, 2
    call cinema_text

    mov ax, 68
    add ax, [scene_offset]
    mov bx, 58
    mov cx, 164
    mov si, 74
    mov dl, CIN_GOLD
    call cinema_fill_rect
    mov ax, 70
    add ax, [scene_offset]
    mov bx, 60
    mov cx, 160
    mov si, 70
    mov dl, CIN_INK
    call cinema_fill_rect

    mov si, txt_asm
    mov bx, 123
    add bx, [scene_offset]
    mov dx, 82
    mov cl, CIN_CYAN
    mov ch, 3
    call cinema_text

    mov ax, 18
    mov bx, 72
    mov cx, 52
    mov dl, CIN_TEAL
    call vga_hline
    mov bx, 91
    call vga_hline
    mov bx, 110
    call vga_hline

    mov ax, 230
    add ax, [scene_offset]
    mov bx, 72
    mov cx, 68
    mov dl, CIN_TEAL
    call vga_hline
    mov bx, 91
    call vga_hline
    mov bx, 110
    call vga_hline

    mov si, txt_direct
    call cinema_lower_third
    call cinema_letterbox
    ret

scene_machine:
    mov word [scene_offset], 0
    mov al, INSTR_LEAD
    call instrument_select
    mov bp, DOC_SCENE2_CS / 100
.loop:
    call draw_machine_frame
    mov ax, N_D
    test bp, 1
    jnz .tone
    mov ax, N_G
.tone:
    call play_100
    add word [scene_offset], 3
    dec bp
    jnz .loop
    ret

draw_evidence_flow:
    mov al, CIN_INK
    call vga_clear
    call cinema_frame
    mov si, txt_source_claim
    mov bx, 70
    mov dx, 28
    mov cl, CIN_GOLD
    mov ch, 2
    call cinema_text

    mov ax, [scene_phase]
    mov cx, ax
    shl ax, 4
    shl cx, 2
    add ax, cx
    add ax, 40
    mov di, ax

    mov ax, 32
    mov bx, 66
    mov cx, di
    mov si, 14
    mov dl, CIN_TEAL
    call cinema_fill_rect
    mov ax, 32
    mov bx, 91
    mov cx, di
    add cx, 28
    mov si, 14
    mov dl, CIN_BLUE
    call cinema_fill_rect
    mov ax, 32
    mov bx, 116
    mov cx, di
    add cx, 56
    mov si, 14
    mov dl, CIN_AMBER
    call cinema_fill_rect

    mov si, txt_evidence_story
    call cinema_lower_third
    call cinema_letterbox
    ret

scene_evidence_flow:
    mov word [scene_phase], 0
    mov al, INSTR_BASS
    call instrument_select
    mov bp, DOC_SCENE3_CS / 100
.loop:
    call draw_evidence_flow
    mov ax, N_EB
    test bp, 1
    jnz .tone
    mov ax, N_F
.tone:
    call play_100
    inc word [scene_phase]
    dec bp
    jnz .loop
    ret

scene_trace:
    mov al, CIN_NAVY
    call vga_clear
    call cinema_frame
    mov si, txt_every_scene
    mov bx, 16
    mov dx, 28
    mov cl, CIN_WHITE
    mov ch, 2
    call cinema_text

    mov ax, 28
    mov bx, 66
    mov cx, 72
    mov si, 52
    mov dl, CIN_TEAL
    call cinema_fill_rect
    mov ax, 124
    mov bx, 66
    mov cx, 72
    mov si, 52
    mov dl, CIN_BLUE
    call cinema_fill_rect
    mov ax, 220
    mov bx, 66
    mov cx, 72
    mov si, 52
    mov dl, CIN_AMBER
    call cinema_fill_rect

    mov si, txt_source
    mov bx, 40
    mov dx, 84
    mov cl, CIN_WHITE
    mov ch, 1
    call cinema_text
    mov si, txt_claim
    mov bx, 142
    mov dx, 84
    call cinema_text
    mov si, txt_scene
    mov bx, 238
    mov dx, 84
    call cinema_text

    mov si, txt_traceable
    call cinema_lower_third
    call cinema_letterbox

    mov al, INSTR_BELL
    call instrument_select
    mov ax, N_C
    call play_100
    mov ax, N_E
    call play_100
    mov ax, N_G
    call play_100
    mov ax, N_BB
    call play_100
    mov ax, N_G
    call play_100
    mov ax, N_E
    call play_100
    mov ax, N_C
    call play_100
    ret

draw_landscape_frame:
    mov al, CIN_SKY
    call vga_clear
    call cinema_frame

    mov ax, 0
    mov bx, 120
    mov cx, 320
    mov si, 68
    mov dl, CIN_SAND
    call cinema_fill_rect

    mov ax, 54
    mov bx, 96
    mov cx, 210
    mov si, 24
    mov dl, CIN_NAVY
    call cinema_fill_rect
    mov ax, 78
    mov bx, 84
    mov cx, 160
    mov si, 18
    mov dl, CIN_BLUE
    call cinema_fill_rect

    mov ax, [scene_phase]
    mov cx, ax
    shl ax, 4
    shl cx, 2
    add ax, cx
    add ax, 36
    mov bx, 48
    mov cx, 14
    mov si, 14
    mov dl, CIN_HOT
    call cinema_fill_rect

    mov si, txt_silicon_story
    mov bx, 34
    mov dx, 24
    mov cl, CIN_WHITE
    mov ch, 2
    call cinema_text
    mov si, txt_machine_story
    call cinema_lower_third
    call cinema_letterbox
    ret

scene_landscape:
    mov word [scene_phase], 0
    mov al, INSTR_BRASS
    call instrument_select
    mov bp, DOC_SCENE5_CS / 100
.loop:
    call draw_landscape_frame
    mov ax, N_F
    test bp, 1
    jnz .tone
    mov ax, N_A
.tone:
    call play_100
    inc word [scene_phase]
    dec bp
    jnz .loop
    ret

draw_spectrum_frame:
    push bp ; scene_spectrum owns BP as its frame counter
    mov al, CIN_INK
    call vga_clear
    call cinema_frame

    mov si, txt_one_timeline
    mov bx, 74
    mov dx, 24
    mov cl, CIN_CYAN
    mov ch, 1
    call cinema_text

    mov bp, spectrum_heights
    add bp, [scene_phase]
    mov di, 34
    mov cx, 8
.bar_loop:
    xor ax, ax
    mov al, [bp]
    mov si, ax
    mov bx, 142
    sub bx, ax
    mov ax, di
    push cx
    mov cx, 20
    mov dl, CIN_GOLD
    call cinema_fill_rect
    pop cx
    add di, 30
    inc bp
    loop .bar_loop

    mov si, txt_score_drives
    call cinema_lower_third
    call cinema_letterbox
    pop bp
    ret

scene_spectrum:
    mov word [scene_phase], 0
    mov al, INSTR_BELL
    call instrument_select
    mov bp, DOC_SCENE6_CS / 100
.loop:
    call draw_spectrum_frame
    mov al, OPL_RHYTHM_REG
    mov bl, 20h | DRUM_BD | DRUM_HH
    call opl_write
    mov ax, N_G
    call play_100
    mov al, OPL_RHYTHM_REG
    mov bl, 20h
    call opl_write
    inc word [scene_phase]
    dec bp
    jnz .loop
    ret

scene_coda:
    mov al, CIN_BLACK
    call vga_clear
    call cinema_frame

    mov si, txt_ledger_remains
    mov bx, 52
    mov dx, 62
    mov cl, CIN_GOLD
    mov ch, 2
    call cinema_text

    mov si, txt_source_claim_scene
    mov bx, 92
    mov dx, 104
    mov cl, CIN_WHITE
    mov ch, 1
    call cinema_text

    mov si, txt_documentary_mode
    call cinema_lower_third
    call cinema_letterbox

    call opl3_4op_voice_init
    mov ax, N_C
    call opl3_4op_key_on
    mov cx, DOC_SCENE7_CS
    call wait_cs
    call opl3_4op_off
    call opl3_4op_disable_all
    ret

spectrum_heights:
    db 24,44,68,36,78,52,88,42,62,30,72,48,82,38,58

txt_assembly:          db "ASSEMBLY",0
txt_beneath:           db "BENEATH THE WRAPPER",0
txt_compiled:          db "A DOCUMENTARY COMPILED BY NASM",0
txt_machine:           db "THE MACHINE",0
txt_asm:               db "ASM",0
txt_direct:            db "DIRECT PORT WRITES NO GUESSWORK",0
txt_source_claim:      db "SOURCE TO CLAIM",0
txt_evidence_story:    db "EVIDENCE BECOMES STORY",0
txt_every_scene:       db "EVERY SCENE HAS A SOURCE",0
txt_source:            db "SOURCE",0
txt_claim:             db "CLAIM",0
txt_scene:             db "SCENE",0
txt_traceable:         db "TRACEABLE FROM SOURCE TO CUT",0
txt_silicon_story:     db "FROM SILICON TO STORY",0
txt_machine_story:     db "A MACHINE CAN TELL ITS OWN STORY",0
txt_one_timeline:      db "ONE TIMELINE AUDIO AND IMAGE",0
txt_score_drives:      db "THE SCORE DRIVES THE CUT",0
txt_ledger_remains:    db "THE LEDGER REMAINS",0
txt_source_claim_scene: db "SOURCE CLAIM SCENE CUT",0
txt_documentary_mode:  db "ASM DOCUMENTARY MODE",0

video_failure:
    mov al, OO_VIDEO
    jmp program_failure

opl_failure:
    mov al, OO_OPL
    jmp program_failure

opl3_failure:
    mov al, OO_OPL3
    jmp program_failure

program_failure:
    push ax
    call opl_shutdown
    call vga_text_mode
    pop ax
    jmp oo_fail
