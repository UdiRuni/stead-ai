"""Collateral check over a shipment split across several bills of lading. Mock data only."""
import subprocess
import sys
from pathlib import Path

import pytest

from steadpoc.collateral import (CHECK_FREE, CHECK_HOLDER, CHECK_MATCH, CHECK_ONE, CHECKS, ORDER,
                                 PLANT, LotRegister, SecurityInterest, bind, bind_split,
                                 check_collateral, check_split, format_result, mock_doc, report,
                                 split_scenarios)

POC = Path(__file__).resolve().parents[1]


def failed(result):
    return {f.check for f in result.findings if not f.passed}


def detail(result, name):
    return next(f.detail for f in result.findings if f.check == name)


def pair(a_teu=25, b_teu=15, **b_changes):
    a = mock_doc(doc_ref="BL-A", teu=a_teu, tonnes=a_teu * 24)
    b = mock_doc(**{"doc_ref": "BL-B", "teu": b_teu, "tonnes": b_teu * 24, **b_changes})
    return a, b


# ---- the clean split binds and ties every part ----

def test_two_clean_bills_bind_together():
    reg = LotRegister()
    result = bind_split("S1", ORDER, pair(), reg)
    assert result.binds and result.reasons == []
    assert result.doc_refs == ("BL-A", "BL-B") and result.doc_ref == "BL-A, BL-B"
    assert reg.docs_for("S1") == ("BL-A", "BL-B") and len(reg) == 2
    assert "2 bills of lading" in detail(result, CHECK_MATCH)
    assert "40 TEU, 960 t" in detail(result, CHECK_MATCH)
    assert "both documents" in detail(result, CHECK_HOLDER)


def test_three_parts_and_uneven_sizes():
    docs = [mock_doc(doc_ref=f"BL-{i}", teu=t, tonnes=t * 24) for i, t in enumerate((1, 1, 38))]
    result = check_split("S", ORDER, docs, LotRegister())
    assert result.binds and "all 3" in detail(result, CHECK_HOLDER)


def test_mixed_document_kinds_are_named_documents():
    a, b = pair(kind="delivery order")
    result = check_split("S", ORDER, (a, b), LotRegister())
    assert result.binds and "2 documents" in detail(result, CHECK_MATCH)


def test_two_delivery_orders_plural():
    docs = [mock_doc(doc_ref=r, kind="delivery order", teu=20, tonnes=480) for r in ("D1", "D2")]
    assert "2 delivery orders" in detail(check_split("S", ORDER, docs, LotRegister()), CHECK_MATCH)


def test_one_document_is_exactly_the_single_check():
    for doc in (mock_doc(), mock_doc(holder="Demo Bank"), mock_doc(grade="PP 571P", tonnes=900)):
        one = check_split("S", ORDER, [doc], LotRegister())
        assert one == check_collateral("S", ORDER, doc, LotRegister())


# ---- quantity: together the parts must carry the whole order ----

@pytest.mark.parametrize("a,b,ok", [(25, 15, True), (20, 20, True), (25, 10, False),
                                    (25, 20, False), (39, 2, False)])
def test_teu_must_add_up_exactly(a, b, ok):
    result = check_split("S", ORDER, pair(a, b), LotRegister())
    assert result.binds is ok
    if not ok:
        assert f"{a + b} TEU together, the order 40" in detail(result, CHECK_MATCH)


def test_part_missing_refuses_with_the_shortfall():
    result = check_split("S", ORDER, [mock_doc(doc_ref="BL-A", teu=25, tonnes=600)], LotRegister())
    assert failed(result) == {CHECK_MATCH}
    assert "25 TEU on the document, 40 on the order" in detail(result, CHECK_MATCH)


def test_tonnes_add_up_within_tolerance():
    a, b = pair(tonnes=350)                         # 600 + 350 = 950 of 960
    assert not check_split("S", ORDER, (a, b), LotRegister()).binds
    assert "950 t together, the order 960 t" in detail(
        check_split("S", ORDER, (a, b), LotRegister()), CHECK_MATCH)
    assert check_split("S", ORDER, (a, b), LotRegister(), tonnes_tolerance=0.011).binds
    assert not check_split("S", ORDER, (a, b), LotRegister(), tonnes_tolerance=0.01).binds


def test_tonnes_too_many_also_refused():
    a, b = pair(tonnes=400)
    assert "1000 t together" in detail(check_split("S", ORDER, (a, b), LotRegister()), CHECK_MATCH)


# ---- identity: every part must name the order ----

@pytest.mark.parametrize("field,value", [("booking", "BK-OTHER"), ("consignee", "Other Plant"),
                                         ("producer", "Borealis"), ("plant", "Schwechat"),
                                         ("grade", "PP 571P")])
def test_one_wrong_part_refuses_and_is_named(field, value):
    result = check_split("S", ORDER, pair(**{field: value}), LotRegister())
    assert CHECK_MATCH in failed(result)
    assert f"BL-B: {field} {value!r}" in detail(result, CHECK_MATCH)
    assert "BL-A:" not in detail(result, CHECK_MATCH)


def test_names_compare_ignoring_case_and_spaces():
    result = check_split("S", ORDER, pair(grade=" pp 575p ", holder="DEMO PLANT BV "), LotRegister())
    assert result.binds


def test_same_document_twice_is_refused():
    a, _ = pair(20, 20)
    a2 = mock_doc(doc_ref="BL-A", teu=20, tonnes=480)
    result = check_split("S", ORDER, (a, a2), LotRegister())
    assert "BL-A is offered twice" in detail(result, CHECK_MATCH)
    assert result.doc_refs == ("BL-A",)


# ---- vessels: one late shipment, one vessel ----

def test_two_vessels_refused_not_handled():
    result = check_split("S", ORDER, pair(vessel="MV OTHER"), LotRegister())
    assert failed(result) == {CHECK_MATCH}
    assert "more than one vessel (MV DEMO, MV OTHER)" in detail(result, CHECK_MATCH)


def test_vessel_compare_ignores_case_and_blank_names():
    assert check_split("S", ORDER, pair(vessel=" mv demo"), LotRegister()).binds
    assert check_split("S", ORDER, pair(vessel=""), LotRegister()).binds


# ---- holder and security on any part ----

def test_bank_holding_one_part_refuses():
    result = check_split("S", ORDER, pair(holder="Demo Bank"), LotRegister())
    assert failed(result) == {CHECK_HOLDER}
    assert "Demo Bank holds the original bill of lading BL-B" in detail(result, CHECK_HOLDER)


def test_pledge_on_one_part_refuses_and_release_day_counts():
    live = [SecurityInterest("BL-B", "Demo Bank", "bank pledge")]
    assert failed(check_split("S", ORDER, pair(), LotRegister(), live)) == {CHECK_FREE}
    on_day = [SecurityInterest("BL-B", "Demo Bank", "bank pledge", released_on=-8)]
    late = [SecurityInterest("BL-B", "Demo Bank", "bank pledge", released_on=-7)]
    assert check_split("S", ORDER, pair(), LotRegister(), on_day).binds
    assert not check_split("S", ORDER, pair(), LotRegister(), late).binds


def test_pledge_on_a_document_outside_the_set_is_ignored():
    other = [SecurityInterest("BL-Z", "Demo Bank", "bank pledge")]
    assert check_split("S", ORDER, pair(), LotRegister(), other).binds


def test_pledges_on_both_parts_all_listed():
    both = [SecurityInterest("BL-A", "Bank 1", "bank pledge"), SecurityInterest("BL-B", "Bank 2", "lien")]
    text = detail(check_split("S", ORDER, pair(), LotRegister(), both), CHECK_FREE)
    assert "Bank 1 holds a bank pledge over BL-A" in text and "Bank 2 holds a lien over BL-B" in text


# ---- register: the set is one lot ----

def test_a_part_already_backing_another_swap_refuses():
    reg = LotRegister()
    reg.tie("BL-B", "OLD")
    result = bind_split("S", ORDER, pair(), reg)
    assert failed(result) == {CHECK_ONE}
    assert "BL-B already backs swap OLD" in detail(result, CHECK_ONE)
    assert reg.docs_for("S") == () and len(reg) == 1      # nothing tied on refusal


def test_swap_with_another_lot_refuses():
    reg = LotRegister()
    reg.tie("BL-X", "S")
    assert "swap S already has lot BL-X" in detail(check_split("S", ORDER, pair(), reg), CHECK_ONE)


def test_rebinding_the_same_set_is_harmless():
    reg = LotRegister()
    assert bind_split("S", ORDER, pair(), reg).binds
    assert bind_split("S", ORDER, pair(), reg).binds
    assert len(reg) == 2


def test_release_frees_every_part():
    reg = LotRegister()
    bind_split("S1", ORDER, pair(), reg)
    assert reg.release_all("S1") == ("BL-A", "BL-B") and len(reg) == 0
    assert reg.release_all("S1") == ()
    assert bind_split("S2", ORDER, pair(), reg).binds


def test_single_release_also_frees_the_whole_split_lot():
    reg = LotRegister()
    bind_split("S1", ORDER, pair(), reg)
    assert reg.release("S1") == "BL-A" and len(reg) == 0


def test_split_lot_blocks_single_document_binds():
    reg = LotRegister()
    bind_split("S1", ORDER, pair(), reg)
    assert not bind("S2", ORDER, mock_doc(doc_ref="BL-A"), reg).binds


def test_tie_all_refuses_bad_input_and_is_all_or_none():
    reg = LotRegister()
    reg.tie("BL-B", "OLD")
    with pytest.raises(ValueError):
        reg.tie_all(("BL-A", "BL-B"), "S")
    assert reg.swap_for("BL-A") is None                   # nothing half-tied
    for bad in ((), ("BL-C", "BL-C"), ("BL-C", " ")):
        with pytest.raises(ValueError):
            reg.tie_all(bad, "S")
    with pytest.raises(ValueError):
        reg.tie_all(("BL-C",), "")


def test_check_alone_never_ties():
    reg = LotRegister()
    check_split("S", ORDER, pair(), reg)
    assert len(reg) == 0


# ---- all reasons at once, bad calls ----

def test_every_failing_check_reported_together():
    reg = LotRegister()
    reg.tie("BL-A", "OLD")
    docs = pair(10, 10, holder="Demo Bank", vessel="MV OTHER")
    result = check_split("S", ORDER, docs, reg, [SecurityInterest("BL-B", "Demo Bank", "letter of credit")])
    assert failed(result) == set(CHECKS)
    text = detail(result, CHECK_MATCH)
    assert "more than one vessel" in text and "20 TEU together" in text


@pytest.mark.parametrize("docs", [(), [None], ["BL-A"]])
def test_bad_document_lists_raise(docs):
    with pytest.raises(ValueError):
        check_split("S", ORDER, docs, LotRegister())


def test_bad_swap_id_and_tolerance_raise():
    with pytest.raises(ValueError):
        check_split(" ", ORDER, pair(), LotRegister())
    for tol in (-0.1, 1, 2):
        with pytest.raises(ValueError):
            check_split("S", ORDER, pair(), LotRegister(), tonnes_tolerance=tol)


def test_generator_input_is_accepted():
    assert check_split("S", ORDER, (d for d in pair()), LotRegister()).binds


# ---- scenarios and report ----

def test_split_scenarios_give_the_expected_verdicts():
    results = split_scenarios()
    assert [r.binds for _, r in results] == [True, False, False, False, False]
    assert [failed(r) for _, r in results[1:]] == [{CHECK_MATCH}, {CHECK_FREE}, {CHECK_MATCH}, {CHECK_ONE}]


def test_report_includes_split_cases_and_house_rules():
    text = report()
    assert text.count("Split:") == 5 and "bills of lading" in text
    assert chr(0x2014) not in text and "Lodestar" not in text
    assert "bill of ladings" not in text and "all 2" not in text


def test_format_of_a_split_result():
    text = format_result(check_split("S", ORDER, pair(), LotRegister()))
    assert text.startswith("Swap S, lot BL-A, BL-B: LOAN MAY BIND") and text.count("[pass]") == 4


def test_command_line_shows_split_cases():
    out = subprocess.run([sys.executable, "-m", "steadpoc.collateral"], cwd=POC,
                         capture_output=True, text=True, check=True).stdout
    assert "Split: two clean bills of lading" in out
