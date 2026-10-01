# Processing pipeline

**ID prefix:** PIPE
**Owner:** <name>
**Status:** implemented
**Updated:** 2026-10-01

> Example spec. Replace it with your own pipeline steps.

## Context

The pipeline turns raw excerpts into an analysis-ready file, and every step can be checked.
Run it with `uv run python -m project.pipeline`. It reads `data/raw/records.csv` and writes `data/processed/records.csv`.

## Requirements

| Step | Input | Output | Notes |
|------|-------|--------|-------|
| 1. Load + validate | `data/raw/records.csv` | records in memory | Stops on bad input (see DATA-001, DATA-003) |
| 2. Clean | records | records | Drops restricted records and normalizes whitespace |
| 3. Write | records | `data/processed/records.csv` | Same columns as the input |
| 4. Topic + summary *(planned)* | records | labels, summaries | LLM step. Quality is defined in `03-evaluation.md` |

## Models and providers

| Step | Model | Provider | Why | Fallback |
|------|-------|----------|-----|----------|
| 4 | <e.g. qwen2.5:7b> | <e.g. local Ollama> | <cost, privacy, quality> | <other model> |

Models are set with `EVAL_BASE_URL` and `EVAL_MODEL` (see `.env.example`), never in code, so switching providers is a config change.

## Acceptance criteria

- **PIPE-001**: Every non-restricted input record appears in the output exactly once. No record is silently dropped.
- **PIPE-002**: Runs of spaces or line breaks in `text` are collapsed to single spaces, and no other change is made to the text.

## Out of scope

## Open questions
