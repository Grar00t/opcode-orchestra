# Opcode Orchestra — launch kit

This launch kit is intentionally evidence-bound. Do not buy stars, fabricate users, invent benchmarks, or claim physical-hardware/audio-quality validation that the repository does not prove.

## One-line hook

**I made DOS sing from raw x86 Assembly: direct OPL2/OPL3 register I/O, executable `.COM` programs, reproducible builds, and a DOSBox-X capture gate that verifies captured emulated synthesized output.**

## Show HN title

**Show HN: Opcode Orchestra — DOS music from raw x86 Assembly and OPL hardware I/O**

## Short post

I wanted the smallest possible stack between code and sound, so I built an Assembly-first DOS music lab around direct AdLib/OPL register writes.

No MIDI player. No JSON score runtime. No mandatory model. NASM assembles the executable code and score data; Python orchestrates builds, finalizes provenance manifests, hashes artifacts, and runs checks.

The repository now includes OPL2/OPL3 scores, a VGA opcode stream, a separate Sound Blaster DSP/DMA demo, deterministic artifact checks, DOS execution gates, and a DOSBox-X audio-capture test that validates PCM/WAV structure plus OPL key-on/key-off events.

What is *not* claimed: audible quality, physical sound-card compatibility, or production readiness.

Repo: https://github.com/Grar00t/opcode-orchestra

## Reproduction commands

```sh
make clean
make
make verify-all
make reproducible
make verify-emulator
make verify-audio-capture
```

For an interactive DOSBox-X run:

```sh
dosbox-x -conf dosbox-x.conf -c "mount c build" -c "c:" -c "b567.com"
```

## What makes it shareable

- The [launch artifact](https://github.com/Grar00t/opcode-orchestra/releases/tag/v0.1.0-launch-20260930) contains the demo, its hash, and a commit-bound receipt. Its audio is captured DOSBox-X synthesis.
- The implementation is inspectable: x86 Assembly, direct OPL/VGA/SB I/O.
- The verification story is unusually explicit: build, emulator execution, audio capture, listening, and real hardware are separate claims.
- The repo has narrow, memorable language instead of generic "AI platform" positioning.

## Distribution sequence

1. Merge only after CI and local verification pass.
2. Add one real 15–30 second capture/video generated from the repository; label it as emulated DOSBox-X output if that is the source.
3. Use the material above as a private author fact sheet. The author must write and submit their own Show HN text: current [HN guidelines](https://news.ycombinator.com/newsguidelines.html) prohibit generated or AI-edited text and automated posting.
4. Post the same artifact, adapted rather than duplicated, to relevant retrocomputing / systems-programming communities.
5. Answer technical questions with exact source paths, commands, and commit hashes.
6. Do not use bots, purchased engagement, sockpuppets, fake testimonials, or fabricated benchmark claims.

## Evidence boundary

Tie each public verification claim to the exact release commit and its receipt. The audio smoke gate establishes emulated synthesized-output capture through DOSBox-X; reproducibility and execution are separate gates. Physical-card compatibility and subjective audio quality remain separate, unproven claims unless separately tested.
