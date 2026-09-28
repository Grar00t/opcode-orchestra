BITS 16

%include "dataset.inc"

; =============================================================================
; WRAPPER LEDGER music dataset - ASM native
; 24 fixed-size supervised transition records.
; Record = section, step, previous_note, target_note, duration_cs.
; =============================================================================

%define N_C   0159h
%define N_D   0183h
%define N_EB  019Ah
%define N_F   01CCh
%define N_G   0205h
%define N_AB  0223h
%define N_BB  0267h
%define R     0000h

DATASET_BEGIN 24

; section 0 - boot pulse
DS_SAMPLE 0, 0, R,    N_C,  50
DS_SAMPLE 0, 1, N_C,  N_G,  50
DS_SAMPLE 0, 2, N_G,  N_EB, 50
DS_SAMPLE 0, 3, N_EB, N_BB, 50
DS_SAMPLE 0, 4, N_BB, N_C,  50
DS_SAMPLE 0, 5, N_C,  N_G,  50
DS_SAMPLE 0, 6, N_G,  N_F,  50
DS_SAMPLE 0, 7, N_F,  N_D,  50

; section 1 - rise
DS_SAMPLE 1, 0, N_D,  N_C,  50
DS_SAMPLE 1, 1, N_C,  N_D,  50
DS_SAMPLE 1, 2, N_D,  N_EB, 50
DS_SAMPLE 1, 3, N_EB, N_F,  50
DS_SAMPLE 1, 4, N_F,  N_G,  50
DS_SAMPLE 1, 5, N_G,  N_AB, 50
DS_SAMPLE 1, 6, N_AB, N_BB, 50
DS_SAMPLE 1, 7, N_BB, N_AB, 50

; section 2 - ledger pulse
DS_SAMPLE 2, 0, N_AB, N_C,  100
DS_SAMPLE 2, 1, N_C,  N_G,  100
DS_SAMPLE 2, 2, N_G,  N_BB, 100
DS_SAMPLE 2, 3, N_BB, N_G,  100

; section 3 - farewell coda
DS_SAMPLE 3, 0, N_G,  N_F,  100
DS_SAMPLE 3, 1, N_F,  N_EB, 100
DS_SAMPLE 3, 2, N_EB, N_D,  100
DS_SAMPLE 3, 3, N_D,  N_C,  200

DATASET_END
