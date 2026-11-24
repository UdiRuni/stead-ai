"""Polygon port areas, positions as printed in regulations, and the first real port file.

The Los Angeles and Long Beach file holds anchorages from 33 CFR 110.214 (read
2026-11-24). Its berths are not defined yet, so it must load for a check and be
refused for a run. No AIS data is used here; the ship positions are invented.
"""
import io
import json
import math
from pathlib import Path

import pytest

from steadpoc.portcalls import (Area, Box, Port, describe_port, load_port, main, parse_dms,
                                port_calls, read_ais)

LALB = Path(__file__).resolve().parents[1] / "data" / "ports" / "los_angeles_long_beach.json"
HEADER = "MMSI,BaseDateTime,LAT,LON,SOG,VesselType,Length"


def dms(d, m, s):
    return d + m / 60 + s / 3600


# ---------- parse_dms ----------

@pytest.mark.parametrize("text", [
    "33°43′05.1″ N 118°08′04.0″ W",            # 2025 Federal Register tables
    "33°-43'-05.1\" N 118°-08'-04.0\" W",       # older CFR layout
    "33°-43′-05.1″N 118°-08′-04.0″W",
    "33-43' 05.1\" N, 118-08' 04.0\" W",
    "33°-43'-05.1' N. 118°-08'-04.0' W.",        # apostrophe printed for seconds
])
def test_parse_dms_reads_every_layout_in_the_source(text):
    lat, lon = parse_dms(text)
    assert lat == pytest.approx(dms(33, 43, 5.1), abs=1e-9)
    assert lon == pytest.approx(-dms(118, 8, 4.0), abs=1e-9)


def test_parse_dms_hemispheres_and_whole_seconds():
    assert parse_dms("10°00′30″ S 020°15′00″ E") == pytest.approx((-dms(10, 0, 30), dms(20, 15, 0)))
    assert parse_dms("0°00′00″ N 0°00′00″ E") == (0.0, 0.0)
    assert parse_dms("33-43' 40.5' N, 118-10' 30\" W") == pytest.approx(
        (dms(33, 43, 40.5), -dms(118, 10, 30)))


@pytest.mark.parametrize("bad", [
    "",
    "33.7 N 118.1 W",                       # decimal degrees, not DMS
    "33°61′00″ N 118°08′04″ W",             # minutes 61
    "33°43′60.0″ N 118°08′04″ W",           # seconds 60
    "91°00′00″ N 118°08′04″ W",             # latitude over 90
    "33°43′05″ N 181°00′00″ W",             # longitude over 180
    "33°43′05″ 118°08′04″",                 # no hemispheres
])
def test_parse_dms_refuses_what_it_cannot_read_safely(bad):
    with pytest.raises(ValueError):
        parse_dms(bad)


# ---------- Area ----------

SQUARE = ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0))


def test_area_contains_inside_outside_and_edges():
    a = Area("sq", "anchorage", SQUARE)
    assert a.contains(0.5, 0.5)
    assert not a.contains(1.5, 0.5) and not a.contains(0.5, -0.1)
    assert a.contains(0.0, 0.5) and a.contains(1.0, 1.0)     # edge and corner count as inside


def test_area_concave_polygon_excludes_the_notch():
    # A "U": the notch between the arms is outside.
    u = Area("u", "berth", ((0, 0), (0, 3), (3, 3), (3, 2), (1, 2), (1, 1), (3, 1), (3, 0)))
    assert u.contains(0.5, 1.5)          # the base
    assert u.contains(2.5, 0.5)          # lower arm
    assert not u.contains(2.0, 1.5)      # the notch
    assert not Box("bbox", "berth", 0, 3, 0, 3).contains(4, 4)


def test_area_accepts_a_repeated_closing_vertex():
    a = Area("closed", "anchorage", SQUARE + (SQUARE[0],))
    assert len(a.vertices) == 4


@pytest.mark.parametrize("verts, msg", [
    (((0, 0), (0, 1)), "at least 3"),
    (((0, 0), (0, 1), (0, 2)), "no area"),
    (((0, 0), (0, 1), (0, 1), (1, 0)), "repeated vertex"),
    (((0, 0), (1, 1), (0, 1), (1, 0)), "cross"),           # a bow tie: wrong vertex order
    (((0, 0), (0, 200), (1, 0)), "out of range"),
    (((0, -179), (0, 179), (1, 179)), "180th meridian"),
])
def test_area_rejects_bad_shapes(verts, msg):
    with pytest.raises(ValueError, match=msg):
        Area("bad", "anchorage", verts)


def test_area_rejects_bad_kind():
    with pytest.raises(ValueError, match="kind"):
        Area("x", "quay", SQUARE)


def test_area_km2_of_a_known_square():
    # 0.01 by 0.01 degrees at the equator is about 1.113 km by 1.113 km.
    a = Area("small", "berth", ((0, 0), (0, 0.01), (0.01, 0.01), (0.01, 0)))
    assert a.area_km2() == pytest.approx(1.1132 ** 2, rel=1e-3)


# ---------- port files ----------

def write_port(tmp_path, boxes, **extra):
    p = tmp_path / "port.json"
    p.write_text(json.dumps({"name": "P", "source": "invented", "boxes": boxes, **extra}),
                 encoding="utf-8")
    return p


BERTH_BOX = {"name": "b", "kind": "berth", "lat_min": 0, "lat_max": 1, "lon_min": 0, "lon_max": 1}


def test_load_port_mixes_boxes_polygons_and_dms(tmp_path):
    p = write_port(tmp_path, [
        BERTH_BOX,
        {"name": "poly", "kind": "anchorage", "polygon": [[2, 0], [2, 1], [3, 1]]},
        {"name": "dms", "kind": "anchorage",
         "vertices_dms": ["4°00′00″ N 0°00′00″ E", "4°00′00″ N 1°00′00″ E", "5°00′00″ N 1°00′00″ E"]},
    ])
    port = load_port(p)
    assert [type(b) for b in port.boxes] == [Box, Area, Area]
    assert port.locate(0.5, 0.5) == "berth"
    assert port.locate(2.2, 0.5) == "anchorage"
    assert port.locate(2.9, 0.1) is None            # inside the polygon's bounds, outside it
    assert port.locate(4.5, 0.9) == "anchorage"


def test_load_port_needs_exactly_one_shape_per_area(tmp_path):
    both = dict(BERTH_BOX, polygon=[[0, 0], [0, 1], [1, 1]])
    with pytest.raises(ValueError, match="exactly one"):
        load_port(write_port(tmp_path, [both]))
    with pytest.raises(ValueError, match="exactly one"):
        load_port(write_port(tmp_path, [{"name": "n", "kind": "berth"}]))


def test_partial_port_loads_only_when_asked(tmp_path):
    p = write_port(tmp_path, [{"name": "a", "kind": "anchorage", "polygon": [[0, 0], [0, 1], [1, 1]]}],
                   missing="no berths yet")
    with pytest.raises(ValueError, match="partial.*no berths yet"):
        load_port(p)
    port = load_port(p, allow_partial=True)
    assert not port.runnable and port.missing == "no berths yet"
    assert "NOT ready for a run" in describe_port(port)


def test_port_without_berth_and_without_missing_note_is_refused():
    with pytest.raises(ValueError, match="berth"):
        Port("P", (Area("a", "anchorage", SQUARE),), source="x")


def test_berth_polygon_wins_over_overlapping_anchorage_and_counts_as_moored():
    port = Port("P", source="invented", boxes=(
        Area("anch", "anchorage", ((0, 0), (0, 2), (2, 2), (2, 0))),
        Area("berth", "berth", ((0.5, 0.5), (0.5, 1.0), (1.0, 1.0), (1.0, 0.5))),
    ))
    assert port.locate(0.7, 0.7) == "berth"
    assert port.locate(1.5, 1.5) == "anchorage"
    rows = [HEADER,
            "1,2024-01-01T00:00:00,9,9,0,70,300",           # sea, opens the data window
            "7,2024-01-03T00:00:00,1.5,1.5,0.2,70,300",     # anchored
            "7,2024-01-03T20:00:00,0.7,0.7,0.1,70,300",     # moored, 20 h later
            "1,2024-02-01T00:00:00,9,9,0,70,300"]
    s = io.StringIO("\n".join(rows) + "\n")
    pings, vessels, report = read_ais([s], port)
    calls, _ = port_calls(pings, vessels, report)
    assert len(calls) == 1 and calls[0].waited_hours == pytest.approx(20.0)


# ---------- the Los Angeles and Long Beach file ----------

@pytest.fixture(scope="module")
def lalb():
    return load_port(LALB, allow_partial=True)


def test_lalb_is_partial_and_refused_for_a_run(lalb):
    assert not lalb.runnable and "berth" in lalb.missing
    with pytest.raises(ValueError, match="partial"):
        load_port(LALB)


def test_lalb_cites_its_sources():
    data = json.loads(LALB.read_text(encoding="utf-8"))
    assert "33 CFR 110.214" in data["source"] and "NAD 83" in data["source"]
    assert "2025-17318" in data["source"] and "2026-11-24" in data["source"]
    assert all("110.214" in b["source"] for b in data["boxes"])


def test_lalb_has_the_six_commercial_anchorages(lalb):
    names = sorted(b.name.split(" (")[0] for b in lalb.boxes)
    assert names == ["Anchorage B", "Anchorage C", "Anchorage D", "Anchorage E",
                     "Anchorage F", "Anchorage G"]
    assert all(isinstance(b, Area) and b.kind == "anchorage" for b in lalb.boxes)


def test_lalb_areas_lie_in_san_pedro_bay(lalb):
    for b in lalb.boxes:
        lat_min, lat_max, lon_min, lon_max = b.bounds
        assert 33.60 < lat_min < lat_max < 33.80, b.name
        assert -118.30 < lon_min < lon_max < -118.05, b.name
        assert 0.5 < b.area_km2() < 40, b.name


def by_name(port, letter):
    return next(b for b in port.boxes if b.name.startswith(f"Anchorage {letter}"))


def test_lalb_f_lies_south_of_d_across_the_long_beach_breakwater(lalb):
    # F is "outside of Long Beach Breakwater" and D begins "near the east end of the
    # Long Beach Breakwater" inside it, so F's northern edge is south of D's southern
    # edge, with a gap for the breakwater. (B and G cannot be compared this way: the
    # Middle Breakwater is not an east-west line, and B reaches further south than G's
    # top.)
    f_top = by_name(lalb, "F").bounds[1]
    d_bottom = by_name(lalb, "D").bounds[0]
    assert f_top < d_bottom
    assert (d_bottom - f_top) * 111.32 * 1000 > 300      # metres between them


def test_lalb_anchorages_do_not_overlap(lalb):
    # Sample a grid; no point may fall strictly inside two anchorages (shared edges allowed).
    areas = list(lalb.boxes)
    step = 0.0015
    lat = 33.640
    while lat < 33.760:
        lon = -118.245
        while lon < -118.110:
            hits = [a.name for a in areas if a.contains(lat, lon)]
            if len(hits) > 1:
                # allowed only on a shared edge: a tiny move must leave one of them
                assert any(not a.contains(lat + 1e-5, lon + 1e-5) or not a.contains(lat - 1e-5, lon - 1e-5)
                           for a in areas if a.name in hits), (lat, lon, hits)
            lon += step
        lat += step


@pytest.mark.parametrize("letter, centre", [
    # Sub-anchorage and explosives anchorage centres printed in the same section:
    # an independent check that the polygon vertices were copied in the right order.
    ("B", "33-43' 52.0\" N, 118-12' 47.9\" W"),    # B-7
    ("B", "33-43' 28.5\" N, 118-13' 10.5\" W"),    # B-9
    ("B", "33-43' 44.5\" N, 118-12' 17\" W"),      # B-11
    ("D", "33-43' 40.5' N, 118-10' 30\" W"),       # D-5
    ("D", "33-43' 40.5' N, 118-9' 57.5\" W"),      # D-6
    ("D", "33-43' 40.5' N, 118-9' 25\" W"),        # D-7
    ("D", "33°43′37.0″N 118°09′05.3″W"),           # explosives anchorage centre
])
def test_lalb_printed_centres_fall_inside_their_anchorage(lalb, letter, centre):
    lat, lon = parse_dms(centre)
    assert by_name(lalb, letter).contains(lat, lon)
    others = [b for b in lalb.boxes if not b.name.startswith(f"Anchorage {letter}")]
    assert not any(b.contains(lat, lon) for b in others)


def test_lalb_first_vertex_matches_the_2025_rule(lalb):
    f = by_name(lalb, "F")
    assert f.vertices[0] == pytest.approx((dms(33, 43, 5.1), -dms(118, 8, 4.0)))
    g = by_name(lalb, "G")
    assert g.vertices[2] == pytest.approx((dms(33, 42, 25.8), -dms(118, 14, 19.2)))


# ---------- command line ----------

def test_check_port_prints_and_succeeds(capsys):
    assert main(["--check-port", str(LALB)]) == 0
    out = capsys.readouterr().out
    assert "6 anchorage, 0 berth" in out and "NOT ready for a run" in out
    assert "Anchorage F" in out and "km2" in out


def test_run_with_partial_port_is_refused(tmp_path, capsys):
    f = tmp_path / "ais.csv"
    f.write_text(HEADER + "\n", encoding="utf-8")
    assert main(["--port", str(LALB), str(f)]) == 2
    assert "partial" in capsys.readouterr().err


def test_run_needs_port_and_files(tmp_path):
    with pytest.raises(SystemExit):
        main([str(tmp_path / "x.csv")])
    with pytest.raises(SystemExit):
        main(["--port", str(LALB)])


def test_check_port_reports_a_broken_file(tmp_path, capsys):
    p = write_port(tmp_path, [{"name": "bow", "kind": "berth",
                               "polygon": [[0, 0], [1, 1], [0, 1], [1, 0]]}])
    assert main(["--check-port", str(p)]) == 2
    assert "cross" in capsys.readouterr().err
