"""How often does a resin price fall past the purchase route's break-even?

PUBLIC DATA, A PROXY. `purchase.py` finds that buying the stock outright is cheaper
for the plant than the $68,000 loan unless the price of the extra lot falls more
than about 3% (through stead.ai) or 5% (direct) while it is held. This module sets
those break-evens against a real price series: how often did prices fall that much
over the same holding period?

The series (poc/data/ppi_thermoplastic_resins_monthly.csv):
  US Bureau of Labor Statistics, Producer Price Index by Commodity: Chemicals and
  Allied Products: Thermoplastic Resins and Plastics Materials, series WPU06621201,
  index Dec 2003 = 100, monthly, not seasonally adjusted. Read on FRED,
  https://fred.stlouisfed.org/data/WPU06621201 (last updated there 2026-11-13),
  retrieved 2026-11-28. BLS data are US public domain.

Why it is only a proxy, and which way it leans:
  - It is all thermoplastic resins, not one polypropylene grade.
  - It is US producer prices, not a European distributor's spot price.
  - A monthly index averages contract and list prices across many products. A single
    grade's spot price swings more, so this series UNDERSTATES how often a plant
    would lose 3% or 5% on its extra lot. Read the shares below as a floor.
  - Month-on-month index changes stand in for a 30-day holding period.

No polypropylene-only public series that may be stored in the repo was found on
2026-11-28. Replace this file with one if a source gives it.

Run `(cd poc && python3 -m steadpoc.pricemoves)`. Output is arithmetic on a public
proxy series, set against assumed break-evens. It is not a forecast.
"""
import argparse
import csv
import math
from dataclasses import dataclass
from pathlib import Path

from .purchase import PurchaseCase

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "ppi_thermoplastic_resins_monthly.csv"
SERIES_LABEL = ("BLS PPI WPU06621201, thermoplastic resins and plastics materials, US, "
                "monthly, not seasonally adjusted (via FRED, retrieved 2026-11-28)")
DAYS_PER_MONTH = 365 / 12
MAX_LISTED = 8      # periods named per line in the report


@dataclass(frozen=True)
class Point:
    month: str      # "YYYY-MM"
    value: float


@dataclass(frozen=True)
class Move:
    start: str
    end: str
    change: float   # -0.05 = a 5% fall from start to end


def _month_index(month: str) -> int:
    """'YYYY-MM' to a running month number; raises ValueError on a bad month."""
    parts = month.split("-")
    if len(parts) != 2 or len(parts[0]) != 4 or len(parts[1]) != 2:
        raise ValueError(f"month must be YYYY-MM: {month!r}")
    year, mon = int(parts[0]), int(parts[1])
    if not 1 <= mon <= 12:
        raise ValueError(f"month must be 01 to 12: {month!r}")
    return year * 12 + mon - 1


def validate(points) -> list:
    """Return the points if they are a clean monthly series, else raise ValueError
    listing every problem: bad month, value not above 0, duplicate, out of order,
    or a missing month. Gaps are never filled."""
    points = list(points)
    problems = []
    if len(points) < 2:
        problems.append("need at least two months")
    prev = None
    seen = set()
    for i, p in enumerate(points):
        try:
            idx = _month_index(p.month)
        except ValueError as e:
            problems.append(f"row {i + 1}: {e}")
            prev = None
            continue
        if not (isinstance(p.value, (int, float)) and math.isfinite(p.value) and p.value > 0):
            problems.append(f"row {i + 1} ({p.month}): value must be a number above 0")
        if p.month in seen:
            problems.append(f"row {i + 1}: duplicate month {p.month}")
        seen.add(p.month)
        if prev is not None:
            if idx <= prev:
                problems.append(f"row {i + 1} ({p.month}): out of order")
            elif idx != prev + 1:
                problems.append(f"row {i + 1} ({p.month}): {idx - prev - 1} month(s) missing before it")
        prev = idx
    if problems:
        raise ValueError("price series rejected: " + "; ".join(problems))
    return points


def load_series(path: Path = DATA_FILE) -> list:
    rows = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or not {"month", "index"} <= set(reader.fieldnames):
            raise ValueError("price series needs columns 'month' and 'index'")
        for n, r in enumerate(reader, start=2):
            try:
                value = float(r["index"])
            except (TypeError, ValueError):
                raise ValueError(f"line {n}: index is not a number: {r['index']!r}")
            rows.append(Point((r["month"] or "").strip(), value))
    return validate(rows)


def months_for_days(days: int) -> int:
    """Holding days to whole months of the series, at least one."""
    if days < 0:
        raise ValueError("holding days cannot be negative")
    return max(1, round(days / DAYS_PER_MONTH))


def moves(points, months: int = 1) -> list:
    """Every overlapping change over `months` months, start to end."""
    if months < 1:
        raise ValueError("months must be at least 1")
    points = validate(points)
    return [Move(points[i].month, points[i + months].month,
                 points[i + months].value / points[i].value - 1)
            for i in range(len(points) - months)]


def falls_beyond(ms, threshold: float) -> list:
    """Moves that fell by MORE than `threshold` (0.03 = a fall of over 3%).

    A threshold of 0 or less means the loan is cheaper with no fall at all, so
    every move counts. None (no break-even) means no move counts."""
    if threshold is None:
        return []
    return [m for m in ms if m.change < -threshold]


def share(part, whole) -> float:
    return len(part) / len(whole) if whole else 0.0


@dataclass(frozen=True)
class Breakeven:
    label: str
    fall: float     # price fall at which the loan becomes cheaper


def breakevens(hold_days: int = 30) -> list:
    """The two break-evens from purchase.py: through stead.ai and direct."""
    through = PurchaseCase(extra_holding_days=hold_days)
    direct = PurchaseCase(extra_holding_days=hold_days, purchase_fee_rate=0.0)
    return [Breakeven("through stead.ai", through.breakeven_price_fall),
            Breakeven("direct", direct.breakeven_price_fall)]


def _pct(x: float) -> str:
    return f"{x:+.1%}"


def report(points, hold_days: int = 30) -> str:
    months = months_for_days(hold_days)
    ms = moves(points, months)
    worst = min(ms, key=lambda m: m.change)
    best = max(ms, key=lambda m: m.change)
    lines = [
        "RESIN PRICE MOVES AGAINST THE PURCHASE BREAK-EVEN. Public proxy series; "
        "break-evens are assumptions.",
        f"Series: {SERIES_LABEL}.",
        f"Window: {points[0].month} to {points[-1].month}, {len(points)} months.",
        f"Holding period: {hold_days} days, read as {months} month(s) of the series; "
        f"{len(ms)} overlapping periods.",
        "",
        f"Largest fall: {_pct(worst.change)} ({worst.start} to {worst.end}). "
        f"Largest rise: {_pct(best.change)} ({best.start} to {best.end}).",
        "",
        "Periods in which the price fell past the break-even (loan cheaper than buying):",
    ]
    for b in breakevens(hold_days):
        hit = falls_beyond(ms, b.fall)
        when = ", ".join(f"{m.start}>{m.end} {_pct(m.change)}" for m in hit[:MAX_LISTED]) or "none"
        if len(hit) > MAX_LISTED:
            when += f", and {len(hit) - MAX_LISTED} more"
        lines.append(f"  {b.label}: fall over {b.fall:.1%}: {len(hit)} of {len(ms)} "
                     f"({share(hit, ms):.0%}). {when}")
    lines += [
        "",
        "Read with care: an index of all thermoplastic resins moves less than one grade's",
        "spot price, so these shares are a floor, not an estimate. Not a forecast.",
    ]
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--file", type=Path, default=DATA_FILE)
    ap.add_argument("--hold-days", type=int, default=30)
    a = ap.parse_args(argv)
    print(report(load_series(a.file), a.hold_days))


if __name__ == "__main__":
    main()
