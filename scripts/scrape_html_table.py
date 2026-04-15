"""
Fetch a public HTML page and extract structured rows from a data table.

Default source: Wikipedia "List of exceptional asteroids" — real tabular
asteroid data in server-rendered HTML (<table class="wikitable">).

Install deps (from repo root):
  pip install -r scripts/requirements-scrape.txt

Example:
  python scripts/scrape_html_table.py --table-index 0
  python scripts/scrape_html_table.py --url "https://en.wikipedia.org/wiki/List_of_exceptional_asteroids" -t 0 -o scripts/output
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

DEFAULT_URL = "https://en.wikipedia.org/wiki/List_of_exceptional_asteroids"
DEFAULT_USER_AGENT = (
    "TodoAppTableScraper/1.0 (+https://github.com/; educational table scrape)"
)


def _cell_text(cell: Any) -> str:
    return re.sub(r"\s+", " ", cell.get_text(separator=" ", strip=True))


def _row_values(tr: Any, n_cols: int) -> list[str]:
    cells = tr.find_all(["th", "td"], recursive=False)
    values = [_cell_text(c) for c in cells]
    if len(values) < n_cols:
        values.extend([""] * (n_cols - len(values)))
    elif len(values) > n_cols:
        values = values[:n_cols]
    return values


def _table_rows(table: Any) -> list[Any]:
    """Rows belonging to this table only (not nested inner tables)."""
    rows: list[Any] = []
    for tr in table.find_all("tr"):
        if tr.find_parent("table") is table:
            rows.append(tr)
    return rows


def wikitable_to_records(table: Any) -> list[dict[str, str]]:
    rows = _table_rows(table)
    if not rows:
        return []

    header_idx: int | None = None
    headers: list[str] = []
    for i, tr in enumerate(rows):
        if not tr.find("th", recursive=False):
            continue
        cells = tr.find_all(["th", "td"], recursive=False)
        cand = [_cell_text(c) for c in cells]
        if cand and any(cand):
            header_idx = i
            headers = cand
            break

    if header_idx is None or not headers:
        return []

    n_cols = len(headers)
    records: list[dict[str, str]] = []
    for tr in rows[header_idx + 1 :]:
        if not tr.find("td", recursive=False):
            continue
        row = _row_values(tr, n_cols)
        if not any(row):
            continue
        records.append(dict(zip(headers, row)))

    return records


def fetch_html(url: str, timeout: float) -> str:
    headers = {"User-Agent": DEFAULT_USER_AGENT}
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def parse_wikitables(html: str) -> list[Any]:
    soup = BeautifulSoup(html, "html.parser")
    return soup.find_all("table", class_=lambda c: c and "wikitable" in c.split())


def write_json(path: Path, records: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv(path: Path, records: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not records:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(records[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(records)


def main() -> int:
    p = argparse.ArgumentParser(description="Scrape HTML tables into JSON/CSV.")
    p.add_argument("--url", default=DEFAULT_URL, help="Page URL with HTML tables.")
    p.add_argument(
        "-t",
        "--table-index",
        type=int,
        default=0,
        help="Zero-based index among tables with class 'wikitable'.",
    )
    p.add_argument(
        "-o",
        "--out-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "output",
        help="Directory for output files.",
    )
    p.add_argument(
        "--format",
        choices=("json", "csv", "both"),
        default="both",
        help="Output format.",
    )
    p.add_argument("--timeout", type=float, default=30.0)
    args = p.parse_args()

    try:
        html = fetch_html(args.url, args.timeout)
    except requests.RequestException as e:
        print(f"HTTP error: {e}", file=sys.stderr)
        return 1

    tables = parse_wikitables(html)
    if not tables:
        print("No wikitable tables found on page.", file=sys.stderr)
        return 1
    if args.table_index < 0 or args.table_index >= len(tables):
        print(f"table-index {args.table_index} out of range (0..{len(tables) - 1}).", file=sys.stderr)
        return 1

    records = wikitable_to_records(tables[args.table_index])
    if not records:
        print("Selected table produced no data rows.", file=sys.stderr)
        return 1

    host = urlparse(args.url).netloc.replace(".", "_")
    slug = Path(urlparse(args.url).path.rstrip("/")).name or "page"
    base = args.out_dir / f"{host}_{slug}_wikitable_{args.table_index}"

    if args.format in ("json", "both"):
        write_json(base.with_suffix(".json"), records)
        print(f"Wrote {base.with_suffix('.json')} ({len(records)} rows)")
    if args.format in ("csv", "both"):
        write_csv(base.with_suffix(".csv"), records)
        print(f"Wrote {base.with_suffix('.csv')} ({len(records)} rows)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
