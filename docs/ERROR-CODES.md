# Error and exit codes

## DOS applications

Application exits use DOS INT 21h/AH=4Ch. Zero means that the implemented
application path completed; it is not an audio-quality or hardware certificate.
The shared diagnostics are defined in `engine/status.inc`:

| Exit | Symbol | Diagnostic / condition |
|---|---|---|
| 0 | Success | Normal return from the implemented program |
| 2 | OO_VIDEO | VGA mode 13h unavailable |
| 3 | OO_OPL | OPL timer/status probe failed |
| 4 | OO_OPL3 | This program requires OPL3 |
| 5 | OO_MEDIA | Invalid or truncated media stream |
| 6 | OO_PCM | PCM setup, transfer or cleanup failed |
| 7 | OO_ARGUMENT | Invalid engine argument; available to callers |

These are process statuses, not every routine's return convention. A hardware
routine that documents CF uses CF=0 for success and CF=1 for failure. Callers
must inspect CF before an instruction that overwrites it. `oo_fail` does not
perform hardware cleanup itself: its caller must release acquired devices.
The retained standalone `opl2_smoke.asm` is a raw diagnostic and does not use
this capability/error model.

## PCM detail

`sb_pcm_play` returns CF and stores detail in `sb_error`:

| Value | Meaning |
|---|---|
| 0 | Transfer completed and no cleanup error reported |
| 1 | Invalid buffer or entry precondition, including IF=0 or already-owned state |
| 2 | DSP reset/version-query protocol failed |
| 3 | Unsupported DSP generation or IRQ/DMA routing |
| 4 | Speaker/transfer DSP command failed |
| 5 | Completion timed out or the clock/poll budget was exhausted |
| 6 | Cleanup failed after an otherwise successful transfer |

Cleanup preserves an earlier error category rather than replacing it with 6.
Therefore a prior transfer failure does not prove subsequent DSP reset succeeded.
DMA masking and interrupt restoration are separate cleanup operations. Error 6
is not evidence that all possible hardware side effects were eliminated.

## Optional C bridge

| Exit | Category |
|---|---|
| 0 | Generation and checked reporting completed |
| 2 | Invalid arguments |
| 3 | Locale/rounding, CPU support or library initialization failed |
| 4 | Allocation failed |
| 5 | A checked MLAsm API operation failed |
| 6 | Invalid/nonfinite/out-of-range library result or invalid version string |
| 7 | Output destination, write/close/rename, or stdout failed |

`REASON` identifies the failing operation. A stdout failure can occur after the
complete destination has already been atomically replaced; status 7 must not be
interpreted as a guarantee that no output file changed.

## Host and optional voice tools

The Python build, parser, syntax and publication tools use 1 for handled
operation failures and argparse's 2 for invalid command-line usage. Their
messages identify the operation. Missing required tools never count as a pass.
Bash entry points also propagate nonzero child exits; those values are not a
new cross-tool ABI.

Voice-specific codes are 20 for active training, 21 for missing speaker selection,
22 for a failed process check, and 2 for an unsupported backend. Missing variables,
missing files and child failures are also nonzero. A zero exit establishes only
checked process output; it does not establish a valid WAV, consent or listening
quality. No real voice rendering was performed by this audit.
