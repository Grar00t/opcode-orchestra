; Build finalizer. NASM resolves payload offsets; the host hashes these bytes.
; Standalone NASM builds remain supported but have no OOMF trailer.
%ifndef OPCODE_ORCHESTRA_MANIFEST_INC
%define OPCODE_ORCHESTRA_MANIFEST_INC 1
%macro OO_FINALIZE 0
    %ifdef SCORE_ACTIVE
        %if SCORE_ACTIVE
            %error "Missing SCORE_END"
        %endif
    %endif
    %ifdef DATASET_ACTIVE
        %if DATASET_ACTIVE
            %error "Missing DATASET_END"
        %endif
    %endif
    %ifdef DOC_ACTIVE
        %if DOC_ACTIVE
            %error "Missing DOC_END"
        %endif
    %endif
    %if OO_BUILD_COM
        %assign __oo_runtime 0
        %assign __oo_kind 0
        %define __oo_start $$
        %define __oo_end $$
        %ifdef SCORE_DATA_END
            %assign __oo_runtime SCORE_CS
            %assign __oo_kind 1
            %define __oo_start SCORE_DATA_BEGIN
            %define __oo_end SCORE_DATA_END
        %elifdef DOC_DATA_END
            %assign __oo_runtime DOC_RUNTIME_CS
            %assign __oo_kind 2
            %define __oo_start DOC_DATA_BEGIN
            %define __oo_end DOC_DATA_END
        %elif OO_BUILD_MEDIA
            %assign __oo_kind 3
            %define __oo_start scene
            %define __oo_end scene_end
        %elif OO_BUILD_PCM
            %assign __oo_kind 4
            %define __oo_start pcm_wave
            %define __oo_end pcm_wave_end
        %endif
        ; 512 bytes of top-of-segment stack space, beyond the PSP and file.
        ; This is a build ceiling, not a proof of arbitrary caller stack depth.
        %if ($ - $$) + 136 > 64768
            %error "COM image exceeds stack-reserved build ceiling"
        %endif
        db 'OOLC'
        dw __oo_kind, OO_BUILD_FEATURES
        dd __oo_runtime
        dw __oo_start - $$, __oo_end - __oo_start
        dd $ - $$ - 16
    %endif
%endmacro
%endif
