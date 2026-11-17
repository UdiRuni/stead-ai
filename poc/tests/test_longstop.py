import math

import pytest

from steadpoc.economics import SwapCase
from steadpoc.longstop import LongStop, report, sensitivity


def test_defaults_follow_the_worked_case():
    case = LongStop()
    assert case.agreed_value_usd == SwapCase().notional_usd == 1_200_000
    assert case.expected_delay_days == SwapCase().delay_days == 11


def test_base_case_arithmetic():
    case = LongStop()
    assert case.chance_of_passing == pytest.approx(math.exp(-19 / 6.65))
    assert case.net_loss_usd == pytest.approx(180_000)
    assert case.pure_cost_usd == pytest.approx(case.chance_of_passing * 180_000)
    assert case.premium_usd == pytest.approx(case.pure_cost_usd / 0.60)


def test_later_long_stop_is_cheaper_and_fatter_tail_is_dearer():
    assert LongStop(long_stop_day=45).premium_usd < LongStop(long_stop_day=30).premium_usd
    assert LongStop(long_stop_day=21).premium_usd > LongStop(long_stop_day=30).premium_usd
    assert LongStop(tail_stretch=1.5).premium_usd > LongStop().premium_usd


def test_premium_scales_with_severity_and_value():
    assert LongStop(net_severity_share=0.30).premium_usd == pytest.approx(2 * LongStop().premium_usd)
    assert LongStop(agreed_value_usd=600_000).premium_usd == pytest.approx(LongStop().premium_usd / 2)


def test_long_stop_must_follow_expected_return():
    with pytest.raises(ValueError):
        LongStop(long_stop_day=11)
    with pytest.raises(ValueError):
        LongStop(net_severity_share=0)


def test_sensitivity_grid_and_report_labels():
    assert len(sensitivity()) == 18
    text = report()
    assert "ASSUMPTIONS, NOT A QUOTE" in text
    assert "published placeholder" in text and "$16,000" in text
    assert chr(0x2014) not in text


def test_the_published_placeholder_is_untouched():
    assert SwapCase().premium_usd == 16_000
