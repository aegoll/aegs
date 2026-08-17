# `aegs` — sub-plan

**Autonomous Economic Governance Standard.** The open specification an AEGL conforms
to: what controls must exist, what evidence must be produced, and how an independent
implementation can be scored.

Master plan: [`../PLAN.md`](../PLAN.md) · Context and rules: [`../CONTEXT.md`](../CONTEXT.md)
Port source (**read-only**): `../x402/aegs/` (13 schemas + crosswalk) and `../x402/conformance/` (7 cases, 18 tests) — [`../x402-REFERENCE.md`](../x402-REFERENCE.md)
Ported in: 13 schemas, the crosswalk, and the 7-case conformance suite — all green here.

**The standard is protocol-neutral.** x402 stablecoins are the first *binding*, not the
subject. AP2, MCP payments, cards and account-to-account are later bindings against the
same control set. Getting the binding boundary right in 0.1 is the difference between a
standard and an x402 accessory.

---

## B0 — Bootstrap and licence 🔨

- [x] B0.1 Licence split recorded in [`LICENSES.md`](LICENSES.md) — **CC-BY-4.0** for spec text (`spec/`, `bindings/`, `crosswalk/`, `schemas/`, `vectors/`, `upstream/`), **Apache-2.0** for tooling. Apache text present as `LICENSE`
- [ ] B0.1a Add `LICENSE-CC-BY-4.0` with the **verbatim** text from `creativecommons.org/licenses/by/4.0/legalcode.txt`. Not written from memory — a licence file that is *almost* the real text is worse than none
- [x] B0.2 Repo layout decided and written in [`README.md`](README.md):
      `spec/` · `schemas/` · `bindings/` · `vectors/` · `conformance/` · `crosswalk/` ·
      `upstream/`. `research/` receives only records measured **after** the split ([W0.5](../PLAN.md))
- [x] B0.3 Version policy in [`CONTRIBUTING.md`](CONTRIBUTING.md) — `AEGS 0.1` moves independently of any implementation's semver; every record and declaration states both. Patch/minor/major defined, errata published rather than silently corrected
- [x] B0.4 **Schema `$id` host decided: GitHub Pages** — `https://aegoll.github.io/aegs/schemas/<name>-0.1.json`. `aegs.dev` was checked and does **not** resolve (DNS `ENOTFOUND`), so the prototype's 13 schemas all carry a `$id` that 404s. Owner's decision, 2026-08-17: free, resolves today, and hosted by the repo itself so the identifier cannot drift from the file it names. Applied at [B1.2a](#b1--import-the-prototypes-schemas-)
- [ ] B0.4a Enable GitHub Pages on this repo, serving `main`, so the `$id` URLs actually resolve. **A `$id` that 404s is a broken standard** — and switching hosts after 0.1 publishes is a breaking change
- [ ] B0.4c **This repo is private** (checked 2026-08-17), and Pages will not serve a private repo. So the `$id` URLs cannot resolve until the repo is public — the identifiers are correct and unserved, which is the right way round, but **AEGS 0.1 cannot publish before this is settled**. Tracked in [`../CONTEXT.md`](../CONTEXT.md) §4a
- [ ] B0.4b Add a redirect or note for anyone who followed the old `aegs.dev` identifier out of the prototype, if any schema ever leaked with it
- [x] B0.5 CI validates every schema as Draft 2020-12 and every example against its schema — [`.github/workflows/ci.yml`](.github/workflows/ci.yml). Jobs also stubbed for the normative-cross-reference linter, vector checks, and the stub-adapter-still-fails assertion
- [x] B0.6 [`CONTRIBUTING.md`](CONTRIBUTING.md) — four change kinds with different bars, the three questions a spec-change issue must answer, hard rules for prose/schemas/vectors/bindings, and what gets declined

**Exit:** repo shaped, licences scoped, schemas validating in CI.

---

## B1 — Import the prototype's schemas 🔨

- [x] B1.1 Schemas and crosswalk ported faithfully — `67dedc3`
- [x] B1.2 Nothing to reconcile — confirmed: this repo held no schemas, so the port was a clean first arrival
- [x] B1.2a `$id` rewritten in all 13 schemas — `bbb2f31`, a separate commit after the faithful port
- [x] B1.3 All 13 validate as Draft 2020-12, before and after the `$id` rewrite
- [ ] B1.4 Inventory table in `spec/control-set.md`, marking engine-backed vs schema-only:

  | Control | State in the reference implementation |
  |---|---|
  | AgentIdentity · EconomicIntent · Policy · BudgetEnvelope | engine-backed |
  | RiskAssessment · TrustAssessment · GovernanceDecision | engine-backed |
  | EvidenceRecord | engine-backed, truncation gap open |
  | ConformanceDeclaration | engine-backed (AEGS-CONF) |
  | Authorization | partial — carried by identity and intent |
  | **AMLAssessment · ComplianceAssessment · IncidentRecord** | **schema only, no engine** |

- [ ] B1.5 Keep the rule that makes 3→13 honest: each schema requires the object be **omitted** rather than zero-filled when the control does not exist, so an implementation cannot assert a screening that never ran
- [ ] B1.6 Add an example document per schema under `schemas/examples/` — a schema with no example gets read three ways

**Exit:** 13 schemas here, validating, with examples, and the capability table honest.

---

## B2 — AEGS 0.1 normative prose 🔨

The largest writing task in the whole plan, and the one that turns 13 schemas into a
standard. Schemas say what a document looks like; only prose says what an
implementation must *do*.

- [x] B2.1 [`spec/00-introduction.md`](spec/00-introduction.md) — scope, non-goals, the claim, and **what is not established stated in the spec itself** rather than in a footnote
- [x] B2.2 RFC 2119, stated once at [INTRO-3](spec/00-introduction.md) and enforced by the linter: capitals are normative, lower case is English, and a backticked keyword is being *named* rather than imposed
- [ ] B2.3 `spec/01-model.md` — agent, controller, operator, counterparty, channel, envelope, verdict, control, profile
- [ ] B2.4 `spec/02-controls.md` — the 13 controls, each with purpose, required inputs, required outputs, and what a conformant implementation must record
- [x] B2.5 [ENV-9](spec/03-envelopes.md) — channels never share an envelope, and an implementation **MAY** share limits but not envelopes, because an envelope carries consumption. A fuller `03-channels.md` on the two-channel *model* can follow; the envelope rule is the enforceable half and it is written
- [ ] B2.6 `spec/04-verdicts.md` — the four verdicts (APPROVE / REVIEW / ESCALATE / REJECT), the **narrowing rule** (no control may widen a verdict another set), and **evaluation order**
- [ ] B2.7 State why order is normative even though the final verdict is order-independent: **the attributed control is not order-independent, and conformance scores attribution**
- [x] B2.8 [`spec/05-arithmetic.md`](spec/05-arithmetic.md) — ARITH-1..9. Rounding pinned to half-up at [ARITH-3](spec/05-arithmetic.md) because every language's default differs and none is wrong in isolation; an implementation inheriting its own has made a decision it did not know it was making
- [x] B2.9 [ARITH-4](spec/05-arithmetic.md) and [ARITH-5](spec/05-arithmetic.md), both naming the defect they come from. ARITH-4 also fixes the **ordering**: the sign is refused *before* any envelope evaluation, which is the part the original bug got wrong
- [ ] B2.10 `spec/06-four-states.md` — **absent ≠ not-run ≠ unknown ≠ zero.** This came from a real bug: an unmeasured vendor history rendered as `0` made every advisor treat established counterparties as strangers
- [ ] B2.11 `spec/07-evidence.md` — append-only, hash-chained, canonical serialisation. Key order, number formatting and separators **change the hash**, so all three are normative
- [ ] B2.12 Document the truncation property honestly in the spec, not only in a security report: any prefix of a hash chain is a valid chain. Specify the anchor requirement for the level that claims tamper-evidence
- [ ] B2.13 `spec/08-identity.md` — pseudonymous by default, selective disclosure as a first-class operation, delegation clamp (a sub-agent may never claim more than its parent). Note that **`spendingLimits` is the sharpest privacy field**: disclosing remaining budget to a seller invites it to charge exactly that
- [x] B2.14a **Profile manifests written** — [`profiles/`](profiles/) with `aegs-1`, `aegs-2`, `none`, a [schema](schemas/profile-0.1.json), a [README](profiles/README.md) and [`tools/check_profiles.py`](tools/check_profiles.py). A profile is a conformance contract; a policy pack is what the rules are
- [ ] B2.14 `spec/09-profiles.md` — the normative prose behind the manifests. The manifests are the machine-readable half; this is the half that explains the requirement levels and why a profile never changes a verdict
- [ ] B2.15 `spec/10-decision-path.md` — the model-exclusion requirement. A conformant layer's decision path MUST be deterministic; an advisory model MAY be consulted only where it can tighten a verdict and never widen one
- [ ] B2.15a Extend it to **external calls, not only models.** Upstream [#2299](https://github.com/x402-foundation/x402/issues/2299) proposes querying external trust providers inside the settlement path with a `fail-open` option. Name the tension: a network call in the decision path is a latency, availability and manipulation surface, and **fail-open is a governance layer that stops governing exactly when it is attacked.** Specify what a conformant layer must do when an external assessor is unreachable — `not-run`, never `pass`
- [ ] B2.15b Note the independent convergence: #2299 uses **UNCERTAIN** as a state distinct from pass and fail. That is `absent ≠ not-run ≠ unknown ≠ zero` arriving from someone else, and it is evidence the four-state rule generalises. Cite it in [B2.10](#b2--aegs-01-normative-prose-)
- [ ] B2.16 `spec/11-conformance.md` — levels, how they are claimed, what evidence a claim needs
- [ ] B2.17 `spec/12-security-considerations.md` — the threat catalogue, including the three findings currently open
- [x] B2.18 Every normative clause cross-referenced. 9 clauses, 33 vectors, no orphans in either direction
- [x] B2.19 [`tools/lint_normative.py`](tools/lint_normative.py), a **real** CI gate rather than `continue-on-error`. It caught two things on its first run, and neither was fixed by exempting anything — see Findings

**Exit:** a specification someone outside this project could implement from, with every MUST tested.

---

## B3 — Rail bindings: making it protocol-neutral ⬜

The vision's core requirement — *"applicable for any Autonomous Economic Governance
Layer or protocol in the future"*. This is where that becomes structural rather than
aspirational.

Grounded in real upstream research — read [`../UPSTREAM-x402.md`](../UPSTREAM-x402.md)
before starting this section. Findings F1, F7 and F8 there change what this binding says.

- [ ] B3.1 `bindings/00-binding-model.md` — what a binding must supply: unit of account, atomic precision, settlement finality semantics, counterparty identity shape, reversibility, and what "vendor" means on that rail
- [ ] B3.2 Separate the **rail-independent** control set from the **rail-dependent** fields. Anything rail-dependent that leaked into the core schemas gets pulled out now, while there is exactly one binding to break
- [ ] B3.3 `bindings/x402-0.1.md` — the first binding, on branch `binding/x402` ([U4](../UPSTREAM-x402.md))
- [ ] B3.4 Include stablecoin specifics: 6-decimal atomic units, chain identity, testnet vs mainnet declaration, settlement confirmation as an evidence event
- [ ] B3.5 Name the **buyer-side / seller-side** split explicitly. x402 has a seller-side veto (`onBeforeSettle`, which can abort with `{abort: true, reason}`) and no standardized buyer-side pre-payment hook. AEGS specifies the buyer side. This is the binding's central claim (F1)
- [ ] B3.6 Compose with x402's SDK spend controls rather than replacing them — `maxAmountPerPayment` over `allowedAssets` becomes **one envelope among several**, with the others being cumulative, windowed, per-vendor and per-resource (F3)
- [ ] B3.7 Specify the AEGS EvidenceRecord ↔ x402 `offer`/`receipt` composition. Their receipts are independently signed (EIP-712 or JWS) and **not** chained; ours is an append-only chain. A signature proves *this happened*; a chain proves *nothing was removed*. Reference their digest, do not duplicate their artifact (F7)
- [ ] B3.8 **Bind to behaviour and digests, not wire shape.** `extension-offer-and-receipt` v0.5 states its behavioural requirements are stable but field placement is not, pending x402's canonical extension architecture. A binding pinned to a moving wire shape breaks on their next merge (F7)
- [ ] B3.9 Reconcile the money representation: PR #2853 upstream uses **decimal strings with a regex** for byte-level digest consistency; AEGS uses **integer atomic units**. Both avoid floats by different routes. Specify the conversion and its rounding, or two conformant implementations will disagree on a hash (F8)
- [ ] B3.10 Map each AEGS control onto a real x402 extension point: `onBeforeSettle`, the SDK client payment path, `authRequirements[]`/`acceptIndexes` from `extension-auth-hints`, and `payment_identifier`
- [ ] B3.11 `bindings/ap2-draft.md` — sketch only, and **informed by upstream [#2452](https://github.com/x402-foundation/x402/issues/2452)** (composition with AP2 mandate verification), which is upstream doing this homework already. Names the questions AP2 raises that x402 does not: mandate shape, delegation, who holds the authorization
- [ ] B3.12 `bindings/mcp-draft.md` — sketch only. Tool-call-as-economic-action; the interesting difference is that the counterparty may be a tool rather than a vendor. Note upstream already has an MCP transport in flight (PR #3106)
- [ ] B3.13 `bindings/card-draft.md` — sketch only. Names what cards break: reversibility, chargebacks, a settlement that arrives days later, and a counterparty identity that is a merchant category code
- [ ] B3.14 Test: the core schemas validate a decision from **each** sketched binding, or the schema is too x402-shaped and is fixed
- [ ] B3.15 Do **not** implement the three sketches. The spec gets the shape; implementations wait for demand

**Exit:** the control set is provably not x402-specific, with one real binding and three sketches.

---

## B4 — Language-neutral test vectors 🔨

Useful immediately, and the bridge to any second implementation. Consumed by
[`../aegoll/PLAN.md`](../aegoll/PLAN.md) A8.

**Align to upstream's format, do not invent a second one.** [PR #2776](https://github.com/x402-foundation/x402/pull/2776)
upstream ships 52 core conformance vectors with a `schema.json` and a dependency-free
runner, already covering *spending limits* and *authorization bypass*. Three reviewer
concerns are open there, and our design answers all three — that is the alignment
opportunity, detailed at [F5](../UPSTREAM-x402.md).

- [x] B4.1 [`vectors/README.md`](vectors/README.md) and [`vectors/schema.json`](vectors/schema.json) — a vector without a clause fails validation. Amounts are **always strings**, because a vector writing `2.5` as a JSON number would have lost precision before any implementation read it, and could not test the very thing ARITH-9 requires
- [x] B4.1a Every vector names its spec version and clause, required by the schema. This is upstream reviewer concern (3) answered by construction rather than by intention
- [ ] B4.1b Answer concern (1): sequence and concurrency vectors need **executable semantics**, not just declared fields. Upstream's runner ignores `variants`, `n_requests` and `concurrent_requests` — which is exactly why structuring and velocity evasion cannot be expressed there. Our runner must execute them or the two open red-team findings have no test
- [ ] B4.2 Expected output covers all four: verdict, **attributed control**, resulting envelope state, and the record hash
- [x] B4.3 [`vectors/arithmetic/`](vectors/arithmetic/) — **33 vectors, all 9 clauses.** Mutation-checked rather than assumed to bite: a half-even implementation fails 1, the prototype's original no-sign-check fails 3
- [x] B4.4 [`vectors/envelopes/`](vectors/envelopes/) — **27 vectors, all 9 clauses.** Headroom including over-committed, the exact-equality boundary, per-call versus cumulative, absent versus zero, count envelopes, and channel separation. Earned-authority multipliers deferred: they are a *policy* mechanism the spec does not require, so vectoring them would test this implementation rather than the standard
- [ ] B4.5 `vectors/verdicts/` — narrowing, attribution, evaluation order, first-match-terminal rules
- [ ] B4.6 `vectors/evidence/` — record projection, canonical serialisation, chain hash continuation
- [ ] B4.7 Every one of the 7 CONF cases represented as vectors
- [ ] B4.8 Every one of the 18 red-team attacks represented as vectors
- [ ] B4.9 **The two known vulnerabilities are vectors on day one** — the negative amount and the 30-digit overflow — so no future implementation ships with the bugs the reference one already had. That alone justifies the vectors before anything else
- [x] B4.10 [`tools/check_vectors.py`](tools/check_vectors.py) reports coverage per clause and fails a vector citing a clause that does not exist — coverage checked in **both** directions

**Exit:** four families populated, the reference implementation at 100%, coverage reported.

---

## B5 — AEGS-CONF, the conformance suite ⬜

Ships as its own installable package. **A conformance suite that arrives as part of
the thing it tests is not a conformance suite.**

- [x] B5.1 Conformance suite ported faithfully — `08802e9` — then repointed at the ported package — `4641e15`
- [ ] B5.2 Package as `aegs-conformance` on PyPI — installable by someone testing a layer that is not `aegoll`
- [x] B5.3 The runner still imports no implementation, and the test that asserts it now bans both `aegoll` and `aegl`
- [ ] B5.4 `conformance/adapters/README.md` — the adapter interface, written for a third party with no access to this codebase
- [x] B5.5 Stub adapter kept and still scores **2/7** — 4 fail, 1 not-implemented. The suite bites
- [ ] B5.6 Add cases past CONF-007 as the spec grows: profile enforcement, binding neutrality, four-state handling, delegation clamp, evidence-chain continuation
- [ ] B5.7 Keep the **right-reason** rule: a verdict that is correct but attributed to the wrong control is recorded separately. It was right by accident, and the same case shaped differently would fail
- [ ] B5.8 Machine-readable report with claimable levels, and a human-readable one that names *why* each case scored as it did
- [ ] B5.9 `aegs-conformance --against <adapter>` runs standalone, exit code by level achieved
- [ ] B5.10 **Score a second implementation.** The single largest open question in the project: the suite has never scored a system nobody here wrote. Options in preference order — a third party takes it up; a deliberately independent reimplementation written from the spec and vectors only; failing both, say so plainly and keep the question open

**Exit:** `pip install aegs-conformance` scores anything that emits Decision Records, and has scored at least one implementation this project did not write.

---

## B6 — AML/CFT: the reach the vision asks for ⬜

*"...can be able to scenarios like basic transactions to Anti Money Laundering stuff."*
This is a real extension and needs to be built as one, because **AML/CFT effectiveness
is currently the project's largest unproven claim**: schema only, no engine, no
labelled data.

- [ ] B6.1 `spec/ext/aml-0.1.md` as a **profile extension**, not core. Core stays useful to a user who has no AML obligation at all
- [ ] B6.2 Specify what the AMLAssessment control MUST record, and — equally — what it MUST NOT imply. No row anywhere says AEGS complies with anything
- [ ] B6.3 Specify sanctions screening properly. Today it is **a boolean on a vendor object: no list, no matching**. The spec must say what a list is, what matching means, and what a null result means
- [ ] B6.4 **FATF Travel Rule — the one real gap the crosswalk found.** AEGS carries no originator or beneficiary data, which matters for any stablecoin deployment between regulated parties. Either specify the fields or formally declare it out of scope in writing
- [ ] B6.4a Independently confirmed upstream: [PR #2853](https://github.com/x402-foundation/x402/pull/2853) adds a compliance-fields extension covering **EU VAT (Arts. 220a/226b) and EN 16931 invoicing** and explicitly **does not reference FATF, travel rules, or AML.** Nobody upstream is covering it either — so this is a real open gap in the ecosystem, not just in AEGS. Say so, with the citation
- [ ] B6.4b Borrow their *verifier disqualification* discipline — constraints stated as MUST NOTs on the evaluator rather than as new required fields (independence, completeness/existence, economic-phase separation, scope-within-commitments). It is a better shape than adding fields, and sequential numbering giving ordering evidence only is the same honest limit as our chain-truncation caveat
- [ ] B6.5 Structuring and layering as *specified controls*, matching the behavioural engine in [A11](../aegoll/PLAN.md). The reference implementation moved 40 × $0.001 with nothing refused
- [ ] B6.6 `IncidentRecord` given required semantics — what raises one, who sees it, what closes it
- [ ] B6.7 `ComplianceAssessment` tied to the active profile, so "controls exercised" is a checkable claim
- [ ] B6.8 State the honest limit in the spec itself: **effectiveness cannot be demonstrated without labelled financial-crime data this project does not have.** The interface is buildable; the effectiveness claim is not
- [ ] B6.9 Vectors for every AML control that has one, and an explicit note where a control cannot be vectored

**Exit:** an AML extension that is specifiable, testable where possible, and honest where not.

---

## B7 — Crosswalk verification ⬜

`AEGS-CROSSWALK-001.md` exists and maps AEGS against NIST AI RMF, ISO/IEC 42001, ISO
37301, GDPR, EU AI Act, FATF and MiCA. Parts of it are unsourced **and labelled so**.
Publishing it unverified is the fastest way to lose the credibility everything else is
built to earn.

- [ ] B7.1 Keep the three-category discipline — Direct / Partial / Outside scope — and the per-framework provenance markers
- [ ] B7.2 NIST AI RMF and EU AI Act rows: sourced already. Re-check citations against current text
- [ ] B7.3 ISO/IEC 42001: currently from **a secondary summary of a paywalled standard**. Obtain the standard or downgrade the rows to clearly marked secondary
- [ ] B7.4 ISO 37301: **unsourced.** Obtain or remove
- [ ] B7.5 FATF Recommendations: **unsourced.** FATF text is free — no excuse for this row staying unsourced
- [ ] B7.6 MiCA: **not attempted.** Attempt it, or formally abandon it in writing
- [ ] B7.7 GDPR and EU AI Act readings reviewed by a **qualified reviewer**. Not optional before external use
- [ ] B7.8 Keep the disclaimer prominent. **It will be quoted as compliance the first time it is public** — the response is labelled rows, not a tidier document
- [ ] B7.9 Do not quietly tidy unsourced rows into sourced-looking ones. A crosswalk with the uncertainty removed is marketing

**Exit:** every row sourced, downgraded, or removed; legal readings reviewed; disclaimer intact.

---

## B8 — Upstream: x402-foundation ⬜

**Planned in full at [`../UPSTREAM-x402.md`](../UPSTREAM-x402.md)** — findings F1–F8 and
tasks U1–U5. That document is research plus engagement plan; only the spec-side artifacts
are tracked here.

- [ ] B8.1 `spec/x402-relationship.md` — what x402 answers (*how* an agent pays, and now *how much per payment*) and what it deliberately leaves open (*whether it should pay at all*), quoting `extension-auth-hints`' own statement that spend limits, budgets and policy enforcement "remain separate concerns"
- [ ] B8.2 The control-set table from [F6](../UPSTREAM-x402.md) becomes a spec appendix: thirteen-plus upstream proposals, each implementing one control of a set nobody upstream has named. **That framing is the contribution**
- [ ] B8.3 `upstream/` folder in this repo (branch `upstream/x402`) holds the inventory, the gap memo, and the contribution log
- [ ] B8.4 Artifact homes decided: the binding is a **branch in this repo**, not a new repo; anything proposed upstream lives on a **fork** of `x402-foundation/x402`. Reasoning at [§4](../UPSTREAM-x402.md)
- [ ] B8.5 Gate: nothing opens upstream until [B2](#b2--aegs-01-normative-prose-) prose and [B4](#b4--language-neutral-test-vectors-) vectors exist ([U4.9](../UPSTREAM-x402.md))

**Exit:** upstream engagement grounded in their issue history, with the spec-side artifacts written here first.

---

## B9 — Publish AEGS 0.1 ⬜

Only once there are vectors, a standalone suite, and a suite that has scored something
other than itself.

- [ ] B9.1 Tag `aegs-0.1.0`, with a release artifact containing spec, schemas, bindings, vectors and crosswalk
- [ ] B9.2 Compatibility policy — what may change in a patch, a minor, a major
- [ ] B9.3 Public conformance declaration process: anyone may run the suite and publish the result, **including a failing one**
- [ ] B9.4 Declaration registry as a plain repo directory with PRs. No hosted service, no operation, no uptime obligation
- [ ] B9.5 Errata process — a standard's errata list is a sign of health, not weakness

**Exit:** a versioned standard anyone can implement, score against, and publicly declare.

---

## B10 — White paper and research paper ⬜

Two documents with different jobs. Conflating them produces one that does neither.

- [ ] B10.1 **White paper** — for practitioners and prospective adopters: the problem, the control set, the profile mechanism, the evidence model, what conformance means. Argument-led
- [ ] B10.2 **Research paper** — measured claims only, from the sealed experiments. Every number traced to an EXP record
- [ ] B10.3 Reproduce every quoted figure from the sealed records at writing time. A figure quoted anywhere else is a copy, and **copies drift**
- [ ] B10.4 Include the limitations section in full. It is the most valuable part of both documents and the reason anyone will trust the rest
- [ ] B10.5 Do not claim AML/CFT effectiveness, regulatory compliance, standards novelty, statistical significance, sanctions screening, risk-score accuracy, concurrency behaviour, or production settlement — see the not-established list in [`../CONTEXT.md`](../CONTEXT.md)
- [ ] B10.6 Name the reviewer problem plainly: the evaluation labels, threat catalogue and conformance cases were **all written by the author of the system under test**
- [ ] B10.7 Venue chosen deliberately — workshop with real review beats an arXiv-only drop for a standards claim
- [ ] B10.8 Do not submit before [B5.10](#b5--aegs-conf-the-conformance-suite-) resolves one way or the other. "Independently implementable" is the paper's central claim

**Exit:** two documents whose every claim traces to a sealed record or a spec clause.

---

## Findings

### F-B2 · The linter earned its place on its first run — 2026-08-17

`tools/lint_normative.py` fails a `MUST` with no cross-referenced test. It flagged two
things immediately, and **neither was fixed by exempting anything** — which is the whole
test of whether a lint rule is any good.

**1. Three `INTRO` clauses carry a `MUST` that constrains the document, not
implementations.** The RFC 2119 conventions, and the rule that every `MUST` needs a test.
There is nothing for a vector to run.

The fix is a marker in the **specification text itself** — *"Constrains this document, not
implementations."* — so a reader sees the distinction too, and the marker cannot drift from
the linter's view of it. A list inside the linter would have been invisible to anyone
reading the spec, and would have quietly grown. One of the three, `INTRO-5`, turned out not
to be meta at all: its `MUST` was inside a *definition* of what a profile is, so it was
reworded rather than marked.

**2. My own closing sentence used `MUST` in caps while talking about the keyword.** The
linter was right. The fix is that it now strips inline code, because a backticked keyword is
being *named* rather than imposed — contorting the prose to dodge a regex would be the
linter dictating the writing.

### F-B6 · The spec found a bug in the implementation, twice — 2026-08-17

Both slices so far have found a real defect in `aegoll` while the clause was being written,
rather than the other way round. That is the argument for writing prose and vectors
together, and it is worth stating because the reverse was the expectation.

**Arithmetic** turned up nothing new — the two vulnerabilities were already known and fixed,
and the clauses documented them. But **envelopes** found [ENV-6](spec/03-envelopes.md):
`binding` and `tightest` are two different questions and the reference report conflated
them, so an approved decision displayed no envelope at all under a heading meaning *closest
to biting*. The column went blank precisely when the agent was healthy and someone was
checking headroom.

Nothing in the implementation's own 449 tests could have caught that, because the code did
exactly what it said — the defect was in what the two concepts *meant*, and only writing
them down as separate requirements made the conflation visible.

### F-B4 · Two rounding vectors where one would look sufficient — 2026-08-17

`0.0000015` rounds to `2` under **both** half-up and half-even. A suite containing only
that vector would pass under either mode and prove nothing about which one an
implementation uses — coverage that reads as thorough and is not. Only `0.0000005`
discriminates: half-up gives `1`, half-even gives `0`.

Both are kept, and the note on each says why. The general lesson is worth carrying into the
remaining families: **a vector that passes under the behaviour it was written to forbid is
not a test.** The cheap way to check is to mutate the implementation and count how many
vectors go red — for arithmetic, a half-even implementation fails 1 and the prototype's
original no-sign-check fails 3.
