"""Purchase route against loan route. All inputs are assumptions (see purchase.py)."""
import math
from dataclasses import replace

import pytest

from steadpoc.economics import SwapCase
from steadpoc.purchase import (LOAN, NO_ACTION, PURCHASE, PurchaseCase, main, report,
                               sensitivity)

BASE = PurchaseCase()
DIRECT = PurchaseCase(purchase_fee_rate=0.0)


# The loan side is the published worked case, untouched
def test_loan_cost_is_the_published_68k():
    assert BASE.loan_cost_usd == 68_000
    assert BASE.stead_on_loan_usd == 24_000


def test_default_carry_matches_the_brief_8k_a_month():
    # 1.2M x 8% / 12 = 8,000 a month; 30 days is 7,890
    assert BASE.swap.notional_usd * BASE.cost_of_capital / 12 == pytest.approx(8_000)
    assert BASE.capital_usd == pytest.approx(7_890.41, abs=0.01)


# Base case: the honest, negative-for-the-loan result
def test_base_purchase_cheaper_than_loan():
    assert BASE.purchase_cost_usd == pytest.approx(31_890.41, abs=0.01)
    assert BASE.cheaper_route == PURCHASE
    assert DIRECT.purchase_cost_usd == pytest.approx(7_890.41, abs=0.01)
    assert DIRECT.cheaper_route == PURCHASE


def test_stead_earns_same_fee_on_both_routes_at_2_percent():
    assert BASE.stead_on_purchase_usd == BASE.stead_on_loan_usd == 24_000
    assert DIRECT.stead_on_purchase_usd == 0


# Break-evens
def test_breakeven_price_fall_about_3_percent_via_us_5_direct():
    assert BASE.breakeven_price_fall == pytest.approx(0.0301, abs=0.0001)
    assert DIRECT.breakeven_price_fall == pytest.approx(0.0501, abs=0.0001)


def test_price_fall_just_past_breakeven_flips_to_loan():
    x = BASE.breakeven_price_fall
    assert replace(BASE, price_change=-(x - 0.001)).cheaper_route == PURCHASE
    assert replace(BASE, price_change=-(x + 0.001)).cheaper_route == LOAN


def test_exact_tie_goes_to_purchase():
    tie = replace(BASE, price_change=-BASE.breakeven_price_fall)
    assert tie.purchase_cost_usd == pytest.approx(tie.loan_cost_usd)
    # an exact tie in floating point: $1M lot, loan 64,000, purchase 44,000 + 20,000
    exact = PurchaseCase(swap=SwapCase(notional_usd=1_000_000), cost_of_capital=0.0,
                         spot_premium=0.044)
    assert exact.purchase_cost_usd == exact.loan_cost_usd == 64_000
    assert exact.cheaper_route == PURCHASE


def test_breakeven_holding_days():
    d = BASE.breakeven_holding_days
    assert d == pytest.approx(44_000 / (1_200_000 * 0.08 / 365))
    assert replace(BASE, extra_holding_days=math.floor(d)).cheaper_route == PURCHASE
    assert replace(BASE, extra_holding_days=math.ceil(d) + 1).cheaper_route == LOAN


def test_breakeven_holding_days_none_without_carry():
    assert PurchaseCase(cost_of_capital=0.0).breakeven_holding_days is None


def test_breakeven_storage_rate():
    r = BASE.breakeven_storage_usd_per_teu_day
    assert r == pytest.approx((68_000 - 31_890.41) / (40 * 30), abs=0.01)
    assert replace(BASE, storage_usd_per_teu_day=r * 0.99).cheaper_route == PURCHASE
    assert replace(BASE, storage_usd_per_teu_day=r * 1.01).cheaper_route == LOAN


def test_breakeven_storage_none_with_zero_holding():
    assert PurchaseCase(extra_holding_days=0).breakeven_storage_usd_per_teu_day is None


def test_breakeven_negative_when_loan_already_cheaper():
    c = PurchaseCase(spot_premium=0.10)
    assert c.cheaper_route == LOAN
    assert c.breakeven_price_fall < 0
    assert c.breakeven_holding_days < 0


# Components and signs
def test_price_rise_is_a_gain_on_the_purchase():
    up = replace(BASE, price_change=0.05)
    assert up.price_loss_usd == -60_000
    assert up.purchase_cost_usd < BASE.purchase_cost_usd


def test_no_negative_zero_in_price_loss():
    assert math.copysign(1, BASE.price_loss_usd) == 1


def test_storage_cost_scales_with_teu_and_days():
    c = PurchaseCase(storage_usd_per_teu_day=10, extra_holding_days=20)
    assert c.storage_usd == 40 * 10 * 20


def test_spot_discount_lowers_purchase_cost():
    assert PurchaseCase(spot_premium=-0.02).spot_premium_usd == -24_000


def test_zero_holding_days_means_only_fee_and_premium():
    c = PurchaseCase(extra_holding_days=0, storage_usd_per_teu_day=50)
    assert c.capital_usd == 0 and c.storage_usd == 0
    assert c.purchase_cost_usd == 24_000


# Feasibility
def test_no_cash_forces_loan_even_if_purchase_cheaper():
    c = PurchaseCase(has_cash=False)
    assert c.purchase_cost_usd < c.loan_cost_usd
    assert c.cheaper_route == LOAN
    assert "no cash" in c.purchase_blockers[0]


def test_no_room_without_outside_rate_forces_loan():
    c = PurchaseCase(has_room=False)
    assert c.cheaper_route == LOAN
    assert "no room" in c.purchase_blockers[0]


def test_no_room_with_outside_rate_is_priced_not_blocked():
    c = PurchaseCase(has_room=False, storage_usd_per_teu_day=5)
    assert c.purchase_blockers == []
    assert c.cheaper_route == PURCHASE


def test_both_blockers_listed():
    assert len(PurchaseCase(has_cash=False, has_room=False).purchase_blockers) == 2


# Delay shorter than safety stock
def test_no_action_when_stock_covers_delay():
    c = PurchaseCase(swap=SwapCase(safety_stock_days=11))
    assert c.cheaper_route == NO_ACTION
    c = PurchaseCase(swap=SwapCase(delay_days=3), has_cash=False)
    assert c.cheaper_route == NO_ACTION


# Bad inputs
@pytest.mark.parametrize("kwargs", [
    {"cost_of_capital": -0.01},
    {"extra_holding_days": -1},
    {"storage_usd_per_teu_day": -1},
    {"purchase_fee_rate": -0.01},
    {"spot_premium": -1.0},
    {"price_change": -1.0},
    {"swap": SwapCase(notional_usd=0)},
    {"swap": SwapCase(notional_usd=-5)},
    {"swap": SwapCase(teu=0)},
])
def test_rejects_bad_inputs(kwargs):
    with pytest.raises(ValueError):
        PurchaseCase(**kwargs)


# Sensitivity and output
def test_sensitivity_grid_shape_and_monotone():
    rows = sensitivity(BASE)
    assert len(rows) == 4 * 5
    by_days = {}
    for days, change, p, l, _ in rows:
        assert l == 68_000
        by_days.setdefault(change, []).append(p)
    for costs in by_days.values():
        assert costs == sorted(costs)          # longer holding never cheaper


def test_sensitivity_has_both_routes():
    routes = {r[4] for r in sensitivity(BASE)}
    assert routes == {LOAN, PURCHASE}


def test_report_labels_assumptions_and_breakevens():
    text = report(BASE)
    assert "Assumptions, not data" in text
    assert "Cheaper for the plant: purchase" in text
    assert "falls by more than 3.0%" in text
    assert "$-0" not in text
    assert "—" not in text                 # house rule: no em dashes


def test_report_shows_blockers():
    assert "Purchase not possible: no cash" in report(PurchaseCase(has_cash=False))


def test_report_zero_holding_does_not_crash():
    assert "no holding period" in report(PurchaseCase(extra_holding_days=0))
    assert "never" in report(PurchaseCase(cost_of_capital=0.0))


def test_cli(capsys):
    main(["--no-room", "--price-change", "-0.06"])
    out = capsys.readouterr().out
    assert "Cheaper for the plant: loan" in out
    assert "no room" in out
