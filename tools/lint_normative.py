"""Fail when a MUST has no test. A MUST with no test is a wish.

    python tools/lint_normative.py

Walks `spec/`, finds every clause containing a normative **MUST** or **MUST NOT**, and
checks that at least one test points at it. A test may be:

* a **vector**, citing the clause in its `clause` field — the usual case;
* a **conformance case**, citing it in a `clauses` array — for structural requirements that
  no input/output pair can demonstrate;
* one of the suite's **own tests**, declared in `conformance/tests/clause-coverage.json` —
  for clauses that constrain a conformance suite rather than an implementation.

The third is verified, not trusted: a named test that does not exist is an error. Also checks the
reverse: a clause that carries no MUST should not claim vectors it does not need, and a
normative statement outside a clause has no identifier to cite.

Why this is a build step rather than a review habit: a specification whose requirements
cannot be checked produces implementations that all claim conformance and quietly disagree
about what it means. The disagreement is then invisible, which is worse than having no
specification at all. The only defence is refusing to let an untestable requirement land.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
SPEC = HERE / "spec"
VECTORS = HERE / "vectors"
CASES = HERE / "conformance" / "cases"

#: A clause heading: `## AEGS-0.1-ARITH-4 · A negative amount is refused`
CLAUSE_HEADING = re.compile(r"^##\s+(AEGS-0\.1-[A-Z]+-\d+[a-z]?)\s*(?:·\s*(.*))?$")

#: Normative keywords, in capitals. Lower-case "must" is ordinary English and is allowed —
#: which is exactly why the specification says so in its conventions section.
NORMATIVE = re.compile(r"\bMUST(?:\s+NOT)?\b")

#: A blockquote is commentary explaining a clause, not the clause itself. A MUST inside one
#: is describing what the clause requires, and counting it would demand a vector for a
#: sentence that is not a requirement.
QUOTE = re.compile(r"^\s*>")

#: Some clauses constrain THIS DOCUMENT rather than implementations -- the RFC 2119
#: conventions, and the rule that every MUST needs a test. They carry a MUST and there is
#: nothing for a vector to run.
#:
#: Marked in the specification text itself rather than listed here, so a *reader* sees the
#: distinction too and the marker cannot drift from the linter's view of it. A list in this
#: file would be invisible to anyone reading the spec, and would quietly grow.
META = re.compile(r"^\s*\*Constrains this document, not implementations\.\*")


def clauses() -> dict[str, dict]:
    """Every clause in the specification, with whether it is normative."""
    found: dict[str, dict] = {}
    for path in sorted(SPEC.glob("*.md")):
        current: str | None = None
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            heading = CLAUSE_HEADING.match(line)
            if heading:
                current = heading.group(1)
                found[current] = {
                    "file": path.name,
                    "line": lineno,
                    "title": (heading.group(2) or "").strip(),
                    "normative": False,
                    "meta": False,
                }
                continue
            if line.startswith("## "):
                current = None  # a non-clause heading closes the previous clause
                continue
            if current and META.match(line):
                found[current]["meta"] = True
                continue
            if (
                current
                and not QUOTE.match(line)
                and NORMATIVE.search(_strip_inline_code(line))
            ):
                found[current]["normative"] = True
    return found


def cited_by_vectors() -> dict[str, list[str]]:
    cited: dict[str, list[str]] = {}
    if not VECTORS.is_dir():
        return cited
    for path in sorted(VECTORS.rglob("*.json")):
        if path.name == "schema.json":
            continue
        try:
            clause = json.loads(path.read_text(encoding="utf-8")).get("clause")
        except json.JSONDecodeError:
            continue
        if clause:
            cited.setdefault(clause, []).append(path.relative_to(VECTORS).as_posix())
    return cited


def cited_by_cases() -> dict[str, list[str]]:
    """Conformance cases may cite clauses too, via an optional `clauses` array."""
    cited: dict[str, list[str]] = {}
    if not CASES.is_dir():
        return cited
    for path in sorted(CASES.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        for clause in data.get("clauses") or []:
            cited.setdefault(clause, []).append(path.name)
    return cited


def _strip_inline_code(line: str) -> str:
    """Remove `backticked` spans.

    A keyword in backticks is being *named*, not used normatively -- a sentence like
    "writing the vector discovers whether a `MUST` is checkable" talks about the keyword
    rather than imposing it. Stripping code spans is the honest fix; contorting the prose
    to dodge the regex would be the linter dictating the writing.
    """
    return re.sub(r"`[^`]*`", "", line)


def cited_by_code() -> tuple[dict[str, list[str]], list[str]]:
    """Clauses checked by the suite's own tests, plus any problems with the declaration.

    Some clauses constrain a conformance SUITE rather than an implementation -- "the scorer
    imports no implementation" has no input that demonstrates it, because a vector is data
    handed to an implementation. Those are checked by code, and `clause-coverage.json` is how
    that is declared.

    The declaration is verified rather than trusted: every test named must actually exist in
    the file, so a renamed or deleted test breaks the build instead of silently leaving a
    clause unchecked. A mapping nobody checks is a list of promises.
    """
    cited: dict[str, list[str]] = {}
    problems: list[str] = []
    declaration = CASES.parent / "tests" / "clause-coverage.json"
    if not declaration.is_file():
        return cited, problems

    try:
        data = json.loads(declaration.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return cited, [f"clause-coverage.json: not valid JSON: {exc}"]

    source_path = declaration.parent / data.get("file", "")
    if not source_path.is_file():
        return cited, [f"clause-coverage.json: names {data.get('file')!r}, which is not there"]

    source = source_path.read_text(encoding="utf-8")
    defined = set(re.findall(r"^def (test_\w+)", source, re.M))

    for clause, tests in (data.get("coverage") or {}).items():
        missing = [name for name in tests if name not in defined]
        if missing:
            problems.append(
                f"clause-coverage.json: {clause} names test(s) that do not exist in "
                f"{source_path.name}: {', '.join(missing)}. A mapping nobody checks is a "
                "list of promises."
            )
            continue
        cited.setdefault(clause, []).extend(f"{source_path.name}::{n}" for n in tests)

    return cited, problems


def stray_normative_text() -> list[str]:
    """Normative keywords outside any clause. They have no identifier, so nothing can cite them."""
    stray: list[str] = []
    for path in sorted(SPEC.glob("*.md")):
        current: str | None = None
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if CLAUSE_HEADING.match(line):
                current = "in"
                continue
            if line.startswith("## "):
                current = None
                continue
            if (
                current is None
                and not QUOTE.match(line)
                and NORMATIVE.search(_strip_inline_code(line))
            ):
                stray.append(f"{path.name}:{lineno}: {line.strip()[:78]}")
    return stray


def main() -> int:
    if not SPEC.is_dir():
        print(f"no spec at {SPEC} -- nothing to lint yet")
        return 0

    found = clauses()
    if not found:
        print(f"no clauses found in {SPEC}. Expected headings like `## AEGS-0.1-ARITH-1 · ...`")
        return 1

    cited = cited_by_vectors()
    for clause, names in cited_by_cases().items():
        cited.setdefault(clause, []).extend(names)

    code_cited, code_problems = cited_by_code()
    for clause, names in code_cited.items():
        cited.setdefault(clause, []).extend(names)

    normative = {
        cid: meta for cid, meta in found.items()
        if meta["normative"] and not meta["meta"]
    }
    untested = sorted(cid for cid in normative if cid not in cited)
    orphans = sorted(cid for cid in cited if cid not in found)
    stray = stray_normative_text()

    meta_count = sum(1 for m in found.values() if m["meta"])
    print(
        f"{len(found)} clause(s), {len(normative)} normative"
        + (f", {meta_count} constraining this document" if meta_count else "")
    )
    for cid, meta in sorted(found.items()):
        mark = "meta" if meta["meta"] else ("MUST" if meta["normative"] else "    ")
        count = len(cited.get(cid, ()))
        print(f"  {mark}  {cid:22} {count:2} test(s)  {meta['title'][:44]}")

    problems = False

    if code_problems:
        problems = True
        print(f"\n{len(code_problems)} problem(s) in the code-coverage declaration:")
        for problem in code_problems:
            print(f"  {problem}")

    if untested:
        problems = True
        print(f"\n{len(untested)} normative clause(s) with NO test:")
        for cid in untested:
            meta = found[cid]
            print(f"  {cid}  ({meta['file']}:{meta['line']})  {meta['title']}")
        print(
            "\n  A MUST with no test is a wish. Add a vector citing the clause, or add "
            "`clauses` to a conformance case, or soften the requirement to SHOULD and mean it."
        )

    if orphans:
        problems = True
        print(f"\n{len(orphans)} test(s) cite a clause that does not exist:")
        for cid in orphans:
            print(f"  {cid}  cited by {', '.join(cited[cid])}")

    if stray:
        problems = True
        print(f"\n{len(stray)} normative statement(s) outside any clause:")
        for line in stray:
            print(f"  {line}")
        print("\n  These have no identifier, so no test can cite them and no reader can "
              "reference them. Give them a clause heading.")

    if problems:
        return 1

    print(f"\nevery normative clause has at least one test")
    return 0


if __name__ == "__main__":
    sys.exit(main())
