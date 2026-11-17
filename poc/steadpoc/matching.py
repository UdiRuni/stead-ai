"""Same-grade stock matching against distributor stock feeds.

QA approves a producer, a plant and a grade code, not a CAS number, so a match
needs all three to be identical. Stock must be at the destination port and
released by the original arrival date. One swap has one counterparty, so lots
are never combined across distributors.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Lot:
    distributor: str
    producer: str
    plant: str
    grade: str
    port: str
    teu: int
    days_until_available: int = 0   # 0 = already bonded at the port


@dataclass(frozen=True)
class Need:
    producer: str
    plant: str
    grade: str
    port: str
    teu: int
    days_until_needed: int          # days from match to the original arrival date (T)


@dataclass(frozen=True)
class Match:
    distributor: str
    lots: tuple[Lot, ...]

    @property
    def teu(self) -> int:
        return sum(lot.teu for lot in self.lots)


def why_not(lot: Lot, need: Need) -> str | None:
    """Why a lot cannot serve the need, in plain words, or None if it fits."""
    if lot.producer != need.producer:
        return "different producer"
    if lot.plant != need.plant:
        return "different producing plant"
    if lot.grade != need.grade:
        return "different grade code"
    if lot.port != need.port:
        return "wrong port"
    if lot.teu <= 0:
        return "no stock in the lot"
    if lot.days_until_available > need.days_until_needed:
        return "available too late"
    return None


def _fits(lot: Lot, need: Need) -> bool:
    return why_not(lot, need) is None


def find_match(need: Need, lots: list[Lot]) -> Match | None:
    """Return the distributor that covers the full need with the fewest lots, or None."""
    if need.teu <= 0:
        raise ValueError("need.teu must be positive")
    by_distributor: dict[str, list[Lot]] = {}
    for lot in lots:
        if _fits(lot, need):
            by_distributor.setdefault(lot.distributor, []).append(lot)
    best: Match | None = None
    for distributor in sorted(by_distributor):
        chosen, covered = [], 0
        # stock already at the port first, then the largest lots
        for lot in sorted(by_distributor[distributor], key=lambda l: (l.days_until_available, -l.teu)):
            if covered >= need.teu:
                break
            chosen.append(lot)
            covered += lot.teu
        if covered >= need.teu and (best is None or len(chosen) < len(best.lots)):
            best = Match(distributor, tuple(chosen))
    return best
