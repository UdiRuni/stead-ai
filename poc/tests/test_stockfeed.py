"""The stock feed parser: the sample feed, every rule in STOCK_FEED.md, and odd inputs."""
from datetime import date
from pathlib import Path

import pytest

from steadpoc.demo import build_demo, demo_stock, main as demo_main
from steadpoc.matching import Need, find_match
from steadpoc.stockfeed import (MAX_SNAPSHOT_AGE_DAYS, REQUIRED, FeedError, load_feed, main,
                                parse_feed, render_report)

SAMPLE = Path(__file__).resolve().parents[1] / "data" / "sample_stock_feed.csv"
HEADER = ",".join(REQUIRED)
SNAP = "2027-02-19"


def feed(*rows: str, header: str = HEADER) -> str:
    return "\n".join([header, *rows]) + "\n"


def row(lot_id="L1", distributor="Hub B", producer="SABIC", plant="Geleen", grade="PP 575P",
        port="Rotterdam", teu="40", available_on="", snapshot_date=SNAP) -> str:
    return ",".join([lot_id, distributor, producer, plant, grade, port, teu, available_on,
                     snapshot_date])


def messages(report, kind="errors"):
    return " | ".join(str(p) for p in getattr(report, kind))


# ---- the sample feed ----

def test_sample_feed_is_clean_and_labelled_illustrative():
    text = SAMPLE.read_text(encoding="utf-8")
    assert "ILLUSTRATIVE" in text.splitlines()[0]
    report = parse_feed(text)
    assert report.ok and report.warnings == []
    assert report.snapshot_date == date(2027, 2, 19) == report.match_date
    assert len({l.lot_id for l in report.lots}) == len(report.lots) == 7


def test_sample_feed_holds_exactly_the_demo_stock():
    strip = lambda lots: [(l.distributor, l.producer, l.plant, l.grade, l.port, l.teu,
                           l.days_until_available) for l in lots]
    assert strip(load_feed(SAMPLE).lots) == strip(demo_stock())


def test_demo_on_the_sample_feed_picks_the_same_lot():
    d = build_demo(stock=load_feed(SAMPLE).lots)
    assert d.match.distributor == "Hub B" and d.match.lots[0].lot_id == "B-2001"
    assert d.term_sheet is not None
    assert [v.verdict for v in d.verdicts] == [v.verdict for v in build_demo().verdicts]


# ---- dates and the match day ----

def test_days_are_counted_from_the_match_day_not_the_snapshot():
    text = feed(row(available_on="2027-03-05"))
    assert parse_feed(text).lots[0].days_until_available == 14
    assert parse_feed(text, date(2027, 2, 20)).lots[0].days_until_available == 13


def test_lot_free_before_the_match_day_counts_as_free_now():
    lot = parse_feed(feed(row(available_on="2027-02-01"))).lots[0]
    assert lot.days_until_available == 0


def test_lot_free_on_the_last_day_still_matches_and_one_day_later_does_not():
    need = Need("SABIC", "Geleen", "PP 575P", "Rotterdam", 40, days_until_needed=10)
    on_time = parse_feed(feed(row(available_on="2027-03-01"))).lots
    late = parse_feed(feed(row(available_on="2027-03-02"))).lots
    assert find_match(need, on_time) is not None
    assert find_match(need, late) is None


def test_snapshot_after_the_match_day_is_an_error():
    report = parse_feed(feed(row()), date(2027, 2, 18))
    assert not report.ok and "after the match date" in messages(report)
    assert report.lots == []


def test_stale_snapshot_is_a_warning_not_an_error():
    report = parse_feed(feed(row()), date(2027, 2, 19 + MAX_SNAPSHOT_AGE_DAYS + 1))
    assert report.ok and "days old" in messages(report, "warnings")
    assert parse_feed(feed(row()), date(2027, 2, 19 + MAX_SNAPSHOT_AGE_DAYS)).warnings == []


def test_negative_max_age_is_refused():
    with pytest.raises(ValueError):
        parse_feed(feed(row()), max_age_days=-1)


def test_several_snapshot_dates_are_one_error_naming_both():
    report = parse_feed(feed(row("L1"), row("L2", snapshot_date="2027-02-18")))
    assert not report.ok and "2027-02-18 (line 3)" in messages(report)
    assert "2027-02-19 (line 2)" in messages(report)


@pytest.mark.parametrize("bad", ["19/02/2027", "2027-2-19", "2027-02-30", "tomorrow", "20270219"])
def test_bad_dates_are_errors(bad):
    assert "not a date" in messages(parse_feed(feed(row(snapshot_date=bad))))
    assert "available_on" in messages(parse_feed(feed(row(available_on=bad))))


# ---- values ----

@pytest.mark.parametrize("bad", ["-1", "2.5", "forty", "1e3", "+4"])
def test_teu_must_be_a_whole_number_of_zero_or_more(bad):
    report = parse_feed(feed(row(teu=bad)))
    assert not report.ok and "teu" in messages(report) and report.lots == []


def test_zero_teu_lot_is_kept_with_a_warning_and_never_matches():
    report = parse_feed(feed(row(teu="0")))
    assert report.ok and "0 TEU" in messages(report, "warnings")
    need = Need("SABIC", "Geleen", "PP 575P", "Rotterdam", 40, 10)
    assert find_match(need, report.lots) is None


@pytest.mark.parametrize("col", [c for c in REQUIRED if c != "available_on"])
def test_every_required_value_must_be_filled(col):
    report = parse_feed(feed(row(**{col: ""})))
    assert not report.ok and f"'{col}' is empty" in messages(report)


def test_values_are_trimmed_but_never_case_folded():
    lots = parse_feed(feed(row(grade="  PP 575P ", port=" Rotterdam"), row("L2", grade="pp 575p"))).lots
    need = Need("SABIC", "Geleen", "PP 575P", "Rotterdam", 40, 10)
    assert lots[0].grade == "PP 575P" and lots[0].port == "Rotterdam"
    assert lots[1].grade == "pp 575p"
    assert find_match(need, lots).lots == (lots[0],)


def test_quoted_value_with_a_comma_is_one_value():
    report = parse_feed(feed(row(distributor='"Hub B, Rotterdam"')))
    assert report.ok and report.lots[0].distributor == "Hub B, Rotterdam"


def test_duplicate_lot_id_names_the_first_line():
    report = parse_feed(feed(row("L1"), row("L1", distributor="Hub C")))
    assert "lot_id 'L1' already used on line 2" in messages(report)


def test_row_with_wrong_number_of_values():
    report = parse_feed(feed(row() + ",extra", "L2,Hub B,SABIC"))
    assert not report.ok
    assert "line 2: has 10 values" in messages(report) and "line 3: has 3 values" in messages(report)


def test_all_errors_are_reported_in_one_pass_and_no_lots_come_back():
    report = parse_feed(feed(row("L1", teu="-5"), row("L2", snapshot_date="x"), row("L3"), row("L3")))
    assert len(report.errors) == 3 and report.lots == []


# ---- header and file shape ----

def test_columns_may_come_in_any_order_and_any_case():
    cols = list(reversed(REQUIRED))
    values = dict(zip(REQUIRED, row().split(",")))
    text = ",".join(c.upper() for c in cols) + "\n" + ",".join(values[c] for c in cols) + "\n"
    report = parse_feed(text)
    assert report.ok and report.lots[0].teu == 40 and report.lots[0].lot_id == "L1"


def test_missing_columns_are_listed():
    header = ",".join(c for c in REQUIRED if c not in ("plant", "teu"))
    report = parse_feed(header + "\n")
    assert "missing column(s): plant, teu" in messages(report)


def test_repeated_column_is_an_error():
    assert "appears twice" in messages(parse_feed(feed(row() + ",40", header=HEADER + ",teu")))


def test_extra_columns_are_ignored_with_a_warning():
    report = parse_feed(feed(row() + ",EUR 1.10/kg", header=HEADER + ",price"))
    assert report.ok and "ignored column(s): price" in messages(report, "warnings")


def test_comments_blank_lines_crlf_and_byte_order_mark():
    text = "﻿# a comment\r\n\r\n" + HEADER + "\r\n# another\r\n" + row() + "\r\n\r\n"
    report = parse_feed(text)
    assert report.ok and len(report.lots) == 1


def test_line_numbers_count_comments_and_blank_lines():
    text = "# note\n\n" + HEADER + "\n" + row(teu="x") + "\n"
    assert str(parse_feed(text).errors[0]).startswith("line 4:")


@pytest.mark.parametrize("text", ["", "\n\n", "# only a comment\n", "﻿"])
def test_empty_feed_is_an_error(text):
    assert "empty" in messages(parse_feed(text))


def test_header_with_no_lots_is_a_warning():
    report = parse_feed(HEADER + "\n")
    assert report.ok and report.lots == [] and "no lots" in messages(report, "warnings")


def test_quoted_value_over_two_lines_is_refused():
    report = parse_feed(feed(row(distributor='"Hub\nB"')))
    assert not report.ok and "more than one line" in messages(report)


# ---- loading, the command and the demo flag ----

def test_load_feed_raises_with_every_error(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text(feed(row(teu="-1"), row("L1")), encoding="utf-8")
    with pytest.raises(FeedError) as caught:
        load_feed(path)
    assert len(caught.value.report.errors) == 2 and "teu" in str(caught.value)


def test_command_exit_codes(tmp_path, capsys):
    assert main([str(SAMPLE)]) == 0
    assert "OK" in capsys.readouterr().out
    bad = tmp_path / "bad.csv"
    bad.write_text(feed(row(teu="x")), encoding="utf-8")
    assert main([str(bad)]) == 1
    assert "REJECTED, 1 error(s)" in capsys.readouterr().out
    assert main([str(tmp_path / "missing.csv")]) == 2


def test_report_text_has_no_em_dash():
    text = render_report(parse_feed(SAMPLE.read_text(encoding="utf-8")), "sample")
    assert "\u2014" not in text and "7 lot(s), 240 TEU, 4 distributor(s)" in text


def test_demo_flag_reads_the_feed_and_says_so(capsys):
    assert demo_main(["--stock-feed", str(SAMPLE)]) == 0
    out = capsys.readouterr().out
    assert "chosen" in out and "Stock read from" in out and "snapshot 2027-02-19" in out


def test_demo_flag_counts_from_t_minus_10_of_the_arrival(tmp_path, capsys):
    # arrival 1 Mar 2027, match on 19 Feb: the Hub D lot free on 5 Mar is 14 days out
    assert demo_main(["--stock-feed", str(SAMPLE), "--arrival", "2027-03-01"]) == 0
    assert "in 14 days  available too late" in capsys.readouterr().out


def test_demo_flag_warns_on_a_stale_feed(capsys):
    assert demo_main(["--stock-feed", str(SAMPLE), "--arrival", "2027-03-15"]) == 0
    assert "days old" in capsys.readouterr().err


def test_demo_flag_refuses_a_bad_feed(tmp_path, capsys):
    bad = tmp_path / "bad.csv"
    bad.write_text(feed(row(teu="-3")), encoding="utf-8")
    assert demo_main(["--stock-feed", str(bad)]) == 2
    assert "teu" in capsys.readouterr().err
    assert demo_main(["--stock-feed", str(tmp_path / "none.csv")]) == 2


def test_demo_flag_with_a_feed_dated_after_the_match_day(capsys):
    # arrival 20 Feb 2027 puts the match on 10 Feb, before the 19 Feb snapshot
    assert demo_main(["--stock-feed", str(SAMPLE), "--arrival", "2027-02-20"]) == 2
    assert "after the match date" in capsys.readouterr().err


def test_demo_flag_with_no_matching_stock_says_no_swap(tmp_path, capsys):
    path = tmp_path / "small.csv"
    path.write_text(feed(row(teu="20"), row("L2", distributor="Hub C", teu="20")), encoding="utf-8")
    assert demo_main(["--stock-feed", str(path)]) == 0
    assert "No swap: no single distributor" in capsys.readouterr().out
