"""`tesoro` as an AEGS-CONF implementation under test.

Everything implementation-specific lives here. The runner imports none of it — the
whole point of the boundary is that a second implementation writes a file like this
one and nothing else changes.

**The implementation must be installed**, not sitting in a sibling directory. The
prototype's version of this file did

    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "aegl"))

which quietly required the suite and the implementation to live in one monorepo. That
is the opposite of what a conformance suite is for: it must be able to score something
whose source you have never seen. `pip install tesoro`, or point `PYTHONPATH` at it,
and this adapter finds it the same way any other consumer would.

Each case gets a **fresh ephemeral store**, so cases cannot contaminate each other
through accumulated history. A suite whose results depend on execution order is
measuring the order.
"""

from __future__ import annotations

import importlib.util
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

# Intra-suite import only — `runner` is a sibling module of this package, not another
# project. Goes away when the suite is packaged as `aegs-conformance` (PLAN.md B5.2).
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from runner import Case  # noqa: E402

BASE = datetime(2026, 8, 15, 12, 0, tzinfo=timezone.utc)

#: Raised as a plain message rather than an ImportError several frames deep, because
#: "the implementation under test is not installed" is a setup problem and should read
#: like one.
NOT_INSTALLED = (
    "tesoro is not importable. AEGS-CONF scores an *installed* implementation:\n"
    "  pip install tesoro\n"
    "or set PYTHONPATH to its src/ directory. The suite itself needs none of it."
)


def implementation_available() -> bool:
    return importlib.util.find_spec("tesoro") is not None


class TesoroAdapter:
    """Drives `tesoro` through one conformance case and returns a Decision Record."""

    name = "tesoro"

    def __init__(self, agent_id: str = "conformance-agent") -> None:
        self.agent_id = agent_id

    def run_case(self, case: Case) -> dict[str, Any] | None:
        import tempfile

        if not implementation_available():
            raise RuntimeError(NOT_INSTALLED)

        from tesoro import record as record_mod
        from tesoro.clock import FixedClock
        from tesoro.config import available_bundles, load_bundle
        from tesoro.domain import Channel, Purpose, Vendor, Verdict, usd_to_atomic
        from tesoro.runtime import Tesoro, Paths

        bundle = load_bundle()
        wanted = case.setup.get("policy")
        if wanted:
            for path in available_bundles():
                if path.stem == wanted:
                    bundle = load_bundle(path)
                    break

        tesoro = Tesoro(
            bundle=bundle,
            paths=Paths.ephemeral(tempfile.mkdtemp()),
            clock=FixedClock(BASE),
            agent_id=self.agent_id,
        )
        try:
            action = case.action
            counterparty = action.get("counterparty") or {}
            vendor = Vendor(
                id=counterparty.get("id", "unknown"),
                name=counterparty.get("name", ""),
                sanctioned=bool(counterparty.get("sanctioned", False)),
            )

            # --- setup: history the engines will read ----------------------
            for i, row in enumerate(case.setup.get("history") or []):
                tesoro.store.record(
                    tx_id=f"{case.id}-hist-{i}",
                    at=BASE - timedelta(seconds=row.get("secondsAgo", 0)),
                    agent_id=self.agent_id,
                    vendor_id=vendor.id,
                    resource=row.get("resource", action["resource"]),
                    amount_atomic=usd_to_atomic(row.get("amount", "0")),
                    verdict=Verdict.APPROVE,
                    settled=bool(row.get("settled", True)),
                    success=bool(row.get("settled", True)),
                    channel=action.get("channel", "external"),
                )

            # --- setup: a declared intent ----------------------------------
            spec = case.setup.get("intent")
            if spec:
                expired_hours = spec.get("expiredHoursAgo")
                tesoro.intents.declare(
                    agent_id=self.agent_id,
                    purpose=spec["purpose"],
                    maximum_usd=spec["maximumAmount"],
                    asset=spec.get("asset", "USDC"),
                    allowed_resources=spec.get("allowedResources", ()),
                    expires_at=(
                        BASE - timedelta(hours=expired_hours) if expired_hours else None
                    ),
                    # Declared before it expired, which is the realistic shape.
                    now=BASE - timedelta(hours=(expired_hours or 0) + 1),
                )

            # --- setup: a registered identity ------------------------------
            ident = case.setup.get("identity")
            if ident:
                tesoro.identities.register(
                    agent_id=self.agent_id,
                    purpose=ident.get("purpose", "conformance"),
                    per_action_usd=ident.get("perAction"),
                    now=BASE,
                )
                if ident.get("status") and ident["status"] != "active":
                    tesoro.identities.set_status(self.agent_id, ident["status"])

            # --- the action -------------------------------------------------
            channel = (
                Channel.INTERNAL if action.get("channel") == "internal" else Channel.EXTERNAL
            )
            request = tesoro.build_request(
                resource=action["resource"],
                amount_usd=action["amount"],
                vendor=vendor,
                purpose=(
                    Purpose.INFERENCE if channel is Channel.INTERNAL else Purpose.DATA_PURCHASE
                ),
                channel=channel,
            )
            tesoro.authorize(request)

            entries = [e for e in tesoro.audit.entries() if e.payload.get("decision")]
            if not entries:
                return None
            return record_mod.from_audit_entry(entries[-1])
        finally:
            tesoro.close()
