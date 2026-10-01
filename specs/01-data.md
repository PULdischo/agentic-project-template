# Data sources and preparation

**ID prefix:** DATA
**Owner:** <name>
**Status:** implemented
**Updated:** 2026-10-01

> Example spec. It describes the sample letters in `data/sample/records.csv`. Replace it with your own data.

## Context

The project works from transcribed letter excerpts. Some excerpts contain private information and are marked restricted. They must stay in `data/raw/`. Details of source, license and sensitivity belong in the data card, `data/README.md`.

## Requirements

Input is a CSV file with one row per excerpt and the columns `id`, `date`, `text` and `restricted`. Bad input should stop the pipeline with a message that names the file and line, so nothing is processed silently.

## Acceptance criteria

- **DATA-001**: Every record has a date in YYYY-MM-DD format. A record with any other date stops the pipeline and the error names the line.
- **DATA-002**: Records marked restricted never appear in `data/processed/`.
- **DATA-003**: Input files have exactly the columns `id, date, text, restricted`, and `restricted` is `true` or `false`.

## Out of scope

- De-identification of restricted records. They are excluded, not transformed.

## Open questions
