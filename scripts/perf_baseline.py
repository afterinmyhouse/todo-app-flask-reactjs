#!/usr/bin/env python3
"""100 sequential GETs; print avg/min/max latency (ms). Stdlib only."""
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

COUNT = 100
TIMEOUT = 15

endpoint = sys.argv[1] if len(sys.argv) > 1 else "https://httpbin.org/get"
latencies: list[float] = []
failures = 0

for i in range(1, COUNT + 1):
    t0 = time.perf_counter()
    try:
        with urlopen(Request(endpoint, method="GET"), timeout=TIMEOUT) as resp:
            resp.read()
    except (URLError, HTTPError, TimeoutError, OSError) as e:
        failures += 1
        print(f"#{i} {e!r}", file=sys.stderr)
        continue
    latencies.append((time.perf_counter() - t0) * 1000)

if latencies:
    n = len(latencies)
    avg = sum(latencies) / n
    print(f"Successful requests: {n}/{COUNT}  (failures: {failures})")
    print(f"Avg latency: {avg:.2f} ms")
    print(f"Min latency: {min(latencies):.2f} ms")
    print(f"Max latency: {max(latencies):.2f} ms")
else:
    print("No successful requests.", file=sys.stderr)
    sys.exit(1)
