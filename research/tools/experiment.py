"""Experiment records: stamped, checksummed, and never silently overwritten.

An experiment record exists so a number in a paper can be traced back to the exact
code, policy and models that produced it. That means two things this module
enforces mechanically:

1. **Every record stamps its world.** Commit hash, dirty-tree flag, policy bundle
   hash, package versions, provider, model, run count, date. A result whose
   provenance is "we ran it in August" is not evidence.
2. **A recorded result is immutable.** `results.json` and `manifest.json` are
   checksummed into `SHA256SUMS`, and `verify()` fails if either changes. Re-running
   an experiment produces a *new* ID; it never edits an old one.

The second rule is the one that matters when conclusions change. This project has
already overturned one of its own conclusions — the advisor evaluation contradicted
what Phase 2 had concluded. That is only visible as a finding if the superseded
record still exists to be contradicted.

Usage:

    python research/tools/experiment.py new EXP-004 "Intent mismatch rates"
    python research/tools/experiment.py seal EXP-004
    python research/tools/experiment.py verify
    python research/tools/experiment.py list
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RESEARCH_DIR = Path(__file__).resolve().parents[1]
EXPERIMENTS = RESEARCH_DIR / "experiments"
REPO_ROOT = RESEARCH_DIR.parent

CHECKSUM_FILE = "SHA256SUMS"
SEALED_FILES = ("manifest.json", "results.json")


# --- environment stamping -------------------------------------------------


def _run(cmd: list[str]) -> str:
    try:
        return subprocess.run(
            cmd, cwd=REPO_ROOT, capture_output=True, text=True, timeout=15
        ).stdout.strip()
    except Exception:  # noqa: BLE001 - provenance is best-effort, never fatal
        return ""


def git_state() -> dict[str, Any]:
    """The commit a result came from, and whether the tree was clean.

    `dirty: true` is recorded rather than refused. A dirty tree does not
    invalidate a measurement, but it does mean the commit hash alone will not
    reproduce it, and a reader is entitled to know that.
    """
    dirty = bool(_run(["git", "status", "--porcelain"]))
    return {
        "commit": _run(["git", "rev-parse", "HEAD"]),
        "branch": _run(["git", "rev-parse", "--abbrev-ref", "HEAD"]),
        "dirty": dirty,
    }


def policy_state() -> dict[str, Any]:
    """Policy bundle names and hashes, so a rule change is visible in the record.

    Reads the **installed** `aegoll`. The prototype's version put
    `REPO_ROOT / "aegl"` on `sys.path`, which is the single-repository layout and resolves to
    nothing here — and then caught the resulting `ImportError` and returned
    `{"error": "ModuleNotFoundError: ..."}`. So a record could be sealed with no policy hash at
    all, and the seal would make that permanent.

    That is the failure this whole module exists to prevent, one level up: a measurement whose
    provenance is a stack trace is not situated, it just looks like it is. So this **raises**.
    An experiment that cannot say which rules it ran against should not be recordable.
    """
    from aegoll.config import available_bundles, load_bundle  # noqa: PLC0415

    bundles = {
        b.name: {"hash": b.hash, "rules": len(b.rules)}
        for b in (load_bundle(p) for p in available_bundles())
    }
    if not bundles:
        raise RuntimeError(
            "no policy bundles found, so a record would carry no policy hash. A rule change "
            "would then be invisible in the results, which is what stamping exists to prevent."
        )
    return bundles


def package_versions(names: tuple[str, ...] = ()) -> dict[str, str]:
    from importlib.metadata import PackageNotFoundError, version  # noqa: PLC0415

    wanted = names or (
        "aegoll", "x402", "claude-agent-sdk", "langgraph", "langchain-core",
        "google-adk", "anthropic", "openai", "groq", "google-genai", "streamlit",
    )
    out: dict[str, str] = {}
    for name in wanted:
        try:
            out[name] = version(name)
        except PackageNotFoundError:
            continue
    return out


def stamp(**extra: Any) -> dict[str, Any]:
    """Everything needed to situate a result. Merged into a manifest."""
    return {
        "recordedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "git": git_state(),
        "policies": policy_state(),
        "packages": package_versions(),
        **extra,
    }


# --- the record -----------------------------------------------------------


@dataclass
class Experiment:
    """One measurement, its provenance and its interpretation."""

    id: str
    title: str
    directory: Path = field(init=False)

    def __post_init__(self) -> None:
        self.directory = EXPERIMENTS / self.id

    @property
    def manifest_path(self) -> Path:
        return self.directory / "manifest.json"

    @property
    def results_path(self) -> Path:
        return self.directory / "results.json"

    @property
    def checksum_path(self) -> Path:
        return self.directory / CHECKSUM_FILE

    @property
    def sealed(self) -> bool:
        return self.checksum_path.exists()

    def create(
        self,
        *,
        question: str = "",
        method: str = "",
        runs: int = 1,
        cost_usd: float = 0.0,
        seed: int | None = None,
        supersedes: str | None = None,
        extra: dict[str, Any] | None = None,
    ) -> Path:
        if self.directory.exists():
            raise FileExistsError(
                f"{self.id} already exists at {self.directory}. Experiment IDs are "
                "never reused -- allocate the next one instead."
            )
        self.directory.mkdir(parents=True)

        manifest = {
            "id": self.id,
            "title": self.title,
            "question": question,
            "runs": runs,
            "seed": seed,
            "costUsd": round(cost_usd, 6),
            # A later experiment may contradict an earlier one. Recording that
            # relationship is the point; deleting the earlier one is not.
            "supersedes": supersedes,
            **stamp(**(extra or {})),
        }
        self.manifest_path.write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
        )
        (self.directory / "method.md").write_text(
            f"# {self.id} — {self.title}\n\n"
            f"## Question\n\n{question or '_TODO_'}\n\n"
            f"## Method\n\n{method or '_TODO: what was run, against what, how many times._'}\n\n"
            "## Why this method\n\n_TODO: and what it cannot show._\n",
            encoding="utf-8",
        )
        (self.directory / "report.md").write_text(
            f"# {self.id} — findings\n\n"
            "## Result\n\n_TODO_\n\n"
            "## Interpretation\n\n_TODO_\n\n"
            "## Limitations\n\n"
            "_TODO: sample size, single-run vs averaged, what varied that was not "
            "controlled, what this cannot support._\n",
            encoding="utf-8",
        )
        if not self.results_path.exists():
            self.results_path.write_text("{}\n", encoding="utf-8")
        return self.directory

    # --- immutability ------------------------------------------------------
    def _digest(self, path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def seal(self) -> dict[str, str]:
        """Freeze the manifest and results. Prose stays editable on purpose.

        `method.md` and `report.md` are interpretation and may be improved as
        understanding does. `manifest.json` and `results.json` are the measurement
        itself, and revising those after the fact is how a record stops being
        evidence.
        """
        if self.sealed:
            raise FileExistsError(
                f"{self.id} is already sealed. To correct a measurement, record a "
                "new experiment with `supersedes` pointing here."
            )
        sums = {name: self._digest(self.directory / name) for name in SEALED_FILES}
        self.checksum_path.write_text(
            "".join(f"{digest}  {name}\n" for name, digest in sorted(sums.items())),
            encoding="utf-8",
        )
        return sums

    def verify(self) -> tuple[bool, list[str]]:
        if not self.sealed:
            return True, [f"{self.id}: not sealed yet"]
        problems: list[str] = []
        recorded: dict[str, str] = {}
        for line in self.checksum_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                digest, name = line.split(maxsplit=1)
                recorded[name.strip()] = digest
        for name, digest in recorded.items():
            path = self.directory / name
            if not path.exists():
                problems.append(f"{self.id}: {name} is missing")
            elif self._digest(path) != digest:
                problems.append(
                    f"{self.id}: {name} changed after sealing -- a sealed result "
                    "must never be edited; supersede it instead"
                )
        return (not problems), problems


# --- collection-level -----------------------------------------------------


def all_experiments() -> list[Experiment]:
    if not EXPERIMENTS.exists():
        return []
    out = []
    for d in sorted(EXPERIMENTS.iterdir()):
        manifest = d / "manifest.json"
        if d.is_dir() and manifest.exists():
            data = json.loads(manifest.read_text(encoding="utf-8"))
            out.append(Experiment(id=data["id"], title=data.get("title", "")))
    return out


def next_id() -> str:
    used = [int(e.id.split("-")[1]) for e in all_experiments() if e.id.startswith("EXP-")]
    return f"EXP-{max(used, default=0) + 1:03d}"


def verify_all() -> tuple[bool, list[str]]:
    problems: list[str] = []
    for exp in all_experiments():
        ok, issues = exp.verify()
        if not ok:
            problems += issues
    return (not problems), problems


# --- cli ------------------------------------------------------------------


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 1
    cmd = args[0]

    if cmd == "list":
        for exp in all_experiments():
            manifest = json.loads(exp.manifest_path.read_text(encoding="utf-8"))
            state = "sealed" if exp.sealed else "OPEN"
            sup = manifest.get("supersedes")
            print(
                f"  {exp.id:9} {state:7} {manifest.get('recordedAt','')[:10]}  "
                f"{exp.title[:52]:52}"
                + (f"  supersedes {sup}" if sup else "")
            )
        print(f"\n  next id: {next_id()}")
        return 0

    if cmd == "verify":
        ok, problems = verify_all()
        for p in problems:
            print(f"  {p}")
        print(f"\n  {'all sealed records intact' if ok else 'RECORDS ALTERED'}")
        return 0 if ok else 1

    if cmd == "new":
        if len(args) < 3:
            print("usage: experiment.py new <ID> <title>")
            return 2
        exp = Experiment(id=args[1], title=" ".join(args[2:]))
        path = exp.create()
        print(f"  created {path}")
        return 0

    if cmd == "seal":
        if len(args) < 2:
            print("usage: experiment.py seal <ID>")
            return 2
        exp = Experiment(id=args[1], title="")
        sums = exp.seal()
        for name, digest in sums.items():
            print(f"  {digest[:16]}…  {name}")
        print(f"  sealed {exp.id}")
        return 0

    print(f"unknown command: {cmd}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
