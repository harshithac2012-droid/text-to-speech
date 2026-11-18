import csv, datetime
from pathlib import Path

LOG = Path("results_log.csv")
FIELDS = ["time", "original", "normalized", "voice", "speed", "backend", "rating", "notes"]


def log_result(**row):
    new = not LOG.exists()
    with LOG.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        row["time"] = datetime.datetime.now().isoformat(timespec="seconds")
        w.writerow({k: row.get(k, "") for k in FIELDS})