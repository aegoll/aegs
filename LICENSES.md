# Licences

Two licences, scoped by directory. The split is deliberate: a specification that cannot be
quoted is not a standard, and tooling that carries no patent grant is a liability for anyone
who adopts it.

| Path | Licence | Why |
|---|---|---|
| `spec/` · `bindings/` · `crosswalk/` · `schemas/` · `vectors/` | **CC-BY-4.0** | Specification text and interface definitions. Must be quotable, reproducible, and build-on-able by anyone — including a competing implementation |
| `conformance/` · any other code | **Apache-2.0** | The patent grant matters for anything with standards ambition, and a conformance suite is code someone runs in CI |
| `upstream/` | CC-BY-4.0 | Analysis and proposal drafts — text |

Attribution for the CC-BY-4.0 portions: **Jayzilva** — https://github.com/aegoll/aegs

## Files

- [`LICENSE`](LICENSE) — Apache-2.0, full text, applies to code
- `LICENSE-CC-BY-4.0` — **to be added**: the verbatim CC-BY-4.0 legal code from
  https://creativecommons.org/licenses/by/4.0/legalcode.txt. It is not written from memory
  here on purpose; a licence file that is *almost* the real text is worse than none

## Contributions

Contributions to the specification are accepted under CC-BY-4.0 and contributions to code
under Apache-2.0, matching the directory they land in. See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## What this does not license

The crosswalk in `crosswalk/` maps AEGS controls against external frameworks — NIST AI RMF,
ISO/IEC 42001, ISO 37301, GDPR, the EU AI Act, FATF, MiCA. **Those framework texts are not
ours and are not licensed here.** ISO standards in particular are paywalled; the crosswalk
quotes clause identifiers and characterises requirements, and marks any row it could not
source from a primary text as UNSOURCED.
