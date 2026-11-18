"""Run every sentence in data/test_sentences.csv through the pipeline.
Saves audio to outputs/ and logs each run so you can rate them afterwards."""
import csv
from pathlib import Path

from logger import log_result
from normalizer import normalize
from tts_client import VOICES, synthesize

OUT = Path("outputs")
OUT.mkdir(exist_ok=True)

with open("data/test_sentences.csv", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

for i, row in enumerate(rows, 1):
    cleaned, changes = normalize(row["text"])
    audio, backend = synthesize(cleaned, VOICES["Default"])
    (OUT / f"{i:03d}_{row['category']}.wav").write_bytes(audio)
    log_result(original=row["text"], normalized=cleaned, voice="Default",
               speed=0.0, backend=backend, rating="", notes=row["category"])
    print(f"[{i}/{len(rows)}] {row['category']}: {len(changes)} changes")