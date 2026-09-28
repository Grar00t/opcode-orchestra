# XTTS v2 — Local Verification Receipt

XTTS is an optional local voice layer. It is not part of the ASM-native core.
No model weights, reference voices, generated WAV files, or private source audio are committed.

## Verified local execution

A prior local run on this machine produced valid Arabic reference-conditioned audio using XTTS v2.
The verification receipt records:

- `model.pth` SHA256: `c7ea20001c6a0a841c77e252d8409f6a74fb423e79b3206a0771ba5989776187`
- `config.json` SHA256: `ef262b1454dd2a77e1461b0b2cd53e19b8a7624cc131b837d36df67356bc75e8`
- `vocab.json` SHA256: `928260878a59da8a72a2a5b7687fea29d5106137669d90945430fe17e415304a`
- `speakers_xtts.pth` SHA256: `f0f6137c19a4eab0cbbe4c99b5babacf68b1746e50da90807708c10e645b943b`
- verified output SHA256: `24b3747756f4003c8e22483d9e312f65ec4937746ec377100ed6595c851b6a39`
- output format: mono PCM16, 24000 Hz
- duration: 5.749333 seconds

The receipt also records the successful API path as:

`Xtts.load_checkpoint(checkpoint_path=..., vocab_path=...) -> get_conditioning_latents(reference) -> inference(language=ar)`

Perceptual speaker identity and transcript accuracy were not independently certified.

## Scope

This receipt proves a prior successful local execution and binds the recorded artifacts by hash. It does not claim that the XTTS cache or private reference files are still present at the same filesystem path today.

XTTS and its model weights remain subject to their own upstream licensing. This repository does not redistribute those weights.
