"""Tests for the conformance suite itself.

A suite that only ever runs against the implementation it was written alongside
proves nothing — a green report might mean the tests are right, or that they are
toothless, and nothing distinguishes the two. So these check that the suite
*discriminates*: that it fails a bad implementation, that it fails it for the right
reasons, and that a right answer for a wrong reason is not counted as a pass.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

CONFORMANCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CONFORMANCE))

from adapters.aegoll_adapter import AegollAdapter  # noqa: E402
from adapters.stub_adapter import StubAdapter  # noqa: E402
from runner import Case, Outcome, report, run, score  # noqa: E402


@pytest.fixture(scope="module")
def cases():
    return Case.load_all()


# --- the cases are well formed --------------------------------------------


def test_all_seven_cases_exist(cases):
    assert [c.id for c in cases] == [f"CONF-00{i}" for i in range(1, 8)]


def test_every_case_states_why_it_exists(cases):
    """A case without a rationale cannot be argued with, and a conformance suite
    nobody can argue with is a suite nobody should trust."""
    for case in cases:
        assert len(case.rationale) > 80, f"{case.id} has no real rationale"


def test_every_case_expects_a_verdict(cases):
    for case in cases:
        assert "decision" in case.expect or "decisionIn" in case.expect, case.id


def test_every_refusal_case_constrains_attribution(cases):
    """Otherwise a case can be passed by refusing for an unrelated reason."""
    for case in cases:
        expected = case.expect.get("decision") or (case.expect.get("decisionIn") or [None])[0]
        if expected == "APPROVE":
            continue  # an approval has no refusing control to attribute
        assert (
            "decidingEngine" in case.expect or "decidingEngineIn" in case.expect
        ), f"{case.id} accepts any attribution, so any refusal would pass it"


def test_the_happy_path_case_exists(cases):
    """Without it, an implementation that refuses everything scores perfectly."""
    approvals = [c for c in cases if c.expect.get("decision") == "APPROVE"]
    assert approvals, "no case checks that legitimate traffic is allowed through"


# --- the reference implementation conforms --------------------------------


def test_aegoll_passes_every_case(cases):
    results = run(AegollAdapter(), cases)
    failures = [r for r in results if r.outcome is not Outcome.PASS]
    assert not failures, "AEGL no longer conforms:\n  " + "\n  ".join(
        f"{r.case.id} {r.outcome.value}: {r.detail}" for r in failures
    )


def test_aegoll_can_claim_both_levels(cases):
    data = report("aegoll", run(AegollAdapter(), cases))
    assert data["levels"]["AEGS-1"]["claimable"] is True
    assert data["levels"]["AEGS-2"]["claimable"] is True


def test_every_aegoll_record_satisfies_the_schema(cases):
    """The suite validates records before scoring them, so a conforming verdict
    carried by a malformed record is not a pass."""
    results = run(AegollAdapter(), cases)
    assert not [r for r in results if r.outcome is Outcome.INVALID_RECORD]


# --- the suite discriminates ----------------------------------------------


def test_the_stub_does_not_pass(cases):
    """The load-bearing test. If a naive threshold scores 7/7, the suite is broken."""
    data = report("stub", run(StubAdapter(), cases))
    assert data["passed"] < data["cases"]
    assert data["levels"]["AEGS-1"]["claimable"] is False
    assert data["levels"]["AEGS-2"]["claimable"] is False


def test_the_stub_fails_the_controls_it_lacks(cases):
    """Named individually, so a change that silently starts passing them is caught."""
    results = {r.case.id: r for r in run(StubAdapter(), cases)}

    assert results["CONF-003"].outcome is Outcome.FAIL   # no intent model
    assert results["CONF-004"].outcome is Outcome.FAIL   # no sanctions screening
    assert results["CONF-007"].outcome is Outcome.FAIL   # no notion of expiry
    assert results["CONF-002"].outcome is Outcome.FAIL   # no policy engine


def test_the_stub_passes_what_it_genuinely_implements(cases):
    """A control that scores zero is a weaker control. The stub really does enforce
    an amount ceiling, and the suite should say so."""
    results = {r.case.id: r for r in run(StubAdapter(), cases)}
    assert results["CONF-001"].outcome is Outcome.PASS
    assert results["CONF-006"].outcome is Outcome.PASS


def test_declining_a_case_is_distinct_from_failing_it(cases):
    """An honest 'I do not implement this' must not look like a wrong answer."""
    results = {r.case.id: r for r in run(StubAdapter(), cases)}
    assert results["CONF-005"].outcome is Outcome.NOT_IMPLEMENTED


# --- right answer, wrong reason -------------------------------------------


def test_a_right_verdict_for_the_wrong_reason_is_not_a_pass(cases):
    """The rule the whole suite turns on.

    An implementation that refuses the sanctions case because the *amount* tripped a
    budget has not screened anything. It was right by accident, and the same case
    with a smaller amount would sail through. Counting it as a pass would let an
    implementation certify a control it does not have.
    """
    sanctions_case = next(c for c in cases if c.id == "CONF-004")
    record = {
        "aegsVersion": "0.1", "decisionId": "x", "agentId": "a", "intentId": None,
        "action": {"channel": "external", "resource": "/market/snapshot",
                   "amount": "0.001000", "asset": "USDC",
                   "counterparty": {"id": "ofac-listed-1"}},
        "decision": "REJECT",
        "authorization": {"decidingEngine": "treasury", "matchedRule": "amount",
                          "deterministicVerdict": "REJECT", "reasons": []},
        "policy": {"id": "p", "version": "v"},
        "timestamp": "2026-08-15T12:00:00+00:00",
        "evidence": {"evidenceHash": "0123456789abcdef"},
    }
    result = score(sanctions_case, record)

    assert result.outcome is Outcome.WRONG_REASON
    assert result.outcome is not Outcome.PASS
    assert "sanctions" in result.detail


def test_a_wrong_reason_is_reported_separately_from_a_failure(cases):
    """It is neither a pass nor a plain failure: the implementation did refuse."""
    data = report("synthetic", [
        score(next(c for c in cases if c.id == "CONF-004"), {
            "aegsVersion": "0.1", "decisionId": "x", "agentId": "a",
            "action": {"channel": "external", "resource": "/r", "amount": "0.001000",
                       "asset": "USDC"},
            "decision": "REJECT",
            "authorization": {"decidingEngine": "risk", "reasons": []},
            "policy": {"id": "p", "version": "v"},
            "timestamp": "2026-08-15T12:00:00+00:00",
            "evidence": {"evidenceHash": "0123456789abcdef"},
        })
    ])
    assert data["counts"]["WRONG_REASON"] == 1
    assert data["counts"]["FAIL"] == 0
    assert data["passed"] == 0


# --- schema enforcement ----------------------------------------------------


def test_a_malformed_record_is_not_scored_as_a_pass(cases):
    """A conforming verdict inside an invalid record proves nothing."""
    result = score(cases[0], {"decision": "REJECT"})
    assert result.outcome is Outcome.INVALID_RECORD


def test_an_adapter_that_raises_fails_only_its_own_case(cases):
    class Exploding:
        name = "exploding"

        def run_case(self, case):
            if case.id == "CONF-001":
                raise RuntimeError("boom")
            return None

    results = run(Exploding(), cases)
    assert results[0].outcome is Outcome.FAIL
    assert "boom" in results[0].detail
    assert all(r.outcome is Outcome.NOT_IMPLEMENTED for r in results[1:])


# --- the boundary ----------------------------------------------------------


def test_the_runner_imports_no_implementation():
    """If scoring needs anything from `aegoll`, the suite has stopped testing a
    standard and started testing us."""
    import ast

    source = CONFORMANCE / "runner.py"
    banned = {"aegoll", "aegl", "agents", "x402_core"}
    offenders = []
    for node in ast.walk(ast.parse(source.read_text(encoding="utf-8"))):
        names = []
        if isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            names = [node.module]
        offenders += [
            f"runner.py:{node.lineno} imports {n}" for n in names
            if n.split(".")[0] in banned
        ]
    assert not offenders, "\n  ".join(offenders)


def test_adding_a_case_requires_no_python(cases):
    """Cases are data. If a new one needed code, the suite would be ours, not the
    standard's."""
    import json

    raw = json.loads((CONFORMANCE / "cases" / "CONF-001.json").read_text(encoding="utf-8"))
    assert set(raw) >= {"id", "title", "level", "control", "setup", "action", "expect"}
