#!/usr/bin/env python3
import sys
from pathlib import Path

import pandas as pd

csv_path = sys.argv[1]
json_path = Path(csv_path).with_suffix(".json")

df = pd.read_csv(csv_path)
df.to_json(json_path, orient="records", indent=2)

print(f"Wrote {json_path}")