# Security and threat model

## Assets and trust boundaries

Protect source integrity, generated binaries, local files, optional private voice
assets, and the integrity of published commits. Runtime code/data is trusted
compiled NASM; malformed declarations and generated-file corruption are tested.
There is no network service, authentication system, external score loader or
privileged resident process added by this project.

Trusted inputs: the reviewed checkout and its parent directories, selected
compiler/assembler/interpreter binaries, the OS/DOS BIOS, and explicitly supplied
MLAsm/TTS executables. Test doubles model faulty ML library returns without
claiming that a hostile in-process library can be sandboxed. Host build scripts
are not safe execution containers for malicious repository code.

## Controls and residual limits

| Threat | Control | Residual boundary |
|---|---|---|
| Partial/stale build output | Private sibling staging, checked NASM, validation before replace, source digest and alias checks | Not a multi-file transaction; source parent directories must be trusted |
| Symlinked build/cleanup destination | Reject build symlink; fixed root-relative cleanup | No protection against privileged concurrent directory replacement |
| Malformed records/truncation | NASM field/scope/count checks; bounded independent binary parsers; media runtime extent | Trusted compiled score readers are not arbitrary-file parsers |
| Faulty optional C results | Index/finiteness/range checks, checked setters, one cleanup path, checked output publication | Arbitrary malicious linked native code remains trusted code |
| Lost/partial C output | Checked writes/close/rename; private mkstemp sibling; existing output preserved on failure | Parent-directory ownership is trusted; stdout failure after rename cannot undo publication |
| Accidental public media/secrets | Ignored private paths, committed-tree policy, explicit push, exact origin | Pattern checks are not comprehensive secret detection; old remote history is not re-audited automatically |
| Voice process side effects | Explicit tools/models, training interlock, quoted arguments, ignored private output, no default publication | External TTS/model licenses, consent, file validity and quality require separate verification |
| CI privilege/supply chain | Read-only token, no persisted checkout credential, immutable action SHAs, pinned optional source/wheel, timeout/concurrency | Hosted runner/APT/toolchain are not a hermetic or formally verified supply chain |
| Interrupt/DMA lifecycle failure | Bounded polling, completion handler, DMA masked before abort, vector/mask restoration | Exclusive supported hardware ownership required; no physical compatibility guarantee |

No finding in the audit establishes an internet-exploitable remote service.
Severity applies to the actual local build/runtime trigger, not an invented
network exposure. Implementation of these controls does not establish legal,
regulatory, licensing or compliance status.

## Publication

`bash scripts/publish-repo.sh --check` scans committed HEAD only. It never stages,
commits, regenerates files, creates a repository or pushes. The explicit `--push`
mode additionally requires a clean tree, a valid branch, a known origin/main
reference and the exact existing Grar00t/opcode-orchestra origin. It checks
outgoing commit trees before a normal non-force push. Fetch remote references
and review the outgoing range before invoking it; stale references can change
what history is considered outgoing.

Symlinks/submodules, binary/oversized content, known private directories, media,
weights, credentials and generated artifacts are rejected by policy. A private
path or novel secret embedded in ordinary text may evade patterns. Review the
actual diff and file list; do not treat a policy PASS as permission to disclose
anything. Generated diagnostic archives are delivery evidence, not source
files to commit.

## Reporting

Provide the affected commit, path/line, a minimal reproduction, expected/actual
behavior, and the tested environment. Do not attach credentials, model weights,
speaker references or private recordings. A claim without a reproducer or
supporting source remains unverified. Release decisions use the separate
verification layers, not a generic security badge.
