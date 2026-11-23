"""Demo: one swap, start to finish, on the worked case of the deck and the brief.

ETA updates come in, the alert fires when the delay outruns the plant's stock, the
matcher looks for identical stock at the destination port, and a one-page term
sheet says who lends what, when, and what each party is paid.

ILLUSTRATIVE. The ETA updates and the distributor stock below are invented for
the demo. The money comes from steadpoc.economics.SwapCase, which is the worked
case published in the deck and the brief: assumptions, not data. The long-stop
cover is proposed, its premium is a placeholder, and no insurer is committed.

The term sheet also shows the long-stop date, the pricing method from
steadpoc.longstop (an estimate on assumptions, shown beside the placeholder,
never in the total) and the per-vessel limit check from steadpoc.accumulation.
The long-stop date, the limit, the vessel and any other exposure on it are
assumptions for underwriters to set.

Run:  (cd poc && python3 -m steadpoc.demo)
      (cd poc && python3 -m steadpoc.demo --html out/demo.html)
      (cd poc && python3 -m steadpoc.demo --delay 4)          no alert
      (cd poc && python3 -m steadpoc.demo --arrival 2027-03-01)  calendar dates
      (cd poc && python3 -m steadpoc.demo --long-stop 21)     earlier long stop
      (cd poc && python3 -m steadpoc.demo --vessel-exposure 2500000)  vessel limit full
      (cd poc && python3 -m steadpoc.demo --stock-feed data/sample_stock_feed.csv)
                                              stock read from a feed file (steadpoc.stockfeed)
      (cd poc && python3 -m steadpoc.demo --no-cash)          purchase route blocked
      (cd poc && python3 -m steadpoc.demo --price-change -0.05 --hold-days 60)

The term sheet also sets the loan against buying the same lots outright
(steadpoc.purchase): cost to the plant, what stead.ai earns, and when the loan wins.
Every purchase input (8% a year cost of capital, 30 days held, own room, no spot
premium, no price move, 2% fee) is an assumption, not data.
"""
import argparse
import sys
from dataclasses import dataclass, replace
from datetime import date, timedelta
from html import escape
from pathlib import Path

from .accumulation import Book, Decision, Limits, Swap
from .economics import SwapCase
from .longstop import LongStop
from .purchase import PURCHASE, PurchaseCase
from .matching import Lot, Match, Need, find_match, why_not
from .stockfeed import FeedError, load_feed
from .warning import Alert, EtaUpdate, evaluate

BANNER = "ILLUSTRATIVE CASE: assumptions, not data. Not an offer of insurance."
NO_CAPACITY = ("The long-stop cover is proposed. Its premium is a placeholder, not a price. "
               "No Lloyd's capacity, insurer, distributor or customer is committed today.")
BOOKING = "BK-DEMO-001"
TEMPORARY_STORAGE_LIMIT_DAYS = 90     # customs limit quoted in the brief
VESSEL = "MV DEMO"                    # invented vessel carrying the late boxes
LONG_STOP_DAY = LongStop().long_stop_day   # T+30, assumption, as in longstop.py


@dataclass(frozen=True)
class Cover:
    """The long-stop terms and the accumulation check for one swap. Assumptions."""
    pricing: LongStop
    vessel: str
    limits: Limits
    other_on_vessel_usd: float        # agreed value of other swaps already on the vessel
    decision: Decision

    @property
    def on_vessel_usd(self) -> float:
        return self.other_on_vessel_usd + self.pricing.agreed_value_usd


def cover_for(case: SwapCase, long_stop_day: int = LONG_STOP_DAY, vessel: str = VESSEL,
              limits: Limits = Limits(), other_on_vessel_usd: float = 0.0) -> Cover:
    """Price the long stop and check the per-vessel limit. Raises ValueError if the
    long stop does not fall after the expected return, or inputs are negative."""
    if other_on_vessel_usd < 0:
        raise ValueError("other exposure on the vessel cannot be negative")
    pricing = LongStop(agreed_value_usd=case.notional_usd, expected_delay_days=case.delay_days,
                       long_stop_day=long_stop_day)
    book = Book(limits=limits)
    if other_on_vessel_usd > 0:
        # the swaps already on this vessel wait for the same boxes' arrival
        book.swaps.append(Swap("OTHER", vessel, other_on_vessel_usd, case.delay_days, long_stop_day))
    swap = Swap(BOOKING, vessel, case.notional_usd, case.delay_days, long_stop_day)
    return Cover(pricing, vessel, limits, other_on_vessel_usd, book.check(swap))


@dataclass(frozen=True)
class Schedule:
    """Days relative to T, the late shipment's scheduled arrival. From the brief."""
    alert: int = -12
    match: int = -10
    bind: int = -8

    def __post_init__(self):
        if not self.alert <= self.match <= self.bind <= 0:
            raise ValueError("schedule must run alert, match, bind, then release at T")


@dataclass(frozen=True)
class Feed:
    """One ETA update as the tracking provider would send it, plus a note for the screen."""
    update: EtaUpdate
    note: str


@dataclass(frozen=True)
class Step:
    feed: Feed
    alert: Alert | None


@dataclass(frozen=True)
class LotVerdict:
    lot: Lot
    verdict: str            # "chosen", "fits, not chosen" or the reason it does not fit


@dataclass(frozen=True)
class TermSheet:
    booking: str
    lender: str
    goods: str
    port: str
    teu: int
    lots: tuple[Lot, ...]
    case: SwapCase
    schedule: Schedule
    cover: Cover
    purchase: PurchaseCase | None = None    # the same lots bought outright; assumptions

    @property
    def return_day(self) -> int:
        return self.case.delay_days


@dataclass(frozen=True)
class Demo:
    case: SwapCase
    schedule: Schedule
    need: Need
    steps: tuple[Step, ...]
    alert: Alert | None
    verdicts: tuple[LotVerdict, ...]
    match: Match | None
    term_sheet: TermSheet | None
    outcome: str
    arrival: date | None = None


NEED_GOODS = ("SABIC", "Geleen", "PP 575P", "Rotterdam")


def demo_feed(case: SwapCase, schedule: Schedule) -> tuple[Feed, ...]:
    """Three invented ETA updates that end at the case's delay, known at the alert day."""
    lead = -schedule.alert
    early, mid = min(2, case.delay_days), min(4, case.delay_days)
    return (
        Feed(EtaUpdate(BOOKING, lead + 8, early), "congestion at the transhipment port"),
        Feed(EtaUpdate(BOOKING, lead + 3, mid), "vessel leaves the transhipment port late"),
        Feed(EtaUpdate(BOOKING, lead, case.delay_days), "boxes rolled to a later ship"),
    )


def demo_stock() -> list[Lot]:
    """Invented distributor stock: one clean match and the near misses a matcher must refuse."""
    producer, plant, grade, port = NEED_GOODS
    return [
        Lot("Hub A", producer, plant, "PP 571P", port, 40),
        Lot("Hub A", producer, plant, grade, "Antwerp", 40),
        Lot("Hub B", producer, plant, grade, port, 40),
        Lot("Hub C", producer, "Al Jubail", grade, port, 40),
        Lot("Hub C", producer, plant, grade, port, 20),
        Lot("Hub D", producer, plant, grade, port, 20),
        Lot("Hub D", producer, plant, grade, port, 40, days_until_available=14),
    ]


def _verdict(lot: Lot, need: Need, match: Match | None, stock: list[Lot]) -> str:
    reason = why_not(lot, need)
    if reason:
        return reason
    if match and any(lot is chosen for chosen in match.lots):
        return "chosen"
    if match and lot.distributor == match.distributor:
        return "fits, not needed"
    held = sum(l.teu for l in stock if l.distributor == lot.distributor and why_not(l, need) is None)
    if held < need.teu:
        return "too small alone; lots are never combined across distributors"
    return "fits; another distributor covers the need in as few or fewer lots"


def build_demo(case: SwapCase = SwapCase(), schedule: Schedule = Schedule(),
               stock: list[Lot] | None = None, feed: tuple[Feed, ...] | None = None,
               arrival: date | None = None, long_stop_day: int = LONG_STOP_DAY,
               limits: Limits = Limits(), other_on_vessel_usd: float = 0.0,
               purchase: PurchaseCase | None = None) -> Demo:
    """`purchase` holds the purchase-route assumptions; its `swap` is always replaced
    by `case`, so both routes price the same shipment."""
    if case.delay_days < 0 or case.safety_stock_days < 0:
        raise ValueError("delay_days and safety_stock_days must be non-negative")
    if case.teu <= 0:
        raise ValueError("teu must be positive")
    if long_stop_day <= 0:
        raise ValueError("the long-stop date must fall after T")
    if other_on_vessel_usd < 0:
        raise ValueError("other exposure on the vessel cannot be negative")
    stock = demo_stock() if stock is None else stock
    feed = demo_feed(case, schedule) if feed is None else feed
    producer, plant, grade, port = NEED_GOODS
    # the match is made at schedule.match, so stock must be free within that many days
    need = Need(producer, plant, grade, port, case.teu, days_until_needed=-schedule.match)

    steps, alert = [], None
    for item in feed:
        found = evaluate(item.update, case.safety_stock_days)
        steps.append(Step(item, found))
        if found is not None:
            alert = found
            break                      # the first alert starts the search; later updates wait

    def done(outcome, verdicts=(), match=None, sheet=None):
        return Demo(case, schedule, need, tuple(steps), alert, tuple(verdicts), match, sheet,
                    outcome, arrival)

    if alert is None:
        return done("No alert: the plant's stock covers the delay, so nothing is offered.")
    if alert.lead_days < -schedule.bind:
        return done(f"Alert came {alert.lead_days} days before arrival, too late to bind a swap "
                    f"by T{schedule.bind}. No swap is offered.")
    match = find_match(need, stock)
    verdicts = [LotVerdict(lot, _verdict(lot, need, match, stock)) for lot in stock]
    if match is None:
        return done("No swap: no single distributor holds enough identical stock at the port "
                    "in time. The plant is told at once, with the days left to act.", verdicts)
    if not case.swap_is_worth_it:
        return done("No swap: it would cost more than the stoppage it avoids.", verdicts, match)
    if long_stop_day <= case.delay_days:
        return done(f"No swap: the late boxes are expected at T+{case.delay_days}, on or after the "
                    f"long-stop date T+{long_stop_day}, so the return leg cannot be covered.",
                    verdicts, match)
    cover = cover_for(case, long_stop_day, VESSEL, limits, other_on_vessel_usd)
    if not cover.decision.accepted:
        return done("No swap: " + "; ".join(cover.decision.reasons) + ". The assumed limit is "
                    "full, so the cover could not be bound.", verdicts, match)
    purchase = replace(purchase or PurchaseCase(), swap=case)
    sheet = TermSheet(BOOKING, match.distributor, f"{producer} {grade}, produced at {plant}",
                      port, case.teu, match.lots, case, schedule, cover, purchase)
    return done("Swap offered: the term sheet below goes to the plant, the distributor and "
                "the underwriter.", verdicts, match, sheet)


# ---------- rendering ----------

def usd(amount: float) -> str:
    return f"${amount:,.0f}"


def day(offset: int, arrival: date | None = None) -> str:
    label = "T" if offset == 0 else f"T{offset:+d}"
    if arrival is None:
        return label
    return f"{label} ({(arrival + timedelta(days=offset)).strftime('%d %b %Y')})"


def _days(n: int) -> str:
    return f"{n} day" if n == 1 else f"{n} days"


def _when_loan_wins(p: PurchaseCase) -> str:
    """Plain list of the break-evens, other inputs held."""
    if p.purchase_blockers:
        return "Here: buying is not possible"
    if p.cheaper_route != PURCHASE:
        fall = p.breakeven_price_fall
        why = (f"the price fall of {-p.price_change:.1%} passes the {fall:.1%} break-even"
               if p.price_change < 0 and fall > 0 else "even with no price move")
        return f"Here, on these assumptions: {why}"
    parts = [f"the price of the extra lot falls more than {p.breakeven_price_fall:.1%} while held"]
    hold = p.breakeven_holding_days
    if hold is not None:
        parts.append(f"it is held longer than {hold:,.0f} days")
    store = p.breakeven_storage_usd_per_teu_day
    if store is not None:
        parts.append(f"outside storage costs more than {usd(store)} per TEU per day")
    parts.append("the plant has no cash or no room for double stock")
    return "If " + ", or ".join(parts) + " (other inputs held)"


def purchase_rows(p: PurchaseCase) -> list[tuple[str, str]]:
    """Rows comparing the loan with buying the same lots outright. Assumptions."""
    if p.swap.downtime_days == 0:
        return [("Route", "No action needed: the plant's stock covers the delay")]
    move = (usd(p.price_loss_usd) if p.price_loss_usd >= 0
            else f"a gain of {usd(-p.price_loss_usd)}")
    total = (usd(p.purchase_cost_usd) if p.purchase_cost_usd >= 0
             else f"A net gain of {usd(-p.purchase_cost_usd)}")
    cost = (f"{total}: capital on the extra lot at "
            f"{p.cost_of_capital:.0%} a year for {_days(p.extra_holding_days)} ({usd(p.capital_usd)}), "
            f"storage {usd(p.storage_usd)}, spot premium {usd(p.spot_premium_usd)}, "
            f"price move {move}, stead.ai fee {p.purchase_fee_rate:.1%} "
            f"({usd(p.purchase_fee_usd)}). All assumptions")
    if p.purchase_blockers:
        verdict = "Not possible: " + "; ".join(p.purchase_blockers) + ". The loan is the route"
    elif p.cheaper_route == PURCHASE:
        verdict = (f"Buying is cheaper than the {usd(p.loan_cost_usd)} loan on these assumptions; "
                   f"the plant keeps the late boxes as stock and takes the price risk on them")
    else:
        verdict = (f"The {usd(p.loan_cost_usd)} loan is cheaper on these assumptions; "
                   f"buying would cost {usd(p.purchase_cost_usd - p.loan_cost_usd)} more")
    return [
        ("Same lots, bought", "The plant buys the lots and keeps the late boxes as stock; no loan, no long stop"),
        ("Cost to the plant", cost),
        ("Against the loan", verdict),
        ("The loan wins", _when_loan_wins(p)),
        ("stead.ai earns", f"{usd(p.stead_on_loan_usd)} on the loan, {usd(p.stead_on_purchase_usd)} on the purchase"),
    ]


def term_sheet_rows(sheet: TermSheet, arrival: date | None = None) -> list[tuple[str, list[tuple[str, str]]]]:
    """The term sheet as sections of (label, value) rows; text and HTML both render this."""
    c, s, cv = sheet.case, sheet.schedule, sheet.cover
    ls = cv.pricing
    lots = "; ".join(f"{lot.teu} TEU, " + ("in bond at the port now" if lot.days_until_available == 0
                     else f"free in {lot.days_until_available} days") for lot in sheet.lots)
    return [
        ("Parties", [
            ("Lender", f"{sheet.lender}, a distributor holding bonded stock in {sheet.port}"),
            ("Borrower", "The insured plant. It stays consignee on the late shipment"),
            ("Long-stop cover", "Proposed. No insurer is committed"),
            ("Arranger", "stead.ai, which would act under a broker or coverholder"),
        ]),
        ("Goods", [
            ("Stock lent", f"{sheet.teu} TEU of {sheet.goods}"),
            ("Repaid with", f"The late shipment, booking {sheet.booking}: same producer, plant and grade code"),
            ("Value", f"{usd(c.notional_usd)} (assumption)"),
            ("Lots", lots),
        ]),
        ("Dates (T is the late shipment's scheduled arrival)", [
            ("Alert", f"{day(s.alert, arrival)}: delay of {c.delay_days} days against "
                      f"{c.safety_stock_days} days of stock"),
            ("Match", day(s.match, arrival)),
            ("Swap bound", day(s.bind, arrival)),
            ("Stock released", f"{day(0, arrival)}: the plant clears it in its own name and pays duty and VAT once"),
            ("Loan repaid", f"{day(sheet.return_day, arrival)}: the late boxes go to the lender's customs "
                            f"warehouse under customs transit (T1), not cleared by the plant"),
            ("Loan length", f"{c.loan_days} days"),
            ("Long-stop date", f"{day(ls.long_stop_day, arrival)}: {_days(ls.long_stop_day - sheet.return_day)} "
                               f"after the expected return (assumption, to be set with underwriters)"),
        ]),
        ("Cost of the swap", [
            ("Lender's yield", f"{usd(c.lender_yield_usd)}, about {c.lender_annualized_yield:.0%} "
                               f"annualized (simple, on {c.loan_days} days)"),
            ("Long-stop premium", f"{usd(c.premium_usd)}, PLACEHOLDER, not yet priced"),
            ("Method estimate", f"{usd(ls.premium_usd)}: {ls.chance_of_passing:.1%} chance the boxes pass "
                                f"the long stop x {usd(ls.net_loss_usd)} net loss "
                                f"({ls.net_severity_share:.0%} of value) / {ls.target_loss_ratio:.0%} loss ratio. "
                                f"Assumptions, not a quote; not in the total"),
            ("stead.ai fee", f"{usd(c.fee_usd)}, {c.fee_rate:.1%} of value"),
            ("Total", usd(c.swap_cost_usd)),
        ]),
        ("Against the alternatives", [
            ("No action", f"Line stops {c.downtime_days} days: {usd(c.stoppage_cost_usd)} at "
                          f"{usd(c.downtime_cost_per_day_usd)} a day (assumption)"),
            ("Partial air freight", f"{usd(c.air_bridge_usd)} (assumption), moves only part of the stock"),
            ("Swap", f"Line stops 0 days: {usd(c.swap_cost_usd)}, "
                     f"{c.loss_reduction_vs(c.air_bridge_usd):.0%} to "
                     f"{c.loss_reduction_vs(c.stoppage_cost_usd):.0%} below the two rows above"),
        ]),
    ] + ([("Or the plant buys the stock outright (assumptions)", purchase_rows(sheet.purchase))]
         if sheet.purchase is not None else []) + [
        ("What makes the return leg safe", [
            ("Boxes lost", "Existing cover: the plant's cargo policy, with the lender named loss payee"),
            ("General Average", "Existing practice: the plant's cargo insurer issues the average guarantee"),
            ("Boxes far later", "New and proposed: pays an agreed value if the late boxes pass the long-stop date"),
            ("Vessel limit", f"{usd(cv.on_vessel_usd)} on {cv.vessel} with this swap, within the "
                             f"{usd(cv.limits.per_vessel_usd)} per-vessel limit (assumption)"),
            ("Customs", f"The late boxes may wait up to {TEMPORARY_STORAGE_LIMIT_DAYS} days in temporary "
                        f"storage before the T1 move; duty and VAT stay suspended"),
            ("Not covered", "Plant default is credit risk: it needs a pledge over the late cargo or trade credit cover"),
        ]),
    ]


def _lot_line(v: LotVerdict) -> tuple[str, str, str, str]:
    lot = v.lot
    when = "now" if lot.days_until_available == 0 else f"in {lot.days_until_available} days"
    return (lot.distributor, f"{lot.producer} {lot.grade} ({lot.plant}), {lot.port}",
            f"{lot.teu} TEU, {when}", v.verdict)


def _step_line(step: Step, d: Demo) -> tuple[str, str, str]:
    u = step.feed.update
    if step.alert:
        verdict = f"ALERT: line would stop {step.alert.stockout_days} days"
    else:
        verdict = f"no alert: {d.case.safety_stock_days} days of stock cover it"
    return (day(-u.days_before_scheduled_arrival, d.arrival),
            f"ETA now {u.delay_days} days late ({step.feed.note})", verdict)


def render_text(d: Demo) -> str:
    c = d.case
    out = [BANNER, "",
           f"stead.ai demo: one stock swap, booking {BOOKING}",
           f"{c.teu} TEU of {d.need.producer} {d.need.grade} arriving at {d.need.port}. "
           f"The plant holds {c.safety_stock_days} days of stock.", "",
           "1. EARLY WARNING (tracking is bought in; we only decide when a change matters)"]
    for step in d.steps:
        when, what, verdict = _step_line(step, d)
        out.append(f"   {when:<6} {what}")
        out.append(f"          -> {verdict}")
    if d.verdicts:
        out += ["", f"2. MATCH: {d.need.teu} TEU, same producer, plant and grade code, in "
                    f"{d.need.port}, free within {d.need.days_until_needed} days, one distributor"]
        for v in d.verdicts:
            who, what, size, verdict = _lot_line(v)
            out.append(f"   {who:<6} {what:<38} {size:<19} {verdict}")
    out += ["", f"RESULT: {d.outcome}"]
    if d.term_sheet:
        out += ["", "3. TERM SHEET", "=" * 78]
        for title, rows in term_sheet_rows(d.term_sheet, d.arrival):
            out.append(title.upper())
            out += [f"   {label:<20} {value}" for label, value in rows]
            out.append("")
        out.append("=" * 78)
    out += ["", NO_CAPACITY]
    return "\n".join(out)


_CSS = """
body{font:15px/1.45 -apple-system,Segoe UI,Helvetica,Arial,sans-serif;color:#16233a;background:#f4f5f7;margin:0;padding:24px}
main{max-width:860px;margin:0 auto}
.banner{background:#fff4e5;border:1px solid #e8a23d;color:#6b4300;padding:8px 12px;border-radius:6px;font-weight:600}
h1{font-size:24px;margin:18px 0 4px} h2{font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:#c2570c;margin:26px 0 8px}
h3{font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:#5b6780;margin:16px 0 4px}
table{border-collapse:collapse;width:100%;background:#fff} td,th{padding:6px 10px;border-bottom:1px solid #e3e6ec;text-align:left;vertical-align:top}
th{font-size:12px;color:#5b6780} .alert td{background:#fdecea;font-weight:600} .chosen td{background:#e8f5ec;font-weight:600}
.result{background:#16233a;color:#fff;padding:10px 14px;border-radius:6px;margin-top:18px}
.sheet{background:#fff;border:1px solid #cfd5e0;border-radius:8px;padding:6px 20px 16px;margin-top:10px}
.sheet td:first-child{width:170px;color:#5b6780} .total td{font-weight:700;border-top:2px solid #16233a}
.foot{font-size:13px;color:#5b6780;margin-top:18px}
@media print{body{background:#fff;padding:0}.sheet{break-before:page;border:0}}
"""


def render_html(d: Demo) -> str:
    """One self-contained page: no scripts, no external files."""
    e, c = escape, d.case
    h = ["<!doctype html>", '<html lang="en"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width,initial-scale=1">',
         "<title>stead.ai demo: one stock swap</title>", f"<style>{_CSS}</style></head><body><main>",
         f'<p class="banner">{e(BANNER)}</p>',
         f"<h1>One stock swap, booking {e(BOOKING)}</h1>",
         f"<p>{c.teu} TEU of {e(d.need.producer)} {e(d.need.grade)} arriving at "
         f"{e(d.need.port)}. The plant holds {c.safety_stock_days} days of stock.</p>",
         "<h2>1. Early warning</h2>",
         "<table><tr><th>Day</th><th>ETA update</th><th>Decision</th></tr>"]
    for step in d.steps:
        cls = ' class="alert"' if step.alert else ""
        h.append(f"<tr{cls}>" + "".join(f"<td>{e(x)}</td>" for x in _step_line(step, d)) + "</tr>")
    h.append("</table>")
    if d.verdicts:
        h += [f"<h2>2. Match</h2><p>Needed: {d.need.teu} TEU, same producer, plant and grade code, in "
              f"{e(d.need.port)}, free within {d.need.days_until_needed} days, from one distributor.</p>",
              "<table><tr><th>Distributor</th><th>Stock</th><th>Size, free</th><th>Verdict</th></tr>"]
        for v in d.verdicts:
            cls = ' class="chosen"' if v.verdict == "chosen" else ""
            h.append(f"<tr{cls}>" + "".join(f"<td>{e(x)}</td>" for x in _lot_line(v)) + "</tr>")
        h.append("</table>")
    h.append(f'<p class="result">{e(d.outcome)}</p>')
    if d.term_sheet:
        h.append('<h2>3. Term sheet</h2><div class="sheet">')
        for title, rows in term_sheet_rows(d.term_sheet, d.arrival):
            h.append(f"<h3>{e(title)}</h3><table>")
            for label, value in rows:
                cls = ' class="total"' if label == "Total" else ""
                h.append(f"<tr{cls}><td>{e(label)}</td><td>{e(value)}</td></tr>")
            h.append("</table>")
        h.append("</div>")
    h.append(f'<p class="foot">{e(NO_CAPACITY)}</p></main></body></html>')
    return "\n".join(h)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python3 -m steadpoc.demo", description="Walk one stock swap on screen.")
    p.add_argument("--delay", type=int, help="days late (default: the worked case, 11)")
    p.add_argument("--stock-days", type=int, help="plant safety stock in days (default: 5)")
    p.add_argument("--arrival", type=date.fromisoformat, help="scheduled arrival, YYYY-MM-DD, to show calendar dates")
    p.add_argument("--long-stop", type=int, default=LONG_STOP_DAY,
                   help=f"long-stop date in days after T (default: {LONG_STOP_DAY}, an assumption)")
    p.add_argument("--vessel-exposure", type=float, default=0.0,
                   help="agreed value of other swaps already on the same vessel, USD (default: 0)")
    p.add_argument("--stock-feed", type=Path,
                   help="read distributor stock from this CSV (format: poc/STOCK_FEED.md); "
                        "days are counted from the match day, T-10 of --arrival, else the feed's snapshot date")
    p.add_argument("--hold-days", type=int, default=30,
                   help="purchase route: days the extra lot is held (default: 30, an assumption)")
    p.add_argument("--price-change", type=float, default=0.0,
                   help="purchase route: price move on the extra lot while held, -0.05 is a 5%% fall (default: 0)")
    p.add_argument("--storage", type=float, default=0.0,
                   help="purchase route: outside storage, USD per TEU per day (default: 0, own room)")
    p.add_argument("--no-cash", action="store_true", help="purchase route: the plant has no cash or credit for it")
    p.add_argument("--no-room", action="store_true", help="purchase route: the plant has no room for double stock")
    p.add_argument("--html", type=Path, help="also write a self-contained HTML page to this path")
    args = p.parse_args(argv)
    case = SwapCase()
    if args.delay is not None:
        case = replace(case, delay_days=args.delay)
    if args.stock_days is not None:
        case = replace(case, safety_stock_days=args.stock_days)
    stock, feed_note = None, None
    if args.stock_feed:
        match_date = args.arrival + timedelta(days=Schedule().match) if args.arrival else None
        try:
            report = load_feed(args.stock_feed, match_date)
        except FeedError as err:
            print(f"error: {args.stock_feed}:", file=sys.stderr)
            for problem in err.report.errors:
                print(f"   {problem}", file=sys.stderr)
            return 2
        except (OSError, UnicodeDecodeError) as err:
            print(f"error: cannot read {args.stock_feed}: {err}", file=sys.stderr)
            return 2
        for problem in report.warnings:
            print(f"warning: {args.stock_feed}: {problem}", file=sys.stderr)
        stock = report.lots
        feed_note = (f"Stock read from {args.stock_feed} (snapshot {report.snapshot_date}, "
                     f"counted from {report.match_date}, {len(stock)} lots).")
    try:
        purchase = PurchaseCase(swap=case, extra_holding_days=args.hold_days,
                                price_change=args.price_change, storage_usd_per_teu_day=args.storage,
                                has_cash=not args.no_cash, has_room=not args.no_room)
        demo = build_demo(case, stock=stock, arrival=args.arrival, long_stop_day=args.long_stop,
                          other_on_vessel_usd=args.vessel_exposure, purchase=purchase)
    except ValueError as err:
        print(f"error: {err}", file=sys.stderr)
        return 2
    print(render_text(demo))
    if feed_note:
        print(feed_note)
    if args.html:
        args.html.parent.mkdir(parents=True, exist_ok=True)
        args.html.write_text(render_html(demo), encoding="utf-8")
        print(f"\nHTML page written to {args.html}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
