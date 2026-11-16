"""Backtest on public data only: replay the engine month by month.

No mentor, syndicate or purchased data is used. What is real and what is not:

PUBLIC (poc/data/schedule_reliability_monthly.csv, Sea-Intelligence press releases):
  the share of vessel arrivals on time and the average delay of late arrivals,
  per month, global.

SIMULATED (assumptions in steadpoc.simulate.Assumptions):
  every individual shipment and its delay (drawn from an exponential shape around
  the published monthly mean), the plant's safety stock, how early the warning
  comes, and the distributors' stock.

So this shows how the engine's workload would have moved with real market
conditions. It does not show that real alerts would have come in time or that
real stock would have been there. Do not quote its outputs as results.

Run: (cd poc && python3 -m steadpoc.backtest)
"""
import csv
import re
from dataclasses import dataclass, replace
from pathlib import Path

from .simulate import Assumptions, Result, run

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "schedule_reliability_monthly.csv"
REQUIRED = ("month", "on_time_pct", "avg_delay_late_days", "source_url", "retrieved")
_MONTH = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


@dataclass(frozen=True)
class Month:
    month: str                              # data month, YYYY-MM
    on_time_share: float                    # 0 to 1
    mean_lateness_days: float | None        # None when the source does not state it
    source_url: str
    retrieved: str

    @property
    def usable(self) -> bool:
        return self.mean_lateness_days is not None


@dataclass(frozen=True)
class MonthResult:
    month: Month
    result: Result


@dataclass(frozen=True)
class Backtest:
    months: tuple[MonthResult, ...]
    skipped: tuple[Month, ...]              # months without a published mean lateness

    @property
    def total(self) -> Result:
        fields = Result.__dataclass_fields__
        return Result(**{f: sum(getattr(m.result, f) for m in self.months) for f in fields})


def load_months(path: Path = DATA_FILE) -> list[Month]:
    """Read and validate the monthly file. Raises ValueError with the line number."""
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"{path}: missing column(s) {', '.join(missing)}")
        months: list[Month] = []
        for line, row in enumerate(reader, start=2):
            where = f"{path} line {line}"
            month = (row["month"] or "").strip()
            if not _MONTH.match(month):
                raise ValueError(f"{where}: month must be YYYY-MM, got {month!r}")
            try:
                pct = float(row["on_time_pct"])
                raw = (row["avg_delay_late_days"] or "").strip()
                lateness = float(raw) if raw else None
            except (TypeError, ValueError):
                raise ValueError(f"{where}: on_time_pct and avg_delay_late_days must be numbers") from None
            if not 0 <= pct <= 100:
                raise ValueError(f"{where}: on_time_pct must be between 0 and 100")
            if lateness is not None and not lateness > 0:
                raise ValueError(f"{where}: avg_delay_late_days must be positive or empty")
            url = (row["source_url"] or "").strip()
            if not url.startswith("https://"):
                raise ValueError(f"{where}: every row needs an https source_url")
            if not (row["retrieved"] or "").strip():
                raise ValueError(f"{where}: every row needs a retrieval date")
            if months and month <= months[-1].month:
                raise ValueError(f"{where}: months must be unique and in ascending order")
            months.append(Month(month, pct / 100, lateness, url, row["retrieved"].strip()))
    if not months:
        raise ValueError(f"{path}: no data rows")
    return months


def backtest(months: list[Month], base: Assumptions = Assumptions()) -> Backtest:
    """Run the engine once per usable month. Deterministic: each month has its own seed."""
    done, skipped = [], []
    for index, month in enumerate(months):
        if not month.usable:
            skipped.append(month)
            continue
        a = replace(base, on_time_share=month.on_time_share,
                    mean_lateness_days=month.mean_lateness_days, seed=base.seed + index)
        done.append(MonthResult(month, run(a)))
    return Backtest(tuple(done), tuple(skipped))


def report(b: Backtest, base: Assumptions = Assumptions()) -> str:
    lines = [
        "BACKTEST ON PUBLIC DATA ONLY. No mentor, syndicate or purchased data.",
        "Public: monthly on-time share and average delay of late vessel arrivals",
        "(global, Sea-Intelligence press releases). SIMULATED: each shipment, the",
        "safety stock, the warning lead time and the distributor stock.",
        "Assumptions, not evidence. Do not quote as results.",
        "",
        f"{base.shipments} simulated shipments per month",
        "month    on time  late days | late  alerts  in time  swapped  stop days avoided",
    ]
    for m in b.months:
        r = m.result
        lines.append(
            f"{m.month.month}   {100 * m.month.on_time_share:5.1f}%  {m.month.mean_lateness_days:9.2f} |"
            f" {r.late:4d}  {r.alerts:6d}  {r.alerts_in_time:7d}  {r.matched:7d}"
            f"  {r.stoppage_days_avoided:5d} of {r.stoppage_days_at_risk}")
    if not b.months:
        lines.append("(no usable months)")
        return "\n".join(lines)
    t = b.total
    per_1000 = lambda r: 1000 * r.alerts / r.shipments if r.shipments else 0.0
    calm = min(b.months, key=lambda m: per_1000(m.result))
    rough = max(b.months, key=lambda m: per_1000(m.result))
    pct = lambda n, d: f"{100 * n / d:.1f}%" if d else "n/a"
    lines += [
        "",
        f"months replayed:               {len(b.months)} ({b.months[0].month.month} to {b.months[-1].month.month})",
        f"months skipped:                {len(b.skipped)}"
        + (f" ({', '.join(m.month for m in b.skipped)}: average delay not published)" if b.skipped else ""),
        f"shipments simulated:           {t.shipments}",
        f"late:                          {t.late} ({pct(t.late, t.shipments)})",
        f"delay outruns safety stock:    {t.alerts} ({pct(t.alerts, t.late)} of late)",
        f"warned early enough to act:    {t.alerts_in_time} ({pct(t.alerts_in_time, t.alerts)} of alerts)",
        f"identical stock found, swapped: {t.matched} ({pct(t.matched, t.alerts_in_time)} of actionable)",
        f"stoppage days avoided:         {t.stoppage_days_avoided} of {t.stoppage_days_at_risk}",
        f"alerts per 1,000 shipments:    {per_1000(t):.0f} on average, from {per_1000(calm.result):.0f}"
        f" ({calm.month.month}) to {per_1000(rough.result):.0f} ({rough.month.month})",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    print(report(backtest(load_months())))
