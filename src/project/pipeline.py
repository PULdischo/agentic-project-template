"""Placeholder pipeline: load records, validate them, drop restricted ones, write the result.

Replace with your project's real steps (see specs/02-pipeline.md).
Run: uv run python -m project.pipeline [input.csv] [output.csv]
"""

import csv
import sys
from datetime import date
from pathlib import Path

from project.paths import PROCESSED, RAW

FIELDS = ["id", "date", "text", "restricted"]


def load(path: Path) -> list[dict]:
    """Read records and validate them at the trust boundary (DATA-001, DATA-003)."""
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != FIELDS:
            raise ValueError(f"{path}: expected columns {FIELDS}, got {reader.fieldnames}")
        rows = list(reader)
    for line, row in enumerate(rows, start=2):
        try:
            date.fromisoformat(row["date"])
        except ValueError:
            raise ValueError(f"{path}:{line}: date {row['date']!r} is not YYYY-MM-DD") from None
        if row["restricted"] not in ("true", "false"):
            raise ValueError(f"{path}:{line}: restricted must be 'true' or 'false'")
    return rows


def clean(rows: list[dict]) -> list[dict]:
    """Drop restricted records (DATA-002) and collapse whitespace in text (PIPE-002)."""
    return [{**r, "text": " ".join(r["text"].split())} for r in rows if r["restricted"] == "false"]


def run(src: Path, dst: Path) -> list[dict]:
    rows = clean(load(src))
    dst.parent.mkdir(parents=True, exist_ok=True)
    with open(dst, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return rows


if __name__ == "__main__":
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else RAW / "records.csv"
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else PROCESSED / "records.csv"
    print(f"wrote {len(run(src, dst))} records to {dst}")
