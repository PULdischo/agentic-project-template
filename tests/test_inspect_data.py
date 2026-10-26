"""scripts/inspect_data.py shows the shape of data but never a value from it (AGENTS.md hard rules)."""

import csv
import subprocess
import sys

from project.paths import ROOT, SAMPLE


def inspect(path):
    script = ROOT / "scripts" / "inspect_data.py"
    return subprocess.run([sys.executable, script, path], capture_output=True, text=True, check=True).stdout


def test_describes_shape_without_values():
    out = inspect(SAMPLE / "records.csv")
    with open(SAMPLE / "records.csv", newline="", encoding="utf-8") as f:
        header, *rows = list(csv.reader(f))
    assert f"{len(rows)} rows, {len(header)} columns" in out
    assert all(f"- {name}:" in out for name in header)
    leaked = [v for row in rows for v in row if len(v) >= 4 and v in out]
    assert not leaked


def test_headerless_csv_does_not_print_first_row(tmp_path):
    f = tmp_path / "noheader.csv"
    f.write_text("r9,1918-05-01,secret words here,true\n")
    out = inspect(f)
    assert "column 1" in out
    assert "secret" not in out and "1918" not in out


def test_jsonl_keys_and_bad_lines(tmp_path):
    f = tmp_path / "x.jsonl"
    f.write_text('{"name": "Ada Lovelace", "age": 36}\nnot json Ada\n')
    out = inspect(f)
    assert "- name:" in out and "1 lines are not valid JSON" in out
    assert "Ada" not in out
