"""Describe the shape of data files without printing any values.

This is how a coding agent learns the format of data/raw/ without the data reaching the model.
Per file it prints the size; for CSV/TSV the columns with value types, counts and max length;
for JSON/JSONL the keys with their JSON types. It never prints a cell value.

Run: uv run python scripts/inspect_data.py [file or folder ...]   (default: data/raw/)
"""

import csv
import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

from project.paths import RAW

MAX_KEYS = 50  # more distinct keys than this usually means the keys are data (ids, names)
JSON_TYPES = {dict: "object", list: "array", str: "string", bool: "bool", int: "number", float: "number"}


def kind(value: str) -> str:
    """The type a CSV cell looks like: empty, bool, int, float, date or text."""
    if value == "":
        return "empty"
    if value.lower() in ("true", "false"):
        return "bool"
    for name, parse in (("int", int), ("float", float), ("date", date.fromisoformat)):
        try:
            parse(value)
            return name
        except ValueError:
            pass
    return "text"


def counts(counter: Counter) -> str:
    return ", ".join(f"{name} {n}" for name, n in counter.most_common())


def describe_csv(path: Path) -> list[str]:
    with open(path, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f, delimiter="\t" if path.suffix == ".tsv" else ",")
        first = next(reader, [])
        # A first row of numbers, dates or long text is data, not a header: never print it.
        has_header = all(kind(c) == "text" and len(c) <= 64 for c in first)
        names = first if has_header else [f"column {i + 1}" for i in range(len(first))]
        kinds, longest = [Counter() for _ in names], [0] * len(names)
        rows = ragged = 0
        for row in reader if has_header else [first, *reader]:
            rows += 1
            ragged += len(row) != len(names)
            for i, value in enumerate(row[: len(names)]):
                kinds[i][kind(value)] += 1
                longest[i] = max(longest[i], len(value))
    out = [f"  {rows} rows, {len(names)} columns" + (f", {ragged} rows with a different column count" if ragged else "")]
    if not has_header:
        out.append("  first row does not look like a header; columns shown by position")
    out += [f"  - {name}: {counts(k)}; max length {n}" for name, k, n in zip(names, kinds, longest)]
    return out


def describe_json(path: Path) -> list[str]:
    records, bad = [], 0
    with open(path, encoding="utf-8", errors="replace") as f:
        if path.suffix == ".jsonl":
            for line in f:
                if line.strip():
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        bad += 1
        else:
            # ponytail: loads the whole file; stream it if a JSON file outgrows memory
            data = json.load(f)
            records = data if isinstance(data, list) else [data]
    keys, types = Counter(), Counter()
    key_types: dict[str, Counter] = {}
    for r in records:
        types[JSON_TYPES.get(type(r), "null")] += 1
        if isinstance(r, dict):
            for k, v in r.items():
                keys[k] += 1
                key_types.setdefault(k, Counter())[JSON_TYPES.get(type(v), "null")] += 1
    out = [f"  {len(records)} records ({counts(types)})" + (f", {bad} lines are not valid JSON" if bad else "")]
    if len(keys) > MAX_KEYS:
        out.append(f"  {len(keys)} distinct keys (not listed: too many, they are probably data)")
    else:
        out += [f"  - {k}: in {n} records; {counts(key_types[k])}" for k, n in keys.most_common()]
    return out


def describe(path: Path) -> list[str]:
    lines = [f"{path} ({path.stat().st_size:,} bytes)"]
    try:
        if path.suffix in (".csv", ".tsv"):
            lines += describe_csv(path)
        elif path.suffix in (".json", ".jsonl"):
            lines += describe_json(path)
        else:
            # ponytail: only CSV/TSV/JSON/JSONL are described; add a reader when raw data uses another format
            lines.append("  format not described")
    except (OSError, ValueError, csv.Error) as e:
        lines.append(f"  could not read: {type(e).__name__}")  # the message may quote data
    return lines


def main(args: list[str]) -> None:
    # ponytail: file names are printed; rename raw files first if their names are sensitive
    for target in [Path(a) for a in args] or [RAW]:
        files = [target] if target.is_file() else sorted(p for p in target.rglob("*") if p.is_file() and p.name != ".gitkeep")
        if not files:
            print(f"{target}: no files")
        for f in files:
            print("\n".join(describe(f)))


if __name__ == "__main__":
    main(sys.argv[1:])
