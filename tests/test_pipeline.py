"""Each pipeline stage produced sane output. Catches silent failures (specs/02-pipeline.md)."""

import csv

import pytest

from project.paths import SAMPLE
from project.pipeline import load, run


@pytest.fixture
def result(tmp_path):
    src = SAMPLE / "records.csv"
    dst = tmp_path / "processed.csv"
    run(src, dst)
    with open(dst, newline="", encoding="utf-8") as f:
        return load(src), list(csv.DictReader(f))


@pytest.mark.spec("DATA-002")
def test_restricted_records_excluded(result):
    _, out = result
    assert out and all(r["restricted"] == "false" for r in out)


@pytest.mark.spec("PIPE-001")
def test_no_silent_drops(result):
    src, out = result
    expected = [r["id"] for r in src if r["restricted"] == "false"]
    assert [r["id"] for r in out] == expected


@pytest.mark.spec("PIPE-002")
def test_whitespace_collapsed_only(result):
    src, out = result
    by_id = {r["id"]: r["text"] for r in src}
    for r in out:
        assert "  " not in r["text"]
        assert r["text"].split() == by_id[r["id"]].split()
