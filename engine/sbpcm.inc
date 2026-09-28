; Opcode Orchestra - Sound Blaster 8-bit PCM backend
; Default base 220h, DSP reset +6, write +Ch, read +Ah, status +Eh.
; Uses DMA channel 1, single-cycle 8-bit playback at ~8 kHz.

%ifndef OPCODE_ORCHESTRA_SBPCM_INC
%define OPCODE_ORCHESTRA_SBPCM_INC 1

SB_BASE      equ 0220h
SB_DSP_RESET equ SB_BASE + 06h
SB_DSP_READ  equ SB_BASE + 0Ah
SB_DSP_WRITE equ SB_BASE + 0Ch
SB_DSP_STATUS equ SB_BASE + 0Eh

DMA1_ADDR  equ 02h
DMA1_COUNT equ 03h
DMA_MASK   equ 0Ah
DMA_MODE   equ 0Bh
DMA_CLEAR  equ 0Ch
DMA1_PAGE  equ 83h

sb_dsp_reset:
    push ax
    push cx
    push dx
    mov dx, SB_DSP_RESET
    mov al, 1
    out dx, al
    mov cx, 100
.delay1:
    loop .delay1
    xor al, al
    out dx, al
    mov cx, 65535
.wait_ready:
    mov dx, SB_DSP_STATUS
    in al, dx
    test al, 80h
    jnz .have_byte
    loop .wait_ready
    stc
    jmp .done
.have_byte:
    mov dx, SB_DSP_READ
    in al, dx
    cmp al, 0AAh
    jne .fail
    clc
    jmp .done
.fail:
    stc
.done:
    pop dx
    pop cx
    pop ax
    ret

; AL = DSP byte
sb_dsp_write_byte:
    push ax
    push cx
    push dx
    mov ah, al
    mov cx, 65535
.wait:
    mov dx, SB_DSP_WRITE
    in al, dx
    test al, 80h
    jz .ready
    loop .wait
    stc
    jmp .done
.ready:
    mov al, ah
    out dx, al
    clc
.done:
    pop dx
    pop cx
    pop ax
    ret
; DS:SI = sample buffer, CX = bytes (1..65535). Starts single-cycle DMA playback.
sb_pcm_play:
    push ax
    push bx
    push cx
    push dx
    push si

    test cx, cx
    jz .fail

    ; Compute 20-bit physical address for DMA channel 1.
    mov bx, ds
    mov dx, bx
    shl bx, 4
    shr dx, 12
    add bx, si
    adc dl, 0

    ; ISA DMA cannot cross a 64 KiB page boundary.
    mov ax, cx
    dec ax
    add ax, bx
    jc .fail

    ; Mask DMA channel 1 and clear address/count flip-flop.
    mov al, 05h
    out DMA_MASK, al
    xor al, al
    out DMA_CLEAR, al

    ; Channel 1 address.
    mov ax, bx
    out DMA1_ADDR, al
    mov al, ah
    out DMA1_ADDR, al
    mov al, dl
    out DMA1_PAGE, al

    ; Count is length-1.
    mov ax, cx
    dec ax
    out DMA1_COUNT, al
    mov al, ah
    out DMA1_COUNT, al

    ; Single-cycle DMA, read from memory, channel 1.
    mov al, 49h
    out DMA_MODE, al
    mov al, 01h
    out DMA_MASK, al
    ; DSP time constant for ~8 kHz: 256 - 1,000,000/8000 = 131.
    mov al, 40h
    call sb_dsp_write_byte
    jc .fail
    mov al, 131
    call sb_dsp_write_byte
    jc .fail

    ; 8-bit single-cycle DMA playback command + length-1.
    mov al, 14h
    call sb_dsp_write_byte
    jc .fail
    mov ax, cx
    dec ax
    call sb_dsp_write_byte
    mov al, ah
    call sb_dsp_write_byte
    clc
    jmp .done
.fail:
    stc
.done:
    pop si
    pop dx
    pop cx
    pop bx
    pop ax
    ret

%endif
