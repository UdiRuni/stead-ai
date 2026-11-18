import pytest

from steadpoc.accumulation import Book, Decision, Limits, Swap, percentile, report, sample_book
from steadpoc.economics import SwapCase
from steadpoc.longstop import LongStop


def swap(i, vessel="A", value=1_000_000, delay=11, long_stop=30, event=None):
    return Swap(f"S{i}", vessel, value, delay, long_stop, event)


# validation

@pytest.mark.parametrize("kwargs", [
    dict(swap_id="", vessel="A", agreed_value_usd=1, expected_delay_days=1),
    dict(swap_id="S", vessel="", agreed_value_usd=1, expected_delay_days=1),
    dict(swap_id="S", vessel="A", agreed_value_usd=0, expected_delay_days=1),
    dict(swap_id="S", vessel="A", agreed_value_usd=-5, expected_delay_days=1),
    dict(swap_id="S", vessel="A", agreed_value_usd=1, expected_delay_days=-1),
    dict(swap_id="S", vessel="A", agreed_value_usd=1, expected_delay_days=30, long_stop_day=30),
    dict(swap_id="S", vessel="A", agreed_value_usd=1, expected_delay_days=31, long_stop_day=30),
])
def test_bad_swaps_are_rejected(kwargs):
    with pytest.raises(ValueError):
        Swap(**kwargs)


def test_zero_delay_swap_is_allowed_and_margin_is_long_stop_minus_delay():
    assert Swap("S", "A", 1, 0).margin_days == 30
    assert swap(1, delay=11).margin_days == 19


@pytest.mark.parametrize("kwargs", [dict(per_vessel_usd=0), dict(per_event_usd=-1)])
def test_limits_must_be_positive(kwargs):
    with pytest.raises(ValueError):
        Limits(**kwargs)


@pytest.mark.parametrize("kwargs", [dict(mean_lateness_days=0), dict(tail_stretch=0),
                                    dict(net_severity_share=0), dict(net_severity_share=1.2)])
def test_book_parameters_are_checked(kwargs):
    with pytest.raises(ValueError):
        Book(**kwargs)


# acceptance

def test_swap_under_the_limits_is_accepted_and_counted():
    book = Book(Limits(3_000_000, 5_000_000))
    assert book.add(swap(1, event="strike")) == Decision(True, ())
    assert book.vessel_exposure_usd("A") == 1_000_000
    assert book.event_exposure_usd("strike") == 1_000_000
    assert book.vessel_exposure_usd("unknown") == 0


def test_exactly_at_the_vessel_limit_is_accepted_one_dollar_over_is_not():
    book = Book(Limits(2_000_000, 10_000_000))
    assert book.add(swap(1)).accepted
    assert book.add(swap(2)).accepted
    refused = book.add(swap(3, value=1))
    assert not refused.accepted
    assert "per-vessel limit" in refused.reasons[0] and "vessel A" in refused.reasons[0]
    assert len(book.swaps) == 2


def test_event_limit_spans_vessels():
    book = Book(Limits(5_000_000, 2_500_000))
    assert book.add(swap(1, "A", event="strike")).accepted
    assert book.add(swap(2, "B", event="strike")).accepted
    d = book.add(swap(3, "C", event="strike"))
    assert not d.accepted and "per-event limit" in d.reasons[0]
    # the same swap with no event, or another event, goes through
    assert book.add(swap(3, "C")).accepted
    assert book.add(swap(4, "D", event="canal")).accepted


def test_both_limits_breached_gives_two_reasons():
    book = Book(Limits(1_500_000, 1_500_000))
    book.add(swap(1, event="strike"))
    d = book.check(swap(2, event="strike"))
    assert not d.accepted and len(d.reasons) == 2


def test_check_does_not_change_the_book():
    book = Book()
    book.check(swap(1))
    assert book.swaps == []


def test_duplicate_id_is_refused():
    book = Book()
    book.add(swap(1, "A"))
    d = book.add(swap(1, "B"))
    assert not d.accepted and "already in the book" in d.reasons[0]


def test_boxes_on_one_vessel_must_share_an_arrival():
    book = Book()
    book.add(swap(1, delay=11))
    d = book.add(swap(2, delay=9))
    assert not d.accepted and "arrive together" in d.reasons[0]
    # a different long stop on the same vessel is fine
    assert book.add(swap(3, delay=11, long_stop=40)).accepted


def test_single_swap_bigger_than_the_vessel_limit_is_refused_on_an_empty_book():
    book = Book(Limits(1_000_000, 10_000_000))
    assert not book.add(swap(1, value=1_000_001)).accepted


# losses

def test_empty_book_has_no_loss():
    book = Book()
    assert book.expected_loss_usd() == 0
    assert book.simulate(100) == [0.0] * 100
    assert book.event_scenario_loss_usd("strike", 50) == 0
    assert book.vessel_worst_loss_usd("A") == 0


def test_expected_loss_is_the_sum_of_longstop_pure_costs():
    book = Book()
    book.add(swap(1, value=1_200_000, delay=11))
    book.add(swap(2, "B", value=800_000, delay=9, long_stop=45))
    expected = (LongStop(1_200_000, 11, 30).pure_cost_usd
                + LongStop(800_000, 9, 45).pure_cost_usd)
    assert book.expected_loss_usd() == pytest.approx(expected)


def test_one_worked_case_swap_matches_longstop_base_case():
    c = SwapCase()
    book = Book()
    book.add(Swap("W", "A", c.notional_usd, c.delay_days))
    assert book.expected_loss_usd() == pytest.approx(LongStop().pure_cost_usd)


def test_simulated_mean_matches_expected_loss_both_ways():
    book = Book()
    for i in range(4):
        book.add(swap(i, "A", value=700_000, delay=11, long_stop=20))
    book.add(swap(9, "B", value=1_000_000, delay=8, long_stop=18))
    for clustered in (True, False):
        losses = book.simulate(40_000, seed=3, clustered=clustered)
        assert sum(losses) / len(losses) == pytest.approx(book.expected_loss_usd(), rel=0.05)


def test_clustering_fattens_the_tail_not_the_mean():
    book = Book(Limits(10_000_000, 10_000_000))
    for i in range(8):
        book.add(swap(i, "A", value=1_000_000, delay=11, long_stop=25))
    clustered = book.simulate(20_000, seed=1, clustered=True)
    independent = book.simulate(20_000, seed=1, clustered=False)
    assert percentile(clustered, 99) > percentile(independent, 99)
    # with one slip per vessel the only outcomes are nothing or the whole vessel
    assert set(clustered) <= {0.0, book.vessel_worst_loss_usd("A")}


def test_one_swap_per_vessel_clustered_equals_independent():
    book = Book()
    for i, v in enumerate("ABCD"):
        book.add(swap(i, v, delay=10 + i))
    assert book.simulate(500, seed=7, clustered=True) == book.simulate(500, seed=7, clustered=False)


def test_simulation_is_reproducible_and_bounded():
    book, _ = sample_book()
    a, b = book.simulate(2_000, seed=5), book.simulate(2_000, seed=5)
    assert a == b
    total_net = sum(book.net_loss_usd(s) for s in book.swaps)
    assert all(0 <= x <= total_net for x in a)
    with pytest.raises(ValueError):
        book.simulate(0)


def test_fatter_tail_raises_expected_loss():
    thin, fat = Book(), Book(tail_stretch=1.5)
    for b in (thin, fat):
        b.add(swap(1))
    assert fat.expected_loss_usd() > thin.expected_loss_usd()


def test_event_scenario_pays_only_swaps_whose_margin_is_exceeded():
    book = Book(Limits(10_000_000, 10_000_000))
    book.add(swap(1, "A", delay=11, event="strike"))   # margin 19
    book.add(swap(2, "B", delay=14, event="strike"))   # margin 16
    book.add(swap(3, "C", delay=14))                   # not in the event
    net = 1_000_000 * 0.15
    assert book.event_scenario_loss_usd("strike", 0) == 0
    assert book.event_scenario_loss_usd("strike", 16) == 0        # equal to margin: arrives on the day
    assert book.event_scenario_loss_usd("strike", 17) == pytest.approx(net)
    assert book.event_scenario_loss_usd("strike", 100) == pytest.approx(2 * net)
    assert book.event_scenario_loss_usd("canal", 100) == 0
    with pytest.raises(ValueError):
        book.event_scenario_loss_usd("strike", -1)


def test_event_stress_never_exceeds_the_event_limit_times_severity():
    book, _ = sample_book()
    cap = book.limits.per_event_usd * book.net_severity_share
    assert book.event_scenario_loss_usd("port strike", 1_000) <= cap


# percentile

def test_percentile_nearest_rank():
    values = list(range(1, 101))
    assert percentile(values, 99) == 99
    assert percentile(values, 100) == 100
    assert percentile(values, 0) == 1
    assert percentile([5], 50) == 5
    with pytest.raises(ValueError):
        percentile([], 50)
    with pytest.raises(ValueError):
        percentile([1], 101)


# sample book and report

def test_sample_book_refuses_three_offers_for_three_different_reasons():
    book, decisions = sample_book()
    refused = {s.swap_id: d.reasons for s, d in decisions if not d.accepted}
    assert set(refused) == {"S04", "S09", "S11"}
    assert "per-vessel limit" in refused["S04"][0]
    assert "per-event limit" in refused["S09"][0]
    assert "arrive together" in refused["S11"][0]
    for v in {s.vessel for s in book.swaps}:
        assert book.vessel_exposure_usd(v) <= book.limits.per_vessel_usd
    assert book.event_exposure_usd("port strike") <= book.limits.per_event_usd


def test_report_is_labelled_and_house_style():
    text = report(trials=2_000)
    assert "SIMULATED BOOK" in text and "NOT A QUOTE" in text
    assert "REFUSED" in text and "99th percentile" in text
    assert chr(0x2014) not in text
    assert "D = 22 days: loss $1,110,000" in text      # all event swaps pay: $7.4M x 15%
    assert "D = 17 days: loss $345,000" in text        # only vessel C, margin 16 days
    assert "lodestar" not in text.lower()


def test_the_published_placeholder_is_untouched():
    assert SwapCase().premium_usd == 16_000
