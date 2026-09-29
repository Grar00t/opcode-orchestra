# Optional local XTTS tooling and historical receipt

XTTS is outside the Assembly core. No real model, speaker input, synthesis,
transcript check or listening test was executed by this hardening audit.
The script's tests use a deliberately non-audio process stub. They establish
interlock/error/output-file behavior only.

## Invocation boundary

Set `TTS_EXE` to an inspected executable and `MODEL_DIR` to an existing directory
containing `model.pth`, `config.json`, and `vocab.json`. Supply either an original
or authorized `SPEAKER` file or a valid `SPEAKER_IDX`. `TEXT` optionally selects
local text; otherwise the original repository text is used. `TTS_BACKEND` is
`native` by default or explicitly `wsl-windows`, which requires `wslpath`.

After setting those environment variables, run:

```sh
bash voice/render_xtts_after_training.sh
```

The default process interlock searches for `[n]iyah-train`; `TRAINING_PATTERN`
can explicitly change it. Exit 20 means active training, 21 missing speaker
selection, 22 failed process check, 2 invalid backend. Missing configuration,
files or tool/process failure also exits nonzero. Success reports only a
nonempty process output at ignored `voice/raw/selective-fear-xtts.wav`.
A raw output directory symlink is rejected. Output is staged privately and a
failed synthesis leaves the previous output intact. Tool logs remain under the
ignored private directory, not in CI artifacts.

There is no implicit Windows export, caller-supplied output directory, model
download, installation or publication. Nonempty output is not a WAV-format,
voice-quality, language, consent or licensing certificate.

## Historical record retained, not independently reverified

The pre-hardening document asserted a prior reference-conditioned XTTS run and
recorded the following SHA-256 values. The underlying private artifacts and
execution log were not supplied to this audit. These are retained recorded
claims, not newly verified hashes:

| Recorded item | Recorded SHA-256 |
|---|---|
| model.pth | c7ea20001c6a0a841c77e252d8409f6a74fb423e79b3206a0771ba5989776187 |
| config.json | ef262b1454dd2a77e1461b0b2cd53e19b8a7624cc131b837d36df67356bc75e8 |
| vocab.json | 928260878a59da8a72a2a5b7687fea29d5106137669d90945430fe17e415304a |
| speakers_xtts.pth | f0f6137c19a4eab0cbbe4c99b5babacf68b1746e50da90807708c10e645b943b |
| output | 24b3747756f4003c8e22483d9e312f65ec4937746ec377100ed6595c851b6a39 |

The old receipt also stated mono PCM16 at 24,000 Hz, duration 5.749333 seconds,
and a checkpoint/conditioning/inference API path. Those statements remain
unverified in this environment. Perceptual speaker identity and transcript
accuracy were not certified even by the old receipt. Upstream software/model
licenses apply independently; this repository does not redistribute weights.
