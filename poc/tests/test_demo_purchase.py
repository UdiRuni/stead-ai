"""The purchase route on the demo term sheet: same numbers as purchase.py, honest wording,
and the edge cases (no cash, no room, price falls, zero holding days, changed cases)."""
from dataclasses import replace

import pytest

from steadpoc.demo import (build_demo, main, purchase_rows, render_html, render_text,
                           term_sheet_rows)
from steadpoc.economics import SwapCase
from steadpoc.purchase import LOAN, PURCHASE, PurchaseCase

CASE = SwapCase()
SECTION = "Or the plant buys the stock outright (assumptions)"


def section(demo):
    found = [rows for title, rows in term_sheet_rows(demo.term_sheet, demo.arrival) if title == SECTION]
    assert len(found) == 1
    return dict(found[0])


def all_labels(demo):
    return [label for _, rows in term_sheet_rows(demo.term_sheet, demo.arrival) for label, _ in rows]


# ---- default: the published worked case ----

def test_default_sheet_carries_the_purchase_route_built_on_the_same_case():
    demo = build_demo()
    p = demo.term_sheet.purchase
    assert p is not None and p.swap == demo.case == CASE
    assert p == PurchaseCase()


def test_default_numbers_match_purchase_module():
    p = PurchaseCase()
    r = section(build_demo())
    assert r["Cost to the plant"].startswith(f"${p.purchase_cost_usd:,.0f}:")
    assert r["Cost to the plant"].startswith("$31,890:")
    assert "8% a year for 30 days ($7,890)" in r["Cost to the plant"]
    assert "stead.ai fee 2.0% ($24,000)" in r["Cost to the plant"]
    assert r["Cost to the plant"].endswith("All assumptions")
    assert r["Against the loan"].startswith("Buying is cheaper than the $68,000 loan")
    assert "3.0%" in r["The loan wins"] and "167 days" in r["The loan wins"]
    assert "$30 per TEU per day" in r["The loan wins"]
    assert "no cash or no room" in r["The loan wins"]
    assert r["stead.ai earns"] == "$24,000 on the loan, $24,000 on the purchase"


def test_published_loan_numbers_untouched():
    rows = {l: v for _, sec in term_sheet_rows(build_demo().term_sheet) for l, v in sec}
    assert rows["Total"] == "$68,000"
    assert "83% to 94%" in rows["Swap"]


def test_section_sits_between_alternatives_and_return_leg():
    titles = [t for t, _ in term_sheet_rows(build_demo().term_sheet)]
    i = titles.index(SECTION)
    assert titles[i - 1] == "Against the alternatives"
    assert titles[i + 1] == "What makes the return leg safe"


def test_row_labels_stay_unique_across_the_sheet():
    labels = all_labels(build_demo())
    assert len(labels) == len(set(labels))


def test_purchase_says_no_loan_and_no_long_stop():
    assert "no loan, no long stop" in section(build_demo())["Same lots, bought"]


# ---- blockers ----

@pytest.mark.parametrize("kw, words", [
    (dict(has_cash=False), "no cash or credit for $1,200,000"),
    (dict(has_room=False), "no room for double stock"),
    (dict(has_cash=False, has_room=False), "no cash"),
])
def test_blocked_purchase_points_to_the_loan(kw, words):
    r = section(build_demo(purchase=PurchaseCase(**kw)))
    assert r["Against the loan"].startswith("Not possible:")
    assert words in r["Against the loan"]
    assert r["Against the loan"].endswith("The loan is the route")
    assert r["The loan wins"] == "Here: buying is not possible"


def test_no_room_with_an_outside_rate_is_not_blocked():
    p = PurchaseCase(has_room=False, storage_usd_per_teu_day=10)
    r = section(build_demo(purchase=p))
    assert not r["Against the loan"].startswith("Not possible")
    assert f"storage ${p.storage_usd:,.0f}" in r["Cost to the plant"]


def test_blocked_purchase_does_not_stop_the_swap():
    demo = build_demo(purchase=PurchaseCase(has_cash=False))
    assert demo.outcome.startswith("Swap offered")


# ---- the loan is cheaper ----

def test_price_fall_beyond_breakeven_makes_the_loan_cheaper():
    p = PurchaseCase(price_change=-0.05)
    assert p.cheaper_route == LOAN
    r = section(build_demo(purchase=p))
    assert r["Against the loan"] == ("The $68,000 loan is cheaper on these assumptions; "
                                     "buying would cost $23,890 more")
    assert "price fall of 5.0% passes the 3.0% break-even" in r["The loan wins"]
    assert "price move $60,000" in r["Cost to the plant"]


def test_expensive_storage_makes_the_loan_cheaper_with_no_price_move():
    r = section(build_demo(purchase=PurchaseCase(storage_usd_per_teu_day=40)))
    assert r["Against the loan"].startswith("The $68,000 loan is cheaper")
    assert r["The loan wins"].endswith("even with no price move")
    assert "-" not in r["The loan wins"]          # no negative break-evens shown


def test_long_holding_makes_the_loan_cheaper():
    r = section(build_demo(purchase=PurchaseCase(extra_holding_days=200)))
    assert r["Against the loan"].startswith("The $68,000 loan is cheaper")


def test_small_price_fall_keeps_purchase_cheaper_and_tightens_breakevens():
    p = PurchaseCase(price_change=-0.02)
    assert p.cheaper_route == PURCHASE
    r = section(build_demo(purchase=p))
    assert r["Against the loan"].startswith("Buying is cheaper")
    assert f"{p.breakeven_holding_days:,.0f} days" in r["The loan wins"]
    assert p.breakeven_holding_days < PurchaseCase().breakeven_holding_days


def test_price_rise_is_shown_as_a_gain():
    r = section(build_demo(purchase=PurchaseCase(price_change=0.05)))
    assert "price move a gain of $60,000" in r["Cost to the plant"]
    assert r["Cost to the plant"].startswith("A net gain of $28,110:")
    assert "$-" not in r["Cost to the plant"]
    assert r["Against the loan"].startswith("Buying is cheaper")


def test_tie_goes_to_purchase():
    # make the purchase cost exactly the loan: fee covers the whole $68,000
    p = PurchaseCase(extra_holding_days=0, purchase_fee_rate=68_000 / 1_200_000)
    assert p.purchase_cost_usd == pytest.approx(p.loan_cost_usd)
    r = section(build_demo(purchase=p))
    assert r["Against the loan"].startswith("Buying is cheaper")


# ---- edge cases ----

def test_zero_holding_days_drops_the_storage_breakeven():
    r = section(build_demo(purchase=PurchaseCase(extra_holding_days=0)))
    assert "for 0 days ($0)" in r["Cost to the plant"]
    assert "per TEU per day" not in r["The loan wins"]
    assert r["Cost to the plant"].startswith("$24,000:")


def test_one_holding_day_is_singular():
    r = section(build_demo(purchase=PurchaseCase(extra_holding_days=1)))
    assert "for 1 day (" in r["Cost to the plant"]


def test_zero_cost_of_capital_has_no_holding_breakeven():
    p = PurchaseCase(cost_of_capital=0)
    assert p.breakeven_holding_days is None
    r = section(build_demo(purchase=p))
    assert "held longer" not in r["The loan wins"]


def test_purchase_follows_a_changed_case_not_its_own_swap():
    case = replace(CASE, delay_days=9)
    stale = PurchaseCase(swap=replace(CASE, notional_usd=1))   # wrong swap on purpose
    demo = build_demo(case, purchase=stale)
    assert demo.term_sheet.purchase.swap == case
    assert demo.term_sheet.purchase.capital_usd == PurchaseCase().capital_usd


def test_assumptions_passed_in_are_kept():
    demo = build_demo(purchase=PurchaseCase(cost_of_capital=0.12, extra_holding_days=45))
    p = demo.term_sheet.purchase
    assert (p.cost_of_capital, p.extra_holding_days) == (0.12, 45)
    assert "12% a year for 45 days" in section(demo)["Cost to the plant"]


def test_purchase_rows_with_no_downtime_say_no_action():
    p = PurchaseCase(swap=replace(CASE, delay_days=3))
    assert purchase_rows(p) == [("Route", "No action needed: the plant's stock covers the delay")]


def test_no_term_sheet_no_purchase_section():
    for demo in (build_demo(replace(CASE, delay_days=4)),          # no alert
                 build_demo(stock=[]),                              # no match
                 build_demo(long_stop_day=11)):                     # long stop too early
        assert demo.term_sheet is None
        assert SECTION.upper() not in render_text(demo)


def test_term_sheet_built_without_purchase_still_renders():
    demo = build_demo()
    bare = replace(demo, term_sheet=replace(demo.term_sheet, purchase=None))
    titles = [t for t, _ in term_sheet_rows(bare.term_sheet)]
    assert SECTION not in titles
    assert "Total" in render_text(bare)


# ---- rendering and honesty ----

def test_text_and_html_show_the_section():
    demo = build_demo()
    assert SECTION.upper() in render_text(demo)
    html = render_html(demo)
    assert SECTION in html and "$31,890" in html


def test_no_em_dashes_and_assumptions_labelled():
    for demo in (build_demo(), build_demo(purchase=PurchaseCase(has_cash=False)),
                 build_demo(purchase=PurchaseCase(price_change=-0.05))):
        text = render_text(demo)
        assert chr(0x2014) not in text
        assert "All assumptions" in text and "(ASSUMPTIONS)" in text
        assert "Lodestar" not in text


# ---- command line ----

def test_cli_flags_reach_the_sheet(capsys):
    assert main(["--no-cash"]) == 0
    assert "Not possible: no cash or credit" in capsys.readouterr().out
    assert main(["--no-room"]) == 0
    assert "no room for double stock" in capsys.readouterr().out
    assert main(["--no-room", "--storage", "40"]) == 0
    out = capsys.readouterr().out
    assert "storage $48,000" in out and "loan is cheaper" in out
    assert main(["--price-change", "-0.05", "--hold-days", "60"]) == 0
    assert "for 60 days" in capsys.readouterr().out


@pytest.mark.parametrize("argv", [["--hold-days", "-1"], ["--storage", "-5"],
                                  ["--price-change", "-1"]])
def test_cli_rejects_bad_purchase_inputs(argv, capsys):
    assert main(argv) == 2
    assert capsys.readouterr().err.startswith("error:")


def test_cli_default_output_unchanged_above_the_new_section(capsys):
    assert main([]) == 0
    out = capsys.readouterr().out
    assert "Total                $68,000" in out
    assert out.index("AGAINST THE ALTERNATIVES") < out.index(SECTION.upper()) \
        < out.index("WHAT MAKES THE RETURN LEG SAFE")
