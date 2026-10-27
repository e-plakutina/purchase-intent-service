"""
Замер latency_ms батч-эндпоинта: 1 строка против 500 в одном запросе, медиана из 10 повторов.
"""

import json
import statistics
import sys
import urllib.request
from pathlib import Path

HOST = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
ROW = json.loads(
    (Path(__file__).resolve().parents[1] / "examples" / "request.json").read_text()
)
REPEATS = 10


def latency_ms(n_rows: int) -> float:
    body = json.dumps({"rows": [ROW] * n_rows}).encode()
    request = urllib.request.Request(
        f"{HOST}/v1/predict/batch",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request) as response:
        return json.load(response)["latency_ms"]


latency_ms(1)

medians = {
    n: statistics.median(latency_ms(n) for _ in range(REPEATS)) for n in (1, 500)
}
for n, ms in medians.items():
    print(f"{n:>4} rows: {ms:.2f} ms")
print(f"500 rows / 1 row: {medians[500] / medians[1]:.1f}x")
