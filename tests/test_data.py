"""Inputs look the way specs/01-data.md says, checked before the pipeline runs."""

import pytest

from project.paths import SAMPLE
from project.pipeline import load

HEADER = "id,date,text,restricted\n"


@pytest.mark.spec("DATA-001", "DATA-003")
def test_sample_data_is_valid():
    assert load(SAMPLE / "records.csv")


@pytest.mark.spec("DATA-001")
def test_bad_date_names_the_line(tmp_path):
    f = tmp_path / "bad.csv"
    f.write_text(HEADER + "r1,1918-03-14,ok,false\nr2,14/03/1918,bad,false\n")
    with pytest.raises(ValueError, match=r"bad.csv:3: date"):
        load(f)


@pytest.mark.spec("DATA-003")
def test_wrong_columns_rejected(tmp_path):
    f = tmp_path / "bad.csv"
    f.write_text("id,date,text\nr1,1918-03-14,ok\n")
    with pytest.raises(ValueError, match="expected columns"):
        load(f)
