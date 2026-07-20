"""Generates a small synthetic sales CSV for demo/testing purposes."""
import csv
import random
from pathlib import Path

random.seed(3)

REGIONS = ["North", "South", "East", "West"]
PRODUCTS = ["Widget A", "Widget B", "Gadget X", "Gadget Y"]

rows = []
for month in range(1, 7):
    for _ in range(20):
        rows.append({
            "date": f"2026-{month:02d}-{random.randint(1,28):02d}",
            "region": random.choice(REGIONS),
            "product": random.choice(PRODUCTS),
            "revenue": round(random.uniform(100, 5000), 2),
            "units_sold": random.randint(1, 50),
        })

out_path = Path(__file__).parent / "sample_sales.csv"
with open(out_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["date", "region", "product", "revenue", "units_sold"])
    writer.writeheader()
    writer.writerows(rows)

print(f"Wrote {len(rows)} rows to {out_path}")
