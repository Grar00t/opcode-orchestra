; Opcode Orchestra - Sound Blaster 8-bit PCM backend
; Default base 220h, DSP reset +6, write +Ch, read +Ah, status +Eh.
; SB16 DSP 4.x, fixed DMA 1, IRQ 5 or 7. Blocking single-cycle 8-bit PCM.
; Exclusive hardware ownership; see docs/HARDWARE.md for the safety contract.

%ifndef OPCODE_ORCHESTRA_SBPCM_INC
%define OPCODE_ORCHESTRA_SBPCM_INC 1
%define SB_HAS_LIFECYCLE 1
%include "contracts.inc"
%include "isa_delay.inc"
%ifndef SB_IRQ
    %define SB_IRQ 7
%endif
%if SB_IRQ != 5 && SB_IRQ != 7
    %error "SB_IRQ must be 5 or 7"
%endif
%ifndef SB_DMA
    %define SB_DMA 1
%endif
%if SB_DMA != 1
    %error "Only 8-bit DMA channel 1 is supported"
%endif
SB_VECTOR equ 8 + SB_IRQ
SB_IRQ_BIT equ 1 << SB_IRQ
SB_IRQ_CONFIG equ 1 << ((SB_IRQ - 3) / 2)
SB_POLLS equ 65535
SB_WAIT_TICKS equ 200           ; > longest supported 65535/8000 s block
sb_old_vector dw 0,0
sb_old_mask db 0
sb_installed db 0
sb_complete db 0
sb_error db 0                  ; 0 success; 1 buffer; 2 probe; 3 config;
                               ; 4 DSP command; 5 completion; 6 cleanup
sb_stall_hi dw 0


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
    mov cx, 8
    call isa_delay_min
    mov al, 0                  ; MOV/OUT preserve the delay's CF
    out dx, al
    jc .fail
    mov cx, SB_POLLS
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
    mov cx, SB_POLLS
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
; Internal start primitive. Caller must own DSP/IRQ and keep buffer resident.
; All GP registers preserved, CF=1 on any invalid buffer or DSP write failure.
sb_pcm_start:
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
    cmp dl, 0fh
    ja .fail

    ; ISA DMA cannot cross a 64 KiB page boundary.
    mov ax, cx
    dec ax
    add ax, bx
    jc .fail

    ; Serialize the shared 8237 byte flip-flop against other IRQ handlers.
    pushf
    cli
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
    popf
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
    jc .fail
    mov al, ah
    call sb_dsp_write_byte
    jc .fail
    clc
    jmp .done
.fail:
    ; A failed command sequence must never leave DMA reading memory.
    mov al, 05h
    out DMA_MASK, al
    stc
.done:
    pop si
    pop dx
    pop cx
    pop bx
    pop ax
    ret

; AL=next DSP byte, CF=1 on bounded timeout. CX/DX preserved.
sb_dsp_read_byte:
    push cx
    push dx
    mov cx, SB_POLLS
.poll:
    mov dx, SB_DSP_STATUS
    in al, dx
    test al, 80h
    jnz .ready
    loop .poll
    stc
    jmp .done
.ready:
    mov dx, SB_DSP_READ
    in al, dx
    clc
.done:
    pop dx
    pop cx
    ret

; CF=0 only for DSP 4.x and the configured IRQ/DMA routing. No mixer writes.
sb_probe:
    push ax
    push bx
    push dx
    mov byte [cs:sb_error], 2
    call sb_dsp_reset
    jc .bad
    mov al, 0e1h
    call sb_dsp_write_byte
    jc .bad
    call sb_dsp_read_byte
    jc .bad
    mov bl, al
    call sb_dsp_read_byte     ; minor version must be consumed, even on mismatch
    jc .bad
    mov byte [cs:sb_error], 3
    cmp bl, 4
    jne .bad
    mov dx, SB_BASE + 4
    mov al, 80h
    out dx, al
    inc dx
    in al, dx
    and al, 0fh
    cmp al, SB_IRQ_CONFIG
    jne .bad
    dec dx
    mov al, 81h
    out dx, al
    inc dx
    in al, dx
    and al, 0bh
    cmp al, 02h
    jne .bad
    clc
    jmp .done
.bad:
    stc
.done:
    pop dx
    pop bx
    pop ax
    ret

; No DOS calls in the ISR. Chain IRQs that do not belong to 8-bit PCM.
sb_irq_handler:
    push ax
    push dx
    mov dx, SB_BASE + 4
    mov al, 82h
    out dx, al
    inc dx
    in al, dx
    test al, 1
    jz .chain
    mov dx, SB_DSP_STATUS
    in al, dx                ; acknowledge 8-bit DSP before PIC EOI
    mov byte [cs:sb_complete], 1
    mov al, 20h
    out 20h, al
    pop dx
    pop ax
    iret
.chain:
    pop dx
    pop ax
    jmp far [cs:sb_old_vector]

sb_irq_install:
    pusha
    push ds
    push es
    in al, 21h
    mov [cs:sb_old_mask], al
    or al, SB_IRQ_BIT
    out 21h, al
    mov ax, 3500h + SB_VECTOR
    int 21h
    mov [cs:sb_old_vector], bx
    mov [cs:sb_old_vector + 2], es
    push cs
    pop ds
    mov dx, sb_irq_handler
    mov ax, 2500h + SB_VECTOR
    int 21h
    mov byte [cs:sb_complete], 0
    mov byte [cs:sb_installed], 1
    in al, 21h
    and al, 0ffh ^ SB_IRQ_BIT
    out 21h, al
    pop es
    pop ds
    popa
    ret

; Read the BIOS tick counter atomically, WITHOUT consuming its midnight flag.
; CX:DX=24-hour tick count. AX/ES and IF preserved.
sb_clock_ticks:
    push ax
    push es
    pushf
    cli
    mov ax, 40h
    mov es, ax
    mov dx, [es:6ch]
    mov cx, [es:6eh]
    popf
    pop es
    pop ax
    ret

sb_wait_complete:
    pusha
    call sb_clock_ticks
    mov bx, dx
    mov di, cx
    mov si, SB_WAIT_TICKS
    xor bp, bp
    mov word [cs:sb_stall_hi], 256
.wait:
    cmp byte [cs:sb_complete], 1
    je .ok
    call sb_clock_ticks
    mov ax, dx
    sub ax, bx
    cmp cx, di
    je .delta
    test cx, cx
    jnz .delta
    add ax, 00b0h            ; midnight reset from 0018:00B0, not 32-bit wrap
.delta:
    test ax, ax
    jz .stalled
    mov bx, dx
    mov di, cx
    cmp ax, si
    jae .timeout
    sub si, ax
    xor bp, bp
    mov word [cs:sb_stall_hi], 256
    jmp .wait
.stalled:
    dec bp
    jnz .wait
    dec word [cs:sb_stall_hi]
    jnz .wait
.timeout:
    mov byte [cs:sb_error], 5
    popa
    stc
    ret
.ok:
    popa
    clc
    ret

; DMA is masked BEFORE reset, then vector restored BEFORE the old IRQ mask bit.
; Reset also aborts a partially accepted DSP command (D0 alone cannot do that).
sb_pcm_shutdown:
    pusha
    push ds
    cmp byte [cs:sb_installed], 0
    je .done
    mov al, 05h
    out DMA_MASK, al
    call sb_dsp_reset
    jc .cleanup_failed
    mov al, 0d3h
    call sb_dsp_write_byte
    jnc .ack
.cleanup_failed:
    cmp byte [cs:sb_error], 0
    jne .ack
    mov byte [cs:sb_error], 6
.ack:
    mov dx, SB_DSP_STATUS
    in al, dx
    in al, 21h
    or al, SB_IRQ_BIT
    out 21h, al
    lds dx, [cs:sb_old_vector]
    mov ax, 2500h + SB_VECTOR
    int 21h
    mov byte [cs:sb_installed], 0
    in al, 21h
    and al, 0ffh ^ SB_IRQ_BIT
    mov ah, [cs:sb_old_mask]
    and ah, SB_IRQ_BIT
    or al, ah
    out 21h, al
.done:
    pop ds
    popa
    ret

; DS:SI buffer, CX=1..65535 bytes. Blocking transfer, no DMA after return.
; CF=0 success, CF=1 failure; sb_error carries the precise category.
; GP/segments and caller IF/DF preserved. Requires IF=1, exclusive DMA/IRQ.
sb_pcm_play:
    pusha
    mov byte [cs:sb_error], 1
    pushf
    pop ax
    test ax, 0200h
    jz .done
    test cx, cx
    jz .done
    cmp byte [cs:sb_installed], 0
    jne .done
    ; Check both segment and physical bounds before touching hardware.
    mov ax, cx
    dec ax
    add ax, si
    jc .done
    mov bx, ds
    mov dx, bx
    shl bx, 4
    shr dx, 12
    add bx, si
    adc dl, 0
    cmp dl, 0fh
    ja .done
    mov ax, cx
    dec ax
    add ax, bx
    jc .done
    call sb_probe
    jc .done
    call sb_irq_install
    mov byte [cs:sb_error], 4
    mov al, 0d1h             ; enable DAC speaker before starting DMA
    call sb_dsp_write_byte
    jc .cleanup
    call sb_pcm_start
    jc .cleanup
    mov byte [cs:sb_error], 0
    call sb_wait_complete
.cleanup:
    call sb_pcm_shutdown
.done:
    popa
    cmp byte [cs:sb_error], 0
    je .ok
    stc
    ret
.ok:
    clc
    ret

%endif
