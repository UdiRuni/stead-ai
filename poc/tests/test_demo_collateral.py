"""The collateral check on the demo: it runs just before bind, every failing reason is
shown, a refused check stops the swap, and the worked-case money never moves."""
from dataclasses import replace

import pytest

from steadpoc.collateral import CHECKS, SecurityInterest
from steadpoc.demo import (COLLATERAL_CASES, COLLATERAL_SECTION, DOC_REF, PLANT, Schedule,
                           CollateralCase, build_demo, collateral_doc, collateral_order,
                           collateral_rows, main, render_html, render_text, term_sheet_rows)
from steadpoc.economics import SwapCase

CASE = SwapCase()
FAILING = {"pledged": [2], "mismatch": [0], "bank-holds": [1, 2], "second-swap": [3]}


def sheet_section(demo, title):
    return dict(dict(term_sheet_rows(demo.term_sheet, demo.arrival))[title])


# ---- the default path: clean documents, the swap is offered as before ----

def test_default_demo_runs_the_check_and_binds():
    d = build_demo()
    assert d.collateral is not None and d.collateral.binds
    assert d.term_sheet.collateral is d.collateral
    assert d.outcome.startswith("Swap offered")
    assert [f.check for f in d.collateral.findings] == list(CHECKS)


def test_worked_case_money_unchanged_by_the_check():
    for name in COLLATERAL_CASES:
        d = build_demo(collateral=COLLATERAL_CASES[name])
        if d.term_sheet:
            assert d.term_sheet.case.swap_cost_usd == 68_000
    total = dict(sum((rows for _, rows in term_sheet_rows(build_demo().term_sheet)), []))["Total"]
    assert total == "$68,000"


def test_term_sheet_section_sits_after_goods_and_lists_four_checks():
    d = build_demo()
    titles = [t for t, _ in term_sheet_rows(d.term_sheet)]
    assert titles[titles.index(COLLATERAL_SECTION) - 1] == "Goods"
    assert titles[titles.index(COLLATERAL_SECTION) + 1].startswith("Dates")
    r = sheet_section(d, COLLATERAL_SECTION)
    assert list(r) == ["Document", "Holder", "Security", "One lot", "Checked"]
    assert all(r[k].startswith("Pass: ") for k in ("Document", "Holder", "Security", "One lot"))
    assert "T-8" in r["Checked"] and "no register, bank or document system" in r["Checked"]


def test_section_labels_do_not_clash_with_other_rows():
    d = build_demo()
    labels = [label for _, rows in term_sheet_rows(d.term_sheet) for label, _ in rows]
    assert len(labels) == len(set(labels))


def test_released_pledge_binds():
    d = build_demo(collateral=COLLATERAL_CASES["released"])
    assert d.collateral.binds and d.term_sheet is not None


# ---- refused paths: the "no swap" outcome is shown on screen ----

@pytest.mark.parametrize("name,failing", FAILING.items())
def test_each_bad_case_refuses_the_loan_with_its_reasons(name, failing):
    d = build_demo(collateral=COLLATERAL_CASES[name])
    assert d.term_sheet is None and d.match is not None
    assert d.outcome.startswith("No swap: the late boxes cannot secure the loan")
    assert [i for i, f in enumerate(d.collateral.findings) if not f.passed] == failing
    for reason in d.collateral.reasons:
        assert reason in d.outcome
    text = render_text(d)
    assert "LOAN DOES NOT BIND" in text and "TERM SHEET" not in text
    assert text.count("[FAIL]") == len(failing)


def test_bank_holds_lists_both_reasons_at_once():
    d = build_demo(collateral=COLLATERAL_CASES["bank-holds"])
    assert "Demo Bank holds the original bill of lading, not Demo Plant BV" in d.outcome
    assert "Demo Bank holds a letter of credit over BL-DEMO-001" in d.outcome


def test_mismatch_names_grade_and_tonnes():
    d = build_demo(collateral=COLLATERAL_CASES["mismatch"])
    assert "'PP 571P' on the document, 'PP 575P' on the order" in d.outcome
    assert "900 t on the document, 960 t on the order" in d.outcome


def test_refusal_points_to_the_purchase_route():
    d = build_demo(collateral=COLLATERAL_CASES["pledged"])
    assert "Buying the lots outright needs no such security" in d.outcome


def test_combined_failures_all_listed():
    cc = CollateralCase("everything wrong", holder="Demo Bank", grade="PP 571P",
                        interests=(SecurityInterest(DOC_REF, "Other Lender", "lien"),),
                        earlier_swap="SW-OLD")
    d = build_demo(collateral=cc)
    assert len(d.collateral.reasons) == 4 and all(r in d.outcome for r in d.collateral.reasons)


def test_interest_on_another_document_is_ignored():
    cc = CollateralCase("pledge on another lot",
                        interests=(SecurityInterest("BL-OTHER", "Demo Bank", "bank pledge"),))
    assert build_demo(collateral=cc).collateral.binds


def test_holder_and_grade_compare_ignoring_case_and_spaces():
    cc = CollateralCase("same, other spelling", holder="  demo plant bv ", grade="pp 575p")
    assert build_demo(collateral=cc).collateral.binds


# ---- the check runs at the bind day, and only when the swap would otherwise bind ----

def test_pledge_released_on_the_bind_day_binds_one_day_later_does_not():
    on = CollateralCase("released on bind day",
                        interests=(SecurityInterest(DOC_REF, "Demo Bank", "bank pledge", released_on=-8),))
    late = CollateralCase("released after bind",
                          interests=(SecurityInterest(DOC_REF, "Demo Bank", "bank pledge", released_on=-7),))
    assert build_demo(collateral=on).collateral.binds
    assert not build_demo(collateral=late).collateral.binds


def test_check_follows_the_schedule_bind_day():
    # the "released" mock pledge ends at T-20, so a bind at T-25 still finds it in force
    early = Schedule(alert=-30, match=-28, bind=-25)
    feed_case = replace(CASE)
    d = build_demo(feed_case, schedule=early, collateral=COLLATERAL_CASES["released"])
    assert d.collateral is not None and not d.collateral.binds
    assert "T-25" in render_text(d)


@pytest.mark.parametrize("kw", [dict(case=replace(CASE, delay_days=4)),    # no alert
                                dict(stock=[]),                              # no match
                                dict(long_stop_day=11),                      # long stop too early
                                dict(other_on_vessel_usd=2_500_000)])        # vessel limit full
def test_no_check_when_the_swap_is_refused_earlier(kw):
    d = build_demo(collateral=COLLATERAL_CASES["pledged"], **kw)
    assert d.collateral is None and d.term_sheet is None
    assert "COLLATERAL CHECK" not in render_text(d)
    assert "Collateral check" not in render_html(d)


def test_not_worth_it_is_refused_before_the_check():
    d = build_demo(replace(CASE, downtime_cost_per_day_usd=1), collateral=COLLATERAL_CASES["pledged"])
    assert "cost more" in d.outcome and d.collateral is None


# ---- mock documents follow the case ----

@pytest.mark.parametrize("teu", [1, 20, 40, 80])
def test_order_and_document_follow_the_case_size(teu):
    case = replace(CASE, teu=teu)
    order, doc = collateral_order(case), collateral_doc(case, COLLATERAL_CASES["clean"])
    assert order.teu == doc.teu == teu and order.tonnes == doc.tonnes == teu * 24
    assert order.consignee == doc.holder == PLANT


def test_bad_mock_inputs_are_refused():
    with pytest.raises(ValueError):
        CollateralCase("negative", tonnes_short=-1)
    with pytest.raises(ValueError):
        collateral_doc(CASE, CollateralCase("all gone", tonnes_short=960))


def test_each_build_uses_a_fresh_register():
    # a clean build after a second-swap build must still bind: no state leaks
    build_demo(collateral=COLLATERAL_CASES["second-swap"])
    assert build_demo().collateral.binds
    assert build_demo().collateral.binds


# ---- rendering and honesty ----

def test_text_shows_mock_label_and_order_of_steps():
    text = render_text(build_demo())
    assert "MOCK DOCUMENTS, a proposed check" in text and "LOAN MAY BIND" in text
    assert text.index("2. MATCH") < text.index("3. COLLATERAL CHECK") < text.index("RESULT:") \
        < text.index("4. TERM SHEET")


def test_html_shows_the_check_and_marks_failures():
    ok = render_html(build_demo())
    assert "<h2>3. Collateral check</h2>" in ok and "<h2>4. Term sheet</h2>" in ok
    assert "loan may bind" in ok and COLLATERAL_SECTION in ok
    bad = render_html(build_demo(collateral=COLLATERAL_CASES["pledged"]))
    assert "loan does not bind" in bad and '<tr class="alert"><td>no other lender' in bad
    assert "Term sheet" not in bad


def test_collateral_rows_with_calendar_dates():
    from datetime import date
    d = build_demo(arrival=date(2027, 3, 1))
    r = dict(collateral_rows(d.collateral, d.schedule.bind, d.arrival))
    assert "T-8 (21 Feb 2027)" in r["Checked"]


@pytest.mark.parametrize("name", list(COLLATERAL_CASES))
def test_no_em_dash_no_banned_name_every_case(name):
    d = build_demo(collateral=COLLATERAL_CASES[name])
    for out in (render_text(d), render_html(d)):
        assert chr(0x2014) not in out and "Lodestar" not in out
        assert "ILLUSTRATIVE CASE" in out
        assert "capacity, insurer, distributor or customer is committed today" in out


# ---- command line ----

@pytest.mark.parametrize("name", list(COLLATERAL_CASES))
def test_cli_every_case_runs(name, capsys):
    assert main(["--collateral", name]) == 0
    out = capsys.readouterr().out
    binds = name in ("clean", "released")
    assert ("LOAN MAY BIND" in out) == binds and ("TERM SHEET" in out) == binds


def test_cli_rejects_unknown_case(capsys):
    with pytest.raises(SystemExit) as exit_info:
        main(["--collateral", "forged"])
    assert exit_info.value.code == 2
    assert "invalid choice" in capsys.readouterr().err


def test_cli_default_still_offers_the_swap(capsys):
    assert main([]) == 0
    out = capsys.readouterr().out
    assert "Swap offered" in out and "Total                $68,000" in out
    assert out.index("COLLATERAL CHECK") < out.index("COST OF THE SWAP")
