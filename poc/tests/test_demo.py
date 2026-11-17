"""The demo must agree with the worked case, stay honest, and survive odd inputs."""
import re
from dataclasses import replace
from datetime import date

import pytest

from steadpoc.demo import (BANNER, NO_CAPACITY, Feed, Schedule, build_demo, day, demo_stock, main,
                           render_html, render_text, term_sheet_rows)
from steadpoc.economics import SwapCase
from steadpoc.matching import Lot, Need, why_not
from steadpoc.warning import EtaUpdate

CASE = SwapCase()
DEMO = build_demo()
TEXT, HTML = render_text(DEMO), render_html(DEMO)


def rows(demo=DEMO):
    return {label: value for _, section in term_sheet_rows(demo.term_sheet, demo.arrival)
            for label, value in section}


# ---- the worked case ----

def test_worked_case_alerts_on_the_third_update_only():
    assert [s.alert is not None for s in DEMO.steps] == [False, False, True]
    assert DEMO.alert.lead_days == 12 and DEMO.alert.stockout_days == CASE.downtime_days == 6


def test_worked_case_matches_one_distributor_with_the_full_lot():
    assert DEMO.match.distributor == "Hub B" and DEMO.match.teu == 40
    assert [v.verdict for v in DEMO.verdicts].count("chosen") == 1


def test_every_refused_lot_says_why():
    verdicts = {(v.lot.distributor, v.lot.grade, v.lot.plant, v.lot.port, v.lot.teu,
                 v.lot.days_until_available): v.verdict for v in DEMO.verdicts}
    assert verdicts[("Hub A", "PP 571P", "Geleen", "Rotterdam", 40, 0)] == "different grade code"
    assert verdicts[("Hub A", "PP 575P", "Geleen", "Antwerp", 40, 0)] == "wrong port"
    assert verdicts[("Hub C", "PP 575P", "Al Jubail", "Rotterdam", 40, 0)] == "different producing plant"
    assert verdicts[("Hub D", "PP 575P", "Geleen", "Rotterdam", 40, 14)] == "available too late"
    assert verdicts[("Hub C", "PP 575P", "Geleen", "Rotterdam", 20, 0)].startswith("too small alone")
    assert all(v.verdict for v in DEMO.verdicts)


def test_term_sheet_numbers_come_from_the_model():
    r = rows()
    assert r["Total"] == "$68,000"
    assert r["Lender's yield"].startswith("$28,000, about 77% annualized")
    assert r["Long-stop premium"].startswith("$16,000") and "PLACEHOLDER" in r["Long-stop premium"]
    assert r["stead.ai fee"] == "$24,000, 2.0% of value"
    assert "6 days: $1,080,000" in r["No action"]
    assert r["Partial air freight"].startswith("$390,000")
    assert "83% to 94%" in r["Swap"]
    assert r["Alert"].startswith("T-12") and r["Match"] == "T-10" and r["Swap bound"] == "T-8"
    assert r["Loan repaid"].startswith("T+11") and r["Loan length"] == "11 days"


def test_term_sheet_follows_a_changed_case():
    changed = build_demo(replace(CASE, delay_days=9, lender_yield_usd=20_000))
    r = rows(changed)
    assert r["Total"] == "$60,000" and r["Loan repaid"].startswith("T+9")
    assert "4 days: $720,000" in r["No action"]


# ---- honesty rules ----

@pytest.mark.parametrize("output", [TEXT, HTML])
def test_output_is_labelled_and_claims_nothing(output):
    plain = re.sub(r"&#x27;", "'", output)
    assert BANNER in plain and NO_CAPACITY in plain
    assert "PLACEHOLDER" in plain and "Proposed. No insurer is committed" in plain
    assert chr(0x2014) not in plain and "lodestar" not in plain.lower()
    assert "risk-free" not in plain.lower() and "guarantee" not in plain.lower().replace("average guarantee", "")
    assert "Long-stop date" in plain and "Not set" in plain


def test_html_is_self_contained_and_escaped():
    assert HTML.startswith("<!doctype html>") and HTML.rstrip().endswith("</html>")
    assert not re.search(r"<script|<link|<img|src=|href=|url\(|@import", HTML, re.I)
    assert "Lloyd&#x27;s" in HTML and "Lloyd's capacity" not in HTML
    for value in ("$68,000", "$28,000", "$16,000", "$24,000", "Hub B", "T+11"):
        assert value in HTML


def test_html_escapes_hostile_stock_names():
    stock = [Lot("<script>x</script>", "SABIC", "Geleen", "PP 575P", "Rotterdam", 40)]
    page = render_html(build_demo(stock=stock))
    assert "<script>" not in page and "&lt;script&gt;" in page


# ---- paths that end without a swap ----

def test_no_alert_when_stock_covers_the_delay():
    for case in (replace(CASE, delay_days=4), replace(CASE, delay_days=5), replace(CASE, delay_days=0),
                 replace(CASE, safety_stock_days=30)):
        d = build_demo(case)
        assert d.alert is None and d.match is None and d.term_sheet is None and not d.verdicts
        assert "No alert" in d.outcome and "TERM SHEET" not in render_text(d)
        assert "Term sheet" not in render_html(d)


def test_one_day_beyond_stock_alerts():
    d = build_demo(replace(CASE, delay_days=6))
    assert d.alert.stockout_days == 1 and d.term_sheet is not None


def test_zero_safety_stock_alerts_on_the_first_late_update():
    d = build_demo(replace(CASE, safety_stock_days=0))
    assert len(d.steps) == 1 and d.alert.stockout_days == 2 and d.alert.lead_days == 20


def test_no_swap_when_no_distributor_has_enough_identical_stock():
    stock = [lot for lot in demo_stock() if lot.distributor != "Hub B"]
    d = build_demo(stock=stock)
    assert d.alert is not None and d.match is None and d.term_sheet is None
    assert "No swap" in d.outcome and "chosen" not in [v.verdict for v in d.verdicts]
    assert build_demo(stock=[]).match is None


def test_partial_lots_from_one_distributor_combine():
    stock = [Lot("Hub C", "SABIC", "Geleen", "PP 575P", "Rotterdam", 20),
             Lot("Hub C", "SABIC", "Geleen", "PP 575P", "Rotterdam", 20, days_until_available=10),
             Lot("Hub C", "SABIC", "Geleen", "PP 575P", "Rotterdam", 20)]
    d = build_demo(stock=stock)
    assert d.match.distributor == "Hub C" and len(d.term_sheet.lots) == 2
    assert [v.verdict for v in d.verdicts] == ["chosen", "fits, not needed", "chosen"]
    assert "20 TEU, in bond at the port now; 20 TEU, in bond at the port now" == rows(d)["Lots"]


def test_identical_twin_lots_are_not_both_marked_chosen():
    twin = Lot("Hub B", "SABIC", "Geleen", "PP 575P", "Rotterdam", 40)
    d = build_demo(stock=[twin, Lot("Hub B", "SABIC", "Geleen", "PP 575P", "Rotterdam", 40)])
    assert [v.verdict for v in d.verdicts] == ["chosen", "fits, not needed"]


def test_tie_between_distributors_is_stable_and_explained():
    stock = [Lot("Hub Z", "SABIC", "Geleen", "PP 575P", "Rotterdam", 40),
             Lot("Hub B", "SABIC", "Geleen", "PP 575P", "Rotterdam", 40)]
    d = build_demo(stock=stock)
    assert d.match.distributor == "Hub B"
    assert d.verdicts[0].verdict.startswith("fits; another distributor")


def test_no_swap_when_it_costs_more_than_the_stoppage():
    d = build_demo(replace(CASE, downtime_cost_per_day_usd=10_000))
    assert d.match is not None and d.term_sheet is None and "cost more" in d.outcome


def test_alert_too_late_to_bind():
    late = (Feed(EtaUpdate("BK", 7, 11), "late notice"),)
    d = build_demo(feed=late)
    assert d.alert.lead_days == 7 and d.term_sheet is None and "too late to bind" in d.outcome
    on_the_line = (Feed(EtaUpdate("BK", 8, 11), "just in time"),)
    assert build_demo(feed=on_the_line).term_sheet is not None


def test_empty_feed_means_no_alert():
    d = build_demo(feed=())
    assert d.steps == () and d.alert is None


# ---- bad inputs ----

@pytest.mark.parametrize("bad", [dict(delay_days=-1), dict(safety_stock_days=-1), dict(teu=0), dict(teu=-40)])
def test_bad_inputs_are_refused(bad):
    with pytest.raises(ValueError):
        build_demo(replace(CASE, **bad))


@pytest.mark.parametrize("bad", [dict(alert=-8, match=-10), dict(match=-6, bind=-8), dict(bind=1)])
def test_schedule_must_run_in_order(bad):
    with pytest.raises(ValueError):
        Schedule(**bad)


def test_why_not_orders_reasons_and_accepts_a_fit():
    need = Need("SABIC", "Geleen", "PP 575P", "Rotterdam", 40, 10)
    assert why_not(Lot("H", "SABIC", "Geleen", "PP 575P", "Rotterdam", 40, 10), need) is None
    assert why_not(Lot("H", "Borealis", "Geleen", "PP 575P", "Rotterdam", 40), need) == "different producer"
    assert why_not(Lot("H", "SABIC", "Geleen", "PP 575P", "Rotterdam", 0), need) == "no stock in the lot"
    assert why_not(Lot("H", "SABIC", "Geleen", "PP 575P", "Rotterdam", 40, 11), need) == "available too late"


# ---- dates and the command line ----

def test_day_labels():
    assert (day(0), day(-12), day(11)) == ("T", "T-12", "T+11")
    assert day(-12, date(2027, 3, 1)) == "T-12 (17 Feb 2027)"
    assert day(11, date(2027, 2, 25)) == "T+11 (08 Mar 2027)"


def test_cli_prints_and_writes_html(tmp_path, capsys):
    target = tmp_path / "new" / "demo.html"
    assert main(["--html", str(target), "--arrival", "2027-03-01"]) == 0
    printed = capsys.readouterr().out
    assert printed.startswith(BANNER) and "$68,000" in printed and "12 Mar 2027" in printed
    assert target.read_text(encoding="utf-8").startswith("<!doctype html>")


def test_cli_no_alert_and_bad_input(capsys):
    assert main(["--delay", "4"]) == 0
    assert "No alert" in capsys.readouterr().out
    assert main(["--delay", "-3"]) == 2
    assert "non-negative" in capsys.readouterr().err
    with pytest.raises(SystemExit):
        main(["--arrival", "next week"])
