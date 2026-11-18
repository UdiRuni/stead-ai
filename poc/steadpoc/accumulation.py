"""Accumulation for the proposed long-stop cover: many swaps behind one late vessel.

SIMULATED BOOK, ASSUMED LIMITS AND TAIL. NOT A QUOTE. Every swap in the sample book
below is invented. The limits, the tail shape and the net severity share are
assumptions for underwriters to replace. Do not quote outputs as a result.

Why this matters: the long-stop cover pays when the late boxes pass the
long-stop date. All boxes on one vessel arrive together, so every swap waiting
on that vessel passes its long stop on the same slip. Pricing each swap alone
(`longstop.py`) gets the average right but hides the bad year. An event (a port
strike, a canal closure) can hold several vessels at once, which stacks further.

What this module does:

1. Accepts or refuses each new swap against two aggregate limits on the agreed
   value: one per vessel and one per named event. Every refusal has a plain reason.
2. Expected loss of the book: the sum of each swap's pure cost from `longstop.py`.
   Correlation does not change the average.
3. Loss distribution by Monte Carlo, two ways: clustered (one slip per vessel,
   shared by every swap on it, which is physically right) and independent (one
   slip per swap, the naive view). The gap between their 99th percentiles is
   the accumulation the per-swap price does not see.
4. Event stress scenario: an event adds D days to every vessel tagged with it;
   every swap whose margin (long stop minus expected return) is under D pays.
   This is a deterministic scenario, as underwriters run them, not a probability.

Model of the slip, as in `longstop.py`: once a vessel is expected `delay` days
late, the further slip is exponential with the public mean lateness (6.65 days,
Sea-Intelligence, September 2026), stretched by `tail_stretch`. Thin tailed;
real tails are probably fatter. Events are not in the Monte Carlo; they are only
in the stress scenario.
"""
import random
from dataclasses import dataclass, field
from typing import Optional

from .longstop import LongStop

MEAN_LATENESS_DAYS = 6.65   # public figure, September 2026, as in longstop.py


@dataclass(frozen=True)
class Swap:
    swap_id: str
    vessel: str
    agreed_value_usd: float
    expected_delay_days: int          # boxes expected at T + this
    long_stop_day: int = 30           # days after T; assumption
    event: Optional[str] = None       # named disruption behind the delay, if known

    def __post_init__(self):
        if not self.swap_id or not self.vessel:
            raise ValueError("a swap needs an id and a vessel")
        if self.agreed_value_usd <= 0:
            raise ValueError("agreed value must be above zero")
        if self.expected_delay_days < 0:
            raise ValueError("expected delay cannot be negative")
        if self.long_stop_day <= self.expected_delay_days:
            raise ValueError("the long stop must fall after the expected return date")

    @property
    def margin_days(self) -> int:
        """Further slip the boxes can take before they pass the long stop."""
        return self.long_stop_day - self.expected_delay_days


@dataclass(frozen=True)
class Limits:
    per_vessel_usd: float = 3_000_000     # assumption
    per_event_usd: float = 7_500_000      # assumption

    def __post_init__(self):
        if self.per_vessel_usd <= 0 or self.per_event_usd <= 0:
            raise ValueError("limits must be above zero")


@dataclass(frozen=True)
class Decision:
    accepted: bool
    reasons: tuple = ()


@dataclass
class Book:
    limits: Limits = field(default_factory=Limits)
    mean_lateness_days: float = MEAN_LATENESS_DAYS
    tail_stretch: float = 1.0
    net_severity_share: float = 0.15      # assumption, as in longstop.py
    swaps: list = field(default_factory=list)

    def __post_init__(self):
        if self.mean_lateness_days <= 0 or self.tail_stretch <= 0:
            raise ValueError("mean lateness and tail stretch must be above zero")
        if not 0 < self.net_severity_share <= 1:
            raise ValueError("net severity share must be above 0 and at most 1")

    # exposure and acceptance

    def vessel_exposure_usd(self, vessel: str) -> float:
        return sum(s.agreed_value_usd for s in self.swaps if s.vessel == vessel)

    def event_exposure_usd(self, event: str) -> float:
        return sum(s.agreed_value_usd for s in self.swaps if event is not None and s.event == event)

    def check(self, swap: Swap) -> Decision:
        reasons = []
        if any(s.swap_id == swap.swap_id for s in self.swaps):
            reasons.append(f"swap {swap.swap_id} is already in the book")
        same_vessel = [s for s in self.swaps if s.vessel == swap.vessel]
        if same_vessel and same_vessel[0].expected_delay_days != swap.expected_delay_days:
            reasons.append(f"vessel {swap.vessel} is already expected at "
                           f"T+{same_vessel[0].expected_delay_days}, this swap says "
                           f"T+{swap.expected_delay_days}; boxes on one vessel arrive together")
        on_vessel = self.vessel_exposure_usd(swap.vessel) + swap.agreed_value_usd
        if on_vessel > self.limits.per_vessel_usd:
            reasons.append(f"vessel {swap.vessel} would carry ${on_vessel:,.0f}, "
                           f"over the ${self.limits.per_vessel_usd:,.0f} per-vessel limit")
        if swap.event is not None:
            on_event = self.event_exposure_usd(swap.event) + swap.agreed_value_usd
            if on_event > self.limits.per_event_usd:
                reasons.append(f"event {swap.event} would carry ${on_event:,.0f}, "
                               f"over the ${self.limits.per_event_usd:,.0f} per-event limit")
        return Decision(accepted=not reasons, reasons=tuple(reasons))

    def add(self, swap: Swap) -> Decision:
        decision = self.check(swap)
        if decision.accepted:
            self.swaps.append(swap)
        return decision

    # losses

    def _pricing(self, swap: Swap) -> LongStop:
        return LongStop(agreed_value_usd=swap.agreed_value_usd,
                        expected_delay_days=swap.expected_delay_days,
                        long_stop_day=swap.long_stop_day,
                        mean_lateness_days=self.mean_lateness_days,
                        tail_stretch=self.tail_stretch,
                        net_severity_share=self.net_severity_share)

    def net_loss_usd(self, swap: Swap) -> float:
        return swap.agreed_value_usd * self.net_severity_share

    def expected_loss_usd(self) -> float:
        return sum(self._pricing(s).pure_cost_usd for s in self.swaps)

    def vessel_worst_loss_usd(self, vessel: str) -> float:
        """Loss if this vessel slips past every long stop on it."""
        return sum(self.net_loss_usd(s) for s in self.swaps if s.vessel == vessel)

    def event_scenario_loss_usd(self, event: str, added_days: float) -> float:
        """Deterministic stress: the event adds `added_days` to every vessel tagged with it."""
        if added_days < 0:
            raise ValueError("added days cannot be negative")
        return sum(self.net_loss_usd(s) for s in self.swaps
                   if s.event == event and s.margin_days < added_days)

    def simulate(self, trials: int = 20_000, seed: int = 18, clustered: bool = True) -> list:
        """Book loss per trial. Clustered: one slip per vessel. Independent: one per swap."""
        if trials <= 0:
            raise ValueError("trials must be above zero")
        rng = random.Random(seed)
        rate = 1 / (self.mean_lateness_days * self.tail_stretch)
        groups = {}
        for s in self.swaps:
            key = s.vessel if clustered else s.swap_id
            groups.setdefault(key, []).append(s)
        losses = []
        for _ in range(trials):
            total = 0.0
            for members in groups.values():
                slip = rng.expovariate(rate)
                total += sum(self.net_loss_usd(s) for s in members if slip > s.margin_days)
            losses.append(total)
        return losses


def percentile(values: list, q: float) -> float:
    """Nearest-rank percentile, q from 0 to 100."""
    if not values:
        raise ValueError("no values")
    if not 0 <= q <= 100:
        raise ValueError("q must be from 0 to 100")
    ordered = sorted(values)
    rank = max(1, -(-len(ordered) * q // 100))
    return ordered[int(rank) - 1]


def sample_book() -> tuple:
    """An invented book: four vessels, one named event. Returns (book, decisions)."""
    book = Book()
    offers = [
        Swap("S01", "A", 1_200_000, 11, event="port strike"),
        Swap("S02", "A", 900_000, 11, event="port strike"),
        Swap("S03", "A", 800_000, 11, event="port strike"),
        Swap("S04", "A", 600_000, 11, event="port strike"),   # over the vessel limit
        Swap("S05", "B", 1_200_000, 9, event="port strike"),
        Swap("S06", "B", 1_000_000, 9, event="port strike"),
        Swap("S07", "C", 1_200_000, 14, event="port strike"),
        Swap("S08", "C", 1_100_000, 14, event="port strike"),
        Swap("S09", "C", 700_000, 14, event="port strike"),   # over the event limit
        Swap("S10", "D", 1_200_000, 8),
        Swap("S11", "D", 700_000, 10),                        # wrong arrival for D
        Swap("S12", "E", 1_200_000, 12),
    ]
    decisions = [(s, book.add(s)) for s in offers]
    return book, decisions


def report(trials: int = 20_000, seed: int = 18) -> str:
    book, decisions = sample_book()
    lines = [
        "LONG-STOP ACCUMULATION. SIMULATED BOOK, ASSUMED LIMITS AND TAIL. NOT A QUOTE.",
        "Public input: 6.65 days average lateness of late vessel arrivals (September 2026).",
        f"Assumed: per-vessel limit ${book.limits.per_vessel_usd:,.0f}, per-event limit "
        f"${book.limits.per_event_usd:,.0f} (agreed value), net severity "
        f"{book.net_severity_share:.0%}, exponential tail, long stop at T+30.",
        "",
        "Offers, in order",
    ]
    for s, d in decisions:
        tag = f", {s.event}" if s.event else ""
        verdict = "accepted" if d.accepted else "REFUSED: " + "; ".join(d.reasons)
        lines.append(f"  {s.swap_id} vessel {s.vessel}, ${s.agreed_value_usd:,.0f}, T+{s.expected_delay_days}{tag}: {verdict}")
    vessels = sorted({s.vessel for s in book.swaps})
    lines += ["", "Exposure by vessel (agreed value) and loss if that vessel passes every long stop"]
    for v in vessels:
        lines.append(f"  vessel {v}: ${book.vessel_exposure_usd(v):,.0f}, worst loss ${book.vessel_worst_loss_usd(v):,.0f}")
    clustered = book.simulate(trials, seed, clustered=True)
    independent = book.simulate(trials, seed, clustered=False)
    lines += [
        "",
        f"Book: {len(book.swaps)} swaps, ${sum(s.agreed_value_usd for s in book.swaps):,.0f} agreed value",
        f"  expected loss (same either way):        ${book.expected_loss_usd():,.0f}",
        f"  99th percentile, swaps independent:     ${percentile(independent, 99):,.0f}",
        f"  99th percentile, one slip per vessel:   ${percentile(clustered, 99):,.0f}",
        f"  worst trial, one slip per vessel:       ${max(clustered):,.0f}  ({trials:,} trials, seed {seed})",
        "",
        "Event stress: a port strike adds D days to every vessel tagged with it",
    ]
    for d in (7, 17, 22):
        lines.append(f"  D = {d:>2} days: loss ${book.event_scenario_loss_usd('port strike', d):,.0f}")
    lines += ["", "Reading: the average does not move, the bad outcome does. The per-vessel and",
              "per-event limits are what keep one late ship or one strike inside a known",
              "loss. Limits, tail and severity are for underwriters to set."]
    return "\n".join(lines)


if __name__ == "__main__":
    print(report())
