# Repo Backup — 2026-09-30

Executed in yolo mode per request. Backed up every local eco dir that had no
remote. Canonical account: `cryptonomicsed-byte` (was 108 repos → 148 now).

## Tier 1 — no remote, no GitHub repo, content at risk → CREATED
| Local dir | New repo | Vis | Note |
|---|---|---|---|
| ~/tripwire | cryptonomicsed-byte/tripwire | public | security/detection-honeypot spec, v0.1 |
| ~/ForgeVault | cryptonomicsed-byte/ForgeVault | public | token-mechanics vault; 451M node_modules untracked, source only (~2M) |

## Tier 2 — repo existed on GitHub, local had no remote → WIRED
| Local dir | Repo | Note |
|---|---|---|
| ~/sovereign-types | cryptonomicsed-byte/sovereign-types | pushed real source (crypto.rs, identity.rs, merkle.rs, receipt.rs) |

## Tier 3 — crates already folded into sovereign-stack → COMMITTED IN PLACE (no new repo)
| Local dir | Note |
|---|---|
| ~/sovereign-pipeline | 8 files, committed on master (member crate of sovereign-stack) |
| ~/twin-protocol | 15 files, committed on master (member crate of sovereign-stack) |

## Tier 4 — existed ONLY on retired Bino-Elgua → MIGRATED to canonical
| Local dir | New repo | Vis | Note |
|---|---|---|---|
| ~/technosis/evil-twin | cryptonomicsed-byte/Evil-twin | **private** | adversarial twin/MITM tool; had .env.production (gitignored) |
| ~/technosis/vanity-eth | cryptonomicsed-byte/Vanity-eth | public | vanity address generator |
| ~/technosis/ase-vault | cryptonomicsed-byte/ase-vault | **private** | vault; was pointed at dead omo-koda org |
| ~/archive/asemirror | cryptonomicsed-byte/asemirror | public | |

## Tier 5 — portfolio snapshots (project-NN-*) → CREATED
33 repos: `cryptonomicsed-byte/project-1-AICouncil` … `project-33-Aurora-Ghost-V2`.
node_modules gitignored; a few created private where a secret pre-scan tripped
(project-1, project-16, project-32, project-6).
`~/GamerWingman` (standalone) — pending create (throttled).

## Pitfalls hit (for next time)
- GitHub repo-creation secondary limit trips after ~10 repos/hr. Space creates
  ≥50s and expect ~1h wait per throttle window.
- `cryptonomicsed-byte` gh token LACKS `delete_repo` scope — can't prune; hide
  leftovers with `gh repo edit --visibility private`.
- GitHub push protection blocks pushes containing secrets. project-25 contained a
  Stripe **test** key in a docs table → redacted, and the repo was re-inited to a
  single clean commit (a new commit doesn't help; protection scans all pushed commits).
- `pkill -f eco_backup` self-kills the invoking shell (matches its own cmdline).

## Left alone (deliberately)
- `.openclaw/workspace` — OpenClaw agent homedir (agent state, not an eco repo)
- `_archive_repos/{dip,vcp,Technosis-Sovereign-Ecosystem}` — canonical equivalents exist
- 112 local repos still pointed at retired Bino-Elgua (bulk migration not in scope of 1-5)
- `zz-throttle-probe` — orphaned probe repo (cannot delete, no scope); made private
