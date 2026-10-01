# SPEC: Spec-Driven Research Project Template

Status: **Implemented v1** · Owner: aj7878@princeton.edu · Last updated: 2026-10-01

## 1. Purpose

A reusable **GitHub template repository** for research and data science projects that use AI coding agents. Clicking **"Use this template"** creates a new project with every general part already in place: spec docs, data folders, tests, evals, and agent instructions.

**Main idea:** project partners make changes in **spec docs**, written in plain Markdown, and a **coding agent** turns those changes into code, tests and evals. Partners should never need to edit code to change what the project does.

### Design principles

- **No vendor lock-in.** Agent instructions live in one tool-neutral file (`AGENTS.md`). Tool-specific files (`CLAUDE.md`, `.github/copilot-instructions.md`) only point to it. Evals call any OpenAI-compatible endpoint, which covers hosted APIs, university endpoints and local Ollama.
- **Stay in your own environment.** Specs, data, code and results sit in one folder the agent can read, so nobody copy-pastes between a chat window and a terminal.
- **Grounded artifacts.** Every behavior is backed by a spec, a script and an evaluation criterion.
- **Evaluate along the way.** Validate inputs, check intermediate steps and inspect outputs. Expect LLM-specific failures such as refusals, content-policy rejections and silent truncation.
- **Lean by default (Ponytail).** The template and the code agents write in it follow the engineering practices in §4. The template itself is kept to the fewest files that do the job.

## 2. Decisions

| # | Decision | Notes |
|---|----------|-------|
| D1 | **Python + uv** is the default stack | `pyproject.toml`, a committed `uv.lock`, and `.python-version`. Every command runs as `uv run …`. pytest is the only dev dependency. |
| D2 | **Distributed as a GitHub template repo** | No cookiecutter or copier. A short "after you create from template" checklist in the README replaces prompting tools. |
| D3 | **Partners may edit specs anywhere** (GitHub web UI, VS Code, Zed, Google Docs exported to Markdown, and so on). No editor is preferred. | Specs must work as plain Markdown with no tooling, and must survive round-trips through editors that strip or mangle formatting (see §5.1). |
| D4 | **Engineering practices adapted from [Ponytail](https://github.com/dietrichgebert/ponytail)** (MIT) | The rules are adapted into `AGENTS.md` rather than requiring the plugin, so there is no dependency or lock-in. They use the same `ponytail:` comment marker, so people who do install the plugin can use its `/ponytail-review` and `/ponytail-debt` commands. Credit goes in the README. |

## 3. Core workflow

```
Partner edits spec  ──►  Agent reads change  ──►  Agent updates code + tests/evals
      ▲                                                     │
      └──── Partner reviews PR + eval report ◄──────────────┘
```

1. A partner edits or adds a file in `specs/`, changing the prose and the **acceptance criteria**, and sets `Status: ready`. In the GitHub web UI this happens on a branch or PR. Locally they can simply save the file.
2. Someone asks the agent to "implement ready specs". It follows `AGENTS.md`:
   1. Find specs with `Status: ready`. Diff each one against the commit recorded in `specs/CHANGELOG.md` for its last implementation, or treat it as new if there is none.
   2. Read the spec and the code it touches. If anything is ambiguous, add it to the spec's *Open questions* and stop working on that criterion.
   3. For each changed criterion, update `src/`, then add or update the smallest test or eval that would fail if that criterion broke.
   4. Run `uv run pytest` and, if evals are affected, `uv run python evals/run_evals.py`.
   5. Set the spec to `Status: implemented` and add a line to `specs/CHANGELOG.md` with the date, spec, criterion IDs, commit and eval report path.
3. The partner reviews the PR and the eval report. If something is wrong or unclear, they change the spec, not the code.

**Traceability rule:** every acceptance criterion has a stable ID (e.g. `DATA-003`). Every test and eval case names the IDs it covers. `scripts/check_coverage.py` (stdlib only) lists criteria that no test or eval covers, and test or eval IDs that match no criterion.

## 4. Engineering practices (adapted from Ponytail → goes in `AGENTS.md`)

### 4.1 The ladder

Before writing code, first understand the problem: read the spec and the code it touches, and trace the real data flow end to end. Then stop at the first rung that holds:

1. Does this need to be built at all? If no acceptance criterion requires it, don't build it.
2. Does it already exist in this repo? Reuse it.
3. Does the Python standard library do it? (`csv`, `json`, `pathlib`, `statistics`, `collections`, `itertools`, `urllib`…)
4. Does an already-installed dependency do it? Use it.
5. Can it be one line? Make it one line.
6. Only then: write the minimum code that works.

### 4.2 Rules

- No abstractions, config layers, classes or plugin systems that a spec does not ask for.
- No new dependency if it can be avoided. Each dependency added gets a one-line reason in the PR description.
- Prefer deletion to addition, and boring code to clever code. Use the fewest files possible.
- The shortest working diff wins, but only once the problem is understood. The smallest change in the wrong place is a second bug.
- Fix bugs at the root cause. Find every caller of the function you touch and fix the shared function once.
- When two approaches are the same size, choose the one that handles edge cases correctly.
- Question complex requests by adding the question to the spec's *Open questions*: "Do you need X, or does Y cover it?"
- Mark deliberate shortcuts that have a known ceiling with a `ponytail:` comment that names the ceiling and an upgrade trigger, e.g.
  `# ponytail: loads whole CSV into memory; switch to chunked reads if raw data > 2 GB`.

### 4.3 Never lazy about (research additions in *italics*)

- Understanding the problem before choosing a rung.
- Input validation at trust boundaries, i.e. anything read from `data/raw/`, external APIs or model outputs.
- Error handling that prevents data loss.
- Security and secrets.
- Accessibility of outputs (figures and reports).
- *Raw data stays immutable. Restricted or sensitive data never leaves the place its data card allows.*
- *Reproducibility: fixed seeds, pinned dependencies (`uv.lock`), and outputs that can be regenerated from `data/raw/` with one command.*
- *Provenance: every processed file can be traced to its inputs and the code that made it.*
- *LLM failure modes: refusals, policy rejections, timeouts and malformed output are detected and counted, never silently dropped.*
- Anything a spec explicitly asks for.

**Every non-trivial piece of logic leaves one runnable check behind:** the smallest test or eval case that fails if the logic breaks, tagged with its criterion ID. Trivial one-liners need no test.

## 5. Folder layout

Kept deliberately small. Each folder exists because a workflow step in §3 uses it.

```
<project>/
├── README.md                     # What this is, folder map, partner workflow, setup, Ponytail credit
├── AGENTS.md                     # Canonical agent instructions: workflow (§3) + practices (§4)
├── CLAUDE.md                     # "@AGENTS.md" (pointer only)
├── NOTICE.md                     # Ponytail MIT license notice (required by the license for adapted text)
├── .github/
│   ├── copilot-instructions.md   # Pointer to AGENTS.md
│   ├── pull_request_template.md  # Spec IDs touched, tests/evals run, deps added, ponytail: markers added
│   └── workflows/tests.yml       # uv sync + pytest + check_coverage on push/PR (no API keys)
├── specs/                        # ← partners work here
│   ├── README.md                 # How to write/change a spec, for any editor; good vs bad criteria
│   ├── _template.md              # Copy to start a new spec
│   ├── 00-project.md             # Goals, research questions, scope, stakeholders
│   ├── 01-data.md                # Sources, rights/licensing, sensitivity, expected shape
│   ├── 02-pipeline.md            # Steps input → output; models/providers used and why
│   ├── 03-evaluation.md          # What "good" looks like; metrics, thresholds, failure categories
│   └── CHANGELOG.md              # Implementation log + decision notes
├── data/
│   ├── README.md                 # Data card: provenance, license, sensitivity, known gaps
│   ├── raw/                      # Immutable sources (git-ignored except .gitkeep)
│   ├── processed/                # Pipeline outputs (git-ignored by default)
│   └── sample/                   # Small, de-identified, committed; used by tests and CI
├── src/project/                  # Renamed per project (README checklist)
│   ├── __init__.py
│   ├── paths.py                  # Only place data paths are defined
│   └── pipeline.py               # Placeholder pipeline exercised by the example tests
├── tests/
│   ├── test_data.py              # Inputs look like the spec says (schema, counts, ranges)
│   └── test_pipeline.py          # Each stage produced sane output (no silent failures)
├── evals/
│   ├── README.md                 # Tests vs evals; how to run and read results
│   ├── cases.jsonl               # One case per line, tagged with criterion IDs
│   ├── run_evals.py              # Stdlib-only runner for any OpenAI-compatible endpoint
│   └── results/                  # Dated reports: YYYY-MM-DD_<label>.json + .md
├── scripts/
│   └── check_coverage.py         # Criterion ↔ test/eval traceability
├── notebooks/                    # Exploration only; nothing the pipeline imports
├── outputs/                      # Figures, tables, reports for humans
├── .env.example                  # EVAL_BASE_URL, EVAL_MODEL, EVAL_API_KEY (names only)
├── .gitignore
├── .python-version
├── pyproject.toml                # pytest as dev dep; registers the `spec` marker
└── uv.lock
```

Cut from v1, on Ponytail grounds: `data/interim/` (create it when a pipeline needs it), the separate `decisions/` folder (notes go in `CHANGELOG.md` until there are too many), `04-models.md` (merged into `02-pipeline.md`), the `tests/` subfolders and `evals/rubrics/` (add them when the work outgrows a single file).

## 6. Component requirements

### 6.1 Spec docs (`specs/`)

To work in any editor (D3), specs use **plain Markdown with no YAML front matter**. Metadata goes in a bold-label block at the top, which survives the GitHub web UI, Google Docs export and rich-text editors:

```markdown
# Data sources and preparation

**ID prefix:** DATA
**Owner:** <partner name>
**Status:** draft | ready | implemented | needs-review
**Updated:** YYYY-MM-DD

## Context
Why this matters, in plain language.

## Requirements
What should happen.

## Acceptance criteria
- **DATA-001**: Every record has a date in YYYY-MM-DD format.
- **DATA-002**: Records marked restricted are never copied out of data/raw/.

## Out of scope

## Open questions
Agent and partners both add here. The agent never guesses past an open question.
```

- **SPEC-01**: A partner with no coding background can write or edit a spec. `specs/README.md` shows good and bad acceptance criteria (testable vs vague) and explains how to edit in the GitHub web UI, locally, or by pasting from Google Docs.
- **SPEC-02**: Criterion IDs are written as `PREFIX-NNN` and never reused or renumbered. A criterion that is removed is struck through, not deleted, so old test references still mean something.
- **SPEC-03**: The agent tolerates formatting drift from other editors (smart quotes, `*` vs `-` bullets, extra blank lines). It may normalize formatting but must not change wording.
- **SPEC-04**: The agent may edit specs only in *Open questions*, the **Status** line, and `CHANGELOG.md`.

### 6.2 Agent instructions (`AGENTS.md`)

- **AGENT-01**: Contains the workflow from §3 and the practices from §4, written so any harness can follow it.
- **AGENT-02**: Hard rules: never modify `data/raw/`; never commit secrets or `.env`; never weaken, skip or delete a test or eval to make it pass; never implement a criterion that has an open question against it.
- **AGENT-03**: Lists the exact commands: `uv sync`, `uv run pytest`, `uv run python evals/run_evals.py [--dry-run]`, `uv run python scripts/check_coverage.py`, and `grep -rn "ponytail:" src/` to list deliberate shortcuts.
- **AGENT-04**: `CLAUDE.md` and `.github/copilot-instructions.md` contain only a pointer to `AGENTS.md`.

### 6.3 Data (`data/`)

- **DATA-01**: `data/raw/` and `data/processed/` are git-ignored, apart from a `.gitkeep`. `data/sample/` is committed, small (target under 1 MB) and de-identified.
- **DATA-02**: `data/README.md` is a data card covering source, license or rights, sensitivity level, collection dates, known gaps and contact.
- **DATA-03**: All data paths come from `src/project/paths.py`, which builds them with `pathlib` relative to the repo root. There are no absolute paths anywhere.

### 6.4 Tests (`tests/`)

- **TEST-01**: `uv run pytest` passes on a fresh copy of the template, using only `data/sample/`, with no network or API keys.
- **TEST-02**: `test_data.py` checks that inputs match `01-data.md` before the pipeline runs.
- **TEST-03**: `test_pipeline.py` checks each stage's output for silent failures (empty output, dropped rows, unchanged data).
- **TEST-04**: Tests declare criteria with `@pytest.mark.spec("DATA-001", ...)`. The marker is registered in `pyproject.toml`.

### 6.5 Evals (`evals/`)

- **EVAL-01**: `run_evals.py` uses only the standard library (`urllib`, `json`) and calls an OpenAI-compatible `/chat/completions` endpoint configured by `EVAL_BASE_URL`, `EVAL_MODEL` and `EVAL_API_KEY`. It has no provider SDKs.
- **EVAL-02**: Each line of `cases.jsonl` has `id`, `criteria`, `input`, and `expected`, where `expected` is `{"equals": …}`, `{"contains": …}`, `{"regex": …}` or `{"judge": "<rubric text>"}`. A case may also have `tags`.
- **EVAL-03**: Each case's outcome is one of `pass | fail | refused | error | malformed`. Refusals and policy rejections are detected and reported separately from failures.
- **EVAL-04**: Reports record the date, base URL host, model, a hash of the cases file and prompts, pass rate per criterion, and the failing cases. They are written as JSON for diffing and Markdown for partners.
- **EVAL-05**: `--dry-run` checks that the cases file is well-formed without calling a model. Whether criterion IDs exist is checked once, by `check_coverage.py`, not in two places. CI runs both.
- **EVAL-06**: The template ships with about three example cases, including one `judge` case and one designed to show a `refused` outcome.

### 6.6 GitHub template

- **GH-01**: The repository is marked as a template on GitHub.
- **GH-02**: The README has an "After creating from template" checklist: rename `src/project/`, update the `pyproject.toml` name, fill in `specs/00-project.md` and `data/README.md`, replace the examples, and delete this `SPEC.md`.
- **GH-03**: CI (`tests.yml`) runs `uv sync`, `uv run pytest`, `check_coverage.py` and `run_evals.py --dry-run`. It needs no secrets.
- **GH-04**: The PR template asks: which criterion IDs changed, what tests or evals were run, any new dependencies (with a reason), and any new `ponytail:` markers.

## 7. Non-goals

- Not a framework or a package. It is conventions, plus three small scripts.
- No provider SDKs, orchestration frameworks or LLM-eval libraries in the base template.
- No domain-specific pipeline code beyond a minimal placeholder that the example tests exercise.
- No R or Quarto support in the base template. A project can add it.

## 8. Acceptance for the template itself

- [ ] "Use this template" → clone → `uv sync && uv run pytest` passes.
- [ ] `uv run python evals/run_evals.py --dry-run` and `scripts/check_coverage.py` pass with no API keys, and CI is green on the template repo.
- [ ] With `EVAL_*` pointed at a local Ollama model, `run_evals.py` writes a report to `evals/results/`.
- [ ] A partner adds a criterion through the GitHub web UI alone. An agent then implements it from `AGENTS.md` alone, in at least two harnesses (e.g. Claude Code and Copilot), and `check_coverage.py` shows it covered.
- [ ] Ponytail self-check: every file in the template is used by a workflow step, and nothing can be deleted without losing a requirement above.

## 9. Open questions

Defaults chosen during implementation are marked **(default)**. Change them by editing this section.

1. **Spec granularity (default):** start with the numbered files 00–03. Projects may add more spec files with new ID prefixes; `check_coverage.py` picks up any `specs/*.md`.
2. **Sensitive data (default):** a `restricted` column, enforced by tests (DATA-002), plus the data card. A machine-checkable sensitivity flag for the whole dataset (DUA/IRB) is deferred until a project needs one.
3. **Agent skills (default):** everything lives in `AGENTS.md` until it gets too long. Add tool-neutral skills (e.g. `implement-specs`) when that happens.
4. **Google Docs flow (default):** export as Markdown, or copy and paste, into `specs/`, as documented in `specs/README.md`. No sync step.
5. **Template license (open):** no `LICENSE` file yet. Choose one (MIT matches Ponytail) and a default license for new projects.
6. **Pushing to GitHub (open):** the folder is not yet a git repo. Create the repo, push, and tick "Template repository" in Settings (GH-01).
