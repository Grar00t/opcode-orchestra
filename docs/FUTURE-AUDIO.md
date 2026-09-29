# Audio backends

The current implementation contains four OPL2 instrument patches, OPL3 routing,
a bank-zero 4-operator pair 0+3, rhythm operators on channels 6..8, a separate
SB16 8-bit PCM/DMA demonstration and public-domain score studies. These are
Assembly implementations, not recorded playback wrappers.

`future-audio.com` requires OPL3. The PC-speaker helper is separate and not an
automatic fallback. The PCM demonstration requires DSP4.x/base220/DMA1 and the
compiled IRQ. Unsupported devices produce an explicit error, not a different
performance silently substituted for the requested one.

Visual changes are driven by program state, not an audio-capture analyzer.
Source/static/instruction tests cover declarations and register/control-flow
behavior. DOS execution tests establish selected guest outcomes. Synthesized
sound, stereo perception, pitch accuracy, electrical timing and real-card
behavior must be evaluated separately as described in [HARDWARE.md](HARDWARE.md).
