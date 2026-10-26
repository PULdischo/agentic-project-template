# <Project name>

<One or two sentences: what this project is and who it's for.>

This project is **spec-driven**. Partners describe what it should do in plain-language docs in [`specs/`](specs/). A coding agent implements those specs as code, tests and evals. Any agent works (Claude Code, Copilot, Codex, Zed, a local model), because all instructions live in [`AGENTS.md`](AGENTS.md).

## How to make a change (partners)

1. Open a spec in [`specs/`](specs/), on the GitHub website or in any editor. See [`specs/README.md`](specs/README.md).
2. Edit the text and the **acceptance criteria**. If parts are still fuzzy, ask the agent to "grill this spec" first. Then set `**Status:** ready`.
3. Ask the coding agent to "implement ready specs". It drafts the pull request description in `pr-draft.md`, but never opens the PR.
4. A person reads the diff and opens the pull request. Review it and the eval report it links to.
5. If something is wrong, change the spec, not the code.

## Folder map

| Path | What's in it | Who edits it |
|------|--------------|--------------|
| `specs/` | What the project should do: goals, data, pipeline, evaluation, changelog | Partners |
| `data/raw/` | Original source data. Never modified, not committed | Nobody (read-only) |
| `data/processed/` | Pipeline outputs, regenerated from raw. Not committed | Pipeline |
| `data/sample/` | Small, de-identified sample, committed. Used by tests and CI | Agent / maintainers |
| `data/README.md` | Data card: source, license, sensitivity | Partners |
| `src/project/` | The code | Agent |
| `tests/` | Checks that always give the same result: data validation and pipeline steps | Agent |
| `evals/` | Checks on model behavior: example cases, runner, dated results | Agent (cases reviewed by partners) |
| `scripts/` | Helpers: `check_coverage.py`, and `inspect_data.py` (data shape without values) | Agent |
| `prompts/` | Reusable agent prompts any tool can follow, e.g. `grill-spec.md` | Maintainers |
| `.claude/` | Claude Code adapter: `/grill-spec` command and permission rules that enforce `AGENTS.md` | Maintainers |
| `notebooks/` | Exploration only. Nothing the pipeline depends on | Anyone |
| `outputs/` | Figures, tables and reports for people | Pipeline |
| `AGENTS.md` | Instructions for coding agents | Maintainers |

## Setup

Requires [uv](https://docs.astral.sh/uv/). It installs the right Python for you.

```bash
uv sync                                       # install
uv run pytest                                 # run tests
uv run python scripts/check_coverage.py       # are all spec criteria covered?
uv run python -m project.pipeline             # data/raw/ → data/processed/
cp .env.example .env                          # then set EVAL_BASE_URL / EVAL_MODEL
uv run python evals/run_evals.py              # run evals, report written to evals/results/
```

Evals work with any OpenAI-compatible endpoint: local [Ollama](https://ollama.com), a hosted API, or a university-provided service. To switch providers, change `.env`. No code changes are needed.

## After creating from this template

- [ ] Rename `src/project/` to your package name, and update `name` in `pyproject.toml` and the imports in `tests/` and `scripts/`.
- [ ] Fill in `specs/00-project.md` (including AI-use disclosure), `data/README.md` and **Project conventions** in `AGENTS.md`.
- [ ] If you use another agent than Claude Code, set up its permissions to match `.claude/settings.json`: no reading `data/raw/`, `data/processed/` or `.env`; no `git push` or opening PRs. These permission rules are guardrails, not a security boundary: an agent can still print data by running code, so the rule in `AGENTS.md` is what counts.
- [ ] Replace the example specs (`01`–`03`), `data/sample/`, `tests/` and `evals/cases.jsonl` with your own, or keep them until your first real spec is ready.
- [ ] Delete `SPEC.md`. It describes this template, not your project.
- [ ] Replace this README's title and intro.

## Credits

Engineering practices in `AGENTS.md` are adapted from [Ponytail](https://github.com/dietrichgebert/ponytail) (MIT). See [`NOTICE.md`](NOTICE.md).
