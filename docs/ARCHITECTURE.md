Architecture
Opcode Orchestra intentionally separates musical data from hardware
synthesis.
Score layer
A score is encoded as pairs:
F-number, duration

Duration is expressed in centiseconds.
A zero F-number is a rest.
Timing layer
The OPL2 engine uses DOS time through:
INT 21h
AH=2Ch

This provides hundredths-of-a-second timing and avoids the earlier
BIOS-delay path.
Synthesis layer
The engine writes directly to the OPL interface:
0x388  register select
0x389  register data

Three melodic channels are currently used:
channel 0  principal
channel 1  lower octave
channel 2  upper octave

Each channel has its own two-operator FM voice configuration.
Verification philosophy
The project does not treat compilation as proof of correctness.
Verification is separated into:
1. source builds,
2. score duration matches its contract,
3. OPL register writes execute,
4. emulator exposes an OPL-compatible device,
5. audible output matches the intended behavior.
The original raw OPL smoke test exists because it isolates emulator
audio from the higher-level engine.
