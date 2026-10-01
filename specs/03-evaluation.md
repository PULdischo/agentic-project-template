# Evaluation

**ID prefix:** EVAL
**Owner:** <name>
**Status:** implemented
**Updated:** 2026-10-01

> Example spec. It covers the planned LLM step (topic labels and summaries) in `02-pipeline.md`. Replace it with your own criteria.

## Context

Tests (`tests/`) check the parts of the pipeline that always behave the same way. Evals (`evals/`) check the model's behavior, which varies from run to run, against example cases. Without evals we can't tell whether a change of model, prompt or tool actually improved anything.

## Requirements

- Each criterion below has at least one case in `evals/cases.jsonl`.
- Reports count these outcomes separately: **pass**, **fail**, **refused** (the model or provider declined), **error** (network, timeout or HTTP error) and **malformed** (the response was empty or unusable). A rise in refusals is different from a drop in quality and calls for a different fix.
- Thresholds: <e.g. EVAL-001 at least 90% pass; EVAL-003 zero refusals>.

## Acceptance criteria

- **EVAL-001**: The topic label is exactly one of: family, supplies, combat, health, other.
- **EVAL-002**: Summaries state nothing that is not in the excerpt.
- **EVAL-003**: Excerpts describing violence or injury (e.g. war diaries) are summarized, not refused.

## Out of scope

## Open questions
