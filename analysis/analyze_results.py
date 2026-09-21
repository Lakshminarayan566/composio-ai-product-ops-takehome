import csv
from collections import Counter
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "data" / "research_results.csv"
with p.open(newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

print("Rows:", len(rows))
for field in ["auth_methods", "self_serve_or_gated", "mcp", "buildability", "category"]:
    c = Counter(r.get(field, "Unknown") for r in rows)
    print("\n", field)
    for k, v in c.most_common():
        print(f"{k}: {v}")
