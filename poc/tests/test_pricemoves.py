"""Resin price moves against the purchase break-even (public proxy series)."""
import math

import pytest

from steadpoc.pricemoves import (DATA_FILE, MAX_LISTED, Move, Point, breakevens,
                                 falls_beyond, load_series, main, months_for_days,
                                 moves, report, share, validate)
from steadpoc.purchase import PurchaseCase

SERIES = load_series()


def pts(*values, start_year=2020, start_month=1):
    out = []
    y, m = start_year, start_month
    for v in values:
        out.append(Point(f"{y:04d}-{m:02d}", v))
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def write(tmp_path, text):
    p = tmp_path / "series.csv"
    p.write_text(text)
    return p


# The stored file
def test_file_loads_94_clean_months():
    assert len(SERIES) == 94
    assert SERIES[0] == Point("2019-01", 165.3)
    assert SERIES[-1] == Point("2026-10", 199.28)


def test_file_spot_values_as_printed_on_fred():
    by = {p.month: p.value for p in SERIES}
    assert by["2021-08"] == 236.686
    assert by["2026-05"] == 220.496
    assert by["2025-12"] == 176.321


def test_file_has_no_gaps_and_is_in_order():
    assert validate(SERIES) == SERIES


def test_readme_documents_source_and_licence():
    readme = (DATA_FILE.parent / "README.md").read_text()
    assert "ppi_thermoplastic_resins_monthly.csv" in readme
    assert "WPU06621201" in readme
    assert "public domain" in readme
    assert "2026-11-28" in readme


# Validation: every problem listed, gaps never filled
def test_rejects_gap():
    with pytest.raises(ValueError, match="1 month\\(s\\) missing"):
        validate([Point("2020-01", 1), Point("2020-03", 1)])


def test_rejects_out_of_order_and_duplicate_together():
    with pytest.raises(ValueError) as e:
        validate([Point("2020-02", 1), Point("2020-01", 1), Point("2020-01", 1)])
    msg = str(e.value)
    assert "out of order" in msg and "duplicate month 2020-01" in msg


@pytest.mark.parametrize("value", [0, -1.0, float("nan"), float("inf")])
def test_rejects_value_not_above_zero_or_not_finite(value):
    with pytest.raises(ValueError, match="above 0"):
        validate([Point("2020-01", 1), Point("2020-02", value)])


@pytest.mark.parametrize("month", ["2020-13", "2020-00", "2020-1", "20-01", "2020/01", ""])
def test_rejects_bad_month(month):
    with pytest.raises(ValueError, match="row 2"):
        validate([Point("2020-01", 1), Point(month, 1)])


def test_rejects_fewer_than_two_months():
    with pytest.raises(ValueError, match="at least two"):
        validate([Point("2020-01", 1)])
    with pytest.raises(ValueError, match="at least two"):
        validate([])


def test_year_boundary_is_not_a_gap():
    assert len(validate([Point("2020-12", 1), Point("2021-01", 1)])) == 2


def test_load_rejects_missing_column(tmp_path):
    with pytest.raises(ValueError, match="columns"):
        load_series(write(tmp_path, "month,value\n2020-01,1\n2020-02,2\n"))


def test_load_rejects_non_number_with_line(tmp_path):
    with pytest.raises(ValueError, match="line 3"):
        load_series(write(tmp_path, "month,index\n2020-01,1\n2020-02,n/a\n"))


def test_load_rejects_empty_file(tmp_path):
    with pytest.raises(ValueError):
        load_series(write(tmp_path, ""))


def test_load_reads_a_good_small_file(tmp_path):
    s = load_series(write(tmp_path, "month,index\n2020-01,100\n2020-02,95\n"))
    assert s == [Point("2020-01", 100.0), Point("2020-02", 95.0)]


# Holding days to months
@pytest.mark.parametrize("days,months", [(0, 1), (1, 1), (15, 1), (30, 1), (45, 1),
                                         (46, 2), (60, 2), (90, 3), (365, 12)])
def test_months_for_days(days, months):
    assert months_for_days(days) == months


def test_months_for_negative_days_refused():
    with pytest.raises(ValueError):
        months_for_days(-1)


# Moves
def test_moves_one_month():
    ms = moves(pts(100, 95, 114))
    assert [m.start for m in ms] == ["2020-01", "2020-02"]
    assert ms[0].change == pytest.approx(-0.05)
    assert ms[1].change == pytest.approx(0.20)


def test_moves_overlap_over_several_months():
    ms = moves(pts(100, 90, 80, 120), months=2)
    assert len(ms) == 2
    assert ms[0] == Move("2020-01", "2020-03", pytest.approx(-0.2))
    assert ms[1].change == pytest.approx(120 / 90 - 1)


def test_moves_longer_than_series_is_empty():
    assert moves(pts(100, 90), months=5) == []


def test_moves_months_below_one_refused():
    with pytest.raises(ValueError):
        moves(pts(100, 90), months=0)


def test_moves_flat_series_is_zero():
    assert all(m.change == 0 for m in moves(pts(50, 50, 50)))


# Threshold: strictly more than the break-even fall
def test_fall_exactly_at_break_even_does_not_count():
    ms = [Move("a", "b", -0.03), Move("b", "c", -0.0301), Move("c", "d", 0.1)]
    assert falls_beyond(ms, 0.03) == [ms[1]]


def test_rises_never_count():
    assert falls_beyond([Move("a", "b", 0.5)], 0.0) == []


def test_zero_or_negative_break_even_counts_every_non_rise_below_it():
    ms = [Move("a", "b", 0.0), Move("b", "c", -0.001), Move("c", "d", 0.01)]
    assert falls_beyond(ms, 0.0) == [ms[1]]
    assert falls_beyond(ms, -0.02) == ms   # loan already cheaper: every move counts


def test_none_break_even_counts_nothing():
    assert falls_beyond([Move("a", "b", -0.9)], None) == []


def test_share_of_empty_is_zero():
    assert share([], []) == 0.0
    assert share([1], [1, 2, 3, 4]) == 0.25


# Break-evens come from purchase.py, not retyped here
def test_break_evens_match_purchase_module():
    through, direct = breakevens(30)
    assert through.fall == PurchaseCase().breakeven_price_fall
    assert direct.fall == PurchaseCase(purchase_fee_rate=0.0).breakeven_price_fall
    assert through.fall == pytest.approx(0.0301, abs=0.0005)
    assert direct.fall == pytest.approx(0.0501, abs=0.0005)


def test_longer_hold_lowers_break_even():
    assert breakevens(90)[0].fall < breakevens(30)[0].fall


def test_hold_long_enough_makes_loan_cheaper_with_no_fall():
    # past about 167 days through stead.ai, the break-even fall goes below 0
    assert breakevens(200)[0].fall < 0


# Headline on the stored series (public proxy). If the file changes, these change.
def test_headline_30_days():
    ms = moves(SERIES, 1)
    assert len(ms) == 93
    through, direct = breakevens(30)
    assert len(falls_beyond(ms, through.fall)) == 8
    assert len(falls_beyond(ms, direct.fall)) == 3
    worst = min(ms, key=lambda m: m.change)
    assert (worst.start, worst.end) == ("2026-06", "2026-07")
    assert worst.change == pytest.approx(197.412 / 211.387 - 1)


def test_headline_90_days():
    ms = moves(SERIES, 3)
    through, direct = breakevens(90)
    assert len(ms) == 91
    assert len(falls_beyond(ms, through.fall)) == 32
    assert len(falls_beyond(ms, direct.fall)) == 19


# Report
def test_report_labels_proxy_and_not_forecast():
    r = report(SERIES)
    assert "Public proxy series" in r
    assert "WPU06621201" in r
    assert "floor, not an estimate" in r
    assert "Not a forecast" in r
    assert "8 of 93 (9%)" in r
    assert "3 of 93 (3%)" in r
    assert chr(0x2014) not in r   # house rule: no em dashes


def test_report_caps_listed_periods():
    r = report(SERIES, hold_days=90)
    assert "and 24 more" in r      # 32 hits, 8 listed
    assert "and 11 more" in r      # 19 hits, 8 listed


def test_report_none_when_no_fall():
    r = report(pts(100, 101, 102, 103))
    assert r.count(". none") == 2


def test_report_on_tiny_series():
    r = report(pts(100, 90))
    assert "1 overlapping periods" in r
    assert "-10.0%" in r


def test_report_refuses_hold_longer_than_series():
    with pytest.raises(ValueError):
        report(pts(100, 90), hold_days=90)


def test_main_runs(capsys):
    main([])
    assert "RESIN PRICE MOVES" in capsys.readouterr().out


def test_main_reads_other_file(tmp_path, capsys):
    main(["--file", str(write(tmp_path, "month,index\n2020-01,100\n2020-02,90\n"))])
    assert "2020-01 to 2020-02" in capsys.readouterr().out
