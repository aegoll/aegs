# AEGS — Autonomous Economic Governance Standard

**An open specification for the layer that decides whether an autonomous agent may spend,
and for the evidence it must produce.**

x402, AP2, cards and account-to-account rails answer *how* an agent pays. AEGS specifies the
layer that answers *whether it should* — the controls that must exist, the evidence that must
be emitted, and how an independent implementation can be scored against both.

**The claim:** autonomous payment should not mean unrestricted payment.

> **Status: draft, pre-0.1.** Thirteen schemas and a regulatory crosswalk exist; the
> normative prose, the rail bindings and the test vectors are being written. See
> [`PLAN.md`](PLAN.md).

---

## Protocol-neutral by construction

AEGS specifies a **control set**, and each payment rail gets a **binding**. x402 with
stablecoins is the first binding because it is the one with a working implementation behind
it — not because the standard is about x402.

| Binding | State |
|---|---|
| **x402** — HTTP 402, stablecoin settlement | first binding, written from a working implementation |
| **AP2** — mandate-based agent payments | sketch |
| **MCP** — tool call as economic action | sketch |
| **Card / account-to-account** | sketch. Named mainly for what they break: reversibility, chargebacks, settlement days later |

A binding must supply its unit of account, atomic precision, settlement finality semantics,
counterparty identity shape, reversibility, and what "vendor" means on that rail. If a core
schema cannot express a decision from a sketched binding, the schema is too x402-shaped and
gets fixed — which is the point of writing the sketches before anyone needs them.

## The thirteen controls

| Control | Reference implementation |
|---|---|
| AgentIdentity · EconomicIntent · Policy · BudgetEnvelope | engine-backed |
| RiskAssessment · TrustAssessment · GovernanceDecision | engine-backed |
| EvidenceRecord | engine-backed, with a documented truncation gap |
| ConformanceDeclaration | engine-backed (AEGS-CONF) |
| Authorization | partial — carried by identity and intent |
| **AMLAssessment · ComplianceAssessment · IncidentRecord** | **schema only, no engine** |

The count going from 3 to 13 is **not** a capability claim, and one rule keeps it honest:
every schema requires its object be **omitted** rather than zero-filled when the control does
not exist. An implementation cannot assert a screening that never ran.

## What conformance means here

- The conformance runner **imports no implementation**. It scores Decision Records.
- A verdict that is correct but attributed to the *wrong control* is recorded separately. It
  was right by accident, and the same case shaped differently would fail.
- The suite ships as its own package. A conformance suite that arrives bundled with the
  thing it tests is not a conformance suite.
- Anyone may run it and publish the result, **including a failing one**.

`pip install aegs-conformance` — note: **not** `pip install aegs`, which is an unrelated
package by someone else.

## Layout

| | |
|---|---|
| `spec/` | normative prose, RFC 2119 |
| `schemas/` | the 13 interface objects, JSON Schema Draft 2020-12 |
| `bindings/` | one document per payment rail |
| `vectors/` | language-neutral test vectors — input, expected verdict, attributed control, envelope state, record hash |
| `conformance/` | AEGS-CONF: cases as data, a runner, and adapters |
| `crosswalk/` | AEGS against NIST AI RMF, ISO/IEC 42001, ISO 37301, GDPR, EU AI Act, FATF, MiCA |
| `upstream/` | engagement with `x402-foundation/x402` |

## The crosswalk is a mapping, not a compliance claim

`AEGS-CROSSWALK-001` places AEGS controls relative to seven frameworks in three categories —
Direct, Partial, Outside scope — with per-framework provenance markers.

**No row says AEGS complies with anything.** NIST AI RMF and EU AI Act rows are sourced;
ISO/IEC 42001 is from a secondary summary of a paywalled standard; **ISO 37301, FATF and MiCA
are unsourced and labelled so.** The legal readings still need a qualified reviewer, and the
unsourced rows stay labelled rather than quietly tidied. A crosswalk with the uncertainty
removed is marketing.

One real gap the crosswalk found and nobody upstream covers either: the **FATF Travel
Rule**. AEGS carries no originator or beneficiary data, which matters for any stablecoin
deployment between regulated parties.

## What is not established

- **AML/CFT effectiveness** — schema only. Effectiveness is not demonstrable without labelled financial-crime data this project does not have
- **Standards novelty** — unestablished
- **Independent implementation** — the suite has never scored a system nobody here wrote. The open question it exists to answer
- **Independent review** — the evaluation labels, threat catalogue and conformance cases were all written by the author of the system under test
- **Sanctions screening** — currently a boolean on a vendor object. No list, no matching

## Licence

Two licences, scoped by directory:

- **CC-BY-4.0** for the specification text — `spec/`, `bindings/`, `crosswalk/`, `schemas/` — so it can be quoted, reproduced and built on
- **Apache-2.0** for the tooling in `conformance/`

See [`LICENSES.md`](LICENSES.md).

## Related

[`aegoll`](https://github.com/aegoll/aegoll) — the reference implementation ·
[`aegoll-integrations`](https://github.com/aegoll/aegoll-integrations) — examples ·
[`Jayzilva/x402`](https://github.com/Jayzilva/x402) — the read-only proof-of-concept
