# Assembly and calling conventions

## Common contract

DOS entry points are 16-bit flat binaries with `org 100h`. Set `DS=CS`, clear DF,
and retain the DOS-provided usable SS:SP. The canonical build reserves 512 bytes
above the image; there is no general arbitrary-caller stack-depth guarantee.
Calls are near, return addresses occupy two bytes, and no routine changes SS.
There is no recursion. IRQ code must not call DOS. Hardware routines and their
scratch globals are non-reentrant.

Unless the table below promises otherwise, treat AX/BX/CX/DX/SI/DI/BP and
arithmetic flags as caller-saved. This conservative contract also applies to
internal cinematic/documentary helpers. DS/CS/SS remain unchanged. ES remains
unchanged except during the VGA acquisition lifetime. IF/DF must remain as on
entry except that application entry points intentionally clear DF. A flag
listed as undefined must not be used as an error result.

All public routines return with the same SP as at entry after the caller's near
return address has been consumed. Tested register/stack cases are in
`cpu_contracts.py`; this convention is not a claim of exhaustive formal proof.

## Public interfaces

| Routine(s) | Inputs / outputs | Preservation / flags |
|---|---|---|
| `opl_write`, `opl3_write1`, `opl_write_port` | AL register, BL byte; explicit-port form DX=388h/38Ah | All GP/segments preserved; arithmetic flags undefined |
| `opl_detect` | AL=0/2/3; CF=1 absent/unrecognized | BX/CX/DX preserved; device timers intentionally touched |
| `opl_init` | Initializes owned three-voice state; CF failure | Caller-saved GP convention; requires caller to inspect CF |
| `opl_shutdown`, `opl_all_off` | Full owned reset, or only melodic voices 0..2 off | GP preserved; arithmetic flags undefined |
| `clock_cs` | AX=0..5999 within current minute | Other GP preserved; arithmetic flags undefined |
| `wait_cs` | CX=0..65535 centiseconds | All GP preserved; arithmetic flags undefined; requires progressing DOS time |
| `opl_key_on` | AX=0..1023, three blocks 4/3/5; CF invalid argument | GP preserved; CF is status |
| `opl_play` | AX valid F-number or zero rest; CX duration | GP preserved; no defined error flag; valid pitch is a caller precondition |
| `instrument_select` | AL=0..3; CF invalid index | GP preserved; updates channels 0..2 while retaining pan cache |
| `opl3_enable` | CF success only after OPL3 detection | Caller-saved AX/BX |
| `opl3_set_pan` | DL=0..8, BL=10h/20h/30h or 0, CL=0..15; CF invalid/inactive | AX preserved; BX/CX caller-saved |
| `opl3_stereo_default` | Routes 0 left, 1 both, 2 right | Caller-saved GP; requires active OPL3 |
| `opl3_4op_voice_init`, pair-enable/disable helpers | Pair 0+3 and its operators | Caller-saved GP; active OPL3 is required; init returns CF from enable on failure |
| `opl3_4op_key_on` | AX F-number; CF invalid/inactive | GP preserved |
| `opl3_4op_off`, `opl_rhythm_off` | Key-off / rhythm disabled | AX/BX caller-saved; no defined status |
| `opl_rhythm_init` | Initializes owned operators/channels 6..8 | AX/BX/CX caller-saved; no defined status |
| `opl_drum_hit` | AL mask in low 5 bits, CX duration; CF invalid mask | AX/BX preserved; CX follows wait contract |
| `vga_mode13` | CF success, ES=A000h | GP preserved; saves previous mode/page/ES |
| `vga_text_mode` | Restores saved mode/page/ES despite legacy name | GP preserved; no status; no-op when not acquired |
| `vga_clear` | AL palette index | GP, ES and flags including DF preserved |
| `vga_putpixel` | AX=x, BX=y, CL=color | GP/ES preserved; unsigned off-screen coordinates ignored |
| `vga_hline` | AX=x, BX=y, CX=length, DL=color | GP/ES/flags preserved; clips at right edge |
| `vga_draw_char5x7` | AL ASCII, BX=x, DX=y, CL=color, CH=scale | Caller-saved GP; scale zero/off-screen rejected; A-Z/space only |
| `cinema_fill_rect`, `cinema_vline` | AX=x, BX=y, CX=width/height, DL=color; rectangle SI=height | Caller-saved GP; clipped drawing |
| `cinema_text`, `cinema_lower_third` | DS:SI terminated trusted text; text BX=x, DX=y, CL=color, CH=scale | Caller-saved GP; not a parser for arbitrary unterminated external memory |
| `media_execute` | DS:SI start, DI exclusive end; CF exact success/failure | DI/segments/IF/DF preserved; other GP caller-saved |
| `sb_pcm_play` | DS:SI sample, CX length; CF result, `sb_error` detail | GP/segments/IF/DF preserved; IF=1, exclusive device ownership required |
| `sb_probe`, `sb_dsp_reset` | CF valid device/reset | See `sbpcm.inc`; caller-saved unless its header promises more |
| `sb_dsp_write_byte` | AL byte, CF timeout | GP preserved |
| `sb_dsp_read_byte` | AL byte, CF timeout | CX/DX preserved |
| `isa_delay_min` | CX minimum PIT down-counter counts, CF timeout | GP/segments/IF/DF preserved |
| `isa_pit_read` | AX latched PIT0 count | Other GP and incoming flags preserved |
| `play_note` | BX=0 or 19..65535 Hz, CX BIOS ticks; CF invalid pitch | AX/CX/DX preserved; DS unchanged |
| `wait_ticks` | CX=0..65535 BIOS ticks | GP/segments/IF/DF preserved |
| `speaker_clock_ticks` | CX:DX atomic BIOS day ticks | AX/ES and IF preserved; does not consume midnight flag |
| `speaker_off` | Gate PIT2 speaker output off | AL and arithmetic flags clobbered; other GP preserved |
| `oo_fail` | AL process status, DS=CS | Does not return; caller must clean devices first |

Internal PCM start/IRQ/install/wait/shutdown routines are not standalone public
playback APIs. Calling `sb_pcm_start` alone bypasses lifecycle guarantees.
`play_song` consumes a trusted compiled PC-speaker table, not OPL score records.

## Macro and source rules

Use the shared range/allocation contracts for constants. NASM `%%` local labels
provide macro hygiene. Byte/word field width is part of the format; do not rely
on assembler truncation. Every complete canonical DSL declaration must close.
Keep ports and masks named, and retain datasheet-defined values beside their
meaning. A source comment is not a hardware measurement.

Changes to calling contracts require a focused executable regression. For
hardware routines use assembled-instruction tests for branch/register behavior,
then separately run emulation and physical checks applicable to the change.
Do not weaken a negative test or change unrelated behavior to obtain a pass.
