"""Purchase route against loan route: when is each one cheaper for the plant?

ASSUMPTIONS, NOT DATA. The loan route is the published worked case
(`economics.py`, $68,000 to the plant). Everything about the purchase route is an
assumption for a plant's treasurer to replace:

- cost_of_capital 8% a year. Not sourced. It is the rate implied by the brief's
  "market price + about $8,000 a month" on $1.2M of stock (1.2M x 8% / 12).
- extra_holding_days 30: days the plant carries one extra lot after buying, until
  it is used up (the plant cuts a later order by one lot).
- storage 0 per TEU per day: the plant has its own room. Without room, an outside
  rate must be given, or the purchase route is not possible.
- spot_premium 0 and price_change 0: spot costs the same as the plant's contract
  price, and the market does not move while the extra lot is held.
- purchase_fee_rate 2%: what stead.ai would charge for finding and clearing the
  stock. Not published anywhere; it reuses the only fee we publish (the loan fee).

The two routes, both from day T, both with 0 days stopped:

    loan     = lender yield + long-stop premium + stead.ai fee   (economics.py)
    purchase = spot premium + capital on the extra lot + storage
               + loss if the price falls while the extra lot is held + fee

On a loan the late boxes go to the lender, so the plant never holds double stock
and carries no price risk. On a purchase the plant keeps the late boxes as stock,
so it pays to carry one extra lot and takes the price move on it.

Run `(cd poc && python3 -m steadpoc.purchase)` for the comparison and a
sensitivity table. Output is arithmetic on assumptions, never a result.
"""
import argparse
from dataclasses import dataclass, field, replace

from .economics import SwapCase

LOAN = "loan"
PURCHASE = "purchase"
NO_ACTION = "no action needed"


@dataclass(frozen=True)
class PurchaseCase:
    swap: SwapCase = field(default_factory=SwapCase)
    cost_of_capital: float = 0.08            # assumption, a year; implied by "$8,000 a month"
    extra_holding_days: int = 30             # assumption
    storage_usd_per_teu_day: float = 0.0     # assumption: own room
    has_room: bool = True
    has_cash: bool = True
    spot_premium: float = 0.0                # share of notional; assumption
    price_change: float = 0.0                # over the holding period; -0.05 = 5% fall
    purchase_fee_rate: float = 0.02          # assumption, not published

    def __post_init__(self):
        if self.swap.notional_usd <= 0 or self.swap.teu <= 0:
            raise ValueError("notional and TEU must be above 0")
        if self.cost_of_capital < 0:
            raise ValueError("cost of capital cannot be negative")
        if self.extra_holding_days < 0:
            raise ValueError("holding days cannot be negative")
        if self.storage_usd_per_teu_day < 0:
            raise ValueError("storage cost cannot be negative")
        if self.purchase_fee_rate < 0:
            raise ValueError("fee rate cannot be negative")
        if self.spot_premium <= -1:
            raise ValueError("spot premium must be above -100%")
        if self.price_change <= -1:
            raise ValueError("price change must be above -100%")

    # Purchase route, cost to the plant
    @property
    def capital_usd(self) -> float:
        return self.swap.notional_usd * self.cost_of_capital * self.extra_holding_days / 365

    @property
    def storage_usd(self) -> float:
        return self.swap.teu * self.storage_usd_per_teu_day * self.extra_holding_days

    @property
    def spot_premium_usd(self) -> float:
        return self.swap.notional_usd * self.spot_premium

    @property
    def price_loss_usd(self) -> float:
        """Loss on the extra lot if the price falls; a rise is a gain (negative)."""
        return -self.swap.notional_usd * self.price_change + 0.0  # no negative zero

    @property
    def purchase_fee_usd(self) -> float:
        return self.swap.notional_usd * self.purchase_fee_rate

    @property
    def purchase_cost_usd(self) -> float:
        return (self.spot_premium_usd + self.capital_usd + self.storage_usd
                + self.price_loss_usd + self.purchase_fee_usd)

    @property
    def loan_cost_usd(self) -> float:
        return self.swap.swap_cost_usd

    # What stead.ai earns on each route
    @property
    def stead_on_loan_usd(self) -> float:
        return self.swap.fee_usd

    @property
    def stead_on_purchase_usd(self) -> float:
        return self.purchase_fee_usd

    @property
    def purchase_blockers(self) -> list:
        reasons = []
        if not self.has_cash:
            reasons.append(f"no cash or credit for ${self.swap.notional_usd:,.0f} of extra stock")
        if not self.has_room and self.storage_usd_per_teu_day == 0:
            reasons.append("no room for double stock and no outside storage rate given")
        return reasons

    @property
    def cheaper_route(self) -> str:
        """Ties go to the purchase: simpler deal, no long stop to insure."""
        if self.swap.downtime_days == 0:
            return NO_ACTION
        if self.purchase_blockers:
            return LOAN
        return PURCHASE if self.purchase_cost_usd <= self.loan_cost_usd else LOAN

    # Break-evens, other inputs held. None means "never, on these inputs".
    @property
    def _purchase_without_price_usd(self) -> float:
        return self.purchase_cost_usd - self.price_loss_usd

    @property
    def breakeven_price_fall(self):
        """Price fall on the extra lot at which the loan becomes cheaper.

        0 or less means the loan is already cheaper with no price move."""
        return (self.loan_cost_usd - self._purchase_without_price_usd) / self.swap.notional_usd

    @property
    def daily_carry_usd(self) -> float:
        return (self.swap.notional_usd * self.cost_of_capital / 365
                + self.swap.teu * self.storage_usd_per_teu_day)

    @property
    def breakeven_holding_days(self):
        """Holding days at which the loan becomes cheaper (fractional)."""
        if self.daily_carry_usd == 0:
            return None
        fixed = self.spot_premium_usd + self.price_loss_usd + self.purchase_fee_usd
        return (self.loan_cost_usd - fixed) / self.daily_carry_usd

    @property
    def breakeven_storage_usd_per_teu_day(self):
        """Outside storage rate at which the loan becomes cheaper."""
        if self.extra_holding_days == 0:
            return None
        rest = self.purchase_cost_usd - self.storage_usd
        return (self.loan_cost_usd - rest) / (self.swap.teu * self.extra_holding_days)


def sensitivity(base: PurchaseCase, price_changes=(-0.10, -0.05, -0.03, 0.0, 0.05),
                holding_days=(15, 30, 60, 90)):
    """Rows of (holding days, price change, purchase cost, loan cost, cheaper route)."""
    rows = []
    for days in holding_days:
        for change in price_changes:
            c = replace(base, extra_holding_days=days, price_change=change)
            rows.append((days, change, c.purchase_cost_usd, c.loan_cost_usd, c.cheaper_route))
    return rows


def _fmt_days(x):
    return "never" if x is None else f"{x:,.0f} days"


def report(case: PurchaseCase) -> str:
    s = case.swap
    lines = [
        "PURCHASE ROUTE AGAINST LOAN ROUTE. Assumptions, not data.",
        f"Worked case: {s.teu} TEU, ${s.notional_usd:,.0f}, {s.delay_days} days late, "
        f"{s.safety_stock_days} days of stock, {s.downtime_days} days stopped with no action.",
        "",
        f"Loan route, cost to the plant:      ${case.loan_cost_usd:>10,.0f}  (published worked case)",
        f"Purchase route, cost to the plant:  ${case.purchase_cost_usd:>10,.0f}",
        f"  capital on extra lot ({case.cost_of_capital:.1%} a year, {case.extra_holding_days} days): "
        f"${case.capital_usd:,.0f}",
        f"  storage:                          ${case.storage_usd:,.0f}",
        f"  spot premium:                     ${case.spot_premium_usd:,.0f}",
        f"  price move on extra lot ({case.price_change:+.1%}):  ${case.price_loss_usd:,.0f}",
        f"  stead.ai fee ({case.purchase_fee_rate:.1%}):              ${case.purchase_fee_usd:,.0f}",
        "",
        f"stead.ai earns: loan ${case.stead_on_loan_usd:,.0f}, purchase ${case.stead_on_purchase_usd:,.0f}",
    ]
    if case.purchase_blockers:
        lines.append("Purchase not possible: " + "; ".join(case.purchase_blockers))
    lines.append(f"Cheaper for the plant: {case.cheaper_route}")
    lines += [
        "",
        "The loan becomes cheaper if, other inputs held:",
        f"  the price of the extra lot falls by more than {case.breakeven_price_fall:.1%} while held,",
        f"  or the extra lot is held longer than {_fmt_days(case.breakeven_holding_days)},",
    ]
    bs = case.breakeven_storage_usd_per_teu_day
    lines.append("  or outside storage costs more than "
                 + ("(no holding period)" if bs is None else f"${bs:,.0f} per TEU per day") + ",")
    lines.append("  or the plant has no cash or no room for double stock.")
    lines += ["", "Sensitivity (cost to the plant, purchase against loan):",
              f"{'held':>6} {'price':>7} {'purchase':>11} {'loan':>9}  cheaper"]
    for days, change, p, l, route in sensitivity(case):
        lines.append(f"{days:>5}d {change:>+7.0%} {p:>11,.0f} {l:>9,.0f}  {route}")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--cost-of-capital", type=float, default=0.08)
    ap.add_argument("--hold-days", type=int, default=30)
    ap.add_argument("--storage", type=float, default=0.0, help="USD per TEU per day")
    ap.add_argument("--no-room", action="store_true")
    ap.add_argument("--no-cash", action="store_true")
    ap.add_argument("--spot-premium", type=float, default=0.0)
    ap.add_argument("--price-change", type=float, default=0.0)
    ap.add_argument("--fee-rate", type=float, default=0.02)
    a = ap.parse_args(argv)
    case = PurchaseCase(cost_of_capital=a.cost_of_capital, extra_holding_days=a.hold_days,
                        storage_usd_per_teu_day=a.storage, has_room=not a.no_room,
                        has_cash=not a.no_cash, spot_premium=a.spot_premium,
                        price_change=a.price_change, purchase_fee_rate=a.fee_rate)
    print(report(case))


if __name__ == "__main__":
    main()
