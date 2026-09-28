BITS 16
ORG 100h
jmp start

%include "sbpcm.inc"

start:
    push cs
    pop ds
    cld
    call sb_dsp_reset
    jc .fail

    mov si, pcm_wave
    mov cx, pcm_wave_end - pcm_wave
    call sb_pcm_play
    jc .fail

    mov ah, 00h
    int 16h
    mov ax, 4C00h
    int 21h

.fail:
    mov ax, 4C02h
    int 21h

; 256 unsigned 8-bit samples: repeated synthetic cycle.
pcm_wave:
%rep 16
    db 128,152,176,198,216,229,236,238
    db 236,229,216,198,176,152,128,104
%endrep
pcm_wave_end:

%if (pcm_wave_end - pcm_wave) != 256
    %error "PCM demo must contain exactly 256 bytes"
%endif
