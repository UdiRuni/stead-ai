"""Port calls from AIS: real vessel arrival and waiting times at one port.

Backtest step 2 (poc/DATA_AUDIT.md section 4), first slice: the extractor. It turns
AIS position reports in the NOAA and BOEM Marine Cadastre CSV layout into port
calls: when a vessel reached the port (first report inside an anchorage or berth
area), when it was first moored at a berth, when it was last seen in the port, and
so how long it waited. A second step measures lateness against the vessel's own
calling pattern, because public data has no carrier schedule (DATA_AUDIT.md,
dataset C): lateness here means "later than this vessel's usual interval", not
"later than promised".

Data: Marine Cadastre AIS, licensed CC0 1.0 Universal
(https://github.com/ocm-marinecadastre/ais-vessel-traffic, read 2026-11-21). Daily
CSV files (zipped or not) with at least these columns, matched without regard to
case: MMSI, BaseDateTime, LAT, LON, SOG, VesselType, Length. VesselName is used if
present. The column names follow the Marine Cadastre CSV layout as we know it; check
them against the first real file before trusting a run.

No real AIS file has been run through this yet. On 2026-11-21 the download hosts
(coast.noaa.gov, marinecadastre.gov and the Azure blob store with the GeoParquet
files) were not reachable from the agent's sandbox. Every test uses invented
reports. Port areas are read from a JSON file (see load_port). Areas may be boxes or
polygons; polygon vertices may be given as printed in a regulation (degrees, minutes,
seconds), so the file can be checked line by line against its source. The first real
port file is poc/data/ports/los_angeles_long_beach.json (2026-11-24): its anchorages
come from 33 CFR 110.214, but it has no berth areas yet, so it passes --check-port and
is refused for a run until berths are drawn from a sourced chart.

Method, with every assumption in Rules:
  - Only reports inside one of the port's boxes are kept, so a day of national data
    (millions of rows) fits in memory.
  - Two in-port reports of one vessel more than visit_gap_hours apart start a new
    call. An AIS outage of that length while at berth would split one call in two.
  - A vessel counts as cargo if any report gives a VesselType in vessel_types (AIS
    codes 70 to 79 are cargo ships) and its largest stated Length is at least
    min_length_m. AIS has no separate code for container ships; length is the proxy.
  - Moored means inside a berth box with SOG at or below moored_sog_kn.
  - A call that starts within visit_gap_hours of the first report in the data, or
    ends within visit_gap_hours of the last, is flagged as cut off: its true arrival
    or departure may lie outside the files read. Cut-off calls are left out of the
    waiting time figures.

Run:  (cd poc && python3 -m steadpoc.portcalls --port PORT.json AIS_2024_01_01.zip ...)
Check a port file only:  (cd poc && python3 -m steadpoc.portcalls --check-port PORT.json)
"""
import argparse
import csv
import io
import json
import math
import re
import statistics
import sys
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, Iterator

REQUIRED_COLUMNS = ("mmsi", "basedatetime", "lat", "lon", "sog", "vesseltype", "length")
BOX_KINDS = ("anchorage", "berth")


@dataclass(frozen=True)
class Box:
    name: str
    kind: str                     # "anchorage" or "berth"
    lat_min: float
    lat_max: float
    lon_min: float
    lon_max: float

    def __post_init__(self):
        if self.kind not in BOX_KINDS:
            raise ValueError(f"box {self.name!r}: kind must be one of {BOX_KINDS}, not {self.kind!r}")
        if not (-90 <= self.lat_min < self.lat_max <= 90):
            raise ValueError(f"box {self.name!r}: need -90 <= lat_min < lat_max <= 90")
        if not (-180 <= self.lon_min < self.lon_max <= 180):
            raise ValueError(f"box {self.name!r}: need -180 <= lon_min < lon_max <= 180")

    def contains(self, lat: float, lon: float) -> bool:
        return self.lat_min <= lat <= self.lat_max and self.lon_min <= lon <= self.lon_max


_DMS = re.compile(
    r"(\d{1,2})\D+?(\d{1,2})\D+?(\d{1,2}(?:\.\d+)?)[^NSns\d]*([NSns])"
    r"[^\d]*?(\d{1,3})\D+?(\d{1,2})\D+?(\d{1,2}(?:\.\d+)?)[^EWew\d]*([EWew])")


def parse_dms(text: str) -> tuple[float, float]:
    """One position as printed in a US regulation, to decimal (lat, lon).

    Accepts the layouts found in 33 CFR 110.214 and its Federal Register amendments,
    for example "33°43′05.1″ N 118°08′04.0″ W", "33°-44'-37.0\" N 118°-13'-00.0\" W"
    and "33-43' 40.5' N, 118-10' 30\" W". Minutes and seconds must be under 60.
    """
    m = _DMS.search(text)
    if not m:
        raise ValueError(f"cannot read a degrees-minutes-seconds position from {text!r}")
    out = []
    for deg, mins, secs, hemi, limit in ((m[1], m[2], m[3], m[4], 90), (m[5], m[6], m[7], m[8], 180)):
        d, mi, se = int(deg), int(mins), float(secs)
        if mi >= 60 or se >= 60:
            raise ValueError(f"minutes and seconds must be under 60 in {text!r}")
        value = d + mi / 60 + se / 3600
        if value > limit:
            raise ValueError(f"position out of range in {text!r}")
        out.append(-value if hemi.upper() in "SW" else value)
    return out[0], out[1]


def _segments_cross(p1, p2, p3, p4) -> bool:
    """True if segment p1-p2 properly crosses segment p3-p4 (shared ends do not count)."""
    def orient(a, b, c):
        v = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        return (v > 1e-15) - (v < -1e-15)
    d1, d2 = orient(p3, p4, p1), orient(p3, p4, p2)
    d3, d4 = orient(p1, p2, p3), orient(p1, p2, p4)
    return d1 * d2 < 0 and d3 * d4 < 0


def _on_segment(p, a, b, eps=1e-12) -> bool:
    cross = (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
    if abs(cross) > eps:
        return False
    return (min(a[0], b[0]) - eps <= p[0] <= max(a[0], b[0]) + eps
            and min(a[1], b[1]) - eps <= p[1] <= max(a[1], b[1]) + eps)


@dataclass(frozen=True)
class Area:
    """A polygon port area: vertices (lat, lon) in order; the last joins the first.

    Positions are treated as flat x-y over the few kilometres of a port, which is
    accurate enough to decide whether a ship is inside an anchorage. A point on an
    edge counts as inside. Areas may not cross the 180th meridian.
    """
    name: str
    kind: str                     # "anchorage" or "berth"
    vertices: tuple[tuple[float, float], ...]

    def __post_init__(self):
        if self.kind not in BOX_KINDS:
            raise ValueError(f"area {self.name!r}: kind must be one of {BOX_KINDS}, not {self.kind!r}")
        vs = self.vertices
        if len(vs) >= 2 and vs[0] == vs[-1]:
            vs = vs[:-1]          # a closing vertex repeated from the source is allowed
            object.__setattr__(self, "vertices", vs)
        if len(vs) < 3:
            raise ValueError(f"area {self.name!r}: needs at least 3 distinct vertices")
        for lat, lon in vs:
            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                raise ValueError(f"area {self.name!r}: vertex ({lat}, {lon}) out of range")
        if len(set(vs)) != len(vs):
            raise ValueError(f"area {self.name!r}: repeated vertex")
        if max(v[1] for v in vs) - min(v[1] for v in vs) > 180:
            raise ValueError(f"area {self.name!r}: crosses the 180th meridian, not supported")
        n = len(vs)
        edges = [(vs[i], vs[(i + 1) % n]) for i in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                if j == i + 1 or (i == 0 and j == n - 1):
                    continue      # neighbours share a vertex
                if _segments_cross(*edges[i], *edges[j]):
                    raise ValueError(f"area {self.name!r}: edges {i + 1} and {j + 1} cross;"
                                     " check the vertex order against the source")
        if self.area_km2() < 1e-6:
            raise ValueError(f"area {self.name!r}: has no area (vertices in a line)")

    @property
    def bounds(self) -> tuple[float, float, float, float]:
        lats = [v[0] for v in self.vertices]
        lons = [v[1] for v in self.vertices]
        return min(lats), max(lats), min(lons), max(lons)

    def contains(self, lat: float, lon: float) -> bool:
        lat_min, lat_max, lon_min, lon_max = self.bounds
        if not (lat_min <= lat <= lat_max and lon_min <= lon <= lon_max):
            return False
        vs = self.vertices
        n = len(vs)
        inside = False
        for i in range(n):
            a, b = vs[i], vs[(i + 1) % n]
            if _on_segment((lat, lon), a, b):
                return True
            if (a[0] > lat) != (b[0] > lat):
                cross_lon = a[1] + (lat - a[0]) * (b[1] - a[1]) / (b[0] - a[0])
                if lon < cross_lon:
                    inside = not inside
        return inside

    def area_km2(self) -> float:
        """Shoelace area on a local flat projection (km per degree at the mean latitude)."""
        vs = self.vertices
        mean_lat = math.radians(sum(v[0] for v in vs) / len(vs))
        ky, kx = 111.32, 111.32 * math.cos(mean_lat)
        pts = [(v[1] * kx, v[0] * ky) for v in vs]
        s = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
                for i in range(len(pts)))
        return abs(s) / 2


@dataclass(frozen=True)
class Port:
    name: str
    boxes: tuple                  # Box or Area, each with name, kind and contains()
    source: str                   # where the areas were drawn from
    missing: str = ""             # what the file still lacks (a partial port), else ""

    def __post_init__(self):
        if not self.boxes:
            raise ValueError(f"port {self.name!r}: needs at least one box")
        if not any(b.kind == "berth" for b in self.boxes) and not self.missing:
            raise ValueError(f"port {self.name!r}: needs at least one berth box")

    @property
    def runnable(self) -> bool:
        """A run needs a berth area, or waiting time and arrivals of ships that never
        anchor cannot be measured."""
        return any(b.kind == "berth" for b in self.boxes)

    def locate(self, lat: float, lon: float) -> str | None:
        """'berth' if in any berth box (berth wins on overlap), 'anchorage', or None."""
        kinds = {b.kind for b in self.boxes if b.contains(lat, lon)}
        if "berth" in kinds:
            return "berth"
        return "anchorage" if kinds else None


def _area_from_json(b: dict):
    name, kind = str(b["name"]), str(b["kind"])
    given = [k for k in ("lat_min", "polygon", "vertices_dms") if k in b]
    if len(given) != 1:
        raise ValueError(f"area {name!r}: give exactly one of lat_min..lon_max (a box),"
                         " polygon or vertices_dms")
    if given[0] == "lat_min":
        return Box(name=name, kind=kind, lat_min=float(b["lat_min"]), lat_max=float(b["lat_max"]),
                   lon_min=float(b["lon_min"]), lon_max=float(b["lon_max"]))
    if given[0] == "polygon":
        return Area(name, kind, tuple((float(lat), float(lon)) for lat, lon in b["polygon"]))
    return Area(name, kind, tuple(parse_dms(str(t)) for t in b["vertices_dms"]))


def load_port(path: str | Path, allow_partial: bool = False) -> Port:
    """Read a port definition: {"name", "source", "boxes": [...]}.

    Each entry of "boxes" has a name and a kind and one of: lat_min, lat_max, lon_min,
    lon_max (a box); "polygon": [[lat, lon], ...]; or "vertices_dms": positions as
    printed in the source. Other keys (for example a per-area "source") are kept in the
    file for the reader and ignored here. A file may say what it still lacks in
    "missing"; such a partial port loads only with allow_partial=True.
    """
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    try:
        boxes = tuple(_area_from_json(b) for b in data["boxes"])
        missing = str(data.get("missing", "") or "")
        if missing and not allow_partial:
            raise ValueError(f"{path}: port file is partial and cannot be used for a run yet:"
                             f" {missing}")
        return Port(name=str(data["name"]), boxes=boxes, source=str(data["source"]),
                    missing=missing)
    except KeyError as missing_key:
        raise ValueError(f"{path}: port file is missing {missing_key}") from None


def describe_port(port: Port) -> str:
    """Plain text check of a port file: every area, its size and where it lies."""
    lines = [f"port: {port.name}", f"source: {port.source}"]
    for b in port.boxes:
        if isinstance(b, Area):
            lat_min, lat_max, lon_min, lon_max = b.bounds
            lines.append(f"  {b.kind:9} {b.name}: polygon, {len(b.vertices)} vertices,"
                         f" {b.area_km2():.2f} km2, lat {lat_min:.4f} to {lat_max:.4f},"
                         f" lon {lon_min:.4f} to {lon_max:.4f}")
        else:
            lines.append(f"  {b.kind:9} {b.name}: box, lat {b.lat_min:.4f} to {b.lat_max:.4f},"
                         f" lon {b.lon_min:.4f} to {b.lon_max:.4f}")
    kinds = [b.kind for b in port.boxes]
    lines.append(f"areas: {len(kinds)} ({kinds.count('anchorage')} anchorage,"
                 f" {kinds.count('berth')} berth)")
    if port.runnable:
        lines.append("status: ready for a run")
    else:
        lines.append("status: NOT ready for a run, no berth area"
                     + (f" ({port.missing})" if port.missing else ""))
    return "\n".join(lines)


@dataclass(frozen=True)
class Rules:
    """Every assumption of the method. Defaults are our choice, not an industry rule."""
    vessel_types: tuple[int, ...] = tuple(range(70, 80))   # AIS cargo codes
    min_length_m: float = 200.0      # proxy for an ocean container ship (assumption)
    moored_sog_kn: float = 0.5       # at or below this in a berth box = moored (assumption)
    visit_gap_hours: float = 24.0    # longer silence in port = a new call (assumption)
    min_interval_days: float = 5.0   # calling pattern sanity bounds (assumption)
    max_interval_days: float = 120.0
    min_history_calls: int = 3       # earlier calls needed before lateness is measured

    def __post_init__(self):
        if self.min_length_m < 0 or self.moored_sog_kn < 0:
            raise ValueError("min_length_m and moored_sog_kn must be 0 or more")
        if self.visit_gap_hours <= 0:
            raise ValueError("visit_gap_hours must be more than 0")
        if not (0 < self.min_interval_days < self.max_interval_days):
            raise ValueError("need 0 < min_interval_days < max_interval_days")
        if self.min_history_calls < 2:
            raise ValueError("min_history_calls must be at least 2 (one interval)")


@dataclass(frozen=True)
class Ping:
    mmsi: str
    t: datetime
    where: str                    # "berth" or "anchorage"
    sog: float | None


@dataclass
class Vessel:
    mmsi: str
    name: str = ""
    types: set = field(default_factory=set)
    length_m: float | None = None


@dataclass
class ReadReport:
    rows: int = 0
    kept: int = 0
    skipped: dict = field(default_factory=dict)     # reason -> count
    first_t: datetime | None = None
    last_t: datetime | None = None
    files: list = field(default_factory=list)

    def skip(self, reason: str) -> None:
        self.skipped[reason] = self.skipped.get(reason, 0) + 1


def _parse_time(text: str) -> datetime:
    return datetime.fromisoformat(text.strip().replace(" ", "T").rstrip("Z"))


def _float_or_none(text: str | None) -> float | None:
    if text is None or not text.strip():
        return None
    return float(text)


def _open_csv_texts(path: Path) -> Iterator[tuple[str, io.TextIOBase]]:
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as z:
            names = [n for n in z.namelist() if n.lower().endswith(".csv")]
            if not names:
                raise ValueError(f"{path}: zip holds no .csv file")
            for n in names:
                with z.open(n) as raw:
                    yield f"{path.name}:{n}", io.TextIOWrapper(raw, encoding="utf-8", newline="")
    else:
        with open(path, encoding="utf-8", newline="") as fh:
            yield path.name, fh


def read_ais(sources: Iterable[str | Path | io.TextIOBase], port: Port
             ) -> tuple[list[Ping], dict[str, Vessel], ReadReport]:
    """Keep the reports inside the port's boxes; count every row skipped, by reason.

    A source may be a path (.csv or .zip) or an open text stream. A file without the
    required columns raises ValueError: a wrong layout must stop the run, not shrink it.
    """
    report = ReadReport()
    pings: list[Ping] = []
    vessels: dict[str, Vessel] = {}

    def streams():
        for s in sources:
            if isinstance(s, (str, Path)):
                yield from _open_csv_texts(Path(s))
            else:
                yield getattr(s, "name", "<stream>"), s

    for label, fh in streams():
        report.files.append(label)
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise ValueError(f"{label}: empty file, no header row")
        lower = {f.strip().lower(): f for f in reader.fieldnames}
        missing = [c for c in REQUIRED_COLUMNS if c not in lower]
        if missing:
            raise ValueError(f"{label}: missing columns {', '.join(missing)}")
        col = {c: lower[c] for c in lower}
        for raw in reader:
            report.rows += 1
            mmsi = (raw.get(col["mmsi"]) or "").strip()
            if not mmsi:
                report.skip("no MMSI")
                continue
            try:
                t = _parse_time(raw.get(col["basedatetime"]) or "")
                lat = float(raw[col["lat"]])
                lon = float(raw[col["lon"]])
            except (ValueError, TypeError):
                report.skip("bad time or position")
                continue
            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                report.skip("position out of range")
                continue
            if report.first_t is None or t < report.first_t:
                report.first_t = t
            if report.last_t is None or t > report.last_t:
                report.last_t = t
            where = port.locate(lat, lon)
            if where is None:
                report.skip("outside the port")
                continue
            try:
                sog = _float_or_none(raw.get(col["sog"]))
                vtype = _float_or_none(raw.get(col["vesseltype"]))
                length = _float_or_none(raw.get(col["length"]))
            except ValueError:
                report.skip("bad speed, type or length")
                continue
            v = vessels.setdefault(mmsi, Vessel(mmsi))
            if vtype is not None:
                v.types.add(int(vtype))
            if length is not None and length > 0:
                v.length_m = max(v.length_m or 0.0, length)
            name = (raw.get(col["vesselname"]) or "").strip() if "vesselname" in col else ""
            if name and not v.name:
                v.name = name
            pings.append(Ping(mmsi, t, where, sog))
            report.kept += 1
    return pings, vessels, report


def is_cargo(v: Vessel, rules: Rules) -> tuple[bool, str]:
    if not v.types:
        return False, "vessel type never stated"
    if not v.types & set(rules.vessel_types):
        return False, f"not a cargo vessel type ({sorted(v.types)})"
    if v.length_m is None:
        return False, "length never stated"
    if v.length_m < rules.min_length_m:
        return False, f"shorter than {rules.min_length_m:g} m ({v.length_m:g} m)"
    return True, ""


@dataclass(frozen=True)
class PortCall:
    mmsi: str
    name: str
    arrived: datetime             # first report inside any port box
    berthed: datetime | None      # first moored report in a berth box; None if never
    left: datetime                # last report inside any port box
    reports: int
    cut_at_start: bool            # true arrival may be before the data
    cut_at_end: bool              # true departure may be after the data

    @property
    def complete(self) -> bool:
        return not (self.cut_at_start or self.cut_at_end)

    @property
    def waited_hours(self) -> float | None:
        if self.berthed is None:
            return None
        return (self.berthed - self.arrived).total_seconds() / 3600

    @property
    def in_port_hours(self) -> float:
        return (self.left - self.arrived).total_seconds() / 3600


def port_calls(pings: list[Ping], vessels: dict[str, Vessel], report: ReadReport,
               rules: Rules = Rules()) -> tuple[list[PortCall], dict[str, str]]:
    """Group in-port reports into calls. Returns calls (by arrival) and excluded vessels."""
    gap = timedelta(hours=rules.visit_gap_hours)
    excluded: dict[str, str] = {}
    by_vessel: dict[str, list[Ping]] = {}
    for p in pings:
        by_vessel.setdefault(p.mmsi, []).append(p)
    calls: list[PortCall] = []
    for mmsi, ps in by_vessel.items():
        ok, why = is_cargo(vessels[mmsi], rules)
        if not ok:
            excluded[mmsi] = why
            continue
        ps.sort(key=lambda p: p.t)
        groups: list[list[Ping]] = [[ps[0]]]
        for prev, cur in zip(ps, ps[1:]):
            if cur.t - prev.t > gap:
                groups.append([cur])
            else:
                groups[-1].append(cur)
        for g in groups:
            moored = [p.t for p in g if p.where == "berth" and p.sog is not None
                      and p.sog <= rules.moored_sog_kn]
            calls.append(PortCall(
                mmsi=mmsi, name=vessels[mmsi].name, arrived=g[0].t,
                berthed=moored[0] if moored else None, left=g[-1].t, reports=len(g),
                cut_at_start=report.first_t is not None and g[0].t - report.first_t < gap,
                cut_at_end=report.last_t is not None and report.last_t - g[-1].t < gap))
    calls.sort(key=lambda c: (c.arrived, c.mmsi))
    return calls, excluded


@dataclass(frozen=True)
class Lateness:
    call: PortCall
    expected: datetime            # previous arrival plus the median of earlier intervals
    days_late: float              # negative = early


def lateness_vs_pattern(calls: list[PortCall], rules: Rules = Rules()) -> list[Lateness]:
    """Lateness of each call against the vessel's own earlier calling interval.

    Uses only calls before the one measured (no look-ahead), so it can be replayed day
    by day like a live warning. Needs rules.min_history_calls earlier calls with a
    known arrival, and a median interval inside the sanity bounds; otherwise the call
    gets no figure. Calls cut off at the start have an unknown arrival and are never
    used, neither as history nor as the call measured.
    """
    out: list[Lateness] = []
    by_vessel: dict[str, list[PortCall]] = {}
    for c in calls:
        if not c.cut_at_start:
            by_vessel.setdefault(c.mmsi, []).append(c)
    for cs in by_vessel.values():
        cs.sort(key=lambda c: c.arrived)
        for i in range(rules.min_history_calls, len(cs)):
            history = cs[:i]
            intervals = [(b.arrived - a.arrived).total_seconds() / 86400
                         for a, b in zip(history, history[1:])]
            median = statistics.median(intervals)
            if not (rules.min_interval_days <= median <= rules.max_interval_days):
                continue
            expected = history[-1].arrived + timedelta(days=median)
            days = (cs[i].arrived - expected).total_seconds() / 86400
            out.append(Lateness(cs[i], expected, round(days, 3)))
    out.sort(key=lambda x: (x.call.arrived, x.call.mmsi))
    return out


def _percentile(values: list[float], q: float) -> float:
    """Nearest-rank percentile, q in (0, 1]."""
    if not 0 < q <= 1:
        raise ValueError("q must be in (0, 1]")
    s = sorted(values)
    return s[max(0, math.ceil(q * len(s)) - 1)]


@dataclass(frozen=True)
class Summary:
    calls: int
    complete: int
    berthed: int                  # complete calls with a moored report
    never_berthed: int            # complete calls that left without mooring
    median_wait_h: float | None
    p90_wait_h: float | None
    share_wait_over_24h: float | None
    measured_lateness: int
    median_days_late: float | None


def summarise(calls: list[PortCall], late: list[Lateness]) -> Summary:
    complete = [c for c in calls if c.complete]
    waits = [c.waited_hours for c in complete if c.waited_hours is not None]
    return Summary(
        calls=len(calls), complete=len(complete), berthed=len(waits),
        never_berthed=sum(1 for c in complete if c.berthed is None),
        median_wait_h=round(statistics.median(waits), 2) if waits else None,
        p90_wait_h=round(_percentile(waits, 0.9), 2) if waits else None,
        share_wait_over_24h=round(sum(w > 24 for w in waits) / len(waits), 4) if waits else None,
        measured_lateness=len(late),
        median_days_late=round(statistics.median(x.days_late for x in late), 3) if late else None)


def write_calls_csv(calls: list[PortCall], late: list[Lateness], out: io.TextIOBase) -> None:
    lat = {(x.call.mmsi, x.call.arrived): x for x in late}
    w = csv.writer(out, lineterminator="\n")
    w.writerow(["mmsi", "name", "arrived", "berthed", "left", "waited_hours",
                "in_port_hours", "reports", "cut_at_start", "cut_at_end",
                "expected_by_pattern", "days_late_vs_pattern"])
    for c in calls:
        x = lat.get((c.mmsi, c.arrived))
        w.writerow([c.mmsi, c.name, c.arrived.isoformat(),
                    c.berthed.isoformat() if c.berthed else "", c.left.isoformat(),
                    "" if c.waited_hours is None else f"{c.waited_hours:.2f}",
                    f"{c.in_port_hours:.2f}", c.reports, int(c.cut_at_start), int(c.cut_at_end),
                    x.expected.isoformat() if x else "", "" if x is None else f"{x.days_late:.3f}"])


def render(port: Port, report: ReadReport, s: Summary, excluded: dict[str, str]) -> str:
    def fmt(v, unit=""):
        return "n/a" if v is None else f"{v:g}{unit}"
    lines = [
        "AIS PORT CALLS. Positions are public data (Marine Cadastre, CC0); the method",
        "and its thresholds are our assumptions (steadpoc.portcalls.Rules).",
        f"port: {port.name} (boxes from: {port.source})",
        f"files read: {len(report.files)}, rows: {report.rows}, in port: {report.kept}",
        f"data window: {report.first_t} to {report.last_t}",
    ]
    for reason, n in sorted(report.skipped.items()):
        lines.append(f"  skipped, {reason}: {n}")
    lines += [
        f"vessels left out (not cargo, too small or unknown): {len(excluded)}",
        f"port calls: {s.calls}, complete: {s.complete} (others cut off by the data window)",
        f"complete calls that moored: {s.berthed}, left without mooring: {s.never_berthed}",
        f"wait from arrival to berth: median {fmt(s.median_wait_h, ' h')}, "
        f"90th percentile {fmt(s.p90_wait_h, ' h')}, "
        f"share over 24 h {fmt(None if s.share_wait_over_24h is None else round(s.share_wait_over_24h * 100, 1), '%')}",
        f"calls with lateness against the vessel's own pattern: {s.measured_lateness}, "
        f"median {fmt(s.median_days_late, ' days')}",
        "Lateness is against the vessel's usual interval, not the carrier schedule.",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python3 -m steadpoc.portcalls",
                                 description="Port calls and waiting times from AIS files.")
    ap.add_argument("files", nargs="*", help="Marine Cadastre AIS CSV or ZIP files")
    ap.add_argument("--port", help="port definition JSON")
    ap.add_argument("--check-port", metavar="PORT.json",
                    help="only read and describe a port file (partial files allowed), then stop")
    ap.add_argument("--csv", help="write one row per call to this file")
    ap.add_argument("--min-length", type=float, default=Rules.min_length_m)
    ap.add_argument("--gap-hours", type=float, default=Rules.visit_gap_hours)
    args = ap.parse_args(argv)
    if args.check_port:
        try:
            print(describe_port(load_port(args.check_port, allow_partial=True)))
        except (OSError, ValueError) as e:
            print(f"error: {e}", file=sys.stderr)
            return 2
        return 0
    if not args.port or not args.files:
        ap.error("a run needs --port and at least one AIS file (or use --check-port)")
    try:
        port = load_port(args.port)
        rules = Rules(min_length_m=args.min_length, visit_gap_hours=args.gap_hours)
        pings, vessels, report = read_ais(args.files, port)
    except (OSError, ValueError, zipfile.BadZipFile) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    calls, excluded = port_calls(pings, vessels, report, rules)
    late = lateness_vs_pattern(calls, rules)
    print(render(port, report, summarise(calls, late), excluded))
    if args.csv:
        with open(args.csv, "w", encoding="utf-8", newline="") as out:
            write_calls_csv(calls, late, out)
        print(f"calls written to {args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
