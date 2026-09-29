# Hardware, timing and ownership model

## Capability policy

The engine recognizes OPL2/OPL3 using the timer/status protocol at 388h and the
status signature. OPL3 programs require the OPL3 result; no silent OPL2 musical
fallback occurs. A recognized signature does not identify every clone/revision.
VGA mode 13h is acquired through BIOS and checked by querying the resulting
mode. This is mode acceptance, not proof of framebuffer appearance.

PCM support is deliberately limited to SB16 DSP 4.x, base 220h, DMA1 and the
compiled IRQ (7 by default; 5 is also a compile-time option). Mixer routing
registers are checked, not reconfigured. Other DSP generations and routing are
rejected. PC-speaker availability is a platform assumption, not a detectable
capability claimed by the software. The supplied DOSBox-X configuration disables
the PC speaker; the legacy speaker helper is not used by the OPL scores.

## OPL register model

OPL2 bank 0 uses address/data 388h/389h. OPL3 bank 1 uses 38Ah/38Bh.
The single write implementation performs six address-port reads after selecting
a register and 35 after writing data. The trace tests verify counts and order;
physical delays remain unmeasured and depend on compatible I/O bus behavior.

Within a bank, channels 0..8 map to modulator offsets
`00 01 02 08 09 0A 10 11 12`; carrier offsets are those values plus 3.
Operator parameters use register bases 20h, 40h, 60h, 80h and E0h.
A0h/B0h encode the ten-bit F-number, block and key-on; C0h encodes
feedback/connection and, in OPL3 mode, left/right bits 10h/20h.

The three-voice score path owns channels 0/1/2 at blocks 4/3/5. Instrument changes
retain those channels' pan state. Rhythm mode owns channels 6/7/8 and BDh bits;
melodic allocation of those channels conflicts with rhythm use. The implemented
4-operator voice owns bank-zero pair 0+3 (104h bit 0); it is not an implementation
of every possible four-operator allocation or algorithm. Compile contracts
reject invalid modes, operator offsets, channels and conflicting declared masks.
They do not infer arbitrary runtime allocations from handwritten port writes.

Initialization supplies release, waveform and routing values for the operators
it owns. Shutdown keys off all channels in relevant banks, clears rhythm and
4-op enables, then disables OPL3 mode. It establishes quiescent state rather
than restoring a previous application's sound. Existing F-number tables are
preserved; pitch accuracy, FM timbre, stereo image and analog output are not
certified by these register tests.

## Time

Musical durations remain centiseconds. `clock_cs` reads DOS INT 21h/AH=2Ch;
`wait_cs` consumes successive deltas modulo 6,000 so waits longer than one
minute terminate under a progressing clock. It polls frequently enough that
more than one minute must not pass between observations. DOS time resolution
can be coarser than one centisecond. A stopped/adjusted DOS clock is outside the
normal musical-wait contract; these waits are not calibrated wall-clock timers.

Short device setup delays use a latched PIT0 counter without reprogramming it.
The documented assumption is reload 65,536, mode 2 or 3, 1.193182 MHz.
Because mode 3 may decrement by two, eight counts correspond to a modeled
minimum approximately 3.35 microseconds and 200 to approximately 83.8 microseconds.
A stalled counter fails after 65,535 observations. This is a conditional bound,
not a measured electrical delay or support for arbitrary PIT0 reprogramming.

PC-speaker and PCM completion waits read BIOS day ticks atomically, handle the
standard midnight wrap, and do not consume the BIOS midnight flag. PCM completion
is bounded by 200 advancing BIOS ticks and a separate finite stalled-clock poll
budget. The former exceeds the supported 65,535-byte transfer at 8,000 samples/s;
the latter is an iteration bound, not a portable wall-clock bound.

## Sound Blaster DMA lifecycle

The public call is blocking. It validates nonzero length, segment-offset wrap,
20-bit address range and 64 KiB DMA-page containment. Physical address is
`DS * 16 + SI`; DMA count is `length - 1`. Invalid buffers fail before playback.
The ISA channel-1 address, page and count registers are programmed under a short
interrupt-masked flip-flop transaction. CPU flags are restored afterwards.

Reset assertion uses the PIT setup delay and requires AAh acknowledgement.
DSP reads/writes have bounded status polling and all five transfer-command
writes are checked. DSP version and mixer IRQ/DMA mapping are checked before
ownership. The code temporarily installs IRQ5/7's vector, preserves the mask
bit, acknowledges 8-bit DSP interrupts at base+Eh, then acknowledges the master
PIC. Non-8-bit interrupts chain to the prior handler. No DOS calls occur in the
ISR. Shared MIDI/TSR use is unsupported because an 8-bit interrupt source need
not be uniquely attributable in such a configuration.

On completion/error, cleanup masks DMA first, resets the DSP to abort partial
command state, switches off its speaker, acknowledges pending DSP status,
restores the old vector, then restores the original PIC mask bit. An IRQ hook,
DMA transfer or prior audio stream from another owner is not supported. A
failed reset after masking DMA reports cleanup failure; it cannot promise an
unknown card's internal analog state. Guest-state tests are not proof of ISA
bus electrical safety on real cards.

## VGA and speaker boundaries

Unsigned coordinates outside 320x200 are ignored; horizontal lines, rectangles
and vertical lines clip at the edge before computing an offset. Bulk VGA writes
clear DF locally and restore incoming flags. Text origins/scales are checked;
the font contains A-Z and space, not all ASCII. BIOS mode/page and ES are restored;
previous pixel data and arbitrary DAC contents are not saved.

The PC-speaker path rejects pitches below 19 Hz that would overflow its 16-bit
PIT divisor. Zero means rest. `speaker_off` disables the gate, but does not
restore an earlier PIT2 programming state. No physical-speaker test is claimed.

## Reference boundaries

Creative's *Sound Blaster Series Hardware Programming Guide* documents DSP
reset/acknowledgement, 8-bit single-cycle commands, mixer IRQ/DMA registers and
interrupt acknowledgement. The implementation targets that interface, not a
general sound-card API. The official DOSBox 0.74-3 manual documents fixed cycles
and headless sound-output settings. See the links in the audit report for the
specific retrieved primary material. Manufacturer compatibility and real write
delays still require physical measurement.
