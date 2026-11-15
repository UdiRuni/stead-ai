"""Synthetic end-to-end run: shipments, delays, alerts, matches, swaps.

SIMULATED DATA. The delay model borrows two public figures (56.4% of vessels on
time and 6.06 days average lateness of late vessels, Sea-Intelligence, July
2026). Everything else (safety stock, warning lead time, distributor stock
depth, downtime cost) is an assumption that the Lab backtest and customer
interviews are meant to replace. Do not quote outputs of this module as results.
"""
import random
from dataclasses import dataclass

from .economics import SwapCase
from .matching import Lot, Need, find_match
from .warning import EtaUpdate, evaluate

GRADES = [("SABIC", "Geleen", "PP 575P"), ("Borealis", "Schwechat", "HD120MO"),
          ("LyondellBasell", "Wesseling", "Moplen HP500N"), ("INEOS", "Lillo", "100-GA12")]
PORTS = ["Rotterdam", "Antwerp"]
DISTRIBUTORS = ["Hub A", "Hub B", "Hub C", "Hub D"]


@dataclass(frozen=True)
class Assumptions:
    shipments: int = 1000
    on_time_share: float = 0.564
    mean_lateness_days: float = 6.06
    mean_safety_stock_days: float = 12.0
    min_lead_days_to_act: int = 8          # a swap must be bound by T-8
    mean_warning_lead_days: float = 10.0
    lots_per_distributor: int = 6
    seed: int = 18


@dataclass(frozen=True)
class Result:
    shipments: int
    late: int
    alerts: int               # delay outruns safety stock
    alerts_in_time: int       # and the warning came early enough to act
    matched: int              # and identical stock was found
    stoppage_days_at_risk: int
    stoppage_days_avoided: int
    stoppage_cost_avoided_usd: float
    swap_cost_usd: float


def _stock(rng: random.Random, a: Assumptions) -> list[Lot]:
    lots = []
    for distributor in DISTRIBUTORS:
        for _ in range(a.lots_per_distributor):
            producer, plant, grade = rng.choice(GRADES)
            lots.append(Lot(distributor, producer, plant, grade, rng.choice(PORTS),
                            teu=rng.choice([10, 20, 40, 60]),
                            days_until_available=rng.choice([0, 0, 0, 5, 12])))
    return lots


def run(a: Assumptions = Assumptions()) -> Result:
    rng = random.Random(a.seed)
    case = SwapCase()
    late = alerts = in_time = matched = at_risk = avoided = 0
    cost_avoided = swap_cost = 0.0
    for i in range(a.shipments):
        if rng.random() < a.on_time_share:
            continue
        late += 1
        delay = max(1, round(rng.expovariate(1 / a.mean_lateness_days)))
        safety = max(0, round(rng.gauss(a.mean_safety_stock_days, 6)))
        lead = max(0, round(rng.gauss(a.mean_warning_lead_days, 4)))
        alert = evaluate(EtaUpdate(f"BK{i:05d}", lead, delay), safety)
        if alert is None:
            continue
        alerts += 1
        at_risk += alert.stockout_days
        if alert.lead_days < a.min_lead_days_to_act:
            continue
        in_time += 1
        producer, plant, grade = rng.choice(GRADES)
        need = Need(producer, plant, grade, rng.choice(PORTS), teu=rng.choice([20, 40]),
                    days_until_needed=alert.lead_days)
        # each alert sees a fresh snapshot of the distributor feeds
        if find_match(need, _stock(rng, a)) is None:
            continue
        this_case = SwapCase(delay_days=delay, safety_stock_days=safety)
        if not this_case.swap_is_worth_it:
            continue
        matched += 1
        avoided += alert.stockout_days
        cost_avoided += this_case.stoppage_cost_usd
        swap_cost += case.swap_cost_usd
    return Result(a.shipments, late, alerts, in_time, matched, at_risk, avoided, cost_avoided, swap_cost)


def summary(r: Result) -> str:
    share = lambda n, d: f"{100 * n / d:.1f}%" if d else "n/a"
    return "\n".join([
        "SIMULATED DATA, assumptions not evidence",
        f"shipments simulated:           {r.shipments}",
        f"late:                          {r.late} ({share(r.late, r.shipments)})",
        f"delay outruns safety stock:    {r.alerts} ({share(r.alerts, r.late)} of late)",
        f"warned early enough to act:    {r.alerts_in_time} ({share(r.alerts_in_time, r.alerts)} of alerts)",
        f"identical stock found, swapped: {r.matched} ({share(r.matched, r.alerts_in_time)} of actionable)",
        f"stoppage days avoided:         {r.stoppage_days_avoided} of {r.stoppage_days_at_risk}",
        f"stoppage cost avoided:         ${r.stoppage_cost_avoided_usd:,.0f}",
        f"total swap cost:               ${r.swap_cost_usd:,.0f}",
    ])
