# Data card

> Fill this in for your project. The example values describe `data/sample/records.csv`.

| Field | Value |
|-------|-------|
| **Name** | <dataset name> (example: transcribed letter excerpts, 1918) |
| **Source** | <archive, collection, URL, or person who provided it> |
| **License / rights** | <license, data use agreement, or permission terms> |
| **Sensitivity** | <public / internal / restricted, plus any IRB or DUA reference> |
| **Collected** | <dates of collection or creation> |
| **Contact** | <name, email> |

## Folders

- `raw/`: original files, exactly as received. **Never modified.** Not committed (see `.gitignore`).
- `processed/`: outputs from `uv run python -m project.pipeline`. Regenerated from `raw/` and not committed.
- `sample/`: a small, de-identified subset that is committed. Used by tests and CI. Must contain nothing restricted.

The coding agent never sees values from `raw/` or `processed/`, because a hosted agent would send them to its provider. It learns their format from `uv run python scripts/inspect_data.py`, which prints columns, types and counts only, and takes examples from `sample/`. That makes `sample/` the only data the agent reads, so keep it representative.

## Where restricted data may go

<e.g. Records marked restricted stay in `raw/` on approved machines only. They are never sent to external model APIs.>

## Known gaps and issues

- <missing years, OCR quality, transcription conventions, known biases>
