"""Split shipments on the demo: two mock bills of lading checked together before bind."""
from dataclasses import replace

import pytest

from steadpoc.collateral import CHECK_FREE, CHECK_MATCH
from steadpoc.demo import (COLLATERAL_CASES, CollateralCase, build_demo, collateral_docs, main,
                           render_html, render_text, split_ref, split_teu)
from steadpoc.economics import SwapCase

CASE = SwapCase()


def failed(result):
    return {f.check for f in result.findings if not f.passed}


@pytest.mark.parametrize("teu,parts,want", [(40, 2, [20, 20]), (41, 2, [21, 20]), (40, 3, [14, 13, 13]),
                                            (1, 1, [1]), (2, 2, [1, 1])])
def test_split_teu_is_even_and_adds_up(teu, parts, want):
    assert split_teu(teu, parts) == want and sum(want) == teu


def test_split_teu_refuses_more_parts_than_boxes():
    with pytest.raises(ValueError):
        split_teu(1, 2)


def test_split_refs_are_lettered():
    assert [split_ref(i) for i in range(3)] == ["BL-DEMO-001A", "BL-DEMO-001B", "BL-DEMO-001C"]


@pytest.mark.parametrize("teu", [2, 20, 40, 81])
def test_split_docs_follow_the_case_size(teu):
    docs = collateral_docs(replace(CASE, teu=teu), COLLATERAL_CASES["split"])
    assert len(docs) == 2 and sum(d.teu for d in docs) == teu
    assert sum(d.tonnes for d in docs) == teu * 24


def test_split_binds_and_money_unchanged():
    d = build_demo(collateral=COLLATERAL_CASES["split"])
    base = build_demo()
    assert d.collateral.binds and d.collateral.doc_refs == ("BL-DEMO-001A", "BL-DEMO-001B")
    assert d.term_sheet is not None
    assert d.term_sheet.case == base.term_sheet.case and d.outcome == base.outcome


@pytest.mark.parametrize("name,check", [("split-pledged", CHECK_FREE), ("split-short", CHECK_MATCH)])
def test_bad_split_cases_refuse_with_one_reason(name, check):
    d = build_demo(collateral=COLLATERAL_CASES[name])
    assert not d.collateral.binds and failed(d.collateral) == {check}
    assert d.term_sheet is None and "No swap" in d.outcome


def test_split_short_names_the_shortfall():
    text = render_text(build_demo(collateral=COLLATERAL_CASES["split-short"]))
    assert "20 TEU on the document, 40 on the order" in text


def test_split_pledged_names_the_second_bill():
    text = render_text(build_demo(collateral=COLLATERAL_CASES["split-pledged"]))
    assert "Demo Bank holds a bank pledge over BL-DEMO-001B" in text


def test_split_with_tonnes_short_and_grade_change():
    cc = CollateralCase("split, wrong", parts=2, tonnes_short=30, grade="PP 571P")
    r = build_demo(collateral=cc).collateral
    text = next(f.detail for f in r.findings if f.check == CHECK_MATCH)
    assert "930 t together" in text and "BL-DEMO-001A: grade" in text and "BL-DEMO-001B: grade" in text


def test_split_earlier_swap_ties_the_first_part():
    r = build_demo(collateral=CollateralCase("x", parts=2, earlier_swap="OLD")).collateral
    assert r.reasons == ["BL-DEMO-001A already backs swap OLD"]


def test_split_bank_holds_both():
    r = build_demo(collateral=CollateralCase("x", parts=2, holder="Demo Bank")).collateral
    assert r.reasons[0].count("Demo Bank holds the original") == 2


@pytest.mark.parametrize("kw", [dict(parts=0), dict(parts=True), dict(parts=2.0),
                                dict(parts=2, offered_parts=0), dict(parts=2, offered_parts=3),
                                dict(offered_parts=2)])
def test_bad_split_cases_rejected(kw):
    with pytest.raises(ValueError):
        CollateralCase("bad", **kw)


def test_split_tonnes_short_cannot_empty_the_last_part():
    with pytest.raises(ValueError):
        collateral_docs(CASE, CollateralCase("x", parts=2, tonnes_short=480))


def test_split_on_one_teu_order_raises():
    with pytest.raises(ValueError):
        collateral_docs(replace(CASE, teu=1), COLLATERAL_CASES["split"])


@pytest.mark.parametrize("name", ["split", "split-pledged", "split-short"])
def test_html_and_text_render_split_cases(name):
    d = build_demo(collateral=COLLATERAL_CASES[name])
    for out in (render_text(d), render_html(d)):
        assert "BL-DEMO-001A" in out and chr(0x2014) not in out and "Lodestar" not in out


def test_cli_split_runs(capsys):
    assert main(["--collateral", "split"]) == 0
    out = capsys.readouterr().out
    assert "LOAN MAY BIND" in out and "2 bills of lading" in out and "Total                $68,000" in out
