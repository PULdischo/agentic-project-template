"""Check that spec criteria and tests/evals point at each other.

Errors (exit 1): a test or eval names an ID that no spec defines, or a criterion
in an `implemented` spec has no test or eval. Criteria in draft/ready specs are listed as to-do.

Run: uv run python scripts/check_coverage.py
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ID = r"[A-Z]+-\d{3}"
NOT_SPECS = {"README.md", "_template.md", "CHANGELOG.md"}


def criteria():
    """Return ({id: (spec, status)} for live criteria, set of struck-through ids)."""
    live, retired = {}, set()
    for f in sorted((ROOT / "specs").glob("*.md")):
        if f.name in NOT_SPECS:
            continue
        text = f.read_text(encoding="utf-8")
        status = re.search(r"[*_]{2}Status:?[*_]{2}:?\s*([\w-]+)", text)
        status = status.group(1).lower() if status else "draft"
        for line in text.splitlines():
            # Bold ID, tolerant of editor drift: **DATA-001**, **DATA-001:**, __DATA-001__
            for cid in re.findall(rf"[*_]{{2}}\s*({ID})", line):
                if "~~" in line:
                    retired.add(cid)
                else:
                    live.setdefault(cid, (f.name, status))
    return live, retired


def references():
    """Return {id: [where it's referenced]} from pytest markers and eval cases."""
    refs = {}
    for f in sorted((ROOT / "tests").rglob("*.py")):
        for args in re.findall(r"mark\.spec\(([^)]*)\)", f.read_text(encoding="utf-8")):
            for cid in re.findall(ID, args):
                refs.setdefault(cid, []).append(str(f.relative_to(ROOT)))
    cases = ROOT / "evals" / "cases.jsonl"
    if cases.exists():
        for line in cases.read_text(encoding="utf-8").splitlines():
            if line.strip():
                case = json.loads(line)
                for cid in case.get("criteria", []):
                    refs.setdefault(cid, []).append(f"evals/cases.jsonl:{case.get('id')}")
    return refs


def main():
    live, retired = criteria()
    refs = references()
    errors, todo = [], []
    for cid, where in sorted(refs.items()):
        if cid in retired:
            print(f"warning: {cid} is retired but still referenced by {', '.join(where)}")
        elif cid not in live:
            errors.append(f"{cid} is referenced by {', '.join(where)} but defined in no spec")
    for cid, (spec, status) in sorted(live.items()):
        if cid not in refs:
            msg = f"{cid} ({spec}, {status}) has no test or eval"
            (errors if status == "implemented" else todo).append(msg)

    covered = sum(1 for cid in live if cid in refs)
    print(f"{covered}/{len(live)} criteria covered")
    for msg in todo:
        print(f"to do: {msg}")
    for msg in errors:
        print(f"error: {msg}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
