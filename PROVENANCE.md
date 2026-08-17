# Provenance

Content in this repository was **ported** from the proof-of-concept at
[`Jayzilva/x402`](https://github.com/Jayzilva/x402), which is read-only and stays intact.

Porting was done by copying rather than by `git subtree split`, so `git log --follow` here
does **not** reach the prototype's commits. That cost was accepted deliberately; this file
and the commit trailers are the mitigation.

**Source commit:** `e3e295b` (branch `agents`) — the state that recorded 13 validating
schemas, AEGS-CONF at 7/7, and the regulatory crosswalk with its unsourced rows labelled.

Every porting commit carries `Ported-from: Jayzilva/x402@e3e295b <source path>` and copies
faithfully first. Changes arrive in separate, later commits so the diff shows what changed
and why.

---

## Ported

| Here | From `Jayzilva/x402` | Commit | Changed since |
|---|---|---|---|
| `schemas/` — 13 JSON Schemas | `aegs/schemas/` | `67dedc3` | `$id` rewritten to a host that resolves — `bbb2f31` |
| `crosswalk/AEGS-CROSSWALK-001.md` | `aegs/AEGS-CROSSWALK-001.md` | `67dedc3` | unchanged; UNSOURCED markers intact |
| `conformance/` — 7 cases, runner, 2 adapters, 18 tests | `conformance/` | `08802e9` | adapter repointed at the installed `aegoll`; runner schema path; fail-fast on a missing implementation — `4641e15` |

**This repository held no schemas before the port.** An earlier draft of the plan said a
kickstart copy was already here; it was not — they existed only in the proof-of-concept.

## Changed after the faithful copy, and why

**`$id` host.** Every schema carried `https://aegs.dev/schemas/…` and `aegs.dev` does not
resolve (DNS `ENOTFOUND`, checked 2026-08-17). A `$id` that 404s is a broken standard, so
all 13 now read `https://aegoll.github.io/aegs/schemas/…`. Still unserved while this repo is
private — correct and unresolvable, which is the right way round.

**The conformance adapter.** It used to insert a sibling directory into `sys.path`, which
quietly required the suite and the implementation to share a monorepo. That is the opposite
of what a conformance suite is for: it must be able to score an implementation whose source
you have never seen. It now requires `aegoll` to be *installed*, and refuses to print a
score it cannot stand behind when it is not.

## Not ported

Not-ported is a decision, not an omission.

| Not ported | Why |
|---|---|
| `research/` — 6 sealed experiments, 5 baseline docs, 31 tests | Their commit stamps point at the POC, and the read-only rule makes that a stable citation target. Records measured *after* the split come here instead ([W0.5](../PLAN.md)) |
| `security/report.md`, `security/redteam/` | Executable attacks belong beside the engines, in `aegoll`. The threat *catalogue* comes here as `spec/12-security-considerations.md` ([B2.17](PLAN.md)) |
| `aegl_aegs.md` | The long-range strategy document, and the origin record. **Linked, never copied.** Copies drift |
| `EXECUTION-PLAN.md` | Superseded plan. Kept in the POC as the decision record — a log with the wrong turns removed is not a log |

## Downstream copies

`aegoll` vendors three of these schemas as package data so it can validate offline. Those
copies are pinned to a commit here and checked for drift by
`aegoll/tools/check_schema_drift.py`. **`schemas/` in this repository is the canonical
version**; a schema change is made here and copied down afterwards, never the reverse.
