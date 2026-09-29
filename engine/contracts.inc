; Shared NASM compile-time contracts. No runtime code.
%ifndef OO_CONTRACTS_INC
%define OO_CONTRACTS_INC 1
%macro REQUIRE_RANGE 4
    %if (%1) < (%2) || (%1) > (%3)
        %error %4
    %endif
%endmacro
%macro REQUIRE_OPL_CHANNEL 1
    REQUIRE_RANGE %1, 0, 8, "OPL channel must be 0..8"
%endmacro
%macro REQUIRE_OPL_OPERATOR 1
    %if !(((%1) >= 0 && (%1) <= 5) || ((%1) >= 8 && (%1) <= 13) || ((%1) >= 16 && (%1) <= 21))
        %error "OPL operator offset is not implemented"
    %endif
%endmacro
; mode (2 or 3), melodic mask, rhythm enabled, four-op pair mask.
; Pair-mask bits describe primary channels 0,1,2 in bank zero.
%macro REQUIRE_OPL_ALLOCATION 4
    %if (%1) != 2 && (%1) != 3
        %error "Unsupported OPL mode"
    %endif
    REQUIRE_RANGE %2, 0, 511, "Invalid melodic channel mask"
    REQUIRE_RANGE %3, 0, 1, "Invalid rhythm flag"
    REQUIRE_RANGE %4, 0, 7, "Invalid four-op pair mask"
    %if (%1) == 2 && (%4) != 0
        %error "Four-op allocation requires OPL3"
    %endif
    %if (%3) && ((%2) & 0x1c0)
        %error "Rhythm and melodic channels conflict"
    %endif
    %if (%2) & ((%4) | ((%4) << 3))
        %error "Four-op and melodic channels conflict"
    %endif
%endmacro
; Physical address and byte count, when known at assembly time.
%macro REQUIRE_DMA_BUFFER 2
    REQUIRE_RANGE %1, 0, 0xfffff, "DMA address outside conventional real-mode range"
    REQUIRE_RANGE %2, 1, 65535, "DMA length must be 1..65535"
    %if (((%1) & 0xffff) + (%2)) > 65536 || ((%1) + (%2)) > 0x100000
        %error "DMA buffer crosses a 64 KiB boundary"
    %endif
%endmacro
%endif
