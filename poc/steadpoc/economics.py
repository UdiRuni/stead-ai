"""Swap economics. The defaults are the worked case used in the deck and the 2-pager.

If you change a default here, the deck and the brief must change too (and the
other way round). poc/tests/test_worked_case.py enforces the published numbers.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class SwapCase:
    notional_usd: float = 1_200_000        # 40 TEU of polypropylene
    teu: int = 40
    delay_days: int = 11                   # late shipment arrives at T+11
    safety_stock_days: int = 5             # thin-stock case
    downtime_cost_per_day_usd: float = 180_000
    lender_yield_usd: float = 28_000       # paid to the distributor hub
    premium_usd: float = 16_000            # placeholder long-stop premium
    fee_rate: float = 0.02                 # stead.ai fee, share of notional
    air_bridge_usd: float = 390_000        # partial air freight alternative

    @property
    def downtime_days(self) -> int:
        """Days the line stops with no action: delay beyond the safety stock."""
        return max(0, self.delay_days - self.safety_stock_days)

    @property
    def stoppage_cost_usd(self) -> float:
        return self.downtime_days * self.downtime_cost_per_day_usd

    @property
    def fee_usd(self) -> float:
        return self.notional_usd * self.fee_rate

    @property
    def swap_cost_usd(self) -> float:
        """Total cost of one swap to the plant (or to its insurer on a covered claim)."""
        return self.lender_yield_usd + self.premium_usd + self.fee_usd

    @property
    def loan_days(self) -> int:
        """Stock goes out at T and the late boxes repay it at T + delay."""
        return self.delay_days

    @property
    def lender_annualized_yield(self) -> float:
        """Simple (not compounded) annualized yield on the lent stock."""
        return self.lender_yield_usd / self.notional_usd * 365 / self.loan_days

    def loss_reduction_vs(self, alternative_cost_usd: float) -> float:
        return 1 - self.swap_cost_usd / alternative_cost_usd

    @property
    def swap_is_worth_it(self) -> bool:
        return self.swap_cost_usd < self.stoppage_cost_usd
