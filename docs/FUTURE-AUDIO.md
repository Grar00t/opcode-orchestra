# Future Audio Pack

Opcode Orchestra now exposes a layered audio architecture instead of a single fixed OPL2 voice.

## Implemented source capabilities

- OPL2 instrument bank with four timbres
- OPL3 enable path
- left / center / right stereo routing
- OPL3 4-operator pair 0+3 configuration
- OPL rhythm-mode percussion
- Sound Blaster DSP reset + 8-bit single-cycle DMA PCM path
- two additional public-domain score studies
- audio-reactive VGA showcase driven by the same ASM program

## Boundaries

Build success proves source consistency, register contracts, and binary generation. It does not by itself prove audible correctness on every real card or emulator.

Hardware/emulator verification should be reported separately for OPL3, rhythm mode, and Sound Blaster DMA.

## Backend map

```text
ASM score / dataset
        |
        +--> OPL2 instruments
        +--> OPL3 stereo / 4-op
        +--> OPL rhythm percussion
        +--> SB 8-bit PCM DMA
        +--> VGA synchronized visuals
```
