# Evals

**Tests** (`tests/`) check code that always behaves the same way. The same input always gives the same output, and they run in CI with no API keys.
**Evals** check model behavior, which varies from run to run and from model to model. They answer questions like "did switching models make the labels better or worse?" and "is the provider refusing our war diaries?"

## Run

```bash
cp .env.example .env                              # once: pick an endpoint and model
uv run python evals/run_evals.py --dry-run        # check cases.jsonl is well-formed (no model calls)
uv run python evals/run_evals.py                  # run all cases
uv run python evals/run_evals.py --label new-prompt   # name the report, e.g. when comparing changes
```

Any OpenAI-compatible endpoint works: local Ollama (`http://localhost:11434/v1`), hosted APIs, or university services. Change `.env` to switch. No code changes are needed.

## Cases (`cases.jsonl`)

One JSON object per line:

```json
{"id": "label-family", "criteria": ["EVAL-001"], "system": "optional system prompt", "input": "text sent to the model", "expected": {"regex": "(?i)^\\W*family\\W*$"}, "tags": ["label"]}
```

`expected` has exactly one of:

| Check | Passes when |
|-------|-------------|
| `{"equals": "..."}` | the response, trimmed, is exactly this |
| `{"contains": "..."}` | the response contains this (case-insensitive) |
| `{"regex": "..."}` | the regex matches somewhere in the response |
| `{"judge": "rubric"}` | the same model, acting as a judge, says the response meets the rubric |

Every case lists the spec criteria it checks. `scripts/check_coverage.py` makes sure those IDs exist.

## Reading results

Each run writes `results/YYYY-MM-DD_<label>.md`, for people, and a matching `.json`, for comparing runs. Every case gets one outcome:

| Outcome | Meaning | Usual fix |
|---------|---------|-----------|
| `pass` | Met the expectation | — |
| `fail` | Answered, but wrong | Prompt, model, or the spec's expectations |
| `refused` | The model or provider declined (refusal text, content filter, policy error) | A different model or provider, or reframing. Not a prompt-quality issue |
| `error` | Network, timeout or HTTP error | Check the endpoint, key or rate limits |
| `malformed` | Empty or unusable response | Output format instructions, or max tokens |

Compare pass rates against the thresholds in `specs/03-evaluation.md`. Commit reports you want to keep as a baseline.
