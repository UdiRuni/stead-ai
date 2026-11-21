"""AIS port call extractor. Every report here is invented; no real AIS file is used."""
import io
import json
import zipfile
from datetime import datetime, timedelta

import pytest

from steadpoc.portcalls import (Box, Port, Rules, _percentile, is_cargo, lateness_vs_pattern,
                                load_port, main, port_calls, read_ais, render, summarise,
                                write_calls_csv, Vessel)

HEADER = "MMSI,BaseDateTime,LAT,LON,SOG,COG,Heading,VesselName,IMO,CallSign,VesselType,Status,Length,Width,Draft,Cargo,TransceiverClass"
# Invented port: anchorage box south of a berth box, plus open sea outside both.
PORT = Port(name="Testport", source="invented for tests", boxes=(
    Box("anchorage A", "anchorage", 10.0, 10.5, 20.0, 21.0),
    Box("berths", "berth", 10.6, 11.0, 20.0, 21.0),
))
ANCH = (10.2, 20.5)
BERTH = (10.8, 20.5)
SEA = (5.0, 5.0)
T0 = datetime(2024, 1, 1)


def line(mmsi="111", t=T0, pos=ANCH, sog="0.1", vtype="70", length="300", name="TEST SHIP"):
    lat, lon = pos
    ts = t.isoformat() if isinstance(t, datetime) else t
    return f"{mmsi},{ts},{lat},{lon},{sog},0,0,{name},IMO1,CALL,{vtype},0,{length},40,12,70,A"


def stream(*lines, header=HEADER):
    s = io.StringIO("\n".join([header, *lines]) + "\n")
    s.name = "test.csv"
    return s


def run(*lines, rules=Rules(), port=PORT):
    pings, vessels, report = read_ais([stream(*lines)], port)
    calls, excluded = port_calls(pings, vessels, report, rules)
    return calls, excluded, report


def h(n):
    return T0 + timedelta(hours=n)


def bracket(*lines, start=-48, end=None):
    """Add sea reports of an unrelated vessel so the data window is wider than the call."""
    last = end if end is not None else 24 * 200
    return (line(mmsi="999", t=h(start), pos=SEA), *lines, line(mmsi="999", t=h(last), pos=SEA))


# ---------- boxes and ports ----------

def test_box_rejects_bad_kind_and_inverted_bounds():
    with pytest.raises(ValueError, match="kind"):
        Box("x", "quay", 0, 1, 0, 1)
    with pytest.raises(ValueError, match="lat"):
        Box("x", "berth", 1, 0, 0, 1)
    with pytest.raises(ValueError, match="lon"):
        Box("x", "berth", 0, 1, 0, 200)


def test_port_needs_a_berth_box():
    with pytest.raises(ValueError, match="berth"):
        Port("p", (Box("a", "anchorage", 0, 1, 0, 1),), "s")
    with pytest.raises(ValueError, match="at least one box"):
        Port("p", (), "s")


def test_berth_wins_where_boxes_overlap():
    port = Port("p", (Box("a", "anchorage", 0, 2, 0, 2), Box("b", "berth", 1, 2, 1, 2)), "s")
    assert port.locate(1.5, 1.5) == "berth"
    assert port.locate(0.5, 0.5) == "anchorage"
    assert port.locate(3, 3) is None


def test_box_edges_are_inside():
    assert PORT.locate(10.0, 20.0) == "anchorage"
    assert PORT.locate(11.0, 21.0) == "berth"


def test_load_port_reads_json_and_reports_missing_keys(tmp_path):
    f = tmp_path / "p.json"
    f.write_text(json.dumps({"name": "P", "source": "s", "boxes": [
        {"name": "b", "kind": "berth", "lat_min": 0, "lat_max": 1, "lon_min": 0, "lon_max": 1}]}))
    assert load_port(f).boxes[0].kind == "berth"
    f.write_text(json.dumps({"name": "P", "boxes": []}))
    with pytest.raises(ValueError, match="source"):
        load_port(f)


# ---------- rules ----------

@pytest.mark.parametrize("kw", [dict(min_length_m=-1), dict(moored_sog_kn=-0.1),
                                dict(visit_gap_hours=0), dict(min_interval_days=0),
                                dict(min_interval_days=10, max_interval_days=10),
                                dict(min_history_calls=1)])
def test_rules_reject_nonsense(kw):
    with pytest.raises(ValueError):
        Rules(**kw)


# ---------- reading ----------

def test_missing_columns_stop_the_run():
    with pytest.raises(ValueError, match="missing columns.*sog"):
        read_ais([stream("1,2024-01-01T00:00:00,10,20", header="MMSI,BaseDateTime,LAT,LON")], PORT)


def test_empty_file_stops_the_run():
    s = io.StringIO("")
    with pytest.raises(ValueError, match="empty"):
        read_ais([s], PORT)


def test_column_names_match_without_case_and_in_any_order():
    header = "lon,lat,mmsi,basedatetime,sog,length,vesseltype"
    s = stream(f"20.5,10.8,111,{T0.isoformat()},0.1,300,70", header=header)
    pings, vessels, rep = read_ais([s], PORT)
    assert rep.kept == 1 and pings[0].where == "berth" and vessels["111"].length_m == 300


def test_bad_rows_are_counted_by_reason_not_fatal():
    calls, _, rep = run(
        line(),
        line(mmsi=""),
        line(t="not a time"),
        line(pos=("x", 20)),
        line(pos=(95, 20)),
        line(pos=SEA),
        line(sog="fast"),
    )
    assert rep.rows == 7 and rep.kept == 1
    assert rep.skipped == {"no MMSI": 1, "bad time or position": 2, "position out of range": 1,
                           "outside the port": 1, "bad speed, type or length": 1}


def test_window_counts_reports_outside_the_port():
    _, _, rep = run(line(t=h(5)), line(mmsi="2", t=h(-10), pos=SEA), line(mmsi="2", t=h(50), pos=SEA))
    assert rep.first_t == h(-10) and rep.last_t == h(50)


def test_reads_csv_and_zip_files(tmp_path):
    body = "\n".join([HEADER, line(t=h(0)), line(t=h(1), pos=BERTH)]) + "\n"
    csv_path = tmp_path / "AIS_2024_01_01.csv"
    csv_path.write_text(body)
    zip_path = tmp_path / "AIS_2024_01_02.zip"
    with zipfile.ZipFile(zip_path, "w") as z:
        z.writestr("AIS_2024_01_02.csv", body.replace("2024-01-01", "2024-01-02"))
    pings, _, rep = read_ais([csv_path, zip_path], PORT)
    assert rep.kept == 4 and len(rep.files) == 2


def test_zip_without_csv_stops(tmp_path):
    zip_path = tmp_path / "x.zip"
    with zipfile.ZipFile(zip_path, "w") as z:
        z.writestr("readme.txt", "nothing")
    with pytest.raises(ValueError, match="no .csv"):
        read_ais([zip_path], PORT)


def test_timestamps_with_space_or_z_are_read():
    calls, _, rep = run(line(t="2024-01-01 00:00:00"), line(t="2024-01-01T01:00:00Z"))
    assert rep.kept == 2


# ---------- which vessels count ----------

@pytest.mark.parametrize("vtype,length,ok,why", [
    ("70", "300", True, ""),
    ("79", "200", True, ""),
    ("80", "300", False, "not a cargo"),       # tanker
    ("", "300", False, "type never stated"),
    ("70", "", False, "length never stated"),
    ("70", "199.9", False, "shorter"),
    ("70", "0", False, "length never stated"),  # 0 is AIS for unknown
])
def test_cargo_filter(vtype, length, ok, why):
    calls, excluded, _ = run(*bracket(line(vtype=vtype, length=length)))
    assert (len(calls) == 1) is ok
    if not ok:
        assert why in excluded["111"]


def test_type_and_length_from_any_report_of_the_vessel():
    calls, excluded, _ = run(*bracket(line(t=h(0), vtype="", length=""),
                                      line(t=h(1), vtype="71", length="250")))
    assert "111" not in excluded and len(calls) == 1 and calls[0].reports == 2


def test_is_cargo_uses_rules():
    v = Vessel("1", types={70}, length_m=150)
    assert not is_cargo(v, Rules())[0]
    assert is_cargo(v, Rules(min_length_m=100))[0]


# ---------- port calls ----------

def test_one_complete_call_with_wait_and_berth():
    calls, _, _ = run(*bracket(
        line(t=h(0), sog="0.0"),              # anchored
        line(t=h(20), sog="0.0"),
        line(t=h(40), pos=BERTH, sog="3.0"),  # moving inside berth area: not moored yet
        line(t=h(41), pos=BERTH, sog="0.4"),  # moored
        line(t=h(60), pos=BERTH, sog="0.0"),
    ))
    (c,) = calls
    assert c.complete and c.arrived == h(0) and c.berthed == h(41) and c.left == h(60)
    assert c.waited_hours == 41 and c.in_port_hours == 60 and c.name == "TEST SHIP"


def test_moored_threshold_is_inclusive_and_missing_speed_is_not_moored():
    calls, _, _ = run(*bracket(line(t=h(0), pos=BERTH, sog=""), line(t=h(2), pos=BERTH, sog="0.5")))
    assert calls[0].berthed == h(2)


def test_call_that_never_moors():
    calls, _, _ = run(*bracket(line(t=h(0)), line(t=h(20)), line(t=h(22), pos=BERTH, sog="6")))
    assert calls[0].berthed is None and calls[0].waited_hours is None


def test_straight_to_berth_waits_zero():
    calls, _, _ = run(*bracket(line(t=h(0), pos=BERTH, sog="0.2")))
    assert calls[0].waited_hours == 0


def test_silence_longer_than_gap_starts_a_new_call():
    calls, _, _ = run(*bracket(line(t=h(0)), line(t=h(24)), line(t=h(48.5))))
    assert [c.arrived for c in calls] == [h(0), h(48.5)]   # 24 h exactly is still one call


def test_unsorted_input_is_sorted_per_vessel():
    calls, _, _ = run(*bracket(line(t=h(5), pos=BERTH), line(t=h(0)), line(t=h(3))))
    assert calls[0].arrived == h(0) and calls[0].berthed == h(5)


def test_duplicate_reports_do_not_break_a_call():
    calls, _, _ = run(*bracket(line(t=h(0)), line(t=h(0)), line(t=h(1), pos=BERTH)))
    assert len(calls) == 1 and calls[0].reports == 3


def test_two_vessels_are_kept_apart():
    calls, _, _ = run(*bracket(line(mmsi="1", t=h(0)), line(mmsi="2", t=h(1), pos=BERTH),
                               line(mmsi="1", t=h(3), pos=BERTH)))
    assert {c.mmsi: c.waited_hours for c in calls} == {"1": 3, "2": 0}


def test_calls_at_the_edge_of_the_data_are_flagged_cut_off():
    calls, _, _ = run(line(t=h(0)), line(t=h(10), pos=BERTH),            # data starts here
                      line(t=h(100)), line(t=h(120), pos=BERTH))       # data ends here
    assert [(c.cut_at_start, c.cut_at_end) for c in calls] == [(True, False), (False, True)]
    assert not any(c.complete for c in calls)


def test_custom_gap_rule():
    calls, _, _ = run(*bracket(line(t=h(0)), line(t=h(10))), rules=Rules(visit_gap_hours=6))
    assert len(calls) == 2


# ---------- lateness against the vessel's own pattern ----------

def weekly(arrivals_days, mmsi="111"):
    rows = []
    for d in arrivals_days:
        rows += [line(mmsi=mmsi, t=T0 + timedelta(days=d)),
                 line(mmsi=mmsi, t=T0 + timedelta(days=d, hours=6), pos=BERTH)]
    return run(*bracket(*rows, end=24 * (max(arrivals_days) + 10)))[0]


def test_lateness_needs_history_and_uses_only_earlier_calls():
    calls = weekly([0, 7, 14, 21, 30])
    late = lateness_vs_pattern(calls)
    assert [(x.call.arrived - T0).days for x in late] == [21, 30]
    assert late[0].days_late == 0
    assert late[1].days_late == 2       # expected day 28, came day 30


def test_early_arrival_is_negative():
    late = lateness_vs_pattern(weekly([0, 7, 14, 21, 26]))
    assert late[-1].days_late == -2


def test_pattern_outside_sanity_bounds_gives_no_figure():
    assert lateness_vs_pattern(weekly([0, 2, 4, 6, 8])) == []          # 2-day shuttle
    assert lateness_vs_pattern(weekly([0, 7, 14, 21]), Rules(min_history_calls=4)) == []


def test_a_late_call_moves_the_median_only_afterwards():
    late = lateness_vs_pattern(weekly([0, 7, 14, 31, 38, 45]))
    by_day = {(x.call.arrived - T0).days: x.days_late for x in late}
    assert by_day[31] == 10              # 7-day pattern, expected day 24
    assert by_day[38] == 0               # median of 7, 7, 17 is still 7


def test_cut_off_calls_are_never_used_for_lateness():
    rows = []
    for d in [0, 7, 14, 21]:
        rows += [line(t=T0 + timedelta(days=d))]
    calls = run(*rows, line(mmsi="999", t=h(24 * 40), pos=SEA))[0]
    assert calls[0].cut_at_start
    assert lateness_vs_pattern(calls) == []   # only 2 earlier usable calls before day 21


# ---------- summary, CSV, text, command line ----------

def test_percentile_nearest_rank():
    assert _percentile([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 0.9) == 9
    assert _percentile([5], 0.9) == 5
    with pytest.raises(ValueError):
        _percentile([1], 0)


def test_summary_leaves_out_cut_off_calls():
    calls, _, _ = run(line(t=h(0)), line(t=h(10), pos=BERTH, sog="0"),    # cut at start
                      line(t=h(100)), line(t=h(120)),
                      line(t=h(130), pos=BERTH),                          # complete, 30 h
                      line(t=h(200)), line(t=h(204), pos=BERTH),          # complete, 4 h
                      line(t=h(300)),                                     # complete, never moored
                      line(t=h(1000)))                                    # cut at end
    s = summarise(calls, [])
    assert s.calls == 5 and s.complete == 3 and s.berthed == 2 and s.never_berthed == 1
    assert s.median_wait_h == 17 and s.share_wait_over_24h == 0.5


def test_summary_of_nothing():
    s = summarise([], [])
    assert s.calls == 0 and s.median_wait_h is None and s.median_days_late is None


def test_csv_has_a_row_per_call():
    calls = weekly([0, 7, 14, 21])
    out = io.StringIO()
    write_calls_csv(calls, lateness_vs_pattern(calls), out)
    rows = out.getvalue().splitlines()
    assert len(rows) == 5 and rows[0].startswith("mmsi,name,arrived")
    assert rows[-1].endswith(",0.000") and rows[1].endswith(",,")


def test_render_labels_public_data_and_assumptions():
    calls, excluded, rep = run(*bracket(line()))
    text = render(PORT, rep, summarise(calls, []), excluded)
    assert "public data" in text and "assumptions" in text and "not the carrier schedule" in text
    assert "\u2014" not in text


def test_command_line(tmp_path, capsys):
    port = tmp_path / "port.json"
    port.write_text(json.dumps({"name": "Testport", "source": "invented", "boxes": [
        {"name": b.name, "kind": b.kind, "lat_min": b.lat_min, "lat_max": b.lat_max,
         "lon_min": b.lon_min, "lon_max": b.lon_max} for b in PORT.boxes]}))
    data = tmp_path / "ais.csv"
    data.write_text("\n".join([HEADER, *bracket(line(t=h(0)), line(t=h(3), pos=BERTH))]) + "\n")
    out = tmp_path / "calls.csv"
    assert main([str(data), "--port", str(port), "--csv", str(out)]) == 0
    text = capsys.readouterr().out
    assert "port calls: 1, complete: 1" in text and "median 3 h" in text
    assert out.read_text().count("\n") == 2


def test_command_line_reports_bad_input(tmp_path, capsys):
    port = tmp_path / "port.json"
    port.write_text("{}")
    data = tmp_path / "ais.csv"
    data.write_text(HEADER + "\n")
    assert main([str(data), "--port", str(port)]) == 2
    assert "error" in capsys.readouterr().err
    assert main([str(tmp_path / "missing.csv"), "--port", str(port)]) == 2
