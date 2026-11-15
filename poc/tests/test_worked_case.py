"""The numbers published in the short deck and the 2-pager must follow from the model.

If one of these fails, either the code or the pitch materials are wrong. Do not
edit the expected values without changing the deck and the brief in the same
pull request.
"""
import pytest

from steadpoc.economics import SwapCase

CASE = SwapCase()


def test_line_stops_six_days_without_action():
    assert CASE.downtime_days == 6


def test_stoppage_range_180k_to_1_08m():
    assert CASE.stoppage_cost_usd == 1_080_000
    assert SwapCase(downtime_cost_per_day_usd=30_000).stoppage_cost_usd == 180_000


def test_no_stoppage_when_stock_covers_delay():
    assert SwapCase(safety_stock_days=11).stoppage_cost_usd == 0


def test_swap_costs_68k_split_28_16_24():
    assert CASE.fee_usd == 24_000
    assert CASE.swap_cost_usd == 68_000


def test_lender_yield_about_77_percent_annualized():
    assert CASE.lender_annualized_yield == pytest.approx(0.774, abs=0.001)


def test_loss_reduction_83_to_94_percent():
    assert round(CASE.loss_reduction_vs(CASE.air_bridge_usd) * 100) == 83
    assert round(CASE.loss_reduction_vs(CASE.stoppage_cost_usd) * 100) == 94


def test_premium_about_1_6m_per_100_swaps():
    assert CASE.premium_usd * 100 == 1_600_000
