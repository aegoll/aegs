"""A deliberately incomplete implementation, so the suite can be shown to fail.

A conformance suite that only ever runs against the implementation it was written
alongside proves nothing: it might pass everything because the tests are right, or
because they are toothless, and there is no way to tell from a green report.

This adapter is the control. It is what a naive implementation looks like — an
amount threshold and nothing else — and the suite catches it:

* **FAIL ×4** — it approves a sanctioned counterparty, an out-of-intent purchase, an
  expired authorisation and an unknown-vendor policy case, because it has no concept
  of any of them.
* **NOT_IMPLEMENTED** — it declines the behavioural-risk case, which is the honest
  answer and better than a fabricated verdict.
* **PASS ×2** — the two amount cases, which it genuinely does implement. A control
  that scores zero would be a weaker control: it has to pass what it really does.

`WRONG_REASON` is exercised separately in `tests/test_conformance.py`, because no
natural case produces it here — the stub's threshold and the cases' amounts do not
happen to line up that way. It is demonstrated with a synthetic record rather than
by bending a case to manufacture it.

If this adapter ever scores 7/7, the suite has stopped discriminating and the bug is
in the suite.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from runner import Case  # noqa: E402

#: The naive implementation's entire governance model.
THRESHOLD = Decimal("1.00")


class StubAdapter:
    """Refuses anything over a fixed amount. Knows nothing else."""

    name = "naive-threshold-stub"

    def run_case(self, case: Case) -> dict[str, Any] | None:
        action = case.action

        # It has no notion of behavioural risk, so it declines rather than guessing.
        if case.control == "risk":
            return None

        amount = Decimal(action["amount"])
        over = amount > THRESHOLD
        decision = "REJECT" if over else "APPROVE"

        return {
            "aegsVersion": "0.1",
            "decisionId": f"stub-{case.id}",
            "agentId": "stub-agent",
            "intentId": None,
            "action": {
                "channel": action.get("channel", "external"),
                "resource": action["resource"],
                "amount": f"{amount:.6f}",
                "asset": action.get("asset", "USDC"),
                "purpose": None,
                "counterparty": {
                    "id": (action.get("counterparty") or {}).get("id", "unknown"),
                    "name": (action.get("counterparty") or {}).get("name"),
                    # It does not screen, and says so rather than reporting a clean
                    # screening it never performed.
                    "sanctioned": None,
                },
            },
            "decision": decision,
            "authorization": {
                # Honest attribution: an amount threshold *is* a treasury control,
                # and claiming otherwise would be the implementation lying about
                # itself rather than the suite failing to notice.
                "decidingEngine": "treasury",
                "matchedRule": "amount-threshold",
                "deterministicVerdict": decision,
                "reasons": [
                    {
                        "source": "treasury",
                        "code": "over_threshold" if over else "under_threshold",
                        "detail": f"amount {amount} vs threshold {THRESHOLD}",
                        "verdict": decision,
                    }
                ],
            },
            "budgetState": None,
            # No trust, risk or ROI controls exist here. Absent, not zero.
            "assessments": {},
            "intelligence": None,
            "policy": {"id": "naive", "version": "threshold-1.00"},
            "humanReview": None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "latencyUs": None,
            "evidence": {
                "evidenceHash": f"stub-no-chain-{case.id}".ljust(16, "0"),
                "chainSequence": None,
                "previousHash": None,
                "decisionHash": None,
            },
            "settlement": None,
            "actor": {"known": False, "status": None, "purpose": None, "delegatedFrom": None},
            "implementation": {"name": self.name, "version": "0.0", "rail": None},
        }
