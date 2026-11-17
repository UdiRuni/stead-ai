"""Backtest on public data only: file validation, honesty labels and the replay."""
from dataclasses import replace

import pytest

from steadpoc.backtest import DATA_FILE, Month, backtest, load_months, report
from steadpoc.simulate import Assumptions, run

HEADER = "month,on_time_pct,avg_delay_late_days,source_url,retrieved\n"
GOOD = "2026-07,56.4,6.06,https://example.org/a,2026-11-16\n"


def write(tmp_path, text):
    path = tmp_path / "months.csv"
    path.write_text(text, encoding="utf-8")
    return path


def month(name="2026-07", share=0.564, lateness=6.06):
    return Month(name, share, lateness, "https://example.org/a", "2026-11-16")


# --- the committed data file -------------------------------------------------

def test_committed_file_loads_and_every_row_is_sourced():
    months = load_months()
    assert len(months) >= 24                      # the plan promises 24 months
    assert all(m.source_url.startswith("https://") and m.retrieved for m in months)
    assert [m.month for m in months] == sorted({m.month for m in months})


def test_committed_file_has_no_month_gaps():
    months = [m.month for m in load_months()]
    y, mo = map(int, months[0].split("-"))
    for name in months:
        assert name == f"{y:04d}-{mo:02d}"
        y, mo = (y, mo + 1) if mo < 12 else (y + 1, 1)


def test_committed_file_agrees_with_the_figures_the_simulation_borrows():
    latest = next(m for m in load_months() if m.month == "2026-09")   # the month the brief quotes
    a = Assumptions()
    assert latest.on_time_share == pytest.approx(a.on_time_share)
    assert latest.mean_lateness_days == pytest.approx(a.mean_lateness_days)


def test_backtest_needs_no_file_outside_the_repo_data_folder():
    assert DATA_FILE.parent.name == "data" and DATA_FILE.exists()


# --- validation --------------------------------------------------------------

def test_empty_lateness_is_kept_as_unknown_not_guessed(tmp_path):
    months = load_months(write(tmp_path, HEADER + "2025-03,57.5,,https://example.org/a,2026-11-16\n"))
    assert months[0].mean_lateness_days is None and not months[0].usable


@pytest.mark.parametrize("row, message", [
    ("2026-13,56.4,6.06,https://example.org/a,2026-11-16", "YYYY-MM"),
    ("July 2026,56.4,6.06,https://example.org/a,2026-11-16", "YYYY-MM"),
    ("2026-07,101,6.06,https://example.org/a,2026-11-16", "between 0 and 100"),
    ("2026-07,-1,6.06,https://example.org/a,2026-11-16", "between 0 and 100"),
    ("2026-07,abc,6.06,https://example.org/a,2026-11-16", "numbers"),
    ("2026-07,56.4,0,https://example.org/a,2026-11-16", "positive"),
    ("2026-07,56.4,-2,https://example.org/a,2026-11-16", "positive"),
    ("2026-07,56.4,6.06,,2026-11-16", "source_url"),
    ("2026-07,56.4,6.06,http://example.org/a,2026-11-16", "source_url"),
    ("2026-07,56.4,6.06,https://example.org/a,", "retrieval date"),
])
def test_bad_rows_are_rejected_with_the_line_number(tmp_path, row, message):
    with pytest.raises(ValueError, match=message) as error:
        load_months(write(tmp_path, HEADER + row + "\n"))
    assert "line 2" in str(error.value)


def test_duplicate_or_unordered_months_are_rejected(tmp_path):
    with pytest.raises(ValueError, match="ascending"):
        load_months(write(tmp_path, HEADER + GOOD + GOOD))
    with pytest.raises(ValueError, match="ascending"):
        load_months(write(tmp_path, HEADER + GOOD + "2026-06,62.6,5.31,https://example.org/b,2026-11-16\n"))


def test_missing_column_and_empty_file_are_rejected(tmp_path):
    with pytest.raises(ValueError, match="missing column"):
        load_months(write(tmp_path, "month,on_time_pct\n2026-07,56.4\n"))
    with pytest.raises(ValueError, match="no data rows"):
        load_months(write(tmp_path, HEADER))
    with pytest.raises(ValueError, match="missing column"):
        load_months(write(tmp_path, ""))


def test_boundary_on_time_shares_are_accepted(tmp_path):
    months = load_months(write(tmp_path, HEADER + "2026-01,0,5,https://example.org/a,2026-11-16\n"
                                                  "2026-02,100,5,https://example.org/a,2026-11-16\n"))
    assert [m.on_time_share for m in months] == [0.0, 1.0]


# --- the replay --------------------------------------------------------------

def test_months_without_lateness_are_skipped_and_reported():
    b = backtest([month("2025-02", lateness=None), month("2025-07")])
    assert [m.month.month for m in b.months] == ["2025-07"]
    assert [m.month for m in b.skipped] == ["2025-02"]
    assert "months skipped:                1 (2025-02" in report(b)


def test_replay_is_deterministic_and_each_month_uses_its_own_inputs():
    months = [month("2026-06", 0.626, 5.31), month("2026-07", 0.564, 6.06)]
    a, b = backtest(months), backtest(months)
    assert a == b
    second = a.months[1].result
    assert second == run(replace(Assumptions(), on_time_share=0.564, mean_lateness_days=6.06,
                                 seed=Assumptions().seed + 1))


def test_totals_add_up_and_stay_consistent():
    b = backtest(load_months())
    t = b.total
    assert t.shipments == Assumptions().shipments * len(b.months)
    assert t.alerts == sum(m.result.alerts for m in b.months)
    assert t.late >= t.alerts >= t.alerts_in_time >= t.matched > 0
    assert t.stoppage_days_avoided <= t.stoppage_days_at_risk
    assert len(b.months) + len(b.skipped) == len(load_months())


def test_a_fully_on_time_month_raises_no_alerts():
    r = backtest([month(share=1.0)]).months[0].result
    assert (r.late, r.alerts, r.matched, r.swap_cost_usd) == (0, 0, 0, 0)


def test_worse_public_conditions_mean_more_alerts():
    """With many shipments the public inputs, not the random draw, drive the count."""
    big = Assumptions(shipments=20_000)
    calm, rough = backtest([month("2025-08", 0.653, 4.80), month("2026-08", 0.499, 6.81)], big).months
    assert rough.result.late > calm.result.late
    assert rough.result.alerts > calm.result.alerts


def test_no_usable_months_still_reports_without_error():
    b = backtest([month(lateness=None)])
    assert b.months == () and "(no usable months)" in report(b)
    assert backtest([]).months == ()


def test_report_is_labelled_and_has_no_em_dash():
    text = report(backtest(load_months()))
    assert text.startswith("BACKTEST ON PUBLIC DATA ONLY")
    assert "SIMULATED" in text and "Do not quote as results" in text
    assert chr(0x2014) not in text
    assert "Month(" not in text
