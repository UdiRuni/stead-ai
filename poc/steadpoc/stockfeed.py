"""Stock feed: the CSV a distributor would send us, and a parser that checks it.

A feed is one snapshot of one or more distributors' stock, one lot per row. The
matcher (steadpoc.matching) needs the same producer, producing plant and grade code
at the destination port, free by the original arrival date, so the feed carries
exactly those fields and nothing we do not use. The schema is written up in
poc/STOCK_FEED.md.

Columns (header row required, any order, names in lower case):

    lot_id        the distributor's own reference for the lot, unique in the feed
    distributor   who holds the stock and would lend it
    producer      as on the QA approval, for example SABIC
    plant         producing plant, as on the QA approval, for example Geleen
    grade         grade code, for example PP 575P
    port          the port where the stock sits, for example Rotterdam
    teu           whole TEU in the lot, 0 or more
    available_on  YYYY-MM-DD when the lot is free to release; empty = free now
    snapshot_date YYYY-MM-DD when the feed was taken, the same on every row

Values are compared exactly after trimming spaces: QA approves exact codes, so the
parser never guesses that "pp 575p" means "PP 575P". Lines starting with "#" are
comments. Extra columns are ignored with a warning, so a feed can carry more than
we read.

The parser never stops at the first problem. It returns every error and warning
with its line number, so a distributor can fix a feed in one pass. A feed with any
error yields no lots: we do not match against half a feed.

ILLUSTRATIVE. No distributor sends us a feed today. The format is our proposal, to
be checked with distributors in the Lab's weeks 7 to 8, and the sample feed in
poc/data/sample_stock_feed.csv is invented. Real feeds may count stock in tonnes or
bags, not TEU; that conversion is an open question, not solved here.

Run:  (cd poc && python3 -m steadpoc.stockfeed data/sample_stock_feed.csv)
      (cd poc && python3 -m steadpoc.stockfeed FEED.csv --match-date 2027-02-19)
"""
import argparse
import csv
import io
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from .matching import Lot

REQUIRED = ("lot_id", "distributor", "producer", "plant", "grade", "port", "teu",
            "available_on", "snapshot_date")
OPTIONAL_EMPTY = ("available_on",)     # the only required column that may be blank
MAX_SNAPSHOT_AGE_DAYS = 1              # assumption: older stock may already be sold


@dataclass(frozen=True)
class Problem:
    line: int          # line in the file, 1 = first line; 0 = the feed as a whole
    message: str

    def __str__(self) -> str:
        return f"line {self.line}: {self.message}" if self.line else self.message


@dataclass
class FeedReport:
    lots: list[Lot] = field(default_factory=list)
    snapshot_date: date | None = None
    match_date: date | None = None
    errors: list[Problem] = field(default_factory=list)
    warnings: list[Problem] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


class FeedError(ValueError):
    def __init__(self, report: FeedReport):
        self.report = report
        super().__init__("stock feed rejected: " + "; ".join(str(p) for p in report.errors))


def _date(text: str) -> date:
    if len(text) != 10:
        raise ValueError
    return date.fromisoformat(text)


def _teu(text: str) -> int:
    if not text.isdigit():           # rejects "-1", "2.5", "1e3", " 4" (already trimmed)
        raise ValueError
    return int(text)


def _data_lines(text: str):
    """Yield (line number, line) for lines that are neither blank nor comments."""
    for number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            yield number, line


def parse_feed(text: str, match_date: date | None = None,
               max_age_days: int = MAX_SNAPSHOT_AGE_DAYS) -> FeedReport:
    """Check a feed and turn it into lots.

    days_until_available is counted from match_date, the day we search for stock.
    If match_date is None, the feed is read on its own snapshot date.
    """
    if max_age_days < 0:
        raise ValueError("max_age_days cannot be negative")
    report = FeedReport(match_date=match_date)
    err = lambda line, msg: report.errors.append(Problem(line, msg))
    warn = lambda line, msg: report.warnings.append(Problem(line, msg))

    text = text.lstrip("﻿")      # a byte order mark from spreadsheet exports
    lines = list(_data_lines(text))
    if not lines:
        err(0, "feed is empty: no header row")
        return report
    numbers = [n for n, _ in lines]
    rows = list(csv.reader(io.StringIO("\n".join(line for _, line in lines))))
    if len(rows) != len(lines):
        err(0, "a quoted value runs over more than one line; put each lot on one line")
        return report

    header_line = numbers[0]
    header = [h.strip().lower() for h in rows[0]]
    seen_cols: set[str] = set()
    for col in header:
        if col in seen_cols:
            err(header_line, f"column '{col}' appears twice")
        seen_cols.add(col)
    missing = [c for c in REQUIRED if c not in seen_cols]
    if missing:
        err(header_line, "missing column(s): " + ", ".join(missing))
    extra = [c for c in header if c not in REQUIRED]
    if extra:
        warn(header_line, "ignored column(s): " + ", ".join(c or "(blank)" for c in extra))
    if report.errors:
        return report

    index = {c: header.index(c) for c in REQUIRED}
    lots: list[Lot] = []
    ids: dict[str, int] = {}
    snapshots: dict[date, int] = {}
    parsed: list[tuple[int, dict, date | None]] = []
    for line, row in zip(numbers[1:], rows[1:]):
        if len(row) != len(header):
            err(line, f"has {len(row)} values, the header has {len(header)}")
            continue
        values = {c: row[i].strip() for c, i in index.items()}
        bad = False
        for c in REQUIRED:
            if not values[c] and c not in OPTIONAL_EMPTY:
                err(line, f"'{c}' is empty")
                bad = True
        if bad:
            continue
        try:
            values["teu"] = _teu(values["teu"])
        except ValueError:
            err(line, f"teu '{values['teu']}' is not a whole number of 0 or more")
            bad = True
        snap = available = None
        try:
            snap = _date(values["snapshot_date"])
        except ValueError:
            err(line, f"snapshot_date '{values['snapshot_date']}' is not a date (YYYY-MM-DD)")
            bad = True
        if values["available_on"]:
            try:
                available = _date(values["available_on"])
            except ValueError:
                err(line, f"available_on '{values['available_on']}' is not a date (YYYY-MM-DD)")
                bad = True
        if values["lot_id"] in ids:
            err(line, f"lot_id '{values['lot_id']}' already used on line {ids[values['lot_id']]}")
            bad = True
        else:
            ids[values["lot_id"]] = line
        if bad:
            continue
        snapshots.setdefault(snap, line)
        if values["teu"] == 0:
            warn(line, f"lot '{values['lot_id']}' holds 0 TEU and can never be lent")
        parsed.append((line, values, available))

    if len(snapshots) > 1:
        dates = ", ".join(f"{d.isoformat()} (line {n})" for d, n in sorted(snapshots.items()))
        err(0, f"one feed is one snapshot, but it has several snapshot dates: {dates}")
    if report.errors:
        return report
    if not parsed:
        warn(0, "feed has a header but no lots")
        return report

    snapshot = next(iter(snapshots))
    report.snapshot_date = snapshot
    on = match_date or snapshot
    report.match_date = on
    if snapshot > on:
        err(0, f"feed is dated {snapshot.isoformat()}, after the match date {on.isoformat()}")
        return report
    age = (on - snapshot).days
    if age > max_age_days:
        warn(0, f"feed is {age} days old on the match date; stock may already be sold")

    for line, v, available in parsed:
        days = 0 if available is None else max(0, (available - on).days)
        lots.append(Lot(v["distributor"], v["producer"], v["plant"], v["grade"], v["port"],
                        v["teu"], days, v["lot_id"]))
    report.lots = lots
    return report


def load_feed(path: Path | str, match_date: date | None = None,
              max_age_days: int = MAX_SNAPSHOT_AGE_DAYS) -> FeedReport:
    """Read and check a feed file. Raises FeedError if it has any error."""
    report = parse_feed(Path(path).read_text(encoding="utf-8"), match_date, max_age_days)
    if not report.ok:
        raise FeedError(report)
    return report


def render_report(report: FeedReport, source: str) -> str:
    out = [f"Stock feed {source}: " + ("OK" if report.ok else f"REJECTED, {len(report.errors)} error(s)")]
    if report.ok:
        out.append(f"   snapshot {report.snapshot_date}, read on {report.match_date}, "
                   f"{len(report.lots)} lot(s), {sum(l.teu for l in report.lots)} TEU, "
                   f"{len({l.distributor for l in report.lots})} distributor(s)")
        for lot in report.lots:
            when = "now" if lot.days_until_available == 0 else f"in {lot.days_until_available} days"
            out.append(f"   {lot.lot_id:<10} {lot.distributor:<8} {lot.producer} {lot.grade} "
                       f"({lot.plant}), {lot.port}, {lot.teu} TEU, free {when}")
    out += [f"   error:   {p}" for p in report.errors]
    out += [f"   warning: {p}" for p in report.warnings]
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python3 -m steadpoc.stockfeed",
                                description="Check a distributor stock feed (CSV).")
    p.add_argument("feed", type=Path)
    p.add_argument("--match-date", type=date.fromisoformat,
                   help="day we search for stock, YYYY-MM-DD (default: the feed's snapshot date)")
    args = p.parse_args(argv)
    try:
        text = args.feed.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        print(f"error: cannot read {args.feed}: {exc}", file=sys.stderr)
        return 2
    report = parse_feed(text, args.match_date)
    print(render_report(report, str(args.feed)))
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
