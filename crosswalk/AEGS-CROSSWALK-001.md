# AEGS-CROSSWALK-001 — regulatory and standards crosswalk

**Status:** draft 0.1 · **Date:** 15 August 2026 · **Supersedes:** nothing

Maps AEGS controls to obligations in seven external instruments, so an implementer
can see where AEGS controls *relate to* something they already have to satisfy — and,
more usefully, where they do not.

---

## Read this before the tables

### What this document does and does not say

Every row says: **"AEGS control X relates to requirement Y."**

No row says, and no row may ever say: *"AEGS = compliance with Y."*

That is not modesty. A compliance determination requires a jurisdiction, a set of
facts about a specific deployment, and a qualified person. AEGS is a technical control
framework; it can record that controls ran and what they found. Whether that satisfies
an obligation is a legal question this document cannot answer and does not attempt to.

An implementation that cites this crosswalk to a regulator, an auditor or a customer
as evidence of compliance is misusing it.

### The three categories

| Category | Meaning |
|---|---|
| **Direct alignment** | The AEGS control produces something the requirement asks for, in substantially the same form. Still not compliance — the requirement may demand organisational context AEGS has no view of. |
| **Partial alignment** | The AEGS control contributes to satisfying the requirement but is insufficient alone. Usually because the requirement covers people, process or governance that a technical layer cannot supply. |
| **Outside scope** | AEGS says nothing about this. Listed deliberately: a crosswalk that only shows matches misrepresents coverage, and the gaps are the more useful half. |

### Provenance — read this too

Standards and regulations differ in how verifiable their structure is from open
sources. Each framework below carries a provenance marker, and **rows marked
`UNSOURCED` are the author's understanding and have not been checked against the
instrument text.** They are included so the shape of the mapping is visible, and they
must be verified before this document is shown to anyone who might rely on it.

| Framework | Provenance | Basis |
|---|---|---|
| NIST AI RMF 1.0 | **Sourced** | Category identifiers from the NIST AI RMF Playbook (`airc.nist.gov`) |
| EU AI Act | **Sourced** | Article numbers and obligations from `artificialintelligenceact.eu` and the EC AI Act Service Desk |
| ISO/IEC 42001:2023 | **Secondary** | Annex A control identifiers from a published summary. The standard itself is paywalled and has **not** been read |
| ISO 37301:2021 | **UNSOURCED** | Paywalled. Structure assumed to follow the ISO management-system format |
| GDPR | **Partly sourced** | Article numbers are well established; the readings below have not been verified against the text or case law |
| FATF Recommendations | **UNSOURCED** | Recommendation numbers from the author's understanding |
| MiCA | **UNSOURCED** | No article-level mapping attempted. See the note in its section |

**A qualified reviewer is required before any of the legal rows are relied upon.**
That is a stated dependency of this document, not a caveat added to it.

---

## The AEGS control set

Thirteen objects, version 0.1. Implementation status in AEGL is shown because a
control that exists only in a schema is a specification, not a capability.

| # | Control | Purpose | In AEGL |
|---|---|---|---|
| 1 | **AgentIdentity** | Who is acting, under whose authority | built |
| 2 | **EconomicIntent** | What the agent was *sent to do* | built |
| 3 | **Policy** | Versioned, content-addressed rules | built |
| 4 | **Authorization** | Scoped, time-bounded permission to act | partial — identity and intent carry it; no standalone object |
| 5 | **BudgetEnvelope** | One spending constraint and its headroom | built |
| 6 | **RiskAssessment** | Risk of this action | built |
| 7 | **TrustAssessment** | What is known of this counterparty | built |
| 8 | **AMLAssessment** | AML/CFT finding | **schema only — no engine** |
| 9 | **ComplianceAssessment** | Which controls were exercised, per profile | **schema only** |
| 10 | **GovernanceDecision** | The verdict and its attribution | built |
| 11 | **EvidenceRecord** | Tamper-evident log entry | built, with a known truncation gap |
| 12 | **IncidentRecord** | Something went wrong, or nearly did | **schema only** |
| 13 | **ConformanceDeclaration** | What an implementation claims, and on whose word | built (AEGS-CONF) |

---

## NIST AI RMF 1.0

*Provenance: sourced.* Voluntary US framework; four functions — GOVERN, MAP, MEASURE,
MANAGE — each with numbered categories.

| AEGS control | NIST category | Alignment | Note |
|---|---|---|---|
| Policy | **GOVERN 1.4** — risk management process and outcomes established through transparent policies | **Direct** | AEGS policy is declarative, versioned and content-addressed |
| Policy · Authorization | **GOVERN 1.2** — trustworthy AI characteristics integrated into policies | **Partial** | AEGS covers the economic dimension only |
| AgentIdentity | **GOVERN 1.6** — mechanisms inventory AI systems | **Partial** | Identifies *agents*, not the organisation's AI inventory |
| AgentIdentity · Authorization | **GOVERN 2.1** — roles, responsibilities and communication lines documented | **Partial** | Machine-side accountability; says nothing about human roles |
| EvidenceRecord · GovernanceDecision | **GOVERN 1.5** — ongoing monitoring and periodic review | **Partial** | Supplies the record; the review is organisational |
| TrustAssessment | **GOVERN 6.1** — policies address third-party risk | **Partial** | Counterparty history, not supplier due diligence |
| RiskAssessment · TrustAssessment | **MAP 1–2** — frame the system, its context and stakeholders | **Partial** | Per-action framing, not system-level |
| RiskAssessment | **MEASURE 2** — assess and benchmark identified risks | **Partial** | AEGS specifies the finding's shape, deliberately not the method |
| IncidentRecord | **MANAGE 4** — risk treatment and incident response | **Partial** | Schema exists; no response process is specified |
| ConformanceDeclaration | **GOVERN 4.3** — practices enable testing and incident identification | **Direct** | AEGS-CONF is exactly this, for the economic controls |
| — | **GOVERN 2.2** — personnel training | **Outside scope** | People, not machines |
| — | **GOVERN 3** — workforce diversity | **Outside scope** | |
| — | **GOVERN 5** — stakeholder engagement | **Outside scope** | |
| — | **GOVERN 1.7** — safe decommissioning | **Outside scope** | AEGS has no lifecycle model |

---

## ISO/IEC 42001:2023 — AI management system

*Provenance: secondary. Annex A identifiers taken from a published summary; the
standard is paywalled and has not been read.* Clauses 4–10 are management-system
requirements; Annex A holds 38 reference controls across objectives A.2–A.10.

| AEGS control | ISO 42001 control | Alignment | Note |
|---|---|---|---|
| Policy | **A.2.2** AI policy | **Partial** | AEGS policy governs economic action; A.2.2 expects an organisational AI policy |
| Policy | **A.2.4** review of the AI policy | **Partial** | Versioning and supersession are supported; the review cadence is organisational |
| AgentIdentity · Authorization | **A.3.2** AI roles and responsibilities | **Partial** | Machine-side only |
| IncidentRecord | **A.3.3** reporting of concerns | **Partial** | A record type, not a reporting channel |
| RiskAssessment | **A.5.2** impact assessment process | **Partial** | Per-action economic risk, not system impact assessment |
| — | **A.5.4 / A.5.5** impact on individuals, societal impact | **Outside scope** | AEGS assesses economic exposure, not societal effect |
| EvidenceRecord | **A.6.2.8** recording of event logs | **Direct** | This is precisely what EvidenceRecord specifies |
| GovernanceDecision · EvidenceRecord | **A.6.2.6** operation and monitoring | **Partial** | Supplies the operational record |
| ConformanceDeclaration | **A.6.2.4** verification and validation | **Partial** | Validates governance behaviour, not the AI system |
| — | **A.7** data for AI systems (provenance, quality, preparation) | **Outside scope** | AEGS governs spending, not training data |
| IncidentRecord | **A.8.4** communication of incidents | **Partial** | Records; does not communicate |
| TrustAssessment | **A.10.3** suppliers | **Partial** | Transactional history, not supplier governance |
| — | **A.4** resources · **A.9** responsible use objectives | **Outside scope** | |

---

## ISO 37301:2021 — compliance management systems

> **UNSOURCED.** The standard is paywalled and has not been read. The rows below are
> the author's understanding of a compliance-management-system structure and **must be
> verified before use**. They are shown so the shape of the relationship is visible.

| AEGS control | ISO 37301 area (unverified) | Alignment | Note |
|---|---|---|---|
| ComplianceAssessment | Compliance obligations and evaluation | **Partial** | AEGS records which controls ran against a *profile*, never a legal conclusion |
| Policy | Compliance policy | **Partial** | Economic scope only |
| EvidenceRecord | Documented information / records | **Direct** | Append-only, tamper-evident, with a stated truncation limit |
| IncidentRecord | Non-compliance and corrective action | **Partial** | Records; no corrective-action workflow |
| ConformanceDeclaration | Performance evaluation | **Partial** | Self-attestation by default, and it says so |
| — | Leadership, culture, competence, whistleblowing | **Outside scope** | Organisational |

---

## GDPR — Regulation (EU) 2016/679

*Provenance: article numbers well established; readings not verified against text or
case law.*

AEGS is **privacy-relevant by construction** rather than privacy-compliant: identity
is pseudonymous by default, and controller, operator, wallets and spending limits are
excluded from counterparty disclosure.

| AEGS control | GDPR article | Alignment | Note |
|---|---|---|---|
| AgentIdentity — selective disclosure | **Art. 5(1)(c)** data minimisation | **Partial** | Counterparties receive a handle and purpose; controller identity is withheld |
| AgentIdentity — pseudonymous by default | **Art. 25** data protection by design and by default | **Partial** | A design position, not an implementation of the article's full obligation |
| EvidenceRecord · GovernanceDecision | **Art. 30** records of processing activities | **Partial** | Records economic decisions, not processing of personal data |
| GovernanceDecision — reasons and attribution | **Art. 22** automated individual decision-making | **Partial, and read carefully** | AEGS decisions are about an *agent's spending*, not about a data subject. Where a governed action does affect a person, Art. 22 obligations are **not** met by AEGS |
| EvidenceRecord — hash chaining | **Art. 32** security of processing | **Partial** | Integrity only, and with a known truncation gap |
| RiskAssessment | **Art. 35** DPIA | **Outside scope** | Economic risk is not a data-protection impact assessment |
| — | Arts. 12–23 data subject rights | **Outside scope** | AEGS holds no data subject records |
| — | Arts. 44–50 international transfers | **Outside scope** | |

> **The trap this table exists to prevent.** Pseudonymous identifiers are still
> personal data where they can be linked to a person. AEGS reduces disclosure; it does
> not remove a controller's obligations, and an append-only journal creates an erasure
> problem rather than solving one.

---

## EU AI Act — Regulation (EU) 2024/1689

*Provenance: sourced.* High-risk obligations under Arts. 9, 12–15 and 26 apply from
2 August 2026.

**Whether an x402 buying agent is a high-risk AI system under Annex III is a legal
question and is not assumed here.** The mapping shows what AEGS would contribute *if*
the obligations applied.

| AEGS control | AI Act article | Alignment | Note |
|---|---|---|---|
| EvidenceRecord | **Art. 12** record-keeping — automatic logging over lifetime | **Direct** | Automatic, append-only, tamper-evident. The closest match in the whole crosswalk |
| EvidenceRecord | **Art. 19** automatically generated logs | **Direct** | Same mechanism |
| EvidenceRecord · ConformanceDeclaration | **Art. 26(6)** deployers retain logs ≥ 6 months | **Partial** | AEGS specifies the record; retention is a deployment policy AEGS does not set |
| GovernanceDecision — REVIEW / ESCALATE verdicts, human override | **Art. 14** human oversight | **Partial** | Provides the *mechanism* — a pausable verdict and a recorded override. The competent, trained, authorised person the article requires is organisational |
| IncidentRecord | **Art. 26** — monitor and report serious incidents | **Partial** | A record type; no reporting channel or timeline |
| RiskAssessment | **Art. 9** risk management system | **Partial** | Per-action economic risk, not a lifecycle risk-management system |
| — | **Art. 13** transparency to deployers · **Art. 15** accuracy and robustness | **Outside scope** | Properties of the AI system, not of the governance layer |
| — | Conformity assessment, CE marking, registration | **Outside scope** | AEGS-CONF is a technical suite and confers no regulatory status |

---

## FATF Recommendations

> **UNSOURCED.** Recommendation numbers are the author's understanding and have **not**
> been verified. FATF is also a standard-setter for *jurisdictions*, so obligations
> reach an implementation only through national law — which makes any direct mapping
> doubly indirect.

| AEGS control | FATF area (unverified) | Alignment | Note |
|---|---|---|---|
| TrustAssessment · AgentIdentity | R.10 customer due diligence | **Partial at best** | Counterparty *history* is not CDD. AEGS has no identity verification |
| AMLAssessment | R.15 new technologies · R.20 suspicious transaction reporting | **Partial — schema only** | The interface exists; **no detection engine exists**, and effectiveness is undemonstrated |
| AMLAssessment — counterpartyScreening | Targeted financial sanctions | **Partial — interface only** | AEGL's sanctions control is a boolean on a vendor object: no list, no matching, no name resolution |
| EvidenceRecord | Record-keeping | **Partial** | Retention periods are jurisdictional and unset |
| — | R.16 Travel Rule — originator/beneficiary information | **Outside scope** | AEGS carries no originator or beneficiary data. **This is a real gap for any stablecoin deployment**, and the x402 extension is where it would belong |
| — | Licensing, VASP registration, national risk assessment | **Outside scope** | Organisational and jurisdictional |

> **Do not read the AML row as coverage.** `AMLAssessment` is a schema with no engine
> behind it. Emitting it without an assessment would assert a screening that never
> happened, which is why the schema requires the object be *omitted* rather than
> zero-filled when the control does not exist.

---

## MiCA — Regulation (EU) 2023/1114

> **UNSOURCED — no article-level mapping attempted.**

MiCA governs crypto-asset issuers and service providers: authorisation, prudential
requirements, custody, market abuse. AEGS governs *an agent's spending decisions*,
which is a different subject.

Two honest observations rather than a table:

1. **Most of MiCA is outside AEGS scope.** Authorisation, capital, custody, white
   papers and market-abuse rules concern the entity providing crypto-asset services.
   AEGS says nothing about any of them.
2. **The overlap, if any, is on the record-keeping and transaction-monitoring side**,
   where an EvidenceRecord and an AMLAssessment might contribute to obligations a CASP
   already has. Whether they do requires reading the text against a specific
   deployment, and is exactly the kind of claim this document refuses to make on
   memory.

A meaningful MiCA mapping needs the regulation text and a qualified reviewer. Until
then this section stays as a stated gap rather than a filled table, because a
confident-looking wrong table is worse than an admitted absence.

---

## What the crosswalk reveals about AEGS

Reading the tables as a whole rather than row by row:

**AEGS is strongest at evidence.** The clearest matches anywhere are AI Act Arts. 12
and 19, and ISO 42001 A.6.2.8 — all about automatic, durable event logging. That is
what AEGS was built around, and it shows.

**AEGS is weakest exactly where it claims least.** AML, sanctions and compliance
assessment are schemas with no engines. Every one of those rows is marked partial or
interface-only, and none of it should be read as coverage.

**A large fraction of every framework is outside scope, and that is correct.** These
instruments govern organisations — training, culture, competence, stakeholder
engagement, licensing. A technical layer that claimed to address them would be
overreaching. The value of listing them is that an implementer can see what AEGS will
never do for them.

**One gap is worth naming on its own: the FATF Travel Rule.** AEGS carries no
originator or beneficiary information. For any deployment moving stablecoins between
regulated parties, that is a real requirement AEGS does not touch — and the x402
governance extension is the natural place to address it.

---

## Status and next steps

This is a **draft with declared unverified sections**. Before it is used in any
external conversation:

1. **Obtain and read** ISO/IEC 42001 and ISO 37301. Both are paywalled; the Annex A
   rows are currently from a secondary summary.
2. **Verify the FATF rows** against the Recommendations text.
3. **Attempt or formally abandon** the MiCA mapping, with reasons.
4. **Have the GDPR and AI Act readings reviewed by a qualified person.** Article
   numbers being right is not the same as the readings being right.
5. **Re-check the AI Act applicability question** — whether these agents are high-risk
   systems at all — which changes whether most of that table applies.

Until then the honest description is: *a structural map showing where AEGS controls
sit relative to seven frameworks, with the legal readings unverified.*
