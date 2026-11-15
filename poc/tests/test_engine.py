import pytest

from steadpoc.matching import Lot, Need, find_match
from steadpoc.simulate import Assumptions, run
from steadpoc.warning import EtaUpdate, evaluate

NEED = Need("SABIC", "Geleen", "PP 575P", "Rotterdam", teu=40, days_until_needed=10)


def lot(distributor="Hub A", grade="PP 575P", plant="Geleen", port="Rotterdam", teu=40, days=0):
    return Lot(distributor, "SABIC", plant, grade, port, teu, days)


def test_alert_only_when_delay_outruns_safety_stock():
    assert evaluate(EtaUpdate("BK1", 12, 11), safety_stock_days=5).stockout_days == 6
    assert evaluate(EtaUpdate("BK1", 12, 11), safety_stock_days=11) is None
    assert evaluate(EtaUpdate("BK1", 12, 0), safety_stock_days=0) is None


def test_alert_rejects_negative_inputs():
    with pytest.raises(ValueError):
        evaluate(EtaUpdate("BK1", 12, -1), safety_stock_days=5)


def test_match_needs_identical_producer_plant_and_grade():
    assert find_match(NEED, [lot()]).distributor == "Hub A"
    assert find_match(NEED, [lot(grade="PP 571P")]) is None
    assert find_match(NEED, [lot(plant="Al Jubail")]) is None
    assert find_match(NEED, [lot(port="Antwerp")]) is None


def test_match_ignores_stock_arriving_after_the_original_date():
    assert find_match(NEED, [lot(days=11)]) is None
    assert find_match(NEED, [lot(days=10)]) is not None


def test_match_never_combines_distributors():
    assert find_match(NEED, [lot("Hub A", teu=20), lot("Hub B", teu=20)]) is None
    match = find_match(NEED, [lot("Hub A", teu=20), lot("Hub A", teu=20), lot("Hub B", teu=20)])
    assert match.distributor == "Hub A" and match.teu == 40


def test_match_prefers_fewest_lots():
    match = find_match(NEED, [lot("Hub A", teu=20), lot("Hub A", teu=20), lot("Hub B", teu=40)])
    assert match.distributor == "Hub B" and len(match.lots) == 1


def test_simulation_is_deterministic_and_consistent():
    a, b = run(), run()
    assert a == b
    assert a.late >= a.alerts >= a.alerts_in_time >= a.matched > 0
    assert a.stoppage_days_avoided <= a.stoppage_days_at_risk
    assert run(Assumptions(on_time_share=1.0)).late == 0
