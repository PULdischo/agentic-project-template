# Agent instructions

This file is the single source of instructions for any coding agent (Claude Code, Copilot, Codex, Zed, local models).
Tool-specific files (`CLAUDE.md`, `.github/copilot-instructions.md`, `.claude/`) only point here or enforce rules written here.

## How this project works

Project partners describe what the project should do in `specs/`. You turn spec changes into code, tests and evals.
Partners should never need to touch code. If the code and a spec disagree, the spec wins. If a spec is unclear, ask, don't guess.

## Commands

```bash
uv sync                                         # install (Python + deps from uv.lock)
uv run pytest                                   # tests: deterministic, no network
uv run python scripts/check_coverage.py         # every criterion covered by a test or eval?
uv run python evals/run_evals.py --dry-run      # validate eval cases without calling a model
uv run python evals/run_evals.py                # run evals against EVAL_BASE_URL / EVAL_MODEL (.env)
uv run python -m project.pipeline               # regenerate data/processed/ from data/raw/
uv run python scripts/inspect_data.py [path]    # shape of data/raw/ (or path): columns, types, counts, no values
grep -rn "ponytail:" src/ tests/ evals/ scripts/   # list deliberate shortcuts and their ceilings
```

## Implement ready specs

When asked to "implement ready specs" (or similar):

1. Find spec files in `specs/` with `**Status:** ready`. For each one, diff it against the commit recorded for it in `specs/CHANGELOG.md` (`git diff <commit> -- specs/<file>`). If there is no entry, treat the whole spec as new.
2. Read the spec and the code it touches, and trace the real data flow end to end. If a criterion is ambiguous or conflicts with another, write the question under that spec's **Open questions**, set `**Status:** needs-review`, and skip that criterion. Never implement past an open question.
3. For each new or changed criterion, change `src/` using the practices below. Then add or update the **smallest** test (`tests/`) or eval case (`evals/cases.jsonl`) that would fail if the criterion broke, tagged with its ID:
   - tests: `@pytest.mark.spec("DATA-001")`
   - eval cases: `"criteria": ["EVAL-001"]`
   - Use tests for behavior that is always the same, and evals for model behavior.
4. Run `uv run pytest` and `uv run python scripts/check_coverage.py`. Both must pass. If you changed prompts, models or eval cases, also run `uv run python evals/run_evals.py` and compare the report against the thresholds in `specs/03-evaluation.md`. Report refusals separately; never hide them.
5. Set the spec to `**Status:** implemented`, and add a line to the top of the table in `specs/CHANGELOG.md` with the date, spec, criteria, commit, eval report path, and the agent and model that made the change.
6. Write the pull request description to `pr-draft.md` (git-ignored), following `.github/pull_request_template.md`. List the assumptions the change makes and what was **not** tested; if any check failed, say so at the top. Do not push or open the PR: a human reads the diff and opens it.
7. Summarize for the partner in plain language: what changed, which criteria are covered, what the eval report shows (including refusals), and any open questions.

## Grill a draft spec

When asked to "grill" a spec (or to help write one), follow `prompts/grill-spec.md`.

## Hard rules

- Never modify anything in `data/raw/`.
- Never look at data values in `data/raw/` or `data/processed/`: don't open them, `cat`/`head` them, or run code that prints rows. You may be a hosted model, and anything you read is sent to your provider. Learn the format with `scripts/inspect_data.py`, take examples from `data/sample/`, and write code that reports counts and structure, not values. Error messages in `src/` name the file, line and column, never the value.
- Never push or open a pull request. A human reads the diff and opens it.
- Never read or print `.env`. Never commit secrets or `.env`. Endpoints and models come from environment variables, never from code.
- Never weaken, skip or delete a test or eval case to make it pass. If one seems wrong, raise it as an open question.
- In `specs/`, only edit **Open questions**, the **Status** line and `CHANGELOG.md`. You may fix formatting drift (bullets, quotes, spacing) but never change a partner's wording.
- Never reuse or renumber criterion IDs.
- All data paths come from `src/project/paths.py`.

## Project conventions

Maintainers fill these in; delete lines that don't apply.

- Units: <e.g. SI; dates as YYYY-MM-DD>
- Naming: <file and variable naming>
- Figures: <style file, colour-blind-safe palette, size, where alt text goes>

## Engineering practices

The best code is the code never written. Be lazy, which means efficient, not careless.

Before writing any code, understand the problem: read the spec and the code it touches, and trace the real flow. Then stop at the first rung that holds:

1. Does this need to be built at all? If no acceptance criterion requires it, don't build it.
2. Does it already exist in this repo? Reuse it.
3. Does the Python standard library do it? (`csv`, `json`, `pathlib`, `statistics`, `collections`, `itertools`, `urllib` …) Use it.
4. Does an already-installed dependency do it? Use it.
5. Can it be one line? Make it one line.
6. Only then: write the minimum code that works.

Rules:

- No abstractions, config layers, classes or plugin systems that a spec doesn't ask for.
- No new dependency if it can be avoided. If you add one, give a one-line reason in the PR description.
- Deletion over addition. Boring over clever. Fewest files possible.
- The shortest working diff wins, but only once you understand the problem. The smallest change in the wrong place is a second bug.
- Fix bugs at the root cause: grep every caller of the function you touch and fix the shared function once.
- When two approaches are the same size, pick the one that handles edge cases correctly.
- Question complex requests by writing "Do you need X, or does Y cover it?" under **Open questions**.
- Mark deliberate shortcuts that have a known ceiling with a `ponytail:` comment naming the ceiling and the upgrade trigger:
  `# ponytail: loads whole CSV into memory; switch to chunked reads if raw data > 2 GB`

Never lazy about:

- understanding the problem before picking a rung
- input validation at trust boundaries: anything read from `data/raw/`, external APIs or model output
- error handling that prevents data loss
- security and secrets
- accessibility of outputs (figures, reports)
- raw data staying immutable, and restricted data never leaving where `data/README.md` allows
- reproducibility: fixed seeds, `uv.lock`, outputs that can be regenerated from `data/raw/` with one command
- provenance: every processed file can be traced to its inputs and the code that made it
- LLM failure modes: refusals, policy rejections, timeouts and malformed output are detected and counted, never silently dropped
- anything a spec explicitly asks for

Lazy code without its check is unfinished. Every non-trivial piece of logic leaves one runnable check behind: the smallest test or eval case that fails if it breaks, tagged with its criterion ID. Trivial one-liners need no test.

---
*Engineering practices adapted from [Ponytail](https://github.com/dietrichgebert/ponytail) (MIT, © 2026 DietrichGebert). See `NOTICE.md`.*
