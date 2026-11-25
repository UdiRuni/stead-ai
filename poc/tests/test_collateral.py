"""Collateral check before a loan binds. Mock data only."""
import subprocess
import sys
from pathlib import Path

import pytest

from steadpoc.collateral import (BANNER, BIND_DAY, CHECK_FREE, CHECK_HOLDER, CHECK_MATCH,
                                 CHECK_ONE, CHECKS, ORDER, PLANT, LotRegister, Order,
                                 SecurityInterest, TransportDoc, bind, check_collateral,
                                 format_result, mock_doc, report, scenarios)

POC = Path(__file__).resolve().parents[1]


def finding(result, name):
    return next(f for f in result.findings if f.check == name)


def failed(result):
    return {f.check for f in result.findings if not f.passed}


# validation

@pytest.mark.parametrize("field,value", [
    ("booking", ""), ("consignee", "  "), ("producer", ""), ("plant", ""), ("grade", ""),
    ("teu", 0), ("teu", -1), ("teu", 2.5), ("teu", True), ("tonnes", 0), ("tonnes", -3),
])
def test_bad_orders_are_rejected(field, value):
    kwargs = dict(booking="B", consignee="P", producer="X", plant="Y", grade="G", teu=1, tonnes=1)
    kwargs[field] = value
    with pytest.raises(ValueError):
        Order(**kwargs)


@pytest.mark.parametrize("field,value", [
    ("doc_ref", ""), ("kind", "invoice"), ("kind", ""), ("holder", ""), ("booking", " "),
    ("teu", 0), ("tonnes", 0), ("tonnes", -1),
])
def test_bad_documents_are_rejected(field, value):
    with pytest.raises(ValueError):
        mock_doc(**{field: value})


def test_delivery_order_is_an_accepted_kind():
    result = check_collateral("S", ORDER, mock_doc(kind="delivery order"), LotRegister())
    assert result.binds
    assert "delivery order" in finding(result, CHECK_MATCH).detail


@pytest.mark.parametrize("kwargs", [dict(doc_ref=""), dict(holder=""), dict(kind="")])
def test_bad_security_interests_are_rejected(kwargs):
    base = dict(doc_ref="D", holder="Bank", kind="pledge")
    base.update(kwargs)
    with pytest.raises(ValueError):
        SecurityInterest(**base)


@pytest.mark.parametrize("tol", [-0.01, 1, 1.5])
def test_tolerance_must_be_in_range(tol):
    with pytest.raises(ValueError):
        check_collateral("S", ORDER, mock_doc(), LotRegister(), tonnes_tolerance=tol)


def test_swap_id_is_required():
    with pytest.raises(ValueError):
        check_collateral("", ORDER, mock_doc(), LotRegister())


# check 1: document matches the order

def test_clean_lot_passes_all_four_checks_in_order():
    result = check_collateral("S", ORDER, mock_doc(), LotRegister())
    assert result.binds and result.reasons == []
    assert tuple(f.check for f in result.findings) == CHECKS


@pytest.mark.parametrize("field,value", [
    ("booking", "BK-OTHER"), ("consignee", "Other Plant"), ("producer", "Borealis"),
    ("plant", "Al Jubail"), ("grade", "PP 571P"), ("teu", 20), ("tonnes", 959),
])
def test_each_mismatch_refuses_and_is_named(field, value):
    changes = {field: value}
    if field == "consignee":
        changes["holder"] = value        # keep check 2 about holder, not consignee
    result = check_collateral("S", ORDER, mock_doc(**changes), LotRegister())
    assert not result.binds
    assert CHECK_MATCH in failed(result)
    assert str(value) in finding(result, CHECK_MATCH).detail or f"{value:g}" in finding(result, CHECK_MATCH).detail


def test_several_mismatches_are_all_listed():
    result = check_collateral("S", ORDER, mock_doc(grade="PP 571P", teu=20, tonnes=480), LotRegister())
    detail = finding(result, CHECK_MATCH).detail
    assert "grade" in detail and "20 TEU" in detail and "480 t" in detail


def test_case_and_outer_spaces_do_not_count_as_a_mismatch():
    doc = mock_doc(grade=" pp 575p ", producer="sabic", consignee=PLANT.upper(), holder=PLANT.lower())
    assert check_collateral("S", ORDER, doc, LotRegister()).binds


def test_inner_differences_in_a_grade_code_do_count():
    assert not check_collateral("S", ORDER, mock_doc(grade="PP575P"), LotRegister()).binds


def test_tonnes_tolerance_edges():
    reg = LotRegister()
    # 1% of 960 t is 9.6 t
    assert check_collateral("S", ORDER, mock_doc(tonnes=969.6), reg, tonnes_tolerance=0.01).binds
    assert check_collateral("S", ORDER, mock_doc(tonnes=950.4), reg, tonnes_tolerance=0.01).binds
    assert not check_collateral("S", ORDER, mock_doc(tonnes=969.7), reg, tonnes_tolerance=0.01).binds
    assert not check_collateral("S", ORDER, mock_doc(tonnes=960.1), reg).binds   # default exact


def test_tolerance_never_excuses_a_teu_gap():
    assert not check_collateral("S", ORDER, mock_doc(teu=39), LotRegister(), tonnes_tolerance=0.5).binds


# check 2: plant holds the documents

def test_bank_holding_the_originals_refuses_even_with_no_interest_on_file():
    result = check_collateral("S", ORDER, mock_doc(holder="Demo Bank"), LotRegister())
    assert failed(result) == {CHECK_HOLDER}
    assert "Demo Bank holds the original" in result.reasons[0]


# check 3: no other lender holds it as security

def test_interest_in_force_refuses():
    interests = [SecurityInterest("BL-DEMO-001", "Demo Bank", "bank pledge")]
    result = check_collateral("S", ORDER, mock_doc(), LotRegister(), interests)
    assert failed(result) == {CHECK_FREE}
    assert "Demo Bank holds a bank pledge" in result.reasons[0]


@pytest.mark.parametrize("released_on,binds", [
    (None, False), (BIND_DAY - 1, True), (BIND_DAY, True), (BIND_DAY + 1, False), (5, False),
])
def test_release_day_against_bind_day(released_on, binds):
    interests = [SecurityInterest("BL-DEMO-001", "Demo Bank", "bank pledge", released_on)]
    assert check_collateral("S", ORDER, mock_doc(), LotRegister(), interests).binds is binds


def test_bind_day_can_be_moved():
    interests = [SecurityInterest("BL-DEMO-001", "Demo Bank", "bank pledge", released_on=-5)]
    assert not check_collateral("S", ORDER, mock_doc(), LotRegister(), interests, bind_day=-8).binds
    assert check_collateral("S", ORDER, mock_doc(), LotRegister(), interests, bind_day=-5).binds


def test_interest_on_another_document_does_not_count():
    interests = [SecurityInterest("BL-OTHER", "Demo Bank", "bank pledge")]
    assert check_collateral("S", ORDER, mock_doc(), LotRegister(), interests).binds


def test_two_lenders_are_both_named():
    interests = [SecurityInterest("BL-DEMO-001", "Bank A", "bank pledge"),
                 SecurityInterest("BL-DEMO-001", "Lender B", "trade finance lien"),
                 SecurityInterest("BL-DEMO-001", "Bank C", "bank pledge", released_on=-30)]
    detail = finding(check_collateral("S", ORDER, mock_doc(), LotRegister(), interests), CHECK_FREE).detail
    assert "Bank A" in detail and "Lender B" in detail and "Bank C" not in detail


# check 4: one lot backs one swap

def test_bind_ties_the_lot_and_a_second_swap_is_refused():
    reg = LotRegister()
    assert bind("S1", ORDER, mock_doc(), reg).binds
    assert reg.swap_for("BL-DEMO-001") == "S1" and len(reg) == 1
    second = bind("S2", ORDER, mock_doc(), reg)
    assert failed(second) == {CHECK_ONE}
    assert "already backs swap S1" in second.reasons[0]
    assert reg.swap_for("BL-DEMO-001") == "S1" and len(reg) == 1


def test_rebinding_the_same_swap_and_lot_is_harmless():
    reg = LotRegister()
    bind("S1", ORDER, mock_doc(), reg)
    assert bind("S1", ORDER, mock_doc(), reg).binds
    assert len(reg) == 1


def test_one_swap_cannot_take_a_second_lot():
    reg = LotRegister()
    bind("S1", ORDER, mock_doc(), reg)
    result = bind("S1", ORDER, mock_doc(doc_ref="BL-DEMO-002"), reg)
    assert failed(result) == {CHECK_ONE}
    assert "one lot per swap" in result.reasons[0]
    assert reg.swap_for("BL-DEMO-002") is None


def test_failed_check_leaves_the_register_unchanged():
    reg = LotRegister()
    assert not bind("S1", ORDER, mock_doc(holder="Demo Bank"), reg).binds
    assert len(reg) == 0
    assert bind("S2", ORDER, mock_doc(), reg).binds      # the lot is still free


def test_check_alone_never_ties_the_lot():
    reg = LotRegister()
    check_collateral("S1", ORDER, mock_doc(), reg)
    assert len(reg) == 0


def test_release_frees_the_lot_for_a_new_swap():
    reg = LotRegister()
    bind("S1", ORDER, mock_doc(), reg)
    assert reg.release("S1") == "BL-DEMO-001"
    assert reg.release("S1") is None
    assert reg.release("never") is None
    assert bind("S2", ORDER, mock_doc(), reg).binds


def test_tie_refuses_directly_too():
    reg = LotRegister()
    reg.tie("D1", "S1")
    with pytest.raises(ValueError):
        reg.tie("D1", "S2")
    with pytest.raises(ValueError):
        reg.tie("D2", "S1")
    with pytest.raises(ValueError):
        reg.tie("", "S3")


# all reasons at once

def test_every_failing_check_is_reported_together():
    reg = LotRegister()
    bind("S1", ORDER, mock_doc(), reg)
    doc = mock_doc(grade="PP 571P", holder="Demo Bank")
    interests = [SecurityInterest("BL-DEMO-001", "Demo Bank", "letter of credit")]
    result = bind("S2", ORDER, doc, reg, interests)
    assert failed(result) == set(CHECKS)
    assert len(result.reasons) == 4


# output

def test_format_shows_verdict_and_each_check():
    text = format_result(check_collateral("S", ORDER, mock_doc(holder="Demo Bank"), LotRegister()))
    assert "LOAN DOES NOT BIND" in text and "[FAIL] plant holds the documents" in text
    assert text.count("[pass]") == 3


def test_scenarios_give_the_expected_verdicts():
    verdicts = [r.binds for _, r in scenarios()]
    assert verdicts == [True, False, False, False, True]


def test_report_is_labelled_mock_and_house_rules_hold():
    text = report()
    assert text.startswith(BANNER)
    assert "\u2014" not in text and "Lodestar" not in text
    assert "assumptions" in text


def test_command_line_runs():
    out = subprocess.run([sys.executable, "-m", "steadpoc.collateral"], cwd=POC,
                         capture_output=True, text=True, check=True).stdout
    assert out.startswith("MOCK DATA") and "LOAN DOES NOT BIND" in out
