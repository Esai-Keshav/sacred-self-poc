"""Print the v2 answers of the last 10 saved requests with word counts, for hand grading.

Run: uv run python grade.py
"""

import db
from config import V2_MAX_WORDS, V2_MIN_WORDS
from prompts import PERSPECTIVES

for item in reversed(db.list_requests()[:10]):
    row = db.get_request(item["id"])
    print(f"\n=== row {row['id']}: {row['situation']}")
    if row["willingness"] is None and row["willingness_v2"] is None:
        print("FALLBACK (out of scope)")
        continue
    for p in PERSPECTIVES:
        v2 = row[f"{p.key}_v2"]
        if v2 is None:
            print(f"-- {p.title} [MISSING]")
            continue
        n = len(v2.split())
        status = "PASS" if V2_MIN_WORDS <= n <= V2_MAX_WORDS else "FAIL"
        print(f"-- {p.title} [{n} {status}]: {v2}")
