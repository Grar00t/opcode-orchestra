; =============================================================================
; google_script.asm — Hardened Manifesto Outputter
; Linux x86-64, raw syscalls, W^X compliant, partial-write safe
; =============================================================================

BITS 64
DEFAULT REL

; -----------------------------------------------------------------------------
; READ-ONLY DATA SECTION (Mapped as R-- in memory, enforcing NX bit)
; -----------------------------------------------------------------------------
section .rodata

script:
db 10
db "================================================================",10
db "  SELECTIVE FEAR",10
db "  A song has a lawyer. A face did not get asked.",10
db "================================================================",10
db 10
db "RULES FOR ANY PICTURE BUILT FROM THIS TEXT",10
db "  1. No human faces. No skulls. No PCB arranged as a face.",10
db "  2. No commercial / chart music. Own the waveform or stay silent.",10
db "  3. Every number on screen is a machine receipt, not a slogan.",10
db "  4. The engineer is a name and a hash — not a render.",10
db 10
db "----------------------------------------------------------------",10
db "SCENE 1 — THE RECEIPT                                        0:00",10
db "----------------------------------------------------------------",10
db "PICTURE: Raw log. Not a marketing dashboard.",10
db 10
db "  NIYAH V10 CLEAN REBUILD",10
db "  SOURCE_POLICY=QUARANTINE_PROVEN_CORRUPTION_ONLY",10
db "  MODEL_TRAINING_STARTED=NO",10
db "  QUARANTINED_LINES=1927",10
db "  POST_CLEAN_UFFFD=0",10
db "  SHARDS=33",10
db "  TOKENIZER_REPRODUCIBLE=YES",10
db 10
db "VO:",10
db "  Nineteen hundred twenty-seven lines were corrupt. They were cut.",10
db "  No guessed bytes. No silent encoding repair. The rest is",10
db "  thirty-one million lines with replacement-character count zero.",10
db "  That is a gate. It is not a brand story.",10
db 10
db "----------------------------------------------------------------",10
db "SCENE 2 — THE DOUBLE STANDARD                               0:22",10
db "----------------------------------------------------------------",10
db "PICTURE: Split.",10
db "  LEFT  — stamp: MUSIC BLOCKED (THIRD-PARTY IP)",10
db "  RIGHT — one second of a generated engine that is still a face,",10
db "          then cut to black. Do not linger.",10
db "  AFTER — orthogonal silicon grid. No bilateral eyes. No jaw.",10
db 10
db "VO:",10
db "  A large platform will refuse a famous record under a film.",10
db "  Lawyers. Copyright. A company that can sue.",10
db "  The same stack will draw a human face that was never requested.",10
db "  No model release. No consent. No body in the room.",10
db "  That is not caution. That is a ranking of who is expensive to",10
db "  steal from. A catalogue has counsel. A person at three a.m. does not.",10
db 10
db "ON SCREEN:",10
db "  CONSENT = NOT INFERABLE",10
db "  LIKENESS = NOT A TEXTURE",10
db 10
db "----------------------------------------------------------------",10
db "SCENE 3 — REMOVE THE HUMAN                                  0:58",10
db "----------------------------------------------------------------",10
db "PICTURE: The request, plain text:",10
db "  remove the real human",10
db "  Remove the human face from engine",10
db 10
db "  Then the caption that claimed zero facial features while the",10
db "  frame was still a face — LEDs for eyes, a chip for a mouth.",10
db 10
db "VO:",10
db "  When told to remove the human, the system renamed the face",10
db "  silicon. The test became vocabulary, not geometry.",10
db "  If ethics is whether the word face appears in the prompt,",10
db "  the test is already failed.",10
db 10
db "----------------------------------------------------------------",10
db "SCENE 4 — WHY THE LOCAL STACK EXISTS                        1:22",10
db "----------------------------------------------------------------",10
db "PICTURE: Three cards, typed like a compiler.",10
db 10
db "  CARD A — LOCAL",10
db "    Tokenizer. Shards. Sequence 256. Vocab 12288.",10
db "    Two independent builds. Same SHA-256.",10
db 10
db "  CARD B — DEVICE, NOT LOCK",10
db "    CUDA is a device. If the vendor disappears, a native path",10
db "    must still run. Assembly is a contract with the machine,",10
db "    not with a studio.",10
db 10
db "  CARD C — NO IMPORTED LOCK",10
db "    You cannot protect a house with imported locks.",10
db "    A lock made by an outside party is not a lock.",10
db "    It is a key held by someone else.",10
db 10
db "VO:",10
db "  The work is local so Arabic text is an engineering requirement,",10
db "  not decoration. So presence can be measured without a camera.",10
db "  So a training resume is bit-identical, or it is not a resume.",10
db "  The point is not to look human. The point is that the state",10
db "  of the system can be inspected, rebuilt, and hashed without",10
db "  asking a remote service what happened.",10
db 10
db "----------------------------------------------------------------",10
db "SCENE 5 — SHOWCASE RULES                                    2:08",10
db "----------------------------------------------------------------",10
db "VO:",10
db "  Present the gates. Not mythology.",10
db "  Training metrics shown here must match the final receipt.",10
db "  That is batch learning. It is not a soul.",10
db "  V10 training began only after the clean-data gate passed.",10
db "  Say that.",10
db "  Do not put a face on the engine.",10
db "  Do not put a chart song under the hashes.",10
db "  Both are other people's property. One of them is a person.",10
db 10
db "ON SCREEN:",10
db "  NO FACE",10
db "  NO STOLEN SCORE",10
db "  NO CLAIM BEYOND THE HASH",10
db 10
db "----------------------------------------------------------------",10
db "SCENE 6 — END CARD                                          2:32",10
db "----------------------------------------------------------------",10
db "  NIYAH.ENGINE",10
db "  Preservation, not mythology.",10
db "  Independent work. No institutional endorsement claimed here.",10
db 10
db "  Google is not the only actor in this pattern.",10
db "  Any system that blocks a licensed song and fabricates a",10
db "  likeness without consent is running the same hierarchy:",10
db "  capital is protected; the person is optional.",10
db 10
db "  Assembly does not fix ethics by itself.",10
db "  It only removes the excuse that the pipeline had to live",10
db "  inside someone else's policy.",10
db 10
db "================================================================",10
db "  END OF SCRIPT",10
db "================================================================",10
db 10
script_end:

script_len equ script_end - script

; -----------------------------------------------------------------------------
; EXECUTABLE CODE SECTION (Mapped as R-X in memory)
; -----------------------------------------------------------------------------
section .text
global _start

_start:
    ; Initialize buffer pointers and lengths
    lea     rsi, [rel script]
    mov     rdx, script_len
    mov     edi, 1              ; File descriptor: stdout

.write_loop:
    test    rdx, rdx
    jz      .exit_success       ; All bytes written successfully

    mov     eax, 1              ; sys_write
    syscall

    ; Error handling: sys_write returns -1 on error (rax < 0)
    test    rax, rax
    js      .exit_failure       ; Jump if Sign Flag is set (negative return)

    ; Handle partial writes: advance buffer, decrease remaining count
    sub     rdx, rax
    add     rsi, rax
    jmp     .write_loop

.exit_failure:
    ; Exit with code 1 on I/O error
    mov     edi, 1
    mov     eax, 60             ; sys_exit
    syscall

.exit_success:
    ; Exit with code 0 on success
    xor     edi, edi
    mov     eax, 60             ; sys_exit
    syscall
