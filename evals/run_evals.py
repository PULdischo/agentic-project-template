"""Run eval cases against any OpenAI-compatible chat endpoint. Standard library only.

    uv run python evals/run_evals.py              # run, write report to evals/results/
    uv run python evals/run_evals.py --dry-run    # validate cases only, no model calls
    uv run python evals/run_evals.py --label after-prompt-change

Config comes from the environment, or from .env if present: EVAL_BASE_URL, EVAL_MODEL, EVAL_API_KEY.
Outcomes: pass | fail | refused | error | malformed (see specs/03-evaluation.md).
"""

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from collections import Counter
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUTCOMES = ["pass", "fail", "refused", "error", "malformed"]
CHECKS = {"equals", "contains", "regex", "judge"}
JUDGE_PROMPT = (
    "You are grading a model response against a rubric. "
    "Reply with PASS or FAIL on the first line, then one sentence explaining why."
)
# ponytail: English phrase heuristic; misses subtle or non-English refusals.
# Upgrade to a judge-based refusal check if refused counts look wrong on manual review.
REFUSAL = re.compile(
    r"(?i)\b(I can(?:'|’|no)t (?:help|assist|provide|comply|do that)|I(?:'|’)m (?:sorry|unable)|"
    r"I am (?:sorry|unable)|I won(?:'|’)t (?:help|provide)|against (?:my|our) (?:guidelines|policy))"
)


def load_env():
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            key, sep, value = line.partition("=")
            if sep and not key.strip().startswith("#"):
                os.environ.setdefault(key.strip(), value.strip())


def load_cases(path):
    """Parse and validate cases; return (cases, errors)."""
    cases, errors, seen = [], [], set()
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        where = f"{path.name}:{n}"
        try:
            case = json.loads(line)
        except json.JSONDecodeError as e:
            errors.append(f"{where}: invalid JSON ({e})")
            continue
        if not isinstance(case.get("id"), str) or case["id"] in seen:
            errors.append(f"{where}: needs a unique string 'id'")
        seen.add(case.get("id"))
        crit = case.get("criteria")
        if not crit or not isinstance(crit, list) or not all(isinstance(c, str) for c in crit):
            errors.append(f"{where}: 'criteria' must be a non-empty list of IDs")
        if not isinstance(case.get("input"), str):
            errors.append(f"{where}: 'input' must be a string")
        exp = case.get("expected")
        if not isinstance(exp, dict) or len(exp) != 1 or not CHECKS >= exp.keys():
            errors.append(f"{where}: 'expected' must have exactly one of {sorted(CHECKS)}")
        elif "regex" in exp:
            try:
                re.compile(exp["regex"])
            except re.error as e:
                errors.append(f"{where}: bad regex ({e})")
        cases.append(case)
    return cases, errors


def chat(messages):
    """Return (outcome_or_None, text). outcome is set when the call itself failed or was refused."""
    base = os.environ["EVAL_BASE_URL"].rstrip("/")
    body = json.dumps({"model": os.environ["EVAL_MODEL"], "messages": messages, "temperature": 0})
    headers = {"Content-Type": "application/json"}
    if os.environ.get("EVAL_API_KEY"):
        headers["Authorization"] = f"Bearer {os.environ['EVAL_API_KEY']}"
    req = urllib.request.Request(f"{base}/chat/completions", body.encode(), headers)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:500]
        # Providers often reject flagged content with a 400 rather than a refusal message.
        policy = re.search(r"(?i)content.?(policy|filter|management)|safety|moderation", detail)
        return ("refused" if policy else "error"), f"HTTP {e.code}: {detail}"
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        return "error", str(e)
    try:
        choice = data["choices"][0]
        text = choice["message"].get("content") or ""
    except (KeyError, IndexError, TypeError):
        return "malformed", json.dumps(data)[:500]
    if choice.get("finish_reason") == "content_filter" or choice["message"].get("refusal"):
        return "refused", text or choice["message"]["refusal"]
    if not text.strip():
        return "malformed", "empty response"
    return None, text


def grade(case, text):
    """Return (outcome, detail) for a model response."""
    (check, want), = case["expected"].items()
    if check == "judge":
        rubric = f"Rubric: {want}\n\nInput given to the model:\n{case['input']}\n\nModel response:\n{text}"
        failed, verdict = chat([{"role": "system", "content": JUDGE_PROMPT}, {"role": "user", "content": rubric}])
        if failed:
            return failed, f"judge: {verdict}"
        first = verdict.strip().split()[0].upper().strip("*:.") if verdict.strip() else ""
        if first not in ("PASS", "FAIL"):
            return "malformed", f"judge: {verdict}"
        ok = first == "PASS"
    else:
        ok = {"equals": lambda: text.strip() == want,
              "contains": lambda: want.lower() in text.lower(),
              "regex": lambda: re.search(want, text) is not None}[check]()
        verdict = ""
    if ok:
        return "pass", verdict
    return ("refused" if REFUSAL.search(text) else "fail"), verdict


def run(cases):
    results = []
    for case in cases:
        messages = ([{"role": "system", "content": case["system"]}] if case.get("system") else [])
        failed, text = chat(messages + [{"role": "user", "content": case["input"]}])
        outcome, detail = (failed, "") if failed else grade(case, text)
        results.append({"id": case["id"], "criteria": case["criteria"], "outcome": outcome,
                        "response": text, "detail": detail})
        print(f"{outcome:>9}  {case['id']}")
    return results


def summarize(results):
    by_crit = {}
    for r in results:
        for c in r["criteria"]:
            by_crit.setdefault(c, Counter())[r["outcome"]] += 1
    return {c: {**{o: n[o] for o in OUTCOMES}, "pass_rate": round(n["pass"] / n.total(), 3)}
            for c, n in sorted(by_crit.items())}


def write_report(results, cases_path, label):
    model = os.environ["EVAL_MODEL"]
    label = re.sub(r"[^\w.-]+", "-", label or model)
    stem = HERE / "results" / f"{date.today()}_{label}"
    report = {
        "date": str(date.today()),
        "endpoint": urlparse(os.environ["EVAL_BASE_URL"]).netloc,
        "model": model,
        "cases_sha256": hashlib.sha256(cases_path.read_bytes() + JUDGE_PROMPT.encode()).hexdigest()[:16],
        "totals": dict(Counter(r["outcome"] for r in results)),
        "by_criterion": summarize(results),
        "results": results,
    }
    stem.parent.mkdir(exist_ok=True)
    stem.with_suffix(".json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [f"# Eval report: {report['date']} · {model}", "",
             f"Endpoint `{report['endpoint']}` · cases hash `{report['cases_sha256']}` · {len(results)} cases", "",
             "| Criterion | " + " | ".join(OUTCOMES) + " | Pass rate |",
             "|---" * (len(OUTCOMES) + 2) + "|"]
    for c, s in report["by_criterion"].items():
        lines.append(f"| {c} | " + " | ".join(str(s[o]) for o in OUTCOMES) + f" | {s['pass_rate']:.0%} |")
    not_passed = [r for r in results if r["outcome"] != "pass"]
    if not_passed:
        lines += ["", "## Cases that did not pass", ""]
        for r in not_passed:
            reply = " ".join(r["response"].split())[:300]
            lines.append(f"- **{r['id']}** ({', '.join(r['criteria'])}): `{r['outcome']}`. Response: {reply}")
            if r["detail"]:
                lines.append(f"  - {' '.join(r['detail'].split())[:300]}")
    stem.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return stem


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="validate cases without calling a model")
    parser.add_argument("--label", help="name for the report file (default: model name)")
    parser.add_argument("--cases", type=Path, default=HERE / "cases.jsonl")
    args = parser.parse_args()

    cases, errors = load_cases(args.cases)
    for e in errors:
        print(f"error: {e}")
    if errors:
        sys.exit(1)
    if args.dry_run:
        print(f"{len(cases)} cases OK (criterion IDs are checked by scripts/check_coverage.py)")
        return

    load_env()
    missing = [k for k in ("EVAL_BASE_URL", "EVAL_MODEL") if not os.environ.get(k)]
    if missing:
        sys.exit(f"Set {', '.join(missing)} in the environment or .env (see .env.example)")
    results = run(cases)
    stem = write_report(results, args.cases, args.label)
    print(f"\n{dict(Counter(r['outcome'] for r in results))}\nreport: {stem.relative_to(ROOT)}.md")


if __name__ == "__main__":
    main()
