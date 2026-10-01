"""The only place data paths are defined. Everything is relative to the repo root."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
RAW = DATA / "raw"
PROCESSED = DATA / "processed"
SAMPLE = DATA / "sample"
OUTPUTS = ROOT / "outputs"
