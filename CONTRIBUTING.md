# Contribution and release gates

Preserve the Assembly core and existing licensing/composition attribution.
Do not add a backend, service, binary format or dependency without a demonstrated
requirement. Read the affected source and calling/format contracts first.
Record the starting commit and run the applicable existing gates before editing.

A material patch needs a reproduction or explicit proof method, a focused
regression and the full applicable suite. Negative assembler tests must identify
the intended rejection diagnostic. Scripted I/O tests must be labeled as such;
never call them physical hardware or listening tests. Do not weaken unrelated
tests to accommodate a patch.

## Release checklist

1. Record commit, tool versions and configuration. Run `make clean`, `make`,
   `make verify`, `make verify-future`, `make -j4 check`, `make verify-cpu`,
   `make reproducible` and `make inspect`. Run configured optional bridge and
   DOS execution targets separately. Resolve failures rather than hiding them.
2. Inspect `git diff --check`, `git diff --stat`, the complete diff and tracked
   file list. Verify the manifest/source hashes, exact documentary embedding,
   alias identity and unchanged intended v1 data. Check a parallel clean build.
3. Review publication policy on the committed result. No build output, test
   archives, private paths, weights, speaker references, generated speech,
   downloaded media, credentials or unrelated editor files may be committed.
4. Ensure every documented Make target exists and commands are runnable with
   the stated prerequisites. Describe breaking behavior in CHANGELOG.md.
5. Attach exact commands, exit codes, logs, artifact hashes and separate status
   for source, static, scripted CPU, emulator, timing, synthesis, PCM, listening
   and real-hardware verification. Execute the manual hardware/audio procedure
   before claiming those layers; otherwise leave them NOT VERIFIED.
6. Review the actual CI run for the release commit. SHA pinning and a valid YAML
   file are not evidence that a workflow executed successfully. Do not merge or
   publish a release solely because compilation passed.

The publisher never commits for you. Review/stage/commit deliberately, fetch
remote references and review outgoing history before the optional explicit push.
