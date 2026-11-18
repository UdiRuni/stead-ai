"""A first pricing method for the proposed long-stop cover.

ASSUMPTIONS, NOT A QUOTE. The only public input is the average lateness of late
vessel arrivals (6.65 days, Sea-Intelligence, September 2026, the figure the brief
quotes). The shape of the delay tail, the share of the agreed value the insurer
loses after it takes over the late boxes, and the target loss ratio are
assumptions for underwriters to replace. Do not quote outputs as a price or a
result. The published worked case keeps its $16,000 placeholder
(`economics.py`); this module only shows how that number would be built.

The cover, as proposed: the distributor lends stock at T and expects the late
boxes at T + delay. If they have not reached it by the long-stop date, the cover
pays the agreed value and the insurer takes over the right to the boxes. Total
loss of the boxes is not this cover's risk: the plant's cargo policy pays that,
with the lender as loss payee. So the insurer's net loss is the agreed value
less what the boxes fetch when they do arrive.

    chance      = P(boxes pass the long stop | already expected `delay` days late)
    net loss    = agreed value x net severity share
    pure cost   = chance x net loss
    premium     = pure cost / target loss ratio

Delay tail: exponential, so the chance of slipping a further d days is
exp(-d / mean lateness). It is the same shape `simulate.py` uses. It is thin
tailed; real delay tails are probably fatter, which is why `tail_stretch`
exists and why the table shows it.
"""
import math
from dataclasses import dataclass

from .economics import SwapCase


@dataclass(frozen=True)
class LongStop:
    agreed_value_usd: float = SwapCase().notional_usd
    expected_delay_days: int = SwapCase().delay_days
    long_stop_day: int = 30                 # days after T; assumption
    mean_lateness_days: float = 6.65        # public figure, September 2026
    tail_stretch: float = 1.0               # 1.0 = exponential; above 1 = fatter tail
    net_severity_share: float = 0.15        # assumption: resale discount, carry, price move
    target_loss_ratio: float = 0.60         # assumption

    def __post_init__(self):
        if self.long_stop_day <= self.expected_delay_days:
            raise ValueError("the long stop must fall after the expected return date")
        if not 0 < self.net_severity_share <= 1 or not 0 < self.target_loss_ratio <= 1:
            raise ValueError("shares must be above 0 and at most 1")

    @property
    def chance_of_passing(self) -> float:
        extra_days = self.long_stop_day - self.expected_delay_days
        return math.exp(-extra_days / (self.mean_lateness_days * self.tail_stretch))

    @property
    def net_loss_usd(self) -> float:
        return self.agreed_value_usd * self.net_severity_share

    @property
    def pure_cost_usd(self) -> float:
        return self.chance_of_passing * self.net_loss_usd

    @property
    def premium_usd(self) -> float:
        return self.pure_cost_usd / self.target_loss_ratio


def sensitivity(days=(21, 30, 45), severities=(0.10, 0.15, 0.25), stretches=(1.0, 1.5)):
    """Premium for each combination, as (long_stop_day, tail_stretch, severity, LongStop)."""
    return [(d, s, v, LongStop(long_stop_day=d, tail_stretch=s, net_severity_share=v))
            for s in stretches for d in days for v in severities]


def report() -> str:
    base, placeholder = LongStop(), SwapCase().premium_usd
    lines = [
        "LONG-STOP PRICING METHOD. ASSUMPTIONS, NOT A QUOTE. Do not cite as a price.",
        "Public input: 6.65 days average lateness of late vessel arrivals (September 2026).",
        "Assumed: exponential delay tail, net severity share, 60% target loss ratio.",
        "",
        f"Base case: ${base.agreed_value_usd:,.0f} agreed value, boxes expected at T+{base.expected_delay_days}, "
        f"long stop at T+{base.long_stop_day}",
        f"  chance the boxes pass the long stop:  {base.chance_of_passing:.1%}",
        f"  net loss if they do ({base.net_severity_share:.0%} of value): ${base.net_loss_usd:,.0f}",
        f"  pure cost:                            ${base.pure_cost_usd:,.0f}",
        f"  premium at a {base.target_loss_ratio:.0%} loss ratio:         ${base.premium_usd:,.0f}",
        f"  published placeholder:                ${placeholder:,.0f}",
        "",
        "Premium by long-stop date, tail and net severity share",
        "tail          long stop   10% sev.   15% sev.   25% sev.",
    ]
    rows = {}
    for d, s, v, case in sensitivity():
        rows.setdefault((s, d), []).append(case.premium_usd)
    for (s, d), premiums in rows.items():
        tail = "exponential" if s == 1.0 else f"{s:g}x fatter"
        lines.append(f"{tail:<13} T+{d:<9}" + "".join(f"${p:>9,.0f} " for p in premiums))
    lines += ["", "Reading: the premium is driven by the long-stop date and the tail, the two",
              "things underwriters and real delay data must set. Accumulation (many swaps",
              "behind one late vessel or one event): python3 -m steadpoc.accumulation"]
    return "\n".join(lines)


if __name__ == "__main__":
    print(report())
